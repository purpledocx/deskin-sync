from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session, joinedload

from app.schemas.booking import BookingCreate, BookingRead, BookingUpdate

from app. models import User, Space, Booking

from app.database import get_db
from app.dependencies import get_current_user
from app.services.booking_service import BookingOverlapError, validate_booking_time
from app.strategies.role_strategy import get_strategy

from typing import Annotated
from datetime import datetime, timedelta, timezone

router = APIRouter(
    prefix="/bookings",
    tags=["bookings"]
)



"""______________________________________INCAPSULATED_FUNCS______________________________________"""



# fetched Booking by ID and verified booking-to-user belongings
def _get_owned_booking(db: Session, booking_id: int, current_user) -> Booking:
    booking = db.query(Booking).filter(Booking.id == booking_id).first()

    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    if not get_strategy(current_user).can_manage_booking(booking, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You have no access to following booking")

    return booking


# Change allowed ONLY until 30 mins beore start_at
def _editable_window(booking: Booking, current_user):
    min_minutes = get_strategy(current_user).min_mins_before_change
    now = datetime.now(timezone.utc)
    start_at = booking.start_at

    if start_at.tzinfo is None:
        start_at = start_at.replace(tzinfo=timezone.utc)

    if start_at - now < timedelta(minutes=min_minutes):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Booking can only be changed or cancelled at least {min_minutes} minutes before start")




"""------------------------------------------ENDPOINTS------------------------------------------"""

# POST: Create Booking
@router.post("/", response_model=BookingRead, status_code=status.HTTP_201_CREATED)
def create_booking(booking_data: BookingCreate, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):


    # get space + validate in case data integrity
    space = db.get(Space, booking_data.space_id)

    if not space:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Space does not exist")

    if not space.is_active:
        raise HTTPException(status_code= status.HTTP_409_CONFLICT, detail="Space is not active")


    # booking in the past is impossible -> check BEFORE overlap validation
    if booking_data.start_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Start time can not be earlier than {datetime.now(timezone.utc).strftime('%H:%M:%S %d-%m-%Y')}")


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



# GET: Get all bookings (own if Student)
@router.get("/", response_model=list[BookingRead]) #returns list
def list_bookings(db: Annotated[Session, Depends(get_db)],current_user: Annotated[User, Depends(get_current_user)]): # Depends(get_current_user) will automatically get user based on JWT

    query = db.query(Booking).options(
        joinedload(Booking.space),
        joinedload(Booking.user)
    )

    if not get_strategy(current_user).can_view_all():
        query = query.filter(Booking.user_id == current_user.id)

    return query.order_by(Booking.start_at).all()


# PUT: Modify Booking
@router.put("/{booking_id}", response_model=BookingRead)
def update_booking(booking_id: int, payload: BookingUpdate, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):


    # get booking + validation
    booking = _get_owned_booking(db, booking_id, current_user)

    if booking.status != "active":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only active bookings can be modified")
    
    _editable_window(booking, current_user)

    if payload.start_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Start time can not be in the past")


    # get space + validation
    space = db.get(Space, payload.space_id)

    if not space:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Space does not exists")
    if not space.is_active:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Space is not active")

    
    # data validation
    try:
        validate_booking_time(
            db = db,
            space_id= payload.space_id,
            start_at= payload.start_at,
            end_at= payload.end_at,
            exclude_booking_id = booking.id
        )
    except BookingOverlapError as err:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err))

    # data modifying
    booking.space_id = payload.space_id
    booking.start_at = payload.start_at
    booking.end_at = payload.end_at

    db.commit()
    db.refresh(booking)

    return booking


# DELETE: Cancel Booking
@router.delete("/{booking_id}", response_model=BookingRead)
def cancel_booking( booking_id: int, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):


    booking = _get_owned_booking(db, booking_id, current_user)


    if booking.status != "active":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Current booking is already cancelled")

    _editable_window(booking, current_user)


    booking.status = "cancelled"


    db.commit()
    db.refresh(booking)

    return booking