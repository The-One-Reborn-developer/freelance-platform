from sqlalchemy import (BigInteger,
                        String,
                        Text,
                        ForeignKey,
                        UniqueConstraint,
                        Boolean,
                        Float,
                        Integer)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import Base


class Bid(Base):
    __tablename__ = 'bids'

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_telegram_id: Mapped[BigInteger] = mapped_column(BigInteger)
    city: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    deadline: Mapped[str] = mapped_column(String(255))
    instrument_provided: Mapped[bool] = mapped_column(Boolean, default=False)
    closed: Mapped[bool] = mapped_column(Boolean, default=False)

    responses = relationship('Response', back_populates='bid')


class Response(Base):
    __tablename__ = 'responses'

    id: Mapped[int] = mapped_column(primary_key=True)
    bid_id: Mapped[int] = mapped_column(ForeignKey('bids.id'))
    performer_telegram_id: Mapped[BigInteger] = mapped_column(BigInteger)
    performer_full_name: Mapped[str] = mapped_column(String(255))
    performer_rate: Mapped[float] = mapped_column(Float, default=0.0)
    performer_experience: Mapped[int] = mapped_column(Integer, default=0)
    chat_started: Mapped[bool] = mapped_column(Boolean, default=False)

    bid = relationship('Bid', back_populates='responses')

    __table_args__ = (
        UniqueConstraint('bid_id', 'performer_telegram_id', name='unique_bid_response'),
    )