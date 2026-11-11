import pytest

from app.models import Booking, Space, User, Role

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
    create_booking as create_booking_service,
    update_booking as update_booking_service,
    validate_booking_time,
)

from datetime import datetime, timezone, timedelta

def _test_day() -> datetime:
    future = datetime.now(timezone.utc) + timedelta(days=60)
    return future.replace(hour=0, minute=0, second=0, microsecond=0)

def date_time(hour: int) -> datetime:  # shortened for comfort reusability lol
    return _test_day() + timedelta(hours=hour)


def create_booking(
    db_session,
    user_id: int,
    space_id: int,
    start_hour: int,
    end_hour: int,
    status: str = "active"
    ):
    booking = Booking(
        user_id=user_id,
        space_id=space_id,
        start_at=date_time(start_hour),
        end_at=date_time(end_hour),
        status=status
    )

    db_session.add(booking)
    db_session.flush()

    return booking


"""------------------------------TESTS------------------------------"""

def test_allows_consecutive_booking(db_session, seeded_data):
    create_booking(
        db_session,
        seeded_data["user_id"],
        seeded_data["space_id"],
        9,
        10
    )
    validate_booking_time(db_session, seeded_data["space_id"], date_time(10), date_time(11))



def test_rejects_partial_overlap(db_session, seeded_data):
    create_booking(db_session, seeded_data["user_id"], seeded_data["space_id"], 9, 11)

    with pytest.raises(BookingOverlapError):
        validate_booking_time(db_session, seeded_data["space_id"], date_time(10), date_time(12))



def test_rejects_booking_inside_existing(db_session, seeded_data):
    create_booking(db_session, seeded_data["user_id"], seeded_data["space_id"], 9, 12)

    with pytest.raises(BookingOverlapError):
        validate_booking_time(db_session, seeded_data["space_id"], date_time(10), date_time(11))



def test_rejects_booking_containing_existing(db_session, seeded_data):
    create_booking(db_session, seeded_data["user_id"], seeded_data["space_id"], 10, 11)

    with pytest.raises(BookingOverlapError):
        validate_booking_time(db_session, seeded_data["space_id"], date_time(9), date_time(12))



def test_allows_booking_when_existing_cancelled(db_session, seeded_data):
    create_booking(db_session, seeded_data["user_id"], seeded_data["space_id"], 9, 11, status="cancelled")

    validate_booking_time(db_session, seeded_data["space_id"], date_time(10), date_time(12))



def test_allows_same_time_different_space(db_session, seeded_data):
    create_booking(db_session, seeded_data["user_id"], seeded_data["space_id"], 9, 11)

    other_space = Space(
        name="Desk A2",
        capacity=1,
        category_id=seeded_data["category_id"],
        is_active=True
    )
    db_session.add(other_space)
    db_session.flush()

    validate_booking_time(db_session, other_space.id, date_time(9), date_time(11))


def test_rejects_invalid_time_range(db_session, seeded_data):
    with pytest.raises(ValueError):
        validate_booking_time(db_session, seeded_data["space_id"], date_time(11), date_time(10))



"""------------------------------CREATE BOOKING (service layer)------------------------------"""

def test_service_creates_active_booking(db_session, seeded_data):
    booking = create_booking_service(db_session, seeded_data["user_id"], seeded_data["space_id"], date_time(9), date_time(10))

    assert booking.id is not None
    assert booking.status == "active"
    assert booking.user_id == seeded_data["user_id"]


def test_service_rejects_unknown_space(db_session, seeded_data):
    with pytest.raises(SpaceNotFoundError):
        create_booking_service(db_session, seeded_data["user_id"], 999999, date_time(9), date_time(10))


def test_service_rejects_inactive_space(db_session, seeded_data):
    space = db_session.get(Space, seeded_data["space_id"])
    space.is_active = False
    db_session.flush()

    with pytest.raises(SpaceInactiveError):
        create_booking_service(db_session, seeded_data["user_id"], seeded_data["space_id"], date_time(9), date_time(10))


def test_service_rejects_booking_in_past(db_session, seeded_data):
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)

    with pytest.raises(BookingInPastError):
        create_booking_service(db_session, seeded_data["user_id"], seeded_data["space_id"], yesterday, yesterday + timedelta(hours=1))


def test_service_rejects_overlap(db_session, seeded_data):
    create_booking(db_session, seeded_data["user_id"], seeded_data["space_id"], 9, 11)

    with pytest.raises(BookingOverlapError):
        create_booking_service(db_session, seeded_data["user_id"], seeded_data["space_id"], date_time(10), date_time(12))



"""------------------------------UPDATE / CANCEL BOOKING (service layer)------------------------------"""

def _owner(db_session, seeded_data) -> User:
    return db_session.get(User, seeded_data["user_id"])


def _stranger(db_session, seeded_data) -> User:
    user = User(
        name="Stranger",
        email="stranger@test.nl",
        password_hash="some-salted-hash",
        role_id=_owner(db_session, seeded_data).role_id
    )
    db_session.add(user)
    db_session.flush()
    return user


def test_service_updates_booking(db_session, seeded_data):
    booking = create_booking(db_session, seeded_data["user_id"], seeded_data["space_id"], 9, 10)

    updated = update_booking_service(db_session, booking.id, _owner(db_session, seeded_data), seeded_data["space_id"], date_time(13), date_time(14))

    assert updated.start_at == date_time(13)
    assert updated.end_at == date_time(14)


def test_service_update_rejects_unknown_booking(db_session, seeded_data):
    with pytest.raises(BookingNotFoundError):
        update_booking_service(db_session, 999999, _owner(db_session, seeded_data), seeded_data["space_id"], date_time(13), date_time(14))


def test_service_update_rejects_other_users_booking(db_session, seeded_data):
    booking = create_booking(db_session, seeded_data["user_id"], seeded_data["space_id"], 9, 10)

    with pytest.raises(BookingAccessDeniedError):
        update_booking_service(db_session, booking.id, _stranger(db_session, seeded_data), seeded_data["space_id"], date_time(13), date_time(14))


def test_service_cancels_booking(db_session, seeded_data):
    booking = create_booking(db_session, seeded_data["user_id"], seeded_data["space_id"], 9, 10)

    cancelled = cancel_booking_service(db_session, booking.id, _owner(db_session, seeded_data))

    assert cancelled.status == "cancelled"


def test_service_cancel_rejects_already_cancelled(db_session, seeded_data):
    booking = create_booking(db_session, seeded_data["user_id"], seeded_data["space_id"], 9, 10, status="cancelled")

    with pytest.raises(BookingNotActiveError):
        cancel_booking_service(db_session, booking.id, _owner(db_session, seeded_data))


def test_service_cancel_rejects_inside_30_min_window(db_session, seeded_data):
    soon = datetime.now(timezone.utc) + timedelta(minutes=10)
    booking = Booking(user_id=seeded_data["user_id"], space_id=seeded_data["space_id"], start_at=soon, end_at=soon + timedelta(hours=1), status="active")
    db_session.add(booking)
    db_session.flush()

    with pytest.raises(BookingLockedError):
        cancel_booking_service(db_session, booking.id, _owner(db_session, seeded_data))