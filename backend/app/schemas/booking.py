from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, model_validator, field_validator


def _ensure_utc(val: datetime) -> datetime:
    return val.replace(tzinfo=timezone.utc) if val.tzinfo is None else val

# base model cuz DRY
class BookingBase(BaseModel):
    """overall fields + reservation validation"""

    space_id: int = Field(gt=0)
    start_at: datetime
    end_at: datetime

    # fix for comfort timezone wirte in (POST/bookings in /docs) (noo need to write Z, just 2030-01-01T10:00:00)
    @field_validator("start_at", "end_at")
    @classmethod
    def ensure_timezone(cls, val):
        return _ensure_utc(val)


    @model_validator(mode="after")
    def check_time_range(self):
        if self.start_at >= self.end_at:
            raise ValueError("Start time needs to be before end time")
        return self



"""____________________Booking_CRUD_operations____________________""" 

class BookingCreate(BookingBase):
    """new booking"""
    pass


class BookingRead(BookingBase):
    """full reservation returned from DB"""

    id: int
    user_id: int
    status: str
    created_at: datetime
    space_name: str
    user_name: str

    # verdict of the role rules for the requesting user, filled in by the router.
    # the frontend renders these instead of re-evaluating the 30-minute rule itself
    can_modify: bool = False
    lock_hint: str | None = None

    model_config = ConfigDict(from_attributes=True) #allows read data direct from sqlalchemy

    


class BookingUpdate(BookingBase):
    """booking updating"""
    pass