from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.tasks.celery_app import get_bids_by_city_task
from app.tasks.celery_app import get_user_by_telegram_id_task
from app.tasks.celery_app import post_response_task
from app.tasks.celery_app import get_all_customer_chats_task
from app.tasks.celery_app import get_bid_by_bid_id_task
from app.tasks.celery_app import get_responses_by_bid_id_task

from app.scripts.send_response import send_response
from app.scripts.get_chat import get_chat

from app.keyboards.cities import cities_keyboard
from app.keyboards.search_bids import (respond_or_look_keyboard,
                                       look_bid_chat_keyboard)

from app.views.errors import (general,
                              no_chats)
from app.views.bid import choose_city
from app.views.search_bids import (bid_info,
                                   no_available_bids,
                                   look_customer_chats_base_content,
                                   look_customer_chats_additional_content,
                                   look_customer_chats_no_responses,
                                   customer_no_chats,
                                   already_responded,
                                   successfully_responded,
                                   click_again)


search_bids_router = Router()


class SearchBids(StatesGroup):
    city = State()
    selection = State()
    chat = State()


@search_bids_router.callback_query(F.data == 'search_bids')
async def search_bids_callback_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SearchBids.city)

    await callback.message.answer(choose_city(), reply_markup=cities_keyboard())


@search_bids_router.callback_query(SearchBids.city)
async def search_bids_city_handler(callback: CallbackQuery, state: FSMContext):
    bids = get_bids_by_city_task.delay(callback.data).get()

    if bids != []:
        for bid in bids:
            customer = get_user_by_telegram_id_task.delay(bid['customer_telegram_id']).get()
            customer_full_name = customer[2]

            await state.set_state(SearchBids.selection)

            await callback.message.answer(bid_info(bid,
                                                   customer_full_name),
                                                   parse_mode='HTML',
                                                   reply_markup=respond_or_look_keyboard(bid))
    elif bids == []:
        await callback.answer(no_available_bids(), show_alert=True)
    else:
        await callback.answer(general(), show_alert=True)


@search_bids_router.callback_query(SearchBids.selection)
async def search_bids_selection_handler(callback: CallbackQuery, state: FSMContext):
    if callback.data.startswith('look_customer_chats'):
        customer_telegram_id = callback.data.split('_')[3]

        chats_ids = get_all_customer_chats_task.delay(customer_telegram_id).get()
        
        if chats_ids:
            await state.set_state(SearchBids.chat)

            for chat_id in chats_ids:
                bid_id = int(chat_id)

                bid_data = get_bid_by_bid_id_task.delay(bid_id).get()

                base_content = look_customer_chats_base_content(bid_id,
                                                                bid_data)

                responses = get_responses_by_bid_id_task.delay(bid_id).get()

                if responses != [] and responses is not None:
                    for response in responses:
                        performer_telegram_id = response['performer_telegram_id']
                        
                        additional_content = look_customer_chats_additional_content(response)
                        
                        full_content = base_content + additional_content
                        
                        await callback.message.answer(full_content,
                                                      parse_mode='HTML',
                                                      reply_markup=look_bid_chat_keyboard(bid_id,
                                                                                          customer_telegram_id,
                                                                                          performer_telegram_id))
                elif responses == []:
                    await callback.message.answer(look_customer_chats_no_responses(bid_id,
                                                                                   bid_data),
                                                                                   parse_mode='HTML')
                else:
                    await callback.answer(general(), show_alert=True)
        else:
            await callback.answer(customer_no_chats(), show_alert=True)
    elif callback.data.startswith('answer_'):
        await state.clear()

        await callback.answer(click_again(), show_alert=True)
    else:
        performer = get_user_by_telegram_id_task.delay(callback.from_user.id).get()
        
        if performer != [] and performer is not None:
            response = post_response_task.delay(callback.data,
                                                performer[1],
                                                performer[2],
                                                performer[5],
                                                performer[6]).get()

            if response == False:
                await callback.answer(already_responded(), show_alert=True)
            elif response == None:
                await callback.answer(general(), show_alert=True)
            else:
                send_response(callback.data,
                              callback.from_user.id)

                await callback.answer(successfully_responded(callback.data),
                                      show_alert=True)
        else:
            await callback.answer(general(), show_alert=True)


@search_bids_router.callback_query(SearchBids.chat)
async def look_bids_write_to_performer_handler(callback: CallbackQuery, state: FSMContext):
    if callback.data.startswith('look_customer_chat_'):
        bid_id = callback.data.split('_')[3]
        customer_telegram_id = callback.data.split('_')[4]
        performer_telegram_id = callback.data.split('_')[5]

        try:
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
                        
                        await callback.message.answer_video(video=video_file_id,
                                                            caption=caption,
                                                            parse_mode='HTML')
                    else:
                        await callback.message.answer(message, parse_mode='HTML')
        except Exception as e:
            await callback.answer(text=no_chats(), show_alert=True)