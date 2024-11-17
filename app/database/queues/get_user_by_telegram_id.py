from sqlalchemy import select

from app.database.models.users import User
from app.database.models.sync_session import sync_session


def get_user_by_telegram_id(telegram_id: int) -> User | list | None:
    """
    Gets a user by telegram_id from the database.

    Args:
        telegram_id (int): The telegram_id of the user to fetch.

    Returns:
        User | None: The user from the database, or None if no user was found.
    """
    with sync_session() as session:
        with session.begin():
            try:
                user = session.scalar(select(User).where(User.telegram_id == telegram_id))

                if user:
                    return [
                        user.id,
                        user.telegram_id,
                        user.full_name,
                        user.is_performer,
                        user.is_customer,
                        user.rate,
                        user.experience,
                        user.chat_id
                    ]
                else:
                    return []
            except Exception as e:
                print(f'Error getting user: {e}')
                return None