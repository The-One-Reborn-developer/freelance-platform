from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.tasks.celery_app import get_user_by_telegram_id_task
from app.tasks.celery_app import put_user_task

from app.keyboards.profile import (performer_profile_keyboard,
    customer_profile_keyboard,)

from app.views.start import (rate_input,
                             experience_input)
from app.views.profile import (customer_base,
                               performer_base,
                               performer_changed)
from app.views.errors import (general,
                              rate_wrong_type,
                              experience_wrong_type)


profile_router = Router()


class PerformerInfoChange(StatesGroup):
    rate = State()
    experience = State()


@profile_router.callback_query(F.data == 'profile')
async def profile_callback_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    user = get_user_by_telegram_id_task.delay(callback.from_user.id).get()

    if user != [] and user is not None:
        if user[4]:
            full_name = user[2]            
            await callback.message.answer(customer_base(full_name),
                                          reply_markup=customer_profile_keyboard())
        elif user[3]:
            full_name = user[2]
            rate = user[5]
            experience = user[6]
            
            await callback.message.answer(performer_base(full_name, rate, experience),
                                          reply_markup=performer_profile_keyboard())
    else:
        await callback.answer(general(), show_alert=True)


@profile_router.callback_query(F.data == 'change_info')
async def profile_performer_name_change_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(PerformerInfoChange.rate)

    await callback.message.answer(rate_input())


@profile_router.message(PerformerInfoChange.rate)
async def profile_performer_rate_change_handler(message: Message, state: FSMContext):
    rate = message.text

    try:
        rate = float(rate)
    except ValueError:
        await message.answer(rate_wrong_type())
        return
    
    await state.update_data(rate=rate)
    await state.set_state(PerformerInfoChange.experience)

    await message.answer(experience_input())


@profile_router.message(PerformerInfoChange.experience)
async def profile_performer_experience_change_handler(message: Message, state: FSMContext):
    experience = message.text

    try:
        experience = int(experience)
    except ValueError:
        await message.answer(experience_wrong_type())
        return

    await state.update_data(experience=message.text)
    
    data = await state.get_data()
    put_user_task.delay(telegram_id=message.from_user.id,
                        rate=float(data['rate']),
                        experience=int(data['experience']))
    
    user = get_user_by_telegram_id_task.delay(message.from_user.id).get()

    if user != [] and user is not None:
        full_name = user[2]
        rate=user[5]
        experience=user[6]

        await state.clear()

        await message.answer(performer_changed(full_name, rate, experience),
                             reply_markup=performer_profile_keyboard())
    else:
        await message.answer(general())