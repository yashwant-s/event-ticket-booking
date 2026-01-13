from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone

class EventCreate(BaseModel):
    name: str = Field(min_length=1, max_length=250)
    address: str = Field(min_length=1, max_length=500)
    event_time: datetime
    pool_size: int = Field(gt=0)
    ticket_price: float = Field(gt=0)

    @field_validator('event_time')
    @classmethod
    def check_future_date(cls, v: datetime) -> datetime:
        now_utc = datetime.now(timezone.utc)
        
        # Ensure the datetime is timezone-aware
        if v.tzinfo is None:
            raise ValueError('Event time must include timezone information')
        
        # Compare timezone-aware datetimes
        if v < now_utc:
            raise ValueError('Event time must be in the future')
        
        return v

class EventSuccessResponse(BaseModel):
    event_name: str
    event_id : int