import pytest

from fastapi.testclient import TestClient
from fastapi import APIRouter, Depends

from app.main import app
from app.database import get_db
from app.models.user import User
from app.dependencies import get_current_user



@pytest.fixture
def client(db_session): # o_0
    
    app.dependency_overrides[get_db] = lambda: db_session # mocking "get_db"

    with TestClient(app) as test_client: # context manager for HTTP requests
        yield test_client # gives test client to test
    
    #after test - clear mocking
    app.dependency_overrides.clear()


@pytest.fixture
def valid_user(client):
    """Makes test user through auth API"""

    user_data = {
        "name": "Kevin Mitnick",
        "email": "igot2phones@gmail.com",
        "password": "K3v1n!100ProcentNot"
    }

    client.post("/auth/register", json=user_data)

    return user_data



"""----------------------------TESTS----------------------------"""



def test_register_user_success(client):
    response = client.post( "/auth/register",
        json={
        "name": "Edward Snowden",
        "email": "edsnowden@lavabit.com",
        "password": "IBelieveInYesterdayWCRY"
    }
    )


    assert response.status_code == 201

    data = response.json()


    # All fields correct check
    assert "id" in data
    assert data["name"] == "Edward Snowden"
    assert data["email"] == "edsnowden@lavabit.com"
    assert data["role"] == "Student"

    assert "password" not in data



def test_register_duplicate_email(client, seeded_data):
    
    response = client.post("/auth/register", json={
        "name": "Assert Twin",
        "email": "test@test.com",
        "password": "ridiculouslysame"
    })

    assert response.status_code == 409
    assert response.json()["detail"] == "User with this email already exists"



def test_login_success(client, valid_user):
    response = client.post("/auth/login", data={
        "username": valid_user["email"],
        "password": valid_user["password"]
    })


    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"

    



def test_login_wrong_password(client, valid_user):

    response = client.post("/auth/login", data={
        "username": valid_user["email"],
        "password": "possiblywrongpasswordL0L"
    })


    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"



def test_login_wrong_email(client):

    response = client.post("/auth/login", data={
        "username": "completelNOTfoundable@gmail.com",
        "password": "nosaltnohash"
    })

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"




def test_protected_route_token_validation(client, valid_user):

    test_router = APIRouter()

    # protected endpoint that needs valid token in header
    @test_router.get("/test-protected")
    def protected_endpoint(current_user: User = Depends(get_current_user)):
        return {"email": current_user.email}

    
    app.include_router(test_router)


    # 1 - request WITHOUT token
    response_no_token = client.get("/test-protected")
    assert response_no_token.status_code == 401


    # get token with login
    login_response = client.post("/auth/login", data={
        "username": valid_user["email"],
        "password": valid_user["password"]
    })

    token = login_response.json()["access_token"]


    # 2 - request WITH token
    response_with_token = client.get("/test-protected", headers={"Authorization": f"Bearer {token}"})


    assert response_with_token.status_code == 200
    assert response_with_token.json()["email"] == valid_user["email"]