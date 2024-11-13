from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.database.queues.post_bid import post_bid

from app.keyboards.cities import cities_keyboard
from app.keyboards.menu import customer_menu_keyboard
from app.keyboards.new_bid import instrument_provided_keyboard


new_bid_router = Router()


class NewBid(StatesGroup):
    city = State()
    description = State()
    deadline = State()
    instrument_provided = State()


@new_bid_router.callback_query(F.data == 'new_bid')
async def new_bid_callback_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(NewBid.city)
    
    content = 'Выберите город ⏬'

    await callback.message.answer(content, reply_markup=cities_keyboard())


@new_bid_router.callback_query(NewBid.city)
async def new_bid_city_handler(callback: CallbackQuery, state: FSMContext):
    await state.update_data(city=callback.data)
    await state.set_state(NewBid.description)

    content = 'Введите описание работы 🛠️'

    await callback.message.answer(content)


@new_bid_router.message(NewBid.description)
async def new_bid_description_handler(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(NewBid.deadline)

    content = 'Введите, до какого числа нужно выполнить работу 📅'

    await message.answer(content)


@new_bid_router.message(NewBid.deadline)
async def new_bid_description_handler(message: Message, state: FSMContext):
    await state.update_data(deadline=message.text)
    await state.set_state(NewBid.instrument_provided)

    content = 'Предоставляете ли Вы инструмент? 🛠️'

    await message.answer(content, reply_markup=instrument_provided_keyboard())


@new_bid_router.callback_query(NewBid.instrument_provided)
async def new_bid_description_handler(callback: CallbackQuery, state: FSMContext):
    await state.update_data(instrument_provided=callback.data)

    data = await state.get_data()

    if data['instrument_provided'] == 'yes':
        data['instrument_provided'] = 1
    elif data['instrument_provided'] == 'no':
        data['instrument_provided'] = 0

    post_bid(customer_telegram_id=callback.from_user.id,
             city=data['city'],
             description=data['description'],
             deadline=data['deadline'],
             instrument_provided=data['instrument_provided'])

    await state.clear()

    content = 'Заявка создана! ☑️\n' \
              'При отклике на заявку Вы получите уведомление.'
    
    await callback.message.answer(content, reply_markup=customer_menu_keyboard())

