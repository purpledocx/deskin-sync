"""seed initial roles

Revision ID: f8e876d50280
Revises: 289295f4e7e6
Create Date: 2026-09-15 19:45:41.975851

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f8e876d50280'
down_revision: Union[str, Sequence[str], None] = '289295f4e7e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    roles = sa.table(
        "roles",
        sa.column("name", sa.String(length=50))
    )

    op.bulk_insert(
        roles,
        [
            {"name": "Student"},
            {"name": "Teacher"},
            {"name": "Admin"}
        ]
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""

    op.execute(
        """
        DELETE FROM roles
        WHERE name IN ('Student', 'Teacher', 'Admin')
        """
    )
    pass
