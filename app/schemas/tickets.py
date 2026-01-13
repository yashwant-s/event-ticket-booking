from pydantic import BaseModel, Field

from app.models.tickets import TicketStatus


class TicketCreate(BaseModel):
    event_id: int
    ticket_count: int = Field(gt=0, lt=3)


class TicketCreateResponse(BaseModel):
    ticket_id : int
    status: TicketStatus
    event_id: int
    amount: float
    ticket_count: int


class TicketCancelledResponse(BaseModel):
    ticket_id: int
    status: TicketStatus
    event_id: int




