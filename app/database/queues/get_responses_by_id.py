from sqlalchemy import select

from app.database.models.bids import Response
from app.database.models.sync_session import sync_session


def get_responses_by_id(bid_id: int) -> bool | None:
    with sync_session() as session:
        with session.begin():
            try:
                responses = session.scalars(select(Response).where(Response.bid_id == bid_id)).all()

                return [
                    {
                        'id': response.id,
                        'bid_id': response.bid_id,
                        'performer_telegram_id': response.performer_telegram_id,
                        'performer_full_name': response.performer_full_name,
                        'performer_rate': response.performer_rate,
                        'performer_experience': response.performer_experience
                    }
                    for response in responses
                ]
            except Exception as e:
                print(f'Error getting responses: {e}')
                return None