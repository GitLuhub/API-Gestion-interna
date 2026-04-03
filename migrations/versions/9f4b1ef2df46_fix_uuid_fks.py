"""fix_uuid_fks

Revision ID: 9f4b1ef2df46
Revises: f37b1ec7beb8
Create Date: 2026-03-31 23:11:50.741039

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9f4b1ef2df46'
down_revision: Union[str, Sequence[str], None] = 'f37b1ec7beb8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Alembic didn't catch this change automatically because changing from String to UUID
    # on foreign keys that were already populated or generated under the hood as UUIDs
    # might be seen as a no-op by autogenerate if it was just a type hint fix.
    # We will explicitly cast the types if needed.
    # However, checking initial migration, they were created as Uuid!
    # So the DB schema is ALREADY correct, we just fixed the SQLAlchemy Model mappings to match.
    # Thus, no DB alterations are actually required.
    pass


def downgrade() -> None:
    pass
