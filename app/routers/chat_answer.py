from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.tasks.celery_app import get_user_by_telegram_id_task

from app.scripts.save_performer_chat_message import save_performer_chat_message
from app.scripts.save_customer_chat_message import save_customer_chat_message

from app.keyboards.chat_answer import chat_answer_keyboard


chat_answer_router = Router()


class ChatAnswer(StatesGroup):
    message = State()


@chat_answer_router.callback_query(F.data.startswith('answer_'))
async def chat_answer_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ChatAnswer.message)

    callback_data = callback.data.split('_')
    bid_id = callback_data[1]
    customer_telegram_id = callback_data[2]
    performer_telegram_id = callback_data[3]
    is_customer = callback_data[4] == 'True'

    customer_full_name = get_user_by_telegram_id_task.delay(customer_telegram_id).get()[2]
    performer_full_name = get_user_by_telegram_id_task.delay(performer_telegram_id).get()[2]

    await state.update_data(bid_id=bid_id,
                            customer_telegram_id=customer_telegram_id,
                            performer_telegram_id=performer_telegram_id,
                            customer_full_name=customer_full_name,
                            performer_full_name=performer_full_name,
                            is_customer=is_customer)
    
    if is_customer:
        content = f'Начните писать ответ мастеру, можете прикрепить видео 📹'
    else:
        content = f'Начните писать ответ заказчику, можете прикрепить видео 📹'

    await callback.answer(content, show_alert=True)


@chat_answer_router.message(ChatAnswer.message)
async def chat_answer_message_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    bid_id = data['bid_id']
    customer_telegram_id = data['customer_telegram_id']
    performer_telegram_id = data['performer_telegram_id']
    customer_full_name = data['customer_full_name']
    performer_full_name = data['performer_full_name']
    is_customer = data['is_customer']

    if is_customer:
        performer_chat_id = get_user_by_telegram_id_task.delay(performer_telegram_id).get()[7]

        if message.video:
            message_content = f'Заказчик {customer_full_name}:\n\n{message.caption}'
            save_customer_chat_message(bid_id,
                                    customer_telegram_id,
                                    performer_telegram_id,
                                    customer_full_name,
                                    performer_full_name,
                                    message.caption,
                                    message.video.file_id)

            await message.bot.send_video(chat_id=performer_chat_id,
                                        video=message.video.file_id,
                                        caption=message_content,
                                        parse_mode='HTML',
                                        reply_markup=chat_answer_keyboard(bid_id,
                                                                        customer_telegram_id,
                                                                        performer_telegram_id,
                                                                        is_customer=False))
        else:
            message_content = f'Заказчик {customer_full_name}:\n\n{message.text}'

            save_customer_chat_message(bid_id,
                                    customer_telegram_id,
                                    performer_telegram_id,
                                    customer_full_name,
                                    performer_full_name,
                                    message.text,
                                    None)

            await message.bot.send_message(chat_id=performer_chat_id,
                                        text=message_content,
                                        parse_mode='HTML',
                                        reply_markup=chat_answer_keyboard(bid_id,
                                                                        customer_telegram_id,
                                                                        performer_telegram_id,
                                                                        is_customer=False))

    elif not is_customer:
        customer_chat_id = get_user_by_telegram_id_task.delay(customer_telegram_id).get()[7]

        if message.video:
            save_performer_chat_message(bid_id,
                                        customer_telegram_id,
                                        performer_telegram_id,
                                        customer_full_name,
                                        performer_full_name,
                                        message.caption,
                                        message.video.file_id)

            message_content = f'<u>Мастер {performer_full_name}</u>:\n\n{message.caption}'

            await message.bot.send_video(chat_id=customer_chat_id,
                                        video=message.video.file_id,
                                        caption=message_content,
                                        parse_mode='HTML',
                                        reply_markup=chat_answer_keyboard(bid_id,
                                                                        customer_telegram_id,
                                                                        performer_telegram_id,
                                                                        is_customer=True))
        else:
            save_performer_chat_message(bid_id,
                                        customer_telegram_id,
                                        performer_telegram_id,
                                        customer_full_name,
                                        performer_full_name,
                                        message.text,
                                        None)

            message_content = f'<u>Мастер {performer_full_name}</u>:\n\n{message.text}'

            await message.bot.send_message(chat_id=customer_chat_id,
                                        text=message_content,
                                        parse_mode='HTML',
                                        reply_markup=chat_answer_keyboard(bid_id,
                                                                        customer_telegram_id,
                                                                        performer_telegram_id,
                                                                        is_customer=True))
