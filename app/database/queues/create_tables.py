from app.database.models.base import Base
from app.database.models.sync_engine import sync_engine


def create_tables() -> None:
    """
    Creates all tables defined in the application's metadata.

    Utilizes the synchronous engine to establish a connection and runs an operation 
    to create all tables. In the event of an error during table creation, logs the 
    exception message.

    This function does not return any value.
    """
    with sync_engine.begin() as conn:
        try:
            Base.metadata.create_all(conn)
        except Exception as e:
            print(f'Error creating tables: {e}')