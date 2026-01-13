


from fastapi import APIRouter, Header, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.repositories.events import EventRepository
from app.schemas.response import ApiSuccessResponse
from app.schemas.events import EventSuccessResponse, EventCreate
from app.services.events import EventService

router = APIRouter()


def get_event_service(db:Session = Depends(get_db)):
    repo = EventRepository(db)
    return EventService(repo)

@router.post("/events", response_model=ApiSuccessResponse[EventSuccessResponse])
async def create_event(
        event_data: EventCreate,
        owner_id: int = Header(..., alias="X-User-Id"),
        service: EventService = Depends(get_event_service)

):
    response = service.create_event(event_data, owner_id)

    return ApiSuccessResponse(message="Event Created successfully",
                              data=response)




