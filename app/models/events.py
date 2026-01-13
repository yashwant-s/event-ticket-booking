from datetime import datetime
from typing import List

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship


from app.models.base import Base


class Event(Base):

    __tablename__ = "events"

    name: Mapped[str] = mapped_column(String(250), nullable=False)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    pool_size: Mapped[int] = mapped_column(nullable=False)
    ticket_price: Mapped[float] = mapped_column(nullable=False)
    owner_id: Mapped[int] = mapped_column(nullable=False)

    pools: Mapped[List["EventTicketPool"]] = relationship(back_populates="event", cascade="all, delete-orphan")
    tickets: Mapped[List["Ticket"]] = relationship(back_populates="event")

class EventTicketPool(Base):

    __tablename__ = "event_ticket_pools"

    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"))
    ticket_count: Mapped[int] = mapped_column(nullable=False)
    event: Mapped["Event"] = relationship(back_populates="pools")




