from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.database.queues.get_bids_by_city import get_bids_by_city
from app.database.queues.get_user_by_id import get_user_by_id
from app.database.queues.post_response import post_response
from app.tasks.celery_app import get_all_customer_chats_task
from app.tasks.celery_app import get_bid_by_id_task
from app.database.queues.get_responses_by_id import get_responses_by_id

from app.scripts.send_response import send_response
from app.scripts.get_chat import get_chat

from app.keyboards.cities import cities_keyboard


search_bids_router = Router()


class SearchBids(StatesGroup):
    city = State()
    selection = State()
    chat = State()


@search_bids_router.callback_query(F.data == 'search_bids')
async def search_bids_callback_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SearchBids.city)

    content = 'Выберите город ⏬'

    await callback.message.answer(content, reply_markup=cities_keyboard())


@search_bids_router.callback_query(SearchBids.city)
async def search_bids_city_handler(callback: CallbackQuery, state: FSMContext):
    bids = get_bids_by_city(callback.data)

    if bids:
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

            await state.set_state(SearchBids.selection)

            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text='Откликнуться 🖐️',
                                             callback_data=str(bid['id']))
                    ],
                    [
                        InlineKeyboardButton(text='Посмотреть переписки заказчика 📨',
                                             callback_data=f'look_customer_chats_{bid["customer_telegram_id"]}')
                    ]
                ]
            )

            await callback.message.answer(content, parse_mode='HTML', reply_markup=keyboard)
    else:
        content = 'На данный момент нет свободных заказов 🙁'

        await callback.message.answer(content)


@search_bids_router.callback_query(SearchBids.selection)
async def search_bids_selection_handler(callback: CallbackQuery, state: FSMContext):
    if callback.data.startswith('look_customer_chats'):
        await state.set_state(SearchBids.chat)

        customer_telegram_id = callback.data.split('_')[3]

        chats_ids = get_all_customer_chats_task.delay(customer_telegram_id).get()
        
        if chats_ids:
            for chat_id in chats_ids:
                bid_id = int(chat_id)
                city = get_bid_by_id_task.delay(bid_id).get()[2]
                description = get_bid_by_id_task.delay(bid_id).get()[3]
                deadline = get_bid_by_id_task.delay(bid_id).get()[4]
                instrument_provided = get_bid_by_id_task.delay(bid_id).get()[5]
                if instrument_provided == 1:
                    instrument_provided = 'Да'
                else:
                    instrument_provided = 'Нет'
                closed = get_bid_by_id_task.delay(bid_id).get()[6]
                if closed == 1:
                    closed = 'Выполнен'
                else:
                    closed = 'Не выполнен'

                content = f'<b>Номер заказа:</b> <u>{bid_id}</u>\n' \
                          f'<b>Город:</b> <i>{city}</i>\n' \
                          f'<b>Описание:</b> {description}\n' \
                          f'<b>Сроки выполнения работы:</b> <i>{deadline}</i>\n' \
                          f'<b>Предоставляет инструмент:</b> <i>{instrument_provided}</i>\n' \
                          f'<b>Статус:</b> <i>{closed}</i>\n\n' \

                responses = get_responses_by_id(bid_id)

                if responses:
                    for response in responses:
                        performer_telegram_id = response['performer_telegram_id']
                        performer_full_name = response['performer_full_name']
                        performer_rate = response['performer_rate']
                        performer_experience = response['performer_experience']

                        content += f'<b>Откликнулся:</b> <i>{performer_full_name}</i>\n' \
                                   f'<b>Ставка:</b> <i>{performer_rate}</i>\n' \
                                   f'<b>Стаж:</b> <i>{performer_experience}</i>'

                        keyboard = InlineKeyboardMarkup(
                            inline_keyboard=[
                                [
                                    InlineKeyboardButton(text='Смотреть переписку этого заказа 📨',
                                                            callback_data=f'look_customer_chat_{bid_id}_{customer_telegram_id}_{performer_telegram_id}')
                                ]
                            ]
                        )
                        
                        await callback.message.answer(content, parse_mode='HTML', reply_markup=keyboard)
    else:
        performer = get_user_by_id(callback.from_user.id)

        response = post_response(callback.data,
                                performer[1],
                                performer[2],
                                performer[5],
                                performer[6])

        if response == False:
            content = 'Вы уже откликнулись на данный заказ!'

            await callback.message.answer(content)
        elif response == None:
            content = 'Произошла ошибка 🙁\nПопробуйте еще раз или обратитесь в поддержку.'

            await callback.message.answer(content)
        else:
            send_response(callback.data)

            content = f'Вы успешно откликнулись на заказ №{callback.data}!\n' \
                'Заказчик получит уведомление о Вашем отклике.'

            await callback.message.answer(content)


@search_bids_router.callback_query(SearchBids.chat)
async def look_bids_write_to_performer_handler(callback: CallbackQuery, state: FSMContext):
    if callback.data.startswith('look_customer_chat_'):
        bid_id = callback.data.split('_')[3]
        customer_telegram_id = callback.data.split('_')[4]
        performer_telegram_id = callback.data.split('_')[5]

        response = get_chat(bid_id,
                            customer_telegram_id,
                            performer_telegram_id)
        
        if response:
            messages = [msg.strip() for msg in response.split("---") if msg.strip()]
            for message in messages:
                if "video_file_id:" in message:
                    lines = message.split("\n")
                    text_lines = []
                    video_file_id = None

                    for line in lines:
                        if line.startswith("video_file_id:"):
                            video_file_id = line.split(":", 1)[1].strip()
                        else:
                            text_lines.append(line.strip())
                    
                    caption = "\n".join(text_lines)
                    
                    await callback.message.answer_video(video=video_file_id, caption=caption)
                else:
                    await callback.message.answer(message)
        else:
            await callback.message.answer("Чат пока пуст или произошла ошибка.")