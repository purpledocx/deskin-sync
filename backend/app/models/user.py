from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(100))

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
    )
    
    password_hash: Mapped[str] = mapped_column(String(255))

    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id"),
    )

    role: Mapped["Role"] = relationship(back_populates="users")

    bookings: Mapped[list["Booking"]] = relationship(
        back_populates="user"
    )