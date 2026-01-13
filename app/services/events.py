from app.exceptions import ApiBaseException
from app.models.events import Event, EventTicketPool
from app.repositories.events import EventRepository
from app.schemas.events import EventCreate, EventSuccessResponse


class EventService:

    def __init__(self, repo: EventRepository):
        self.repo = repo


    def create_event(self, event_data: EventCreate, owner_id: int):

        try:
            pool_list = []
            curr_tickets = event_data.pool_size

            while curr_tickets > 0:
                curr_batch_size = min(1000, curr_tickets)
                curr_tickets -= curr_batch_size
                
                pool = EventTicketPool(ticket_count=curr_batch_size)
                pool_list.append(pool)

            new_event = Event(
                name=event_data.name,
                address=event_data.address,
                event_time=event_data.event_time,
                pool_size=event_data.pool_size,
                ticket_price=event_data.ticket_price,
                owner_id=owner_id,
                pools=pool_list
            )

            saved_event = self.repo.save_event_with_pool(new_event, pool_list)

            return EventSuccessResponse(event_id=saved_event.id,
                                        event_name=saved_event.name)
        except Exception as e:
            raise ApiBaseException("failed to create event, service unavailable", status_code=503)





