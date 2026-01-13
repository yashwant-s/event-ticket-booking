


from fastapi import APIRouter, Header, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.repositories.events import EventRepository
from app.repositories.tickets import TicketRepository
from app.schemas.response import ApiSuccessResponse
from app.schemas.tickets import TicketCreate, TicketCreateResponse, TicketCancelledResponse

from app.services.tickets import TicketService

router = APIRouter()


def get_ticket_service(db:Session = Depends(get_db)):
    repo = TicketRepository(db)
    return TicketService(repo)

@router.post("/tickets", response_model=ApiSuccessResponse[TicketCreateResponse])
async def book_ticket(
        ticket_data: TicketCreate,
        user_id: int = Header(..., alias="X-User-Id"),
        service: TicketService = Depends(get_ticket_service)

):
    response = service.book_ticket(ticket_data, user_id)

    return ApiSuccessResponse(message="Ticket booked successfully",
                              data=response)


@router.delete("/tickets/{ticket_id}", response_model=ApiSuccessResponse[TicketCancelledResponse])
async def cancel_ticket(
        ticket_id: int,
        user_id: int = Header(..., alias="X-User-Id"),
        service: TicketService = Depends(get_ticket_service)
):
    response = service.cancel_ticket(ticket_id, user_id)
    
    return ApiSuccessResponse(
        message="Ticket cancelled successfully",
        data=response
    )





