"""Add voice_profiles table with versioning

Revision ID: 3ebc18e4e56b
Revises: 9c82a719496c
Create Date: 2025-09-27 23:51:56.467425

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3ebc18e4e56b"
down_revision: Union[str, Sequence[str], None] = "9c82a719496c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # This migration is now empty since voice_profiles table was created in the initial migration
    # The table creation was moved to the initial migration to avoid conflicts
    pass


def downgrade() -> None:
    """Downgrade schema."""
    # This migration is now empty since voice_profiles table was created in the initial migration
    pass
