from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.tasks.celery_app import post_bid_task

from app.keyboards.cities import cities_keyboard
from app.keyboards.new_bid import instrument_provided_keyboard

from app.views.bid import (choose_city,
                        input_description,
                        input_deadline,
                        choose_instrument_provided,
                        bid_exists,
                        bid_created)
from app.views.errors import general


new_bid_router = Router()


class NewBid(StatesGroup):
    city = State()
    description = State()
    deadline = State()
    instrument_provided = State()


@new_bid_router.callback_query(F.data == 'new_bid')
async def new_bid_callback_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(NewBid.city)

    await callback.message.answer(choose_city(), reply_markup=cities_keyboard())


@new_bid_router.callback_query(NewBid.city)
async def new_bid_city_handler(callback: CallbackQuery, state: FSMContext):
    await state.update_data(city=callback.data)
    await state.set_state(NewBid.description)

    await callback.message.answer(input_description())


@new_bid_router.message(NewBid.description)
async def new_bid_description_handler(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(NewBid.deadline)

    await message.answer(input_deadline())


@new_bid_router.message(NewBid.deadline)
async def new_bid_description_handler(message: Message, state: FSMContext):
    await state.update_data(deadline=message.text)
    await state.set_state(NewBid.instrument_provided)

    await message.answer(choose_instrument_provided(),
                         reply_markup=instrument_provided_keyboard())


@new_bid_router.callback_query(NewBid.instrument_provided)
async def new_bid_description_handler(callback: CallbackQuery, state: FSMContext):
    await state.update_data(instrument_provided=callback.data)

    data = await state.get_data()

    new_bid = post_bid_task.delay(customer_telegram_id=callback.from_user.id,
                                  city=data['city'],
                                  description=data['description'],
                                  deadline=data['deadline'],
                                  instrument_provided=1 if data['instrument_provided'] == 'yes' else 0).get()
    
    if new_bid == False:
        await state.clear()

        await callback.answer(bid_exists(), show_alert=True)
    elif new_bid == None:
        await state.clear()

        await callback.answer(general(), show_alert=True)
    else:    
        await state.clear()

        await callback.answer(bid_created(), show_alert=True)

