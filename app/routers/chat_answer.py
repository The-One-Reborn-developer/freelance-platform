from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


chat_answer_router = Router()


class ChatAnswer(StatesGroup):
    message = State()


@chat_answer_router.callback_query(F.data.startswith('answer_'))
async def chat_answer_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ChatAnswer.message)

    content = 'Начните писать ответ, можете прикрепить видео 📹'

    await callback.answer(content)

    callback_data = callback.data.split('_')
    bid_id = callback_data[1]
    customer_telegram_id = callback_data[2]
    performer_telegram_id = callback_data[3]
    customer_full_name = callback_data[4]
    performer_full_name = callback_data[5]

    await callback.message.answer(f'bid_id: {bid_id}\ncustomer_telegram_id: {customer_telegram_id}\n'
                                  f'performer_telegram_id: {performer_telegram_id}\ncustomer_full_name: {customer_full_name}\n'
                                  f'performer_full_name: {performer_full_name}')