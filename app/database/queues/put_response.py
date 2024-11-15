from sqlalchemy import select

from app.database.models.bids import Response
from app.database.models.sync_session import sync_session


def put_response(bid_id: int, performer_telegram_id: int, **kwargs) -> None:
    with sync_session() as session:
        with session.begin():
            try:
                response = session.scalar(select(Response).where(Response.bid_id == bid_id,
                                                             Response.performer_telegram_id == performer_telegram_id))

                if response:
                    for key, value in kwargs.items():
                        setattr(response, key, value)
            except Exception as e:
                print(f'Error updating response: {e}')