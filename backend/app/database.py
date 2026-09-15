import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, DateTime
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from datetime import datetime
from typing import Generator

load_dotenv()

database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(database_url, pool_pre_ping=True)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


class Base(DeclarativeBase):
    type_annotation_map = {
        datetime: DateTime(timezone=True)
    }
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()