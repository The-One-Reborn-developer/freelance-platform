from sqlalchemy import select

from app.database.models.bids import Bid
from app.database.models.sync_session import sync_session


def get_bids_by_city(city: str) -> list[dict] | None:
    """
    Retrieves all bids for the specified city.

    Args:
        city (str): The name of the city to filter bids.

    Returns:
        list[dict]: A list of dictionaries with bid details for each bid in the specified city.
    """
    with sync_session() as session:
        with session.begin():
            try:
                bids = session.scalars(select(Bid).where(Bid.city == city, Bid.closed == False)).all()

                if bids:
                    return [
                        {
                            'id': bid.id,
                            'customer_telegram_id': bid.customer_telegram_id,
                            'city': bid.city,
                            'description': bid.description,
                            'deadline': bid.deadline,
                            'instrument_provided': bid.instrument_provided,
                            'closed': bid.closed
                        }
                        for bid in bids
                    ]
                else:
                    return []
            except Exception as e:
                print(f'Error getting bids: {e}')
                return None