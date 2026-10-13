import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import get_db
from app.models import Space,SpaceFacility, Facility, Booking

from datetime import datetime, timedelta



"""------------------------------------------------------------FIXTURE------------------------------------------------------------"""


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


"""------------------------------------------------------------HELPER_FUNCTIONS------------------------------------------------------------"""


def _slot(offset_hrs: int = 0, length_hrs: int = 1): #time slot start: +60days from now + offset | end: length_hrs

    #base time += 60 days from now
    base = (datetime.now() + timedelta(days=60)).replace(minute=0, second=0, microsecond=0)
    # shift start by offset
    start = base + timedelta(hours=offset_hrs)
    #return tuple for testing slot
    return start, start + timedelta(hours=length_hrs)



def _add_booking(db, user_id, space_id, start, end, status="active"):

    booking = Booking(user_id=user_id, space_id=space_id, start_at=start, end_at=end, status=status)
    db.add(booking)
    db.flush()
    return booking


def _availability(client, start, end):
    return client.get("/spaces/availability", params={"start_at": start.isoformat(), "end_at": end.isoformat()})

# extracts specific space by ID from API response
def _find(response, space_id):
    return next(item for item in response.json() if item["id"] == space_id)



"""------------------------------------------------------------TESTS------------------------------------------------------------"""



def test_free_space_is_available(client, seeded_data):

    """ empty space is shown as available """
    
    start, end = _slot()
    response = _availability(client, start, end)

    assert response.status_code == 200
    assert _find(response, seeded_data["space_id"])["is_available"] is True



def test_overlapping_active_booking_makes_space_unavailable(client, db_session, seeded_data):

    """ overlapping active bookings block the space """

    b_start, b_end = _slot(0, 2)
    _add_booking(db_session, seeded_data["user_id"], seeded_data["space_id"], b_start, b_end)

    start, end = _slot(1, 2) # partly overlap
    response = _availability(client, start, end)

    assert _find(response, seeded_data["space_id"])["is_available"] is False



def test_back_to_back_booking_does_not_block(client, db_session, seeded_data):

    """ back-to-back bookings (end time == start time) do not conflict """

    b_start, b_end = _slot(0, 1)
    _add_booking(db_session, seeded_data["user_id"], seeded_data["space_id"], b_start, b_end)

    start, end = _slot(1, 1) # starts exactly after first
    response = _availability(client, start, end)

    assert _find(response, seeded_data["space_id"])["is_available"] is True



def test_cancelled_booking_does_not_block(client, db_session, seeded_data):

    """ cancelled bookings don't block the slot """

    b_start, b_end = _slot(0, 1)
    _add_booking(db_session, seeded_data["user_id"], seeded_data["space_id"], b_start, b_end, status="cancelled")
    response = _availability(client, b_start, b_end)
    assert _find(response, seeded_data["space_id"])["is_available"] is True



def test_booking_other_spaces_not_affect_this_one(client, db_session, seeded_data):

    """ booking one space does not change the availability of other spaces """
    
    # create other Space
    other = Space(name="Desk B4", capacity=1, category_id=seeded_data["category_id"], is_active=True)
    db_session.add(other)
    db_session.flush()

    # book other space
    start, end = _slot(0, 2)
    _add_booking(db_session, seeded_data["user_id"], other.id, start, end)

    # availability for ALL spaces
    response = _availability(client, start, end)

    # check if ONLY BOOKED is reserved
    assert _find(response, other.id)["is_available"] is False
    assert _find(response, seeded_data["space_id"])["is_available"] is True



def test_inactive_space_is_not_listed(client, db_session, seeded_data):

    """ disabled/inactive spaces are hidden from availability list"""

    # add inactive space
    inactive = Space(name="Desk Y3", capacity=1, category_id=seeded_data["category_id"], is_active=False)
    db_session.add(inactive)
    db_session.flush()

    start, end = _slot()
    repsonse = _availability(client, start, end)

    # assert inactive space != API response
    assert inactive.id not in [item["id"] for item in repsonse.json()]


def test_response_contains_category_capacity_and_facilities(client, db_session, seeded_data):

    screen = Facility(name="Screen") # add Screen facility and space with it
    db_session.add(screen)
    db_session.flush()
    space = db_session.get(Space, seeded_data["space_id"])
    db_session.add(SpaceFacility(space=space, facility=screen))
    db_session.flush()

    start, end = _slot()
    item = _find(_availability(client, start, end), seeded_data["space_id"])
    

    assert item["category"] == "Desk" # validate ALL metadata
    assert item["capacity"] == 1
    assert item["facilities"] == ["Screen"]



def test_invalid_time_range_returns_400(client, seeded_data):

    """ 400 Bad Request if start time is after end time """

    end, start = _slot() # reversed
    response = _availability(client, start, end)

    assert response.status_code == 400



def test_missing_query_params_returns_422(client):

    # without start/end_at
    response = client.get("/spaces/availability")

    assert response.status_code == 422



def test_space_bookings_returns_only_active_in_window_without_user_data(client, db_session, seeded_data):
    uid, sid = seeded_data["user_id"], seeded_data["space_id"]
    a_start, a_end = _slot(0, 2)
    _add_booking(db_session, uid, sid, a_start, a_end)                      # active, inside window
    c_start, c_end = _slot(3, 1)
    _add_booking(db_session, uid, sid, c_start, c_end, status="cancelled")  # cancelled
    o_start, o_end = _slot(20, 1)
    _add_booking(db_session, uid, sid, o_start, o_end)                      # outside window

    w_start, _ = _slot(-1)
    _, w_end = _slot(8)
    response = client.get(f"/spaces/{sid}/bookings", params={"start_at": w_start.isoformat(), "end_at": w_end.isoformat()})

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert set(response.json()[0].keys()) == {"start_at", "end_at"}


def test_space_bookings_unknown_space_404(client):
    start, end = _slot()
    response = client.get("/spaces/999999/bookings", params={"start_at": start.isoformat(), "end_at": end.isoformat()})
    assert response.status_code == 404


def test_space_bookings_invalid_range_400(client, seeded_data):
    start, end = _slot()
    response = client.get(f"/spaces/{seeded_data['space_id']}/bookings", params={"start_at": end.isoformat(), "end_at": start.isoformat()})
    assert response.status_code == 400