from sqlalchemy.orm import sessionmaker

from app.database.models.sync_engine import sync_engine


sync_session = sessionmaker(sync_engine, expire_on_commit=False)