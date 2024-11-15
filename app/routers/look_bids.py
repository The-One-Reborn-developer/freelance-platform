from aiogram import Router, F
from aiogram.types import (Message,
                           CallbackQuery,
                           InlineKeyboardButton,
                           InlineKeyboardMarkup)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.database.queues.get_bids_by_id import get_bids_by_id
from app.database.queues.get_user_by_id import get_user_by_id
from app.database.queues.close_bid import close_bid
from app.database.queues.get_responses_by_id import get_responses_by_id
from app.database.queues.put_response import put_response

from app.scripts.save_customer_chat_message import save_customer_chat_message

from app.keyboards.menu import customer_menu_keyboard


look_bids_router = Router()


class LookBids(StatesGroup):
    selection = State()
    write_to_performer = State()
    message = State()


@look_bids_router.callback_query(F.data == 'look_bids')
async def look_bids_callback_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(LookBids.selection)

    bids = get_bids_by_id(callback.from_user.id)

    if bids:
        for bid in bids:
            if bid['instrument_provided'] == 1:
                bid['instrument_provided'] = 'Да'
            elif bid['instrument_provided'] == 0:
                bid['instrument_provided'] = 'Нет'
            
            content = f'<b>Номер заказа:</b> <u>{bid["id"]}</u>\n' \
                      f'<b>Описание:</b> {bid["description"]}\n' \
                      f'<b>До какого числа нужно выполнить работу:</b> <i>{bid["deadline"]}</i>\n' \
                      f'<b>Предоставляет инструмент:</b> <i>{bid["instrument_provided"]}</i>'
            
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text='Просмотреть отклики',
                                             callback_data=f'look_responses_{bid["id"]}'),
                    ],
                    [
                        InlineKeyboardButton(text='Закрыть заказ как выполненный ✅',
                                             callback_data=f'close_bid_{bid["id"]}')
                    ]
                ]
            )

            await callback.message.answer(content, parse_mode='HTML', reply_markup=keyboard)
    else:
        content = 'На данный момент у Вас нет активных заказов 🙂'

        await callback.message.answer(content)


@look_bids_router.callback_query(LookBids.selection)
async def look_bids_selection_handler(callback: CallbackQuery, state: FSMContext):
    if callback.data.startswith('close_bid_'):
        bid_id = callback.data.split('_')[2]
        
        bid_closed = close_bid(int(bid_id))

        if bid_closed:
            user = get_user_by_id(callback.from_user.id)
            content = f'Заказ №{bid_id} закрыт как выполненный ✅'
            
            await callback.message.answer(content)
        elif not bid_closed:
            content = f'Заказ №{bid_id} уже закрыт как выполненный или не найден.'
            
            await callback.message.answer(content)
        else:
            content = 'Произошла ошибка 🙁\nПопробуйте еще раз или обратитесь в поддержку.'
            
            await callback.message.answer(content)
    elif callback.data.startswith('look_responses_'):
        await state.set_state(LookBids.write_to_performer)

        bid_id = callback.data.split('_')[2]

        responses = get_responses_by_id(bid_id)

        if responses:
            for response in responses:
                content = f'<b>Отклик:</b> <u>{response["id"]}</u>\n' \
                          f'<b>Имя исполнителя:</b> {response["performer_full_name"]}\n' \
                          f'<b>Ставка:</b> {response["performer_rate"]}\n' \
                          f'<b>Стаж работы в годах:</b> {response["performer_experience"]}'
                
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(text='Написать подрядчику ✉️',
                                                 callback_data=f'write_to_performer_{response["performer_telegram_id"]}_{bid_id}'),
                        ]
                    ]
                )

                await callback.message.answer(content, parse_mode='HTML', reply_markup=keyboard)
        else:
            content = 'На данный момент у заказа нет откликов 🙂'

            await callback.message.answer(content)


@look_bids_router.callback_query(LookBids.write_to_performer)
async def look_bids_write_to_performer_handler(callback: CallbackQuery, state: FSMContext):
    performer_telegram_id = callback.data.split('_')[3]
    performer_chat_id = get_user_by_id(performer_telegram_id)[7]

    bid_id = callback.data.split('_')[4]

    await state.update_data(performer_telegram_id=performer_telegram_id,
                            performer_chat_id=performer_chat_id,
                            bid_id=bid_id)
    await state.set_state(LookBids.message)

    content = 'Введите текст сообщения.'

    await callback.message.answer(content)


@look_bids_router.message(LookBids.message)
async def look_bids_write_to_performer_handler(message: Message, state: FSMContext):
    data = await state.get_data()

    performer_chat_id = data['performer_chat_id']
    customer_full_name = get_user_by_id(message.from_user.id)[2]

    bid_id = data['bid_id']

    put_response(bid_id=bid_id,
                 performer_telegram_id=data['performer_telegram_id'],
                 chat_started=True)

    message_content = f'Сообщение от заказчика {customer_full_name}:\n\n{message.text}'

    await message.bot.send_message(chat_id=performer_chat_id,
                                   text=message_content)
    
    customer_telegram_id = get_user_by_id(message.from_user.id)[1]
    performer_telegram_id = data['performer_telegram_id']
    performer_full_name = get_user_by_id(performer_telegram_id)[2]

    save_customer_chat_message(bid_id,
                               customer_telegram_id,
                               performer_telegram_id,
                               customer_full_name,
                               performer_full_name,
                               message.text)
    
    content = 'Сообщение отправлено!'

    await state.clear()

    await message.answer(content, reply_markup=customer_menu_keyboard())