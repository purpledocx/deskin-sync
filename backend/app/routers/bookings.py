from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.booking import BookingCreate, BookingRead
from app. models.user import User
from app.models.space import Space
from app.database import get_db
from app.dependencies import get_current_user
from app.services.booking_service import BookingOverlapError, validate_booking_time

from typing import Annotated
router = APIRouter(
    prefix="/bookings",
    tags=["bookings"]
)

@router.post("/", response_model=BookingRead, status_code=status.HTTP_201_CREATED)
def create_booking(booking_data: BookingCreate, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):


    # get space + validate in case data integrity
    space = db.get(Space, booking_data.space_id)

    if not space:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Space does not exist")

    if not space.is_active:
        raise HTTPException(status_code= status.HTTP_409_CONFLICT, detail="Space is not active")


    # validate data -> create booking with following data -> add it to db -> return booking
    try:
        validate_booking_time(
            db = db,
            space_id = booking_data.space_id,
            start_at = booking_data.start_at,
            end_at = booking_data.end_at
        )
    except BookingOverlapError as err:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err))

    booking = Booking(
        user_id = current_user.id,
        space_id = current_user.space_id,
        start_at = current_user.start_at,
        end_at = current_user.end_at,
        status = "active"
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)

    return booking