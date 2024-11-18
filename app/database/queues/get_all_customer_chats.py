from app.database.queues.get_responses_by_customer_telegram_id import get_responses_by_customer_telegram_id


def get_all_customer_chats(customer_telegram_id: int) -> list | None:
    try:
        customer_responses = get_responses_by_customer_telegram_id(customer_telegram_id)

        started_chats = []

        if customer_responses:
            for response in customer_responses:
                if response['chat_started']:
                    print(f'response {response} appended to started_chats')
                    started_chats.append(response['bid_id'])

        return started_chats
    except Exception as e:
        print(f'Error getting all customer chats: {e}')
        return None