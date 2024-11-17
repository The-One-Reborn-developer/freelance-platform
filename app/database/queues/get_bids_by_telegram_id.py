from sqlalchemy import select

from app.database.models.bids import Bid
from app.database.models.sync_session import sync_session


def get_bids_by_telegram_id(telegram_id: int) -> list[dict] | None:
    with sync_session() as session:
        with session.begin():
            try:
                bids = session.scalars(select(Bid).where(Bid.customer_telegram_id == telegram_id,
                                                         Bid.closed == False)).all()

                if bids:
                    return [
                        {
                            'id': bid.id,
                            'customer_telegram_id': bid.customer_telegram_id,
                            'city': bid.city,
                            'description': bid.description,
                            'deadline': bid.deadline,
                            'instrument_provided': bid.instrument_provided
                        }
                        for bid in bids
                    ]
                else:
                    return []
            except Exception as e:
                print(f'Error getting bids: {e}')
                return None