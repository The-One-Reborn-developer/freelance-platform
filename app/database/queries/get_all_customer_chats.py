from app.database.queries.get_responses_by_customer_telegram_id import get_responses_by_customer_telegram_id


def get_all_customer_chats(customer_telegram_id: int) -> list | None:
    try:
        customer_responses = get_responses_by_customer_telegram_id(customer_telegram_id)

        started_chats = set()

        if customer_responses:
            for response in customer_responses:
                if response['chat_started']:
                    started_chats.add(response['bid_id'])

        return list(started_chats)
    except Exception as e:
        print(f'Error getting all customer chats: {e}')
        return None