import requests

from app.tasks.celery_app import get_bid_by_bid_id_task
from app.tasks.celery_app import get_user_by_telegram_id_task


def send_response(bid_id: int):
    url = 'http://127.0.0.1:5000/response'

    customer_telegram_id = get_bid_by_bid_id_task.delay(bid_id).get()[1]
    customer_chat_id = get_user_by_telegram_id_task.delay(customer_telegram_id).get()[7]

    content = f'На Ваш заказ №{bid_id} откликнулись!\n' \
               'Выберите "Просмотреть мои заказы" в меню, чтобы узнать больше.'

    response = requests.post(url, json={'chat_id': customer_chat_id, 'text': content, 'parse_mode': 'html'})

    if response.status_code == 200:
        return True
    else:
        return False