from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from app.database import Base

class SpaceFacility(Base):
    __tablename__ = "space_facilities"

    space_id: Mapped[int] = mapped_column(ForeignKey("spaces.id"), primary_key=True)

    facility_id: Mapped[int] = mapped_column(ForeignKey("facilities.id"), primary_key=True)

    space: Mapped["Space"] = relationship(back_populates="facility_links")
    
    facility: Mapped["Facility"] = relationship(back_populates="space_links")