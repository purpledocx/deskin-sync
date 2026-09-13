from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from app.database import Base

class Facility(Base):
    __tablename__ = "facilities"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(100), unique=True)

    space_links: Mapped[list["SpaceFacility"]] = relationship(back_populates="facility", cascade="all, delete-orphan")