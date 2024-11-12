from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import CommandStart

from app.database.queues.post_user import post_user
from app.database.queues.get_user_by_id import get_user_by_id

from app.keyboards.start import start_keyboard
from app.keyboards.menu import (performer_menu_keyboard,
                                customer_menu_keyboard)


start_router = Router()


@start_router.message(CommandStart())
async def start_command_handler(message: Message):
    user = get_user_by_id(message.from_user.id)

    if user:
        content = 'Вы уже зарегистрированы в боте!\n\n' \
                  'Выберите опцию ⏬'
        
        if user[3]:
            keyboard = performer_menu_keyboard()
        elif user[4]:
            keyboard = customer_menu_keyboard()

        await message.answer(content, reply_markup=keyboard)
    else:
        post_user(message.from_user.id)

        content = 'Здравствуйте! Добро пожаловать в бота для поиска заказчиков/подрядчиков.\n\n' \
                  'Пожалуйста, укажите, кто Вы ⏬'
        
        await message.answer(content, reply_markup=start_keyboard())