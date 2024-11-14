import requests

from app.database.queues.get_bid_by_id import get_bid_by_id
from app.database.queues.get_user_by_id import get_user_by_id


def send_response(bid_id: int):
    url = 'http://127.0.0.1:5000/'

    customer_telegram_id = get_bid_by_id(bid_id)[1]
    customer_chat_id = get_user_by_id(customer_telegram_id)[7]

    content = f'На Ваш заказ №{bid_id} откликнулись!\n' \
               'Выберите "Просмотреть мои заказы" в меню, чтобы узнать больше.'

    response = requests.post(url, json={'chat_id': customer_chat_id, 'text': content, 'parse_mode': 'html'})

    if response.status_code == 200:
        return True
    else:
        return False