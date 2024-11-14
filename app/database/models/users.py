from sqlalchemy import BigInteger, String, Boolean, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database.models.base import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[BigInteger] = mapped_column(BigInteger)
    full_name: Mapped[str] = mapped_column(String(255), nullable=True)
    is_performer: Mapped[bool] = mapped_column(Boolean, default=False)
    is_customer: Mapped[bool] = mapped_column(Boolean, default=False)
    rate: Mapped[float] = mapped_column(Float, default=0.0)
    experience: Mapped[int] = mapped_column(Integer, default=0)
    chat_id: Mapped[BigInteger] = mapped_column(BigInteger, nullable=True)