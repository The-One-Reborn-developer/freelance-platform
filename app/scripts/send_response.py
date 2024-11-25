import requests

from app.tasks.celery_app import get_bid_by_bid_id_task
from app.tasks.celery_app import get_user_by_telegram_id_task


def send_response(bid_id: int,
                  performer_telegram_id: int):
    url = 'http://flask:5000/response'

    bid_data = get_bid_by_bid_id_task.delay(bid_id).get()
    customer_telegram_id = bid_data[1]
    bid_description = bid_data[3]
    bid_deadline = bid_data[4]
    bid_instrument_provided = bid_data[5]

    performer_data = get_user_by_telegram_id_task.delay(performer_telegram_id).get()
    performer_full_name = performer_data[2]
    performer_rate = performer_data[5]
    performer_experience = performer_data[6]
    
    customer_chat_id = get_user_by_telegram_id_task.delay(customer_telegram_id).get()[7]

    content = f'На Ваш заказ №{bid_id} откликнулись!\n' \
            f'<b>Описание:</b> {bid_description}\n' \
            f'<b>Сроки выполнения работы:</b> <i>{bid_deadline}</i>\n' \
            f'<b>Предоставляет инструмент:</b> <i>{"Да" if bid_instrument_provided == 1 else "Нет"}</i>\n\n' \
            f'<b>Откликнулся:</b> <i>{performer_full_name}</i>\n' \
            f'<b>Ставка:</b> <i>{performer_rate}</i>\n' \
            f'<b>Стаж:</b> <i>{performer_experience}</i>\n\n' \
            'Выберите "Просмотреть мои заказы" в меню, чтобы узнать больше.'

    response = requests.post(url, json={'chat_id': customer_chat_id,
                                        'text': content,
                                        'parse_mode': 'html',
                                        'reply_markup': {'inline_keyboard': [[{'text': 'Просмотреть мои заказы 📂',
                                                                               'callback_data': 'look_bids'}]]}})

    if response.status_code == 200:
        return True
    else:
        return False