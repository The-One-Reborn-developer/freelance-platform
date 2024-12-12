from sqlalchemy import select

from app.database.models.users import User
from app.database.models.sync_session import sync_session


def put_user(telegram_id: int, **kwargs) -> None:
    """
    Updates the user with the given telegram_id in the database with the given key-value arguments.

    Args:
        telegram_id (int): The telegram_id of the user to update.
        **kwargs: The key-value arguments to update the user with.

    Returns:
        None
    """
    with sync_session() as session:
        with session.begin():
            try:
                user = session.scalar(select(User).where(User.telegram_id == telegram_id))

                if user:
                    for key, value in kwargs.items():
                        setattr(user, key, value)
            except Exception as e:
                print(f'Error updating user: {e}')