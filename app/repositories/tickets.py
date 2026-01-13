from sqlalchemy.orm import Session
from sqlalchemy import select, func, update

from app.models.events import EventTicketPool, Event
from app.models.tickets import Ticket, TicketStatus
from app.exceptions import ApiBaseException


class TicketRepository:

    def __init__(self, session: Session):
        self.session = session

    def get_pools_with_tickets(self, event_id: int):
        stmt = select(EventTicketPool).where(
            EventTicketPool.event_id == event_id,
            EventTicketPool.ticket_count > 0
        )
        result = self.session.execute(stmt)
        return result.scalars().all()

    def attempt_booking_on_pool(self, pool_id: int, ticket_count: int):
        
        stmt = update(EventTicketPool).where(
            EventTicketPool.id == pool_id,
            EventTicketPool.ticket_count >= ticket_count
        ).values(
            ticket_count=EventTicketPool.ticket_count - ticket_count
        )
        
        result = self.session.execute(stmt)
        self.session.commit()
        return result.rowcount > 0

    def get_user_ticket_count(self, user_id: int, event_id: int):
        
        stmt = select(func.sum(Ticket.count)).where(
            Ticket.user_id == user_id,
            Ticket.event_id == event_id,
            Ticket.status.in_([TicketStatus.booked, TicketStatus.pending])
        )
        
        result = self.session.execute(stmt)
        count = result.scalar()
        return count or 0

    def create_ticket(self, ticket: Ticket):
        self.session.add(ticket)
        self.session.commit()
        self.session.refresh(ticket)
        return ticket

    def get_ticket_price_for_event(self, event_id: int):
        stmt = select(Event.ticket_price).where(Event.id == event_id)
        result = self.session.execute(stmt)
        price = result.scalar()
        
        if price is None:
            raise ApiBaseException(
                message=f"Event with ID {event_id} not found",
                status_code=404
            )
        
        return price

    def get_ticket_by_ticket_id(self, ticket_id: int):
        stmt = select(Ticket).where(Ticket.id == ticket_id)
        result = self.session.execute(stmt)
        ticket = result.scalar_one_or_none()
        
        if ticket is None:
            raise ApiBaseException(
                message=f"Ticket with ID {ticket_id} not found",
                status_code=404
            )
        
        return ticket

    def update_ticket_status(self, ticket: Ticket, new_status: TicketStatus):
        ticket.status = new_status
        self.session.add(ticket)
        self.session.commit()
        self.session.refresh(ticket)
        return ticket

    def add_tickets_to_random_ticket_pool(self, tickets_to_add: int, event_id: int):
        stmt = select(EventTicketPool).where(
            EventTicketPool.event_id == event_id
        ).order_by(func.rand()).limit(1).with_for_update()
        
        result = self.session.execute(stmt)
        pool = result.scalar_one_or_none()
        
        if pool:
            pool.ticket_count += tickets_to_add
            self.session.commit()

    def release_tickets_to_pool(self, pool_id: int, count: int):
        stmt = update(EventTicketPool).where(
            EventTicketPool.id == pool_id
        ).values(
            ticket_count=EventTicketPool.ticket_count + count
        )
        
        self.session.execute(stmt)
        self.session.commit()


