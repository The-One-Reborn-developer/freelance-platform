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
    customer_full_name = callback_data[4]
    performer_full_name = callback_data[5]
    is_customer = callback_data[6] == 'True'

    await state.update_data(bid_id=bid_id,
                            customer_telegram_id=customer_telegram_id,
                            performer_telegram_id=performer_telegram_id,
                            customer_full_name=customer_full_name,
                            performer_full_name=performer_full_name,
                            is_customer=is_customer)
    
    if is_customer:
        content = f'Начните писать ответ заказчику, можете прикрепить видео 📹 {is_customer}'
    else:
        content = f'Начните писать ответ мастеру, можете прикрепить видео 📹 {is_customer}'

    await callback.answer(content, show_alert=True)


@chat_answer_router.message(ChatAnswer.message)
async def chat_answer_message_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    bid_id = data['bid_id']
    customer_telegram_id = data['customer_telegram_id']
    performer_telegram_id = data['performer_telegram_id']
    customer_full_name = data['customer_full_name']
    performer_full_name = data['performer_full_name']
    is_customer = data['is_customer']  # Determines if the sender is the customer

    # Determine recipient and sender roles
    if is_customer:  # Customer is sending the message
        recipient_chat_id = get_user_by_telegram_id_task.delay(performer_telegram_id).get()[7]
        sender_name = f"Заказчик {customer_full_name}"
    else:  # Performer is sending the message
        recipient_chat_id = get_user_by_telegram_id_task.delay(customer_telegram_id).get()[7]
        sender_name = f"Мастер {performer_full_name}"

    # Handle message content based on type
    if message.video:
        message_caption = message.caption or ""
        save_performer_chat_message(
            bid_id=bid_id if not is_customer else None,
            customer_telegram_id=customer_telegram_id,
            performer_telegram_id=performer_telegram_id,
            customer_full_name=customer_full_name,
            performer_full_name=performer_full_name,
            content=message_caption,
            file_id=message.video.file_id
        )
        message_content = f"<u>{sender_name}</u>:\n\n{message_caption}"
        await message.bot.send_video(
            chat_id=recipient_chat_id,
            video=message.video.file_id,
            caption=message_content,
            parse_mode='HTML',
            reply_markup=chat_answer_keyboard(
                bid_id,
                customer_telegram_id,
                performer_telegram_id,
                customer_full_name,
                performer_full_name,
                is_customer=not is_customer  # Flip is_customer for replies
            )
        )
    else:
        save_performer_chat_message(
            bid_id=bid_id if not is_customer else None,
            customer_telegram_id=customer_telegram_id,
            performer_telegram_id=performer_telegram_id,
            customer_full_name=customer_full_name,
            performer_full_name=performer_full_name,
            content=message.text,
            file_id=None
        )
        message_content = f"<u>{sender_name}</u>:\n\n{message.text}"
        await message.bot.send_message(
            chat_id=recipient_chat_id,
            text=message_content,
            parse_mode='HTML',
            reply_markup=chat_answer_keyboard(
                bid_id,
                customer_telegram_id,
                performer_telegram_id,
                customer_full_name,
                performer_full_name,
                is_customer=not is_customer  # Flip is_customer for replies
            )
        )
