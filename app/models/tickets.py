from enum import Enum as PyEnum
from sqlalchemy import ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class TicketStatus(PyEnum):
    booked = 'booked'
    cancelled = 'cancelled'
    pending = 'pending'

class Ticket(Base):
    __tablename__ = "tickets"
    
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"))
    user_id: Mapped[int] = mapped_column(nullable=False)
    amount: Mapped[float] = mapped_column(nullable=False)
    count: Mapped[int] = mapped_column(nullable=False)
    status: Mapped[TicketStatus] = mapped_column(Enum(TicketStatus), default=TicketStatus.pending)
   
    event: Mapped["Event"] = relationship(back_populates="tickets")
