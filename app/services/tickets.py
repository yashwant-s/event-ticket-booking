import random
from cachetools import TTLCache


from app.exceptions import ApiBaseException
from app.models.tickets import Ticket, TicketStatus
from app.repositories.tickets import TicketRepository
from app.schemas.tickets import TicketCreate, TicketCreateResponse, TicketCancelledResponse


price_cache = TTLCache(maxsize=10000, ttl=3600)


class TicketService:

    def __init__(self, repo :TicketRepository):

        self.repo = repo



    def book_ticket(self, booking_data: TicketCreate, user_id: int):
        MAX_TICKETS_PER_USER = 2

        current_ticket_holdings = self.repo.get_user_ticket_count(user_id, booking_data.event_id)

        if current_ticket_holdings + booking_data.ticket_count > MAX_TICKETS_PER_USER:
            raise ApiBaseException(message=f"Ticket quota for user exceeded the limit. You can only hold {MAX_TICKETS_PER_USER} tickets max.",
                                   status_code=400)

        ticket_pools = self.repo.get_pools_with_tickets(booking_data.event_id)

        if not ticket_pools:
            raise ApiBaseException(
                message="Event sold out or does not exist",
                status_code=404
            )

        random.shuffle(ticket_pools)

        required_ticket_count = booking_data.ticket_count
        booked_pools = []

        for pool in ticket_pools:

            if required_ticket_count==0:
                break

            ticket_available = min(pool.ticket_count, required_ticket_count)
            result = self.repo.attempt_booking_on_pool(pool_id=pool.id, ticket_count=ticket_available)

            if result :
                required_ticket_count -= ticket_available
                booked_pools.append((pool.id, ticket_available))

        if required_ticket_count:

            self._rollback_partial_bookings(booked_pools)
            raise ApiBaseException(message= "Not enough tickets available to fulfill your request",
                                   status_code=400)



        if price_cache.get(booking_data.event_id):
             unit_price = price_cache[booking_data.event_id]
        else:
             unit_price = self.repo.get_ticket_price_for_event(booking_data.event_id)
             price_cache[booking_data.event_id] = unit_price
        
        total_amount = unit_price*booking_data.ticket_count
        new_ticket = Ticket(
            event_id = booking_data.event_id,
            user_id=user_id,
            amount = total_amount,
            count = booking_data.ticket_count,
            status= TicketStatus.booked

        )
        ticket = self.repo.create_ticket(new_ticket)

        return TicketCreateResponse(ticket_id=ticket.id,
                                    event_id=ticket.event_id,
                                    status=ticket.status,
                                    amount=ticket.amount,
                                    ticket_count=ticket.count
                                    )

    def _rollback_partial_bookings(self, booked_pools):
        for pool_id, count in booked_pools:
            self.repo.release_tickets_to_pool(pool_id, count)

    def cancel_ticket(self, ticket_id, user_id):

        ticket = self.repo.get_ticket_by_ticket_id(ticket_id)

        if ticket.user_id != user_id:
            raise ApiBaseException(message="You are not allowed to cancel this ticket", status_code=401)
        if ticket.status == TicketStatus.cancelled:
            raise ApiBaseException(message="This ticket is already cancelled", status_code=400)

        ticket_count = ticket.count

        self.repo.update_ticket_status(ticket, TicketStatus.cancelled)

        self.repo.add_tickets_to_random_ticket_pool(ticket_count, ticket.event_id)

        return TicketCancelledResponse(
            ticket_id=ticket_id,
            status=ticket.status,
            event_id=ticket.event_id
        )








