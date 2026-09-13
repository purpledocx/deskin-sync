from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from app.database import Base

class SpaceCategory(Base):
    __tablename__ = "space_categories"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(100), unique=True)

    spaces: Mapped[list["Space"]] = relationship(back_populates="category")