from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.database.queues.get_responses_by_performer_telegram_id import get_responses_by_performer_telegram_id
from app.database.queues.get_bid_by_id import get_bid_by_id
from app.database.queues.get_user_by_id import get_user_by_id

from app.scripts.save_performer_chat_message import save_performer_chat_message

from app.keyboards.menu import performer_menu_keyboard


look_chats_router = Router()


class LookChats(StatesGroup):
    message = State()


@look_chats_router.callback_query(F.data == 'look_chats')
async def look_chats_handler(callback: CallbackQuery):
    responses = get_responses_by_performer_telegram_id(callback.from_user.id)

    if responses:
        for response in responses:
            bid_closed = get_bid_by_id(response["bid_id"])[6]
            
            if bid_closed:
                continue
            else:
                customer_telegram_id = get_bid_by_id(response["bid_id"])[1]
                customer_full_name = get_user_by_id(customer_telegram_id)[2]

                content = f'<b>Отклик:</b> <u>{response["id"]}</u>\n' \
                          f'<b>Номер заказа:</b> <i>{response["bid_id"]}</i>\n' \
                          f'<b>Имя заказчика:</b> <i>{customer_full_name}</i>'
                        
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(text='Написать заказчику ✉️',
                                                callback_data=f'write_to_customer_{customer_telegram_id}_{response["bid_id"]}')
                        ]
                    ]
                )
                
                await callback.message.answer(content, reply_markup=keyboard, parse_mode='HTML')
    else:
        content = 'Вам ещё не писал заказчик.\n' \
                  'Как только какой-либо заказчик напишет Вам, вы сможете увидеть его здесь.'

        await callback.message.answer(content, reply_markup=performer_menu_keyboard())


@look_chats_router.callback_query(F.data.startswith('write_to_customer_'))
async def write_to_customer_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(LookChats.message)
    await state.update_data(customer_telegram_id=callback.data.split('_')[3],
                            bid_id=callback.data.split('_')[4])

    content = 'Введите текст сообщения.'

    await callback.message.answer(content)


@look_chats_router.message(LookChats.message)
async def look_chats_message_handler(message: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    customer_telegram_id = data['customer_telegram_id']
    performer_telegram_id = message.from_user.id
    bid_id = data['bid_id']
    customer_full_name = get_user_by_id(customer_telegram_id)[2]
    performer_full_name = get_user_by_id(performer_telegram_id)[2]
    
    save_performer_chat_message(bid_id,
                      customer_telegram_id,
                      performer_telegram_id,
                      customer_full_name,
                      performer_full_name,
                      message.text)
    
    message_content = f'Сообщение от подрядчика {get_user_by_id(message.from_user.id)[2]}:\n\n{message.text}'

    await message.bot.send_message(chat_id=customer_telegram_id,
                                   text=message_content)
    
    content = 'Сообщение отправлено!'

    await state.clear()

    await message.answer(content, reply_markup=performer_menu_keyboard())