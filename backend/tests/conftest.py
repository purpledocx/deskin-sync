import os
from pathlib import Path
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent # loadenv couldnt find .env so this added
dotenv_path = BASE_DIR / ".env"

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models
from app.database import Base
from app.models.role import Role
from app.models.space import Space
from app.models.space_category import SpaceCategory
from app.models.user import User


test_database_url = os.getenv("TEST_DATABASE_URL")


if not test_database_url:
    raise RuntimeError("TEST_DATABASE_URL is not set")
if "deskin_sync_test" not in test_database_url:
    raise RuntimeError("Test must use the deskin_sync_test database, NOT main database")


test_engine = create_engine(
    test_database_url,
    pool_pre_ping=True
)


"""-----------FIXTURES------------"""

@pytest.fixture(scope="session", autouse=True)
def test_database_schema():
    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()



@pytest.fixture
def db_session():
    connection = test_engine.connect()
    transaction = connection.begin()

    session = Session(
        bind=connection,
        join_transaction_mode="create_savepoint"
    )
    yield session

    session.close()
    transaction.rollback()
    connection.close()



@pytest.fixture
def seeded_data(db_session):
    role = Role(name="Student")
    category = SpaceCategory(name="Desk")

    db_session.add_all([role, category])
    db_session.flush()


    user = User(
        name="Test User",
        email="test@test.com",
        password_hash="some-salted-hash",
        role_id=role.id
    )
    space = Space(
        name="Desk A7",
        capacity=1,
        category_id=category.id,
        is_active=True
    )

    db_session.add_all([user, space])
    db_session.flush()


    return {
        "user_id": user.id,
        "space_id": space.id,
        "category_id": category.id 
    }