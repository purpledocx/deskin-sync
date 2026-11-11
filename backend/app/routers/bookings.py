from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Booking, User
from app.schemas.booking import BookingCreate, BookingRead, BookingUpdate
from app.services.booking_service import (
    BookingAccessDeniedError,
    BookingInPastError,
    BookingLockedError,
    BookingNotActiveError,
    BookingNotFoundError,
    BookingOverlapError,
    SpaceInactiveError,
    SpaceNotFoundError,
    cancel_booking as cancel_booking_service,
    change_block_reason,
    create_booking as create_booking_service,
    update_booking as update_booking_service,
)
from app.strategies.role_strategy import get_strategy

from typing import Annotated
from datetime import datetime, timedelta, timezone

router = APIRouter(
    prefix="/bookings",
    tags=["bookings"]
)



"""______________________________________INCAPSULATED_FUNCS____________________________________________________________________________"""
# All business rules live in booking service
# router only translate service errors into HTTP codes

_ERROR_STATUS = {
    BookingNotFoundError: status.HTTP_404_NOT_FOUND,
    SpaceNotFoundError: status.HTTP_404_NOT_FOUND,
    BookingAccessDeniedError: status.HTTP_403_FORBIDDEN,
    BookingInPastError: status.HTTP_400_BAD_REQUEST,
    SpaceInactiveError: status.HTTP_409_CONFLICT,
    BookingOverlapError: status.HTTP_409_CONFLICT,
    BookingNotActiveError: status.HTTP_409_CONFLICT,
    BookingLockedError: status.HTTP_409_CONFLICT,
}
_BOOKING_ERRORS = tuple(_ERROR_STATUS)


def _as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value


# fetched Booking by ID and verified booking-to-user belongings
def _get_owned_booking(db: Session, booking_id: int, current_user) -> Booking:
    booking = db.query(Booking).filter(Booking.id == booking_id).first()

    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    if not get_strategy(current_user).can_manage_booking(booking, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You have no access to following booking")

    return booking


def _to_http(err: Exception) -> HTTPException:
    return HTTPException(_ERROR_STATUS[type(err)], str(err))


# Attaches the verdict of the role rules to the booking, so the UI only has to
# render it instead of deciding it again
def _with_permissions(booking: Booking, current_user) -> Booking:
    if booking.status != "active":
        booking.can_modify = False
        booking.lock_hint = None
    elif not get_strategy(current_user).can_manage_booking(booking, current_user):
        booking.can_modify = False
        booking.lock_hint = "Only the owner of this booking or an admin can change it"
    else:
        reason = change_block_reason(booking, current_user)
        booking.can_modify = reason is None
        booking.lock_hint = reason

    return booking




"""------------------------------------------ENDPOINTS------------------------------------------------------------------------------------"""

# POST: Create Booking
@router.post("/", response_model=BookingRead, status_code=status.HTTP_201_CREATED)
def create_booking(booking_data: BookingCreate, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):


    # all business rules live in booking service (see sequence diagram)
    try:
        booking = create_booking_service(
            db = db,
            user_id = current_user.id,
            space_id = booking_data.space_id,
            start_at = booking_data.start_at,
            end_at = booking_data.end_at
        )
    
    except _BOOKING_ERRORS as err:
        raise _to_http(err) from err

    return _with_permissions(booking, current_user)



# GET: Get all bookings (own if Student)
@router.get("/", response_model=list[BookingRead]) #returns list
def list_bookings(db: Annotated[Session, Depends(get_db)],current_user: Annotated[User, Depends(get_current_user)]): # Depends(get_current_user) will automatically get user based on JWT

    query = db.query(Booking).options(
        joinedload(Booking.space),
        joinedload(Booking.user)
    )

    if not get_strategy(current_user).can_view_all():
        query = query.filter(Booking.user_id == current_user.id)

    bookings = query.order_by(Booking.start_at).all()

    return [_with_permissions(booking, current_user) for booking in bookings]


# PUT: Modify Booking
@router.put("/{booking_id}", response_model=BookingRead)
def update_booking(booking_id: int, payload: BookingUpdate, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):

    try:
        booking = update_booking_service(db, booking_id, current_user, payload.space_id, payload.start_at, payload.end_at)
    except _BOOKING_ERRORS as err:
        raise _to_http(err) from err

    return _with_permissions(booking, current_user)

# DELETE: Cancel Booking
@router.delete("/{booking_id}", response_model=BookingRead)
def cancel_booking( booking_id: int, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):

    try:
        booking = cancel_booking_service(db, booking_id, current_user)
    except _BOOKING_ERRORS as err:
        raise _to_http(err) from err

    return _with_permissions(booking, current_user)