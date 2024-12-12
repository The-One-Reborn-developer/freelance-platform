from sqlalchemy import select

from app.database.models.bids import Bid
from app.database.models.sync_session import sync_session


def get_bid_by_bid_id(bid_id: int) -> list | None:
    with sync_session() as session:
        with session.begin():
            try:
                bid = session.scalar(select(Bid).where(Bid.id == bid_id))

                if bid:
                    return [
                        bid.id,
                        bid.customer_telegram_id,
                        bid.city,
                        bid.description,
                        bid.deadline,
                        bid.instrument_provided,
                        bid.closed
                    ]
                else:
                    return []
            except Exception as e:
                print(f'Error getting bids: {e}')
                return None