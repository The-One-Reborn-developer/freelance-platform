from app.database.queries.get_responses_by_performer_telegram_id import get_responses_by_performer_telegram_id


def get_all_performer_chats(performer_telegram_id: int) -> list | None:
    try:
        performer_responses = get_responses_by_performer_telegram_id(performer_telegram_id)

        started_chats = []

        if performer_responses:
            for response in performer_responses:
                if response['chat_started']:
                    started_chats.append(response['bid_id'])

        return started_chats
    except Exception as e:
        print(f'Error getting all performer chats: {e}')
        return None