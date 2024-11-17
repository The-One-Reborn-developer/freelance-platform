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

    user = get_user_by_telegram_id_task.delay(message.from_user.id).get()

    if user != [] and user is not None:
        content = 'Выберите опцию ⏬'

        if user[3]:
            keyboard = performer_menu_keyboard()
        elif user[4]:
            keyboard = customer_menu_keyboard()

        await message.answer(content, reply_markup=keyboard)
    elif user == []:
        post_user_task.delay(message.from_user.id)

        content = 'Здравствуйте! Добро пожаловать в бота для поиска заказчиков/подрядчиков.\n\n' \
                  'Пожалуйста, укажите, кто Вы ⏬'

        await message.answer(content, reply_markup=start_keyboard())
    else:
        content = 'Произошла ошибка 🙁\nПопробуйте еще раз или обратитесь в поддержку.'

        await message.answer(content)


@start_router.callback_query(F.data == 'customer')
async def customer_callback_handler(callback: CallbackQuery, state: FSMContext):
    await state.update_data(type=callback.data)
    await state.set_state(CustomerRegistration.name)

    content = 'Введите ФИО 📜'

    await callback.message.answer(content)


@start_router.message(CustomerRegistration.name)
async def customer_registration_name_handler(message: Message, state: FSMContext):
    await state.update_data(name=message.text)

    data = await state.get_data()
    put_user_task.delay(telegram_id=message.from_user.id,
                        full_name=data['name'],
                        is_customer=True,
                        chat_id=message.chat.id)

    content = 'Вы успешно зарегистрированы как заказчик!\n\n' \
              'Выберите опцию ⏬'
    
    await state.clear()

    await message.answer(content, reply_markup=customer_menu_keyboard())


@start_router.callback_query(F.data == 'performer')
async def performer_callback_handler(callback: CallbackQuery, state: FSMContext):
    await state.update_data(type=callback.data)
    await state.set_state(PerformerRegistration.name)

    content = 'Введите ФИО 📜'

    await callback.message.answer(content)


@start_router.message(PerformerRegistration.name)
async def performer_registration_name_handler(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(PerformerRegistration.rate)

    content = 'Введите свою ставку в ₽'

    await message.answer(content)


@start_router.message(PerformerRegistration.rate)
async def performer_registration_rate_handler(message: Message, state: FSMContext):
    rate = message.text

    if not rate.isdigit():
        content = 'Пожалуйста, введите свою ставку в ₽ числом.'

        await message.answer(content)
        return
    
    await state.update_data(rate=rate)
    await state.set_state(PerformerRegistration.experience)

    content = 'Введите свой стаж в годах (только число).'

    await message.answer(content)


@start_router.message(PerformerRegistration.experience)
async def performer_registration_experience_handler(message: Message, state: FSMContext):
    experience = message.text

    try:
        experience = int(experience)
    except ValueError:
        content = 'Пожалуйста, введите свой стаж в годах числом.'

        await message.answer(content)
        return
    
    await state.update_data(experience=experience)

    data = await state.get_data()

    put_user_task.delay(telegram_id=message.from_user.id,
                        full_name=data['name'],
                        is_performer=True,
                        rate=float(data['rate']),
                        experience=int(data['experience']),
                        chat_id=message.chat.id)

    content = 'Вы успешно зарегистрированы как исполнитель!\n\n' \
              'Выберите опцию ⏬'
    
    await state.clear()

    await message.answer(content, reply_markup=performer_menu_keyboard())
