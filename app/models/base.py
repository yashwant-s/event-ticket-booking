from datetime import datetime

from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import DateTime
from app.core.utils import get_utc_now

class Base(DeclarativeBase):
    __abstract__=True

    id : Mapped[int]= mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default = get_utc_now, nullable=False )
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default= None, onupdate=get_utc_now, nullable=True)
