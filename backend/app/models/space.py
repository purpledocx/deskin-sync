from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String
from app.database import Base

class Space(Base):
    __tablename__ = "spaces"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(100), unique=True)

    category_id: Mapped[int] = mapped_column(ForeignKey("space_categories.id"))

    is_active: Mapped[bool] = mapped_column(default=True)

    capacity: Mapped[int] = mapped_column(default=1) 
    
    category: Mapped["SpaceCategory"] = relationship(back_populates="spaces")

    bookings: Mapped[list["Booking"]] = relationship(back_populates="space")

    facility_links: Mapped[list["SpaceFacility"]] = relationship(back_populates="space", cascade="all, delete-orphan")