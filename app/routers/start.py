from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters.command import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from app.tasks.celery_app import post_user_task
from app.tasks.celery_app import put_user_task
from app.tasks.celery_app import get_user_by_telegram_id_task

from app.keyboards.start import start_keyboard
from app.keyboards.menu import (performer_menu_keyboard,
                                customer_menu_keyboard)

from app.views.start import (choose_option,
                             not_registered,
                             name_input,
                             customer_successful_registration,
                             rate_input,
                             experience_input,
                             performer_successful_registration)
from app.views.errors import (general,
                              rate_wrong_type,
                              experience_wrong_type)


start_router = Router()


class PerformerRegistration(StatesGroup):
    name = State()
    rate = State()
    experience = State()


class CustomerRegistration(StatesGroup):
    name = State()


@start_router.message(CommandStart())
async def start_command_handler(message: Message, state: FSMContext):
    await state.clear()

    await message.answer('Мы переехали: <a href="https://t.me/servis_plus_webapp_bot">новый бот</a>', parse_mode='HTML')
    '''
    user = get_user_by_telegram_id_task.delay(message.from_user.id).get()

    if user != [] and user is not None:
        keyboard = None

        if user[3]:
            keyboard = performer_menu_keyboard()
        elif user[4]:
            keyboard = customer_menu_keyboard()

        await message.answer(choose_option(), reply_markup=keyboard)
    elif user == []:
        post_user_task.delay(message.from_user.id)

        await message.answer(not_registered(), reply_markup=start_keyboard())
    else:
        await message.answer(general())
    '''


@start_router.callback_query(F.data == 'customer')
async def customer_callback_handler(callback: CallbackQuery, state: FSMContext):
    await state.update_data(type=callback.data)
    await state.set_state(CustomerRegistration.name)

    await callback.message.answer(name_input())


@start_router.message(CustomerRegistration.name)
async def customer_registration_name_handler(message: Message, state: FSMContext):
    await state.update_data(name=message.text)

    data = await state.get_data()
    put_user_task.delay(telegram_id=message.from_user.id,
                        full_name=data['name'],
                        is_customer=True,
                        chat_id=message.chat.id)
    
    await state.clear()

    await message.answer(customer_successful_registration(), reply_markup=customer_menu_keyboard())


@start_router.callback_query(F.data == 'performer')
async def performer_callback_handler(callback: CallbackQuery, state: FSMContext):
    await state.update_data(type=callback.data)
    await state.set_state(PerformerRegistration.name)

    await callback.message.answer(name_input())


@start_router.message(PerformerRegistration.name)
async def performer_registration_name_handler(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(PerformerRegistration.rate)

    await message.answer(rate_input())


@start_router.message(PerformerRegistration.rate)
async def performer_registration_rate_handler(message: Message, state: FSMContext):
    rate = message.text

    try:
        rate = float(rate)
    except ValueError:
        await message.answer(rate_wrong_type())
        return
    
    await state.update_data(rate=rate)
    await state.set_state(PerformerRegistration.experience)

    await message.answer(experience_input())


@start_router.message(PerformerRegistration.experience)
async def performer_registration_experience_handler(message: Message, state: FSMContext):
    experience = message.text

    try:
        experience = int(experience)
    except ValueError:
        await message.answer(experience_wrong_type())
        return
    
    await state.update_data(experience=experience)

    data = await state.get_data()

    put_user_task.delay(telegram_id=message.from_user.id,
                        full_name=data['name'],
                        is_performer=True,
                        rate=float(data['rate']),
                        experience=int(data['experience']),
                        chat_id=message.chat.id)
    
    await state.clear()

    await message.answer(performer_successful_registration(), reply_markup=performer_menu_keyboard())
