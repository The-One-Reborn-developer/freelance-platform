from sqlalchemy import select

from app.database.models.bids import Response
from app.database.models.sync_session import sync_session

from app.database.queries.get_bids_by_telegram_id import get_bids_by_telegram_id


def get_responses_by_customer_telegram_id(customer_telegram_id: int) -> list[dict] | None:
    with sync_session() as session:
        with session.begin():
            try:
                bids = get_bids_by_telegram_id(customer_telegram_id)

                if bids:
                    all_responses = []

                    for bid in bids:
                        bid_responses = session.scalars(select(Response).where(Response.bid_id == bid['id'],
                                                                            Response.chat_started == True)).all()

                        all_responses.extend(bid_responses)

                    return [
                        {
                            'id': response.id,
                            'bid_id': response.bid_id,
                            'performer_telegram_id': response.performer_telegram_id,
                            'performer_full_name': response.performer_full_name,
                            'performer_rate': response.performer_rate,
                            'performer_experience': response.performer_experience,
                            'chat_started': response.chat_started
                        }
                        for response in all_responses
                    ]
                else:
                    return []
            except Exception as e:
                print(f'Error getting responses: {e}')
                return None