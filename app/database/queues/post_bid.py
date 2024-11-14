from sqlalchemy import select

from app.database.models.bids import Bid
from app.database.models.sync_session import sync_session


def post_bid(customer_telegram_id: int,
             city: str,
             description: str,
             deadline: str,
             instrument_provided: bool) -> bool | None:
    """
    Creates a new bid in the database if the bid does not already exist.

    Args:
        customer_telegram_id (int): The telegram ID of the customer who made the bid.
        city (str): The city of the bid.
        description (str): The description of the bid.
        price (int): The price of the bid.

    Returns:
        None
    """
    with sync_session() as session:
        with session.begin():
            try:
                bid = session.scalar(select(Bid).where(Bid.customer_telegram_id == customer_telegram_id,
                                                       Bid.city == city,
                                                       Bid.description == description,
                                                       Bid.deadline == deadline,
                                                       Bid.instrument_provided == instrument_provided))

                if not bid:
                    bid = Bid(customer_telegram_id=customer_telegram_id,
                              city=city,
                              description=description,
                              deadline=deadline,
                              instrument_provided=instrument_provided)
                    session.add(bid)

                    return True
                else:
                    return False
            except Exception as e:
                print(f'Error creating bid: {e}')
                return None