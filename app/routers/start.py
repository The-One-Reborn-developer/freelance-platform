from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import CommandStart

from app.database.queues.post_user import post_user

from app.keyboards.start import start_keyboard


start_router = Router()


@start_router.message(CommandStart())
async def start_command_handler(message: Message):
    post_user(message.from_user.id, message.from_user.username)

    content = 'Здравствуйте! Добро пожаловать в бота для поиска заказчиков/исполнителей.\n' \
              'Пожалуйста, укажите, кто Вы ⏬'
    
    await message.answer(content, reply_markup=start_keyboard())