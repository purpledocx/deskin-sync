import pytest

from app.models.booking import Booking
from app.models.space import Space
from app.services.booking_service import BookingOverlapError, validate_booking_time

from datetime import datetime, timezone


def date_time(hour: int) -> datetime:  # shortened for comfort reusability lol
    return datetime(2026, 10, 15, hour, 0, tzinfo=timezone.utc)


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