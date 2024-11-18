from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.tasks.celery_app import get_user_by_telegram_id_task

from app.keyboards.menu import (customer_menu_keyboard,
                                performer_menu_keyboard,
                                both_menu_keyboard)


menu_router = Router()


@menu_router.callback_query(F.data == 'menu')
async def menu_callback_handler(callback: CallbackQuery):
    user = get_user_by_telegram_id_task.delay(callback.from_user.id).get()

    if user != [] and user is not None:
        content = 'Выберите опцию ⏬'

        if user[4]:
            keyboard = customer_menu_keyboard()
        elif user[3]:
            keyboard = performer_menu_keyboard()

        await callback.message.answer(content, reply_markup=keyboard) # TODO: REPLACE BACK TO SEPARATE KEYBOARDS AFTER DEVELOPMENT
        #await callback.message.answer(content, reply_markup=both_menu_keyboard())
    else:
        content = 'Произошла ошибка 🙁\nПопробуйте еще раз или обратитесь в поддержку.'

        await callback.answer(content, show_alert=True)