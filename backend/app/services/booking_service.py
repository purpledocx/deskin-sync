from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Booking, Space
from datetime import datetime, timezone


class BookingOverlapError(ValueError):
    """Space is already bookoed for the selected time"""


class SpaceNotFoundError(LookupError):
    """Requested space does not exist"""


class SpaceInactiveError(ValueError):
    """Requested space exists but can not be booked"""


class BookingInPastError(ValueError):
    """Requested start time lies in the past"""


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
            Booking.end_at > start_at,
            Booking.id != exclude_booking_id # added cuz found a bug 409 status_code when was coding api_update tests
        )
    )

    existing_booking_id = db.scalar(statement)

    if existing_booking_id is not None:
        raise BookingOverlapError(
            "This space is already booked for the selected time"
        )


def get_bookable_space(db: Session, space_id: int) -> Space:
    """Fetch a space and make sure it can be booked (sequence diagram: steps 6-11)"""

    space = db.get(Space, space_id)

    if space is None:
        raise SpaceNotFoundError("Space does not exist")
    if not space.is_active:
        raise SpaceInactiveError("Space is not active")

    return space


def create_booking(
    db: Session,
    user_id: int,
    space_id: int,
    start_at: datetime,
    end_at: datetime
) -> Booking:
    """Create an active booking (sequence diagram: steps 6-23).
    The router only translates the errors raised here into HTTP status codes"""

    get_bookable_space(db, space_id)

    # booking in the past is impossible -> checked BEFORE the overlap query, saves a DB round trip
    now = datetime.now(timezone.utc)
    if start_at < now:
        raise BookingInPastError(f"Start time can not be earlier than {now.strftime('%H:%M:%S %d-%m-%Y')}")

    validate_booking_time(db=db, space_id=space_id, start_at=start_at, end_at=end_at)

    booking = Booking(
        user_id=user_id,
        space_id=space_id,
        start_at=start_at,
        end_at=end_at,
        status="active"
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)

    return booking
