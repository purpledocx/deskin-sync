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
    end_at: datetime,
    exclude_booking_id: int | None = None
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