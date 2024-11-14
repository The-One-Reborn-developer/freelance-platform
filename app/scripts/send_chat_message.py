import requests

from app.database.queues.get_bid_by_id import get_bid_by_id
from app.database.queues.get_user_by_id import get_user_by_id


def send_chat_message(receiver_id: int, message: str):
    url = 'http://127.0.0.1:5000/chat'

    response = requests.post(url, json={'chat_id': receiver_id, 'text': message, 'parse_mode': 'html'})

    if response.status_code == 200:
        return True
    else:
        return False