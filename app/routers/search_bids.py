from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.database.queues.get_bids_by_city import get_bids_by_city
from app.database.queues.get_user_by_id import get_user_by_id

from app.keyboards.cities import cities_keyboard


search_bids_router = Router()


class SearchBids(StatesGroup):
    city = State()


@search_bids_router.callback_query(F.data == 'search_bids')
async def search_bids_callback_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SearchBids.city)

    content = 'Выберите город ⏬'

    await callback.message.answer(content, reply_markup=cities_keyboard())


@search_bids_router.callback_query(SearchBids.city)
async def search_bids_city_handler(callback: CallbackQuery, state: FSMContext):
    bids = get_bids_by_city(callback.data)

    if bids:
        content = 'Найдены заявки:\n\n'
        for bid in bids:
            customer = get_user_by_id(bid['customer_telegram_id'])
            customer_full_name = customer[2]

            if bid['instrument_provided'] == 1:
                bid['instrument_provided'] = 'Да'
            elif bid['instrument_provided'] == 0:
                bid['instrument_provided'] = 'Нет'
        
            content = f'<b>Номер заказа:</b> <u>{bid["id"]}</u>\n' \
                      f'<b>Заказчик:</b> <i>{customer_full_name}</i>\n' \
                      f'<b>Описание:</b> {bid["description"]}\n' \
                      f'<b>До какого числа нужно выполнить работу:</b> <i>{bid["deadline"]}</i>\n' \
                      f'<b>Предоставляет инструмент:</b> <i>{bid["instrument_provided"]}</i>'
            
            await state.clear()
            
            await callback.message.answer(content, parse_mode='HTML')
    else:
        await state.clear()

        content = 'На данный момент нет свободных заказов 🙁'

        await callback.message.answer(content)