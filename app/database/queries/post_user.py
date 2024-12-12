from sqlalchemy import select

from app.database.models.users import User
from app.database.models.sync_session import sync_session


def post_user(telegram_id: int) -> None:
    """
    Creates a new user in the database if the user does not already exist.

    Args:
        telegram_id (int): The telegram ID of the user to create.

    Returns:
        None
    """
    with sync_session() as session:
        with session.begin():
            try:
                user = session.scalar(select(User).where(User.telegram_id == telegram_id))

                if not user:
                    user = User(telegram_id=telegram_id)
                    session.add(user)
            except Exception as e:
                print(f'Error creating user: {e}')