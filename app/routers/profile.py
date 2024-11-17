from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.tasks.celery_app import get_user_by_telegram_id_task
from app.tasks.celery_app import put_user_task

from app.keyboards.profile import profile_keyboard


profile_router = Router()


class CustomerInfoChange(StatesGroup):
    name = State()


class PerformerInfoChange(StatesGroup):
    name = State()
    rate = State()
    experience = State()


@profile_router.callback_query(F.data == 'profile')
async def profile_callback_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    user = get_user_by_telegram_id_task.delay(callback.from_user.id).get()

    if user != [] and user is not None:
        if user[4]:
            content = 'Ваш профиль:\n\n' \
                    f'Имя: {user[2]}'
            
            await callback.message.answer(content, reply_markup=profile_keyboard())
        elif user[3]:
            content = 'Ваш профиль:\n\n' \
                    f'Имя: {user[2]}\n' \
                    f'Ставка: {user[5]}₽\n' \
                    f'Стаж работы в годах: {user[6]}'
            
            await callback.message.answer(content, reply_markup=profile_keyboard())
    else:
        content = 'Произошла ошибка 🙁\nПопробуйте еще раз или обратитесь в поддержку.'

        await callback.message.answer(content)


@profile_router.callback_query(F.data == 'change_info')
async def profile_change_info_callback_handler(callback: CallbackQuery, state: FSMContext):
    user = get_user_by_telegram_id_task.delay(int(callback.from_user.id)).get()

    if user != [] and user is not None:
        if user[4]:
            await state.set_state(CustomerInfoChange.name)

            content = 'Введите ФИО 📜'

            await callback.message.answer(content)
        elif user[3]:
            await state.set_state(PerformerInfoChange.name)

            content = 'Введите ФИО 📜'

            await callback.message.answer(content)
    else:
        content = 'Произошла ошибка 🙁\nПопробуйте еще раз или обратитесь в поддержку.'

        await callback.message.answer(content)


@profile_router.message(CustomerInfoChange.name)
async def profile_customer_name_change_handler(message: Message, state: FSMContext):
    put_user_task.delay(telegram_id=message.from_user.id,
                        full_name=message.text)

    user = get_user_by_telegram_id_task.delay(message.from_user.id).get()

    if user != [] and user is not None:
        if user[4]:
            content = 'Информация изменена ☑️\n\n' \
                    'Ваш профиль:\n\n' \
                    f'Имя: {user[2]}'
            
            await message.answer(content, reply_markup=profile_keyboard())
    else:
        content = 'Произошла ошибка 🙁\nПопробуйте еще раз или обратитесь в поддержку.'

        await message.answer(content)


@profile_router.message(PerformerInfoChange.name)
async def profile_performer_name_change_handler(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(PerformerInfoChange.rate)

    content = 'Введите свою ставку в ₽'

    await message.answer(content)


@profile_router.message(PerformerInfoChange.rate)
async def profile_performer_rate_change_handler(message: Message, state: FSMContext):
    rate = message.text

    if not rate.isdigit():
        content = 'Пожалуйста, введите свою ставку в ₽ числом.'

        await message.answer(content)
        return
    
    await state.update_data(rate=rate)
    await state.set_state(PerformerInfoChange.experience)

    content = 'Введите свой стаж в годах (только число).'

    await message.answer(content)


@profile_router.message(PerformerInfoChange.experience)
async def profile_performer_experience_change_handler(message: Message, state: FSMContext):
    experience = message.text

    try:
        experience = int(experience)
    except ValueError:
        content = 'Пожалуйста, введите свой стаж в годах числом.'

        await message.answer(content)
        return

    await state.update_data(experience=message.text)
    
    data = await state.get_data()
    put_user_task.delay(telegram_id=message.from_user.id,
                        full_name=data['name'],
                        rate=float(data['rate']),
                        experience=int(data['experience']))
    
    user = get_user_by_telegram_id_task.delay(message.from_user.id).get()

    if user != [] and user is not None:
        content = 'Информация изменена ☑️\n\n' \
                'Ваш профиль:\n\n' \
                f'Имя: {user[2]}\n' \
                f'Ставка: {user[5]}₽\n' \
                f'Стаж работы в годах: {user[6]}'
        

        await state.clear()

        await message.answer(content, reply_markup=profile_keyboard())
    else:
        content = 'Произошла ошибка 🙁\nПопробейте ещё раз или обратитесь в поддержку.'

        await message.answer(content)