"""Initial migration with voice profile versioning

Revision ID: 9c82a719496c
Revises: 
Create Date: 2025-09-27 23:33:05.609644

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9c82a719496c'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create brands table
    op.create_table('brands',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('canonical_url', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_brands_name'), 'brands', ['name'], unique=False)
    
    # Create voice_profiles table
    op.create_table('voice_profiles',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('brand_id', sa.UUID(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('metrics', sa.JSON(), nullable=False),
        sa.Column('target_demographic', sa.String(), nullable=False),
        sa.Column('style_guide', sa.JSON(), nullable=False),
        sa.Column('writing_example', sa.String(), nullable=False),
        sa.Column('llm_model', sa.String(), nullable=False),
        sa.Column('source', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id'),
        sa.UniqueConstraint('brand_id', 'version', name='uq_voice_profile_brand_version')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('voice_profiles')
    op.drop_index(op.f('ix_brands_name'), table_name='brands')
    op.drop_table('brands')
