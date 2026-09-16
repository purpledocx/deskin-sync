from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


# base model added cuz DRY
class BookingBase(BaseModel):
    """overall fields + reservation validation"""

    space_id: int = Field(gt=0)
    start_at: datetime
    end_at: datetime

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

    model_config = ConfigDict(from_attributes=True) #allows read data direct from sqlalchemy


class BookingUpdate(BookingBase):
    """booking updating"""
    pass