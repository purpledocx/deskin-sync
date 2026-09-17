import os
from pathlib import Path
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent # loadenv couldnt find .env so this added
dotenv_path = BASE_DIR / ".env"

import pytest
from sqlalchemy import create_engine, select
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

    # pytest test_auth was complaining, added student role for all tests
    student_role = session.scalar(select(Role).where(Role.name == "Student"))
    if not student_role:
        student_role = Role(name="Student")
        session.add(student_role)
        session.flush()

    yield session

    session.close()
    transaction.rollback()
    connection.close()



@pytest.fixture
def seeded_data(db_session):

    #check if there is student role | added cuz pytest twst_auth was wild | leave it here cuz wihtout it somehow test_auth.py fails o_0
    student_role = db_session.scalar(select(Role).where(Role.name == "Student"))
    if not student_role:
        student_role = Role(name="Student")
        db_session.add(student_role)
        db_session.flush()
    
    
    category = SpaceCategory(name="Desk")

    db_session.add(category)
    db_session.flush()


    user = User(
        name="Test User",
        email="test@test.com",
        password_hash="some-salted-hash",
        role_id=student_role.id
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