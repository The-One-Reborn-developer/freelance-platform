from aiogram import Router, F
from aiogram.types import (Message,
                           CallbackQuery,
                           InlineKeyboardButton,
                           InlineKeyboardMarkup)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.tasks.celery_app import get_bids_by_telegram_id_task
from app.tasks.celery_app import get_bid_by_bid_id_task
from app.tasks.celery_app import get_user_by_telegram_id_task
from app.tasks.celery_app import close_bid_task
from app.tasks.celery_app import get_responses_by_bid_id_task
from app.tasks.celery_app import put_response_task
from app.tasks.celery_app import get_all_performer_chats_task

from app.scripts.save_customer_chat_message import save_customer_chat_message
from app.scripts.get_chat import get_chat

from app.keyboards.chat_answer import chat_answer_keyboard


look_bids_router = Router()


class LookBids(StatesGroup):
    selection = State()
    performer_actions = State()
    message = State()
    chat = State()


@look_bids_router.callback_query(F.data == 'look_bids')
async def look_bids_callback_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(LookBids.selection)

    bids = get_bids_by_telegram_id_task.delay(callback.from_user.id).get()

    if bids == []:
        content = 'На данный момент у Вас нет активных заказов 🙂'

        await callback.answer(content, show_alert=True)
    elif bids == None:
        content = 'Произошла ошибка 🙁\nПопробуйте еще раз или обратитесь в поддержку.'

        await callback.answer(content, show_alert=True)
    else:
        for bid in bids:
            if bid['instrument_provided'] == 1:
                bid['instrument_provided'] = 'Да'
            elif bid['instrument_provided'] == 0:
                bid['instrument_provided'] = 'Нет'

            content = f'<b>Номер заказа:</b> <u>{bid["id"]}</u>\n' \
                f'<b>Описание:</b> {bid["description"]}\n' \
                f'<b>Сроки выполнения работ:</b> <i>{bid["deadline"]}</i>\n' \
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


@look_bids_router.callback_query(LookBids.selection)
async def look_bids_selection_handler(callback: CallbackQuery, state: FSMContext):
    if callback.data.startswith('close_bid_'):
        bid_id = callback.data.split('_')[2]

        bid_closed = close_bid_task.delay(int(bid_id))

        if bid_closed:
            content = f'Заказ №{bid_id} закрыт как выполненный ✅'

            await callback.answer(content, show_alert=True)
        elif not bid_closed:
            content = f'Заказ №{bid_id} уже закрыт как выполненный или не найден.'

            await callback.answer(content, show_alert=True)
        else:
            content = 'Произошла ошибка 🙁\nПопробуйте еще раз или обратитесь в поддержку.'

            await callback.answer(content, show_alert=True)
    elif callback.data.startswith('look_responses_'):
        await state.set_state(LookBids.performer_actions)

        bid_id = callback.data.split('_')[2]

        responses = get_responses_by_bid_id_task.delay(bid_id).get()

        if responses != [] and responses is not None:
            for response in responses:
                content = f'<b>Отклик на заказ №{bid_id}:</b> <u>{response["id"]}</u>\n' \
                    f'<b>Имя исполнителя:</b> {response["performer_full_name"]}\n' \
                    f'<b>Ставка:</b> {response["performer_rate"]}\n' \
                    f'<b>Стаж работы в годах:</b> {response["performer_experience"]}'

                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(text='Войти в чат с мастером ✉️',
                                                 callback_data=f'write_to_performer_{response["performer_telegram_id"]}_{bid_id}'),
                        ],
                        [
                            InlineKeyboardButton(text='Посмотреть переписки мастера 📨',
                                                 callback_data=f'look_performer_chats_{response["performer_telegram_id"]}')
                        ]
                    ]
                )

                await callback.message.answer(content, parse_mode='HTML', reply_markup=keyboard)
        elif responses == []:
            content = 'На данный момент у заказа нет откликов 🙂'

            await callback.answer(content, show_alert=True)
        else:
            content = 'Произошла ошибка 🙁\nПопробуйте еще раз или обратитесь в поддержку.'

            await callback.answer(content, show_alert=True)


@look_bids_router.callback_query(LookBids.performer_actions)
async def look_bids_write_to_performer_handler(callback: CallbackQuery, state: FSMContext):
    if callback.data.startswith('write_to_performer_'):
        performer_telegram_id = callback.data.split('_')[3]
        performer_chat_id = get_user_by_telegram_id_task.delay(performer_telegram_id).get()[7]

        bid_id = callback.data.split('_')[4]

        await state.update_data(performer_telegram_id=performer_telegram_id,
                                performer_chat_id=performer_chat_id,
                                bid_id=bid_id)
        await state.set_state(LookBids.message)

        content = 'Начните писать мастеру, можете прикрепить видео 📹'

        await callback.answer(content, show_alert=True)
    elif callback.data.startswith('look_performer_chats_'):
        performer_telegram_id = callback.data.split('_')[3]

        chats = get_all_performer_chats_task.delay(performer_telegram_id).get()

        if chats:
            await state.set_state(LookBids.chat)

            for chat in chats:
                bid_id = int(chat)

                customer_telegram_id = get_bid_by_bid_id_task.delay(bid_id).get()[1]
                customer_full_name = get_user_by_telegram_id_task.delay(
                    get_bid_by_bid_id_task.delay(bid_id).get()[1]).get()[2]
                city = get_bid_by_bid_id_task.delay(bid_id).get()[2]
                description = get_bid_by_bid_id_task.delay(bid_id).get()[3]
                deadline = get_bid_by_bid_id_task.delay(bid_id).get()[4]
                instrument_provided = get_bid_by_bid_id_task.delay(bid_id).get()[5]
                if instrument_provided == 1:
                    instrument_provided = 'Да'
                else:
                    instrument_provided = 'Нет'
                closed = get_bid_by_bid_id_task.delay(bid_id).get()[6]
                if closed == 1:
                    closed = 'Выполнен'
                else:
                    closed = 'Не выполнен'

                content = f'<b>Заказ №:</b> <u>{bid_id}</u>\n' \
                    f'<b>Имя заказчика:</b> {customer_full_name}\n' \
                    f'<b>Город:</b> {city}\n' \
                    f'<b>Описание:</b> {description}\n' \
                    f'<b>Сроки выполнения работ:</b> <i>{deadline}</i>\n' \
                    f'<b>Предоставляет инструмент:</b> <i>{instrument_provided}</i>\n' \
                    f'<b>Статус заказа:</b> {closed}'

                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(text='Смотреть переписку этого заказа 📨',
                                                 callback_data=f'look_performer_chat_{bid_id}_{customer_telegram_id}_{performer_telegram_id}')
                        ]
                    ]
                )

                await callback.message.answer(content, parse_mode='HTML', reply_markup=keyboard)
        else:
            content = 'У данного мастера ещё нет переписок.'

            await callback.answer(content, show_alert=True)


@look_bids_router.message(LookBids.message)
async def look_bids_write_to_performer_handler(message: Message, state: FSMContext):
    data = await state.get_data()

    performer_chat_id = data['performer_chat_id']
    customer_full_name = get_user_by_telegram_id_task.delay(message.from_user.id).get()[2]

    bid_id = data['bid_id']

    put_response_task.delay(bid_id=bid_id,
                            performer_telegram_id=data['performer_telegram_id'],
                            chat_started=True)

    customer_telegram_id = get_user_by_telegram_id_task.delay(message.from_user.id).get()[1]
    performer_telegram_id = data['performer_telegram_id']
    performer_full_name = get_user_by_telegram_id_task.delay(performer_telegram_id).get()[2]

    if message.video:
        message_content = f'Заказчик {customer_full_name}:\n\n{message.caption}'

        save_customer_chat_message(bid_id,
                                   customer_telegram_id,
                                   performer_telegram_id,
                                   customer_full_name,
                                   performer_full_name,
                                   message.caption,
                                   message.video.file_id)

        await message.bot.send_video(chat_id=performer_chat_id,
                                     video=message.video.file_id,
                                     caption=message_content,
                                     parse_mode='HTML',
                                     reply_markup=chat_answer_keyboard(bid_id,
                                                                       customer_telegram_id,
                                                                       performer_telegram_id,
                                                                       is_customer=False))
    else:
        message_content = f'Заказчик {customer_full_name}:\n\n{message.text}'

        save_customer_chat_message(bid_id,
                                   customer_telegram_id,
                                   performer_telegram_id,
                                   customer_full_name,
                                   performer_full_name,
                                   message.text,
                                   None)

        await message.bot.send_message(chat_id=performer_chat_id,
                                       text=message_content,
                                       parse_mode='HTML',
                                       reply_markup=chat_answer_keyboard(bid_id,
                                                                         customer_telegram_id,
                                                                         performer_telegram_id,
                                                                         is_customer=False))


@look_bids_router.callback_query(LookBids.chat)
async def look_bids_write_to_performer_handler(callback: CallbackQuery, state: FSMContext):
    if callback.data.startswith('look_performer_chat_'):
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

                    await callback.message.answer_video(video=video_file_id,
                                                        caption=caption,
                                                        parse_mode='HTML')
                else:
                    await callback.message.answer(message,
                                                  parse_mode='HTML')
        else:
            await callback.answer("Чат пока пуст или произошла ошибка.", show_alert=True)
