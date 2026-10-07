
from sqlalchemy.orm import Session, selectinload, joinedload # joinedload - left outer join, selectinload - 2nd  request with IN
from sqlalchemy import select, func

from app.models import Booking, Space, SpaceFacility

from datetime import  datetime

def get_spaces_availability( db: Session, start_at: datetime, end_at: datetime) -> list[dict]:

    #space_id all ACTIVE or OVERLAPPING spaces
    busy_until = dict(
        db.execute(
            select(Booking.space_id, func.max(Booking.end_at))
            .where(Booking.status == "active",
                   Booking.start_at < end_at,
                   Booking.end_at > start_at)
            .group_by(Booking.space_id)
        ).all()
    )


    # SELECT space_facility.id, space_facility.space_id, space_facility.facility_id,
    # facility.id, facility.name
    # FROM space_facility
    # LEFT OUTER JOIN facility ON facility.id = space_facility.facility_id
    # WHERE space_facility.space_id IN (1, 2, 3...);
    spaces = db.scalars(
        select(Space)
        .where(Space.is_active.is_(True))
        .options(
            # joinedload for single object (many-to-one)
            joinedload(Space.category),
            # selectinload for collection (one-to-many) to avoid duplicates + nested join for facility data
            selectinload(Space.facility_links).joinedload(SpaceFacility.facility)
        ).order_by(Space.name)
    ).all()

    return [
        {
            "id": space.id,
            "name": space.name,
            "capacity": space.capacity,
            "category": space.category.name, #joinedload
            "facilities": sorted(link.facility.name for link in space.facility_links),
            "is_available": space.id not in busy_until,
            "available_from": busy_until.get(space.id)
        }
        for space in spaces
    ]
