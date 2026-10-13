from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, text
from datetime import datetime
from app.database import Base

class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    space_id: Mapped[int] = mapped_column(ForeignKey("spaces.id"))

    start_at: Mapped[datetime] = mapped_column()
    end_at: Mapped[datetime] = mapped_column()

    status: Mapped[str] = mapped_column(String(20), default="active")

    created_at: Mapped[datetime] = mapped_column(server_default=text("NOW()"))

    user: Mapped["User"] = relationship(back_populates="bookings")
    space: Mapped["Space"] = relationship(back_populates="bookings")

    @property
    def space_name(self) -> str:
        return self.space.name

    @property
    def user_name(self) -> str:
        return self.user.name
