"""Add Video.analyzed_at

Revision ID: 5b30936df41f
Revises: ecb50fb78a45
Create Date: 2018-04-28 22:41:10.392981

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '5b30936df41f'
down_revision = 'ecb50fb78a45'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('video',
                  sa.Column('analyzed_at', sa.DateTime(timezone=True), nullable=True))


def downgrade():
    op.drop_column('video', 'analyzed_at')
