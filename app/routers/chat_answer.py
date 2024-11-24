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

    await callback.message.answer(f'Ответ пользователю {callback.data.split("_")[1]}')