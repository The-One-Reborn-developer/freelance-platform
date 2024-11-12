from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.database.queues.put_user import put_user
from app.database.queues.get_user_by_id import get_user_by_id

from app.keyboards.menu import (customer_menu_keyboard,
                                performer_menu_keyboard)


menu_router = Router()


@menu_router.callback_query(F.data == 'customer')
async def customer_callback_handler(callback: CallbackQuery):
    put_user(callback.from_user.id, is_customer=True)

    content = 'Вы успешно зарегистрировались как заказчик!\n' \
              'Теперь Вы можете опубликовать свой заказ ⏬'
    
    await callback.message.answer(content, reply_markup=customer_menu_keyboard())


@menu_router.callback_query(F.data == 'performer')
async def performer_callback_handler(callback: CallbackQuery):
    put_user(callback.from_user.id, is_performer=True)

    content = 'Вы успешно зарегистрировались как исполнитель!\n' \
              'Теперь Вы можете искать заказы ⏬'
    
    await callback.message.answer(content, reply_markup=performer_menu_keyboard())


@menu_router.callback_query(F.data == 'menu')
async def menu_callback_handler(callback: CallbackQuery):
    user = get_user_by_id(callback.from_user.id)

    content = 'Выберите опцию ⏬'

    if user[4]:
        keyboard = customer_menu_keyboard()
    elif user[3]:
        keyboard = performer_menu_keyboard()

    await callback.message.answer(content, reply_markup=keyboard)