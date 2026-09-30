from pydantic import BaseModel
# for juist format api respond btw
class SpaceAvailabilityRead(BaseModel):
    id: int
    name: str
    capacity: int
    category: str
    facilities: list[str]
    is_available: bool