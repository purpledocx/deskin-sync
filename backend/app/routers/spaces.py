from fastapi import APIRouter, Query, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas import SpaceAvailabilityRead
from app.database import get_db
from app.services.space_service import get_spaces_availability

from datetime import datetime
from typing import Annotated

router = APIRouter(prefix="/spaces", tags=["spaces"])

@router.get("/availability", response_model=list[SpaceAvailabilityRead])
def spaces_availability(start_at: Annotated[datetime, Query()], end_at: Annotated[datetime, Query()], db: Annotated[Session, Depends(get_db)]):

    if start_at >= end_at:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "start_at must be earlier than end_at")

    return get_spaces_availability(db, start_at, end_at)