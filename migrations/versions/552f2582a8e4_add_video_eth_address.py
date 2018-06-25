"""Add Video.eth_address

Revision ID: 552f2582a8e4
Revises: 5b30936df41f
Create Date: 2018-06-25 16:44:41.938224

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '552f2582a8e4'
down_revision = '5b30936df41f'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('video', sa.Column('eth_address', sa.String(length=42), nullable=True))


def downgrade():
    op.drop_column('video', 'eth_address')
