from app.routers.auth import router as auth_router
from app.routers.bookings import router as booking_router
from app.routers.spaces import router as space_router

__all__ = [
    "auth_router",
    "booking_router",
    "space_router",
]