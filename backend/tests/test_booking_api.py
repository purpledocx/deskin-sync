import pytest

from datetime import datetime, timezone, timedelta

# testclient - can make CRUD request
from fastapi.testclient import TestClient

from app.main import app
from app.database import get_db
from app.dependencies import get_current_user

from app.models import Booking, User, Space, Role



"""------------------------------------------------------------FIXTURES------------------------------------------------------------"""


@pytest.fixture
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def auth_as(db_session, client):
    """Overrides get_current_user so requests act as the given user without going through login"""

    def _auth_as(user: User):
        app.dependency_overrides[get_current_user] = lambda: user
        return client

    yield _auth_as

    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def other_user(db_session, seeded_data):
    
    role = db_session.get(Role, db_session.query(User).get(seeded_data["user_id"]).role_id)
    user = User(
        name="Other User",
        email="other@test.nl",
        password_hash="some-salted-hash",
        role_id=role.id
    )

    db_session.add(user)
    db_session.flush()
    return user


@pytest.fixture
def admin_user(db_session, seeded_data):
    admin_role = Role(name="Admin")
    db_session.add(admin_role)
    db_session.flush()

    user = User(
        name="Admin User",
        email="admin@test.nl",
        password_hash="very-salted-hash",
        role_id=admin_role.id
    )
    db_session.add(user)
    db_session.flush()

    return user


"""------------------------------------------------------------HELPER_FUNCTIONS------------------------------------------------------------"""


def _test_day() -> datetime:
    """Always 60 days ahead of whenever the test is actually run"""

    future = datetime.now(timezone.utc) + timedelta(days=60)
    return future.replace(hour=0, minute=0, second=0, microsecond=0)


def date_time(hour: int) -> datetime:
    return _test_day() + timedelta(hours=hour)


def far_future(hours_from_now: int = 5) -> tuple[datetime, datetime]:
    """Generate safe future time range to prevent triggering 30-min rules

    returns tuple containing two UTC datetime objects: (start, end), where the end time is 1 hour after the start
        
        !!! call `.isoformat()` on these objects only when building the request body !!!
    """

    start = datetime.now(timezone.utc) + timedelta(hours=hours_from_now)
    end = start + timedelta(hours=1)
    return start, end


def insert_booking(db_session, user_id: int, space_id: int, start_at: datetime, end_at: datetime, status: str = "active") -> Booking:
    booking = Booking(
        user_id = user_id,
        space_id = space_id,
        start_at = start_at,
        end_at = end_at,
        status = status
    )

    db_session.add(booking)
    db_session.flush()
    return booking



"""------------------------------------------------------------TESTS------------------------------------------------------------"""



"""~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~CREATE~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"""


def test_create_booking_success(db_session, auth_as, seeded_data):
    user = db_session.get(User, seeded_data["user_id"])
    client = auth_as(user)

    start, end = far_future()
    response = client.post("/bookings/", json={
        "space_id": seeded_data["space_id"],
        "start_at": start.isoformat(),
        "end_at": end.isoformat()
    })

    assert response.status_code == 201

    data = response.json()
    assert data["space_id"] == seeded_data["space_id"]
    assert data["user_id"] == seeded_data["user_id"]
    assert data["status"] == "active"


def test_create_booking_without_token(client, seeded_data):
    start, end = far_future()

    response = client.post("/bookings/", json={
        "space_id": seeded_data["space_id"],
        "start_at": start.isoformat(),
        "end_at": end.isoformat()
    })

    assert response.status_code == 401


def test_create_nonexistent_space(db_session, auth_as, seeded_data):
    user = db_session.get(User, seeded_data['user_id'])
    client = auth_as(user)

    start, end = far_future()
    response = client.post("/bookings/", json={
        "space_id": 999999,
        "start_at": start.isoformat(),
        "end_at": end.isoformat()
    })

    assert response.status_code == 404

def test_create_booking_inactive_space(db_session, auth_as, seeded_data):
    inactive_space = Space(
        name="Broken Desk",
        capacity=1,
        category_id=seeded_data["category_id"],
        is_active=False
    )
    db_session.add(inactive_space)
    db_session.flush()

    user = db_session.get(User, seeded_data["user_id"])
    client = auth_as(user)

    start, end = far_future()
    response = client.post("/bookings/", json={
        "space_id": inactive_space.id,
        "start_at": start.isoformat(),
        "end_at": end.isoformat()
    })

    assert response.status_code == 409


def test_create_booking_overlap(db_session, auth_as, seeded_data):
    insert_booking(db_session, seeded_data["user_id"], seeded_data["space_id"], date_time(9), date_time(11))

    user = db_session.get(User, seeded_data["user_id"])
    client = auth_as(user)

    response = client.post("/bookings/", json={
        "space_id": seeded_data["space_id"],
        "start_at": date_time(10).isoformat(),
        "end_at": date_time(12).isoformat()
    })

def test_create_booking_with_naive_datetime_returns_290(db_session, auth_as, client, seeded_data):
    
    user = db_session.get(User, seeded_data["user_id"])
    client = auth_as(user)
    start = (datetime.now() + timedelta(days=60)).replace(minute=0, second=0, microsecond=0)

    response = client.post("/bookings/", json={
        "space_id": seeded_data["space_id"],
        "start_at": start.isoformat(),
        "end_at": (start + timedelta(hours=1)).isoformat()
    })

    assert response.status_code == 201




"""~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~READ(LIST)~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"""



def test_list_booking_student_sees_only_own(db_session, auth_as, seeded_data, other_user):
    #insert 2 different bookings
    insert_booking(db_session, seeded_data["user_id"], seeded_data["space_id"], date_time(9), date_time(10))
    insert_booking(db_session, other_user.id, seeded_data["space_id"], date_time(11), date_time(12))

    #make authorizations as user + get response
    user = db_session.get(User, seeded_data["user_id"])
    client = auth_as(user)
    response = client.get('/bookings/')

    #tests    
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["user_id"] == seeded_data["user_id"]


def test_list_booking_admin_sees_all(db_session, auth_as, seeded_data, admin_user):
    #insert 2 different bookings
    insert_booking(db_session, seeded_data["user_id"], seeded_data["space_id"], date_time(9), date_time(10))
    insert_booking(db_session, admin_user.id, seeded_data["space_id"], date_time(11), date_time(12))

    #make authorizations as admin + get response
    client = auth_as(admin_user)
    response = client.get("/bookings/")

    #tests
    assert response.status_code == 200
    assert len(response.json()) == 2



"""~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~UPDATE~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"""


def test_update_booking_success(db_session, auth_as, seeded_data):

    start, end = far_future()
    booking = insert_booking(db_session, seeded_data["user_id"], seeded_data["space_id"], start, end)

    user = db_session.get(User, seeded_data["user_id"])
    client = auth_as(user)

    new_start, new_end = far_future(8)
    response = client.put(f"/bookings/{booking.id}", json={
        "space_id": seeded_data["space_id"],
        "start_at": new_start.isoformat(),
        "end_at": new_end.isoformat()
    })

    assert response.status_code == 200

    data = response.json()
    assert data["space_id"] == seeded_data["space_id"]
    assert data["id"] == booking.id


def test_update_booking_not_owner_forbidden(db_session, auth_as, seeded_data, other_user):

    start, end = far_future()
    booking = insert_booking(db_session, seeded_data["user_id"], seeded_data["space_id"], start, end)

    client = auth_as(other_user)

    new_start, new_end = far_future(8)
    response = client.put(f"/bookings/{booking.id}", json={
        "space_id": seeded_data["space_id"],
        "start_at": new_start.isoformat(),
        "end_at": new_end.isoformat()
    })

    assert response.status_code == 403


def test_update_booking_too_close_to_start_rejected(db_session, auth_as, seeded_data):

    """basically test of 30min rule"""

    soon = datetime.now(timezone.utc) + timedelta(minutes=10)
    booking = insert_booking(db_session, seeded_data["user_id"], seeded_data["space_id"], soon, soon + timedelta(hours=1))

    user = db_session.get(User, seeded_data["user_id"])
    client = auth_as(user)

    new_start, new_end = far_future(8)
    response = client.put(f"/bookings/{booking.id}", json={
        "space_id": seeded_data["space_id"],
        "start_at": new_start.isoformat(),
        "end_at": new_end.isoformat()
    })

    assert response.status_code == 409


def test_update_booking_exclude_itself_from_overlap(db_session, auth_as, seeded_data):

    # booking creation + auth
    start, end = far_future()
    booking = insert_booking(db_session, seeded_data["user_id"], seeded_data["space_id"], start, end)

    user = db_session.get(User, seeded_data["user_id"])
    client = auth_as(user)


    # request for update

    #same timerange as itself -> must NOT be treated as conflict
    response = client.put(f"/bookings/{booking.id}", json={
        "space_id": seeded_data["space_id"],
        "start_at": start.isoformat(),
        "end_at": end.isoformat()
    })

    #assert result
    assert response.status_code == 200




"""~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~DELETE~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"""


def test_cancel_booking_success(db_session, auth_as, seeded_data):

    # booking creation + auth
    start, end = far_future()
    booking = insert_booking(db_session, seeded_data["user_id"], seeded_data["space_id"], start, end)

    user = db_session.get(User, seeded_data["user_id"])
    client = auth_as(user)

    response = client.delete(f"/bookings/{booking.id}")

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"

def test_cancel_already_cancelled_booking_rejected(db_session, auth_as, seeded_data):

    # booking creation + auth
    start, end = far_future()
    booking = insert_booking(db_session, seeded_data["user_id"], seeded_data["space_id"], start, end, status="cancelled")

    user = db_session.get(User, seeded_data["user_id"])
    client = auth_as(user)

    response = client.delete(f"/bookings/{booking.id}")

    assert response.status_code == 409

def test_cancel_booking_not_found(db_session, auth_as, seeded_data):

    user = db_session.get(User, seeded_data["user_id"])
    client = auth_as(user)

    response = client.delete(f"/bookings/999999")

    assert response.status_code == 404



def test_teacher_can_cancell_other_users_booking(db_session, auth_as, seeded_data):

    start = (datetime.now() + timedelta(days=60)).replace(minute=0, second=0, microsecond=0)
    booking = Booking(
        user_id = seeded_data["user_id"],
        space_id = seeded_data["space_id"],
        start_at = start,
        end_at = start + timedelta(hours=1),
        status = "active"
    )

    teacher_role = Role(name="Teacher")
    db_session.add_all([booking, teacher_role])
    db_session.flush()

    teacher = User(
        name="Teacher",
        email="teacher@test.com",
        password_hash="super-salted-hash",
        role_id=teacher_role.id
    )
    db_session.add(teacher)
    db_session.flush()
    
    client = auth_as(teacher)
    response = client.delete(f"/bookings/{booking.id}")

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"

def test_admin_can_cancel_booking_inside_30_min_window(db_session, auth_as, seeded_data, admin_user):
    soon = datetime.now(timezone.utc) + timedelta(minutes=10)
    booking = insert_booking(db_session, seeded_data["user_id"], seeded_data["space_id"], soon, soon + timedelta(hours=1))

    client = auth_as(admin_user)
    response = client.delete(f"/bookings/{booking.id}")

    assert response.status_code == 200