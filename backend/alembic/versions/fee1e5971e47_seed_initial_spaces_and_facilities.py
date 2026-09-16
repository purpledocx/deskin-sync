"""seed initial spaces and facilities

Revision ID: fee1e5971e47
Revises: f8e876d50280
Create Date: 2026-09-16 15:43:45.024021

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fee1e5971e47'
down_revision: Union[str, Sequence[str], None] = 'f8e876d50280'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""


    connection = op.get_bind()

    # INSERT function because DRY | wanted to simplify ***_category_id insert to write it in one line
    def insert(table: str,  *, returning: bool = False, **values):

        columns = ", ".join(values)

        placeholders = ", ".join(f":{col}" for col in values)

        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        if returning:
            sql += " RETURNING id"
        
        result = connection.execute(sa.text(sql), values)

        return result.scalar_one() if returning else None



    # making space_categories with insert()
    desk_category_id = insert("space_categories", name="Desk", returning=True)

    meeting_room_category_id = insert("space_categories", name="Meeting room", returning=True)


    insert(
        "spaces",
        name = "Desk A1",
        capacity = 1,
        category_id = desk_category_id,
        is_active = True
    )


    meeting_room_id = insert(
        "spaces",
        name = "Meeting Room B1",
        capacity = 6,
        category_id = meeting_room_category_id,
        is_active = True,
        returning= True
        )

    screen_id = insert("facilities", name="Screen", returning=True)
    whiteboard_id = insert("facilities", name= "Whiteboard", returning=True)

    insert("space_facilities", space_id = meeting_room_id, facility_id = screen_id)
    insert("space_facilities", space_id = meeting_room_id, facility_id = whiteboard_id)
    pass


def downgrade() -> None:
    """Downgrade schema."""

    connection = op.get_bind()


    def delete_by_names(table: str, names: list[str]) -> None:
        connection.execute(
            sa.text(f"DELETE FROM {table} WHERE name = ANY(:names)"),
            {"names": names}
        )

    space_names = ["Desk A1", "Meeting Room B1"]

    connection.execute(
        sa.text("""
        DELETE FROM space_facilities
        WHERE space_id IN (SELECT id FROM spaces WHERE name = ANY(:names))
        """),
        {"names": space_names}
    )

    
    delete_by_names("spaces", space_names)
    delete_by_names("facilities", ["Screen", "Whiteboard"])
    delete_by_names("space_categories", ["Desk", "Meeting room"])
    
    pass
