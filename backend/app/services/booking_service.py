from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.booking import Booking
from datetime import datetime


class BookingOverlapError(ValueError):
    """Space is already bookoed for the selected time"""


def validate_booking_time(
    db: Session,
    space_id: int,
    start_at: datetime,
    end_at: datetime
) -> None:
    """Check for conflits in acive booking in requested time """

    if start_at>= end_at:
        raise ValueError("Booking start time must be before end time")

    statement = (
        select(Booking.id)
        .where(
            Booking.space_id == space_id,
            Booking.status == "active",
            Booking.start_at < end_at,
            Booking.end_at > start_at
        )
    )

    existing_booking_id = db.scalar(statement)

    if existing_booking_id is not None:
        raise BookingOverlapError(
            "This space is already booked for the selected time"
        )


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
        space_id = booking_data.space_id,
        start_at = booking_data.start_at,
        end_at = booking_data.end_at,
        status = "active"
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)

    return booking