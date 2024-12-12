from sqlalchemy import select

from app.database.models.bids import Bid
from app.database.models.sync_session import sync_session


def close_bid(bid_id: int) -> bool | None:
    with sync_session() as session:
        with session.begin():
            try:
                bid = session.scalar(select(Bid).where(Bid.id == bid_id))

                if bid:
                    bid.closed = True
                    return True
                else:
                    return False
            except Exception as e:
                print(f'Error closing bid: {e}')
                return None