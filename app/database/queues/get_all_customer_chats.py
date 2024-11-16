from app.database.queues.get_responses_by_customer_telegram_id import get_responses_by_customer_telegram_id


def get_all_customer_chats(customer_telegram_id: int) -> list:
    customer_responses = get_responses_by_customer_telegram_id(customer_telegram_id)

    started_chats = []

    if customer_responses:
        for response in customer_responses:
            if response['chat_started']:
                started_chats.append(response['bid_id'])

    return started_chats