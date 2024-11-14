from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.database.queues.get_bids_by_id import get_bids_by_id
from app.database.queues.get_user_by_id import get_user_by_id
from app.database.queues.close_bid import close_bid


look_bids_router = Router()


class LookBids(StatesGroup):
    selection = State()


@look_bids_router.callback_query(F.data == 'look_bids')
async def look_bids_callback_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(LookBids.selection)

    bids = get_bids_by_id(callback.from_user.id)

    if bids:
        for bid in bids:
            if bid['instrument_provided'] == 1:
                bid['instrument_provided'] = 'Да'
            elif bid['instrument_provided'] == 0:
                bid['instrument_provided'] = 'Нет'
            
            content = f'<b>Номер заказа:</b> <u>{bid["id"]}</u>\n' \
                      f'<b>Описание:</b> {bid["description"]}\n' \
                      f'<b>До какого числа нужно выполнить работу:</b> <i>{bid["deadline"]}</i>\n' \
                      f'<b>Предоставляет инструмент:</b> <i>{bid["instrument_provided"]}</i>'
            
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text='Просмотреть отклики',
                                             callback_data=f'look_responses_{bid["id"]}'),
                    ],
                    [
                        InlineKeyboardButton(text='Закрыть заказ как выполненный ✅',
                                             callback_data=f'close_bid_{bid["id"]}')
                    ]
                ]
            )

            await callback.message.answer(content, parse_mode='HTML', reply_markup=keyboard)
    else:
        content = 'На данный момент у Вас нет активных заказов 🙂'

        await callback.message.answer(content)


@look_bids_router.callback_query(LookBids.selection)
async def look_bids_selection_handler(callback: CallbackQuery, state: FSMContext):
    if callback.data.startswith('close_bid_'):
        bid_id = callback.data.split('_')[2]
        
        bid_closed = close_bid(int(bid_id))

        if bid_closed:
            user = get_user_by_id(callback.from_user.id)
            content = f'Заказ №{bid_id} закрыт как выполненный ✅'
            
            await callback.message.answer(content)
        elif not bid_closed:
            content = f'Заказ №{bid_id} уже закрыт как выполненный или не найден.'
            
            await callback.message.answer(content)
        else:
            content = 'Произошла ошибка 🙁\nПопробуйте еще раз или обратитесь в поддержку.'
            
            await callback.message.answer(content)
    elif callback.data.startswith('look_responses_'):
        bid_id = callback.data.split('_')[2]