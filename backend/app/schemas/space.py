from pydantic import BaseModel, ConfigDict
from datetime import datetime
# for juist format api respond btw
class SpaceAvailabilityRead(BaseModel):
    id: int
    name: str
    capacity: int
    category: str
    facilities: list[str]
    is_available: bool
    available_from: datetime | None = None

class SpaceBookingSlot(BaseModel):
    start_at: datetime
    end_at: datetime

    model_config = ConfigDict(from_attributes=True)