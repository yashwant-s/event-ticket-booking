from typing import List

from sqlalchemy.orm import Session

from app.models.events import Event, EventTicketPool


class EventRepository:

    def __init__(self, session:Session):
        self.session = session

    def save_event_with_pool(self, event: Event, pools: List[EventTicketPool]):
        self.session.add(event)
        self.session.commit()
        self.session.refresh(event)
        return event
