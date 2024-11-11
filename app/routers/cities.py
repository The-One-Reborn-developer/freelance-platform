from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.keyboards.cities import cities_keyboard


cities_router = Router()


@cities_router.callback_query(F.data == 'search_bids')
async def performer_cities_callback_handler(callback: CallbackQuery):
    content = 'Выберите город ⏬'

    await callback.message.answer(content, reply_markup=cities_keyboard())


@cities_router.callback_query(F.data == 'new_bid')
async def customer_cities_callback_handler(callback: CallbackQuery):
    content = 'Выберите город ⏬'

    await callback.message.answer(content, reply_markup=cities_keyboard())