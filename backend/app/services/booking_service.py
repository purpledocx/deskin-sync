from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Booking, Space
from app.strategies.role_strategy import get_strategy

from datetime import datetime, timezone, timedelta


"""------------------------------------------ERRORS------------------------------------------------------------------------------------"""
# Server raises these, routers translates them into HTTP codes


class BookingOverlapError(ValueError):
    """Space is already bookoed for the selected time"""


class SpaceNotFoundError(LookupError):
    """Requested space does not exist"""


class SpaceInactiveError(ValueError):
    """Requested space exists but can not be booked"""


class BookingInPastError(ValueError):
    """Requested start time lies in the past"""


class BookingNotActiveError(ValueError):
    """Booking is cancelled and can no longer be changed"""


class BookingLockedError(ValueError):
    """Booking is inside the change window of the user's role"""

class BookingNotFoundError(LookupError):
    """Requested booking does not exist"""


class BookingAccessDeniedError(LookupError):
    """Requested booking does not exist"""



"""------------------------------------------RULES------------------------------------------------------------------------------------"""


def _as_utc(val: datetime) -> datetime:
    return val.replace(tzinfo=timezone.utc) if val.tzinfo is None else val

def _ensure_changable(booking: Booking, user, not_active_mesg: str) -> None:
    if booking.status != "active":
        raise BookingNotActiveError(not_active_mesg)
    
    reason = change_block_reason(booking, user)
    if reason:
        raise BookingLockedError(reason)


def change_block_reason(booking: Booking, user) -> str | None:

    min_minutes = get_strategy(user).min_mins_before_change
    time_left = _as_utc(booking.start_at) - datetime.now(timezone.utc)

    if time_left >= timedelta(minutes=min_minutes):
        return None
    
    if min_minutes == 0:
        return "Booking has already started and can no longer be changed or cancelled"

    return f"Booking can only be changed or cancelled at least {min_minutes} minutes before start"

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
            Booking.id != exclude_booking_id #  a booking must not conflict with itself on update
        )
    )

    if db.scalar(statement) is not None:
        raise BookingOverlapError("This space is already booked for selected time. Try to book it different timeframe")


def get_bookable_space(db: Session, space_id: int) -> Space:
    """Fetch a space and make sure it can be booked (sequence diagram: steps 6-11)"""

    space = db.get(Space, space_id)

    if space is None:
        raise SpaceNotFoundError("Space does not exist")
    if not space.is_active:
        raise SpaceInactiveError("Space is not active")

    return space


def get_managable_booking(db: Session, booking_id: int, user) -> Booking:
    """ fetch a booking and make sure users role can manage it """

    booking = db.get(Booking, booking_id)

    if booking is None:
        raise BookingNotFoundError("Booking not found")
    if not get_strategy(user).can_manage_booking(booking, user):
        raise BookingAccessDeniedError("You have no access to following booking")

    return booking

"""------------------------------------------USE CASES------------------------------------------------------------------------------------"""


def create_booking(db: Session, user_id: int, space_id: int, start_at: datetime, end_at: datetime) -> Booking:

    """Create an active booking, this router only translates the errors raised here into HTTP status codes"""

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


def update_booking(db: Session, booking_id: int, user, space_id: int, start_at: datetime, end_at: datetime) -> Booking:
    
    """Move an active booking to another space / time"""

    booking = get_managable_booking(db, booking_id, user)
    _ensure_changable(booking, user, "Only active bookings can be modified")

    if start_at <= datetime.now(timezone.utc):
        raise BookingInPastError("Start time can not be in the past")

    get_bookable_space(db, space_id)
    validate_booking_time(db, space_id, start_at, end_at, booking.id)

    booking.space_id = space_id
    booking.start_at = start_at
    booking.end_at = end_at

    db.commit()
    db.refresh(booking)

    return booking


def cancel_booking(db: Session, booking_id: int, user) -> Booking:
    
    booking = get_managable_booking(db, booking_id, user)
    _ensure_changable(booking, user, "Current booking is already cancelled")

    booking.status = "cancelled"

    db.commit()
    db.refresh(booking)

    return booking