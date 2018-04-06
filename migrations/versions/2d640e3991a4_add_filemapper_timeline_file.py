"""Add FileMapper.timeline_file

Revision ID: 2d640e3991a4
Revises: 
Create Date: 2018-04-06 19:22:19.034313

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2d640e3991a4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('file_mapper', sa.Column('timeline_file', sa.String(length=50), nullable=True))


def downgrade():
    op.drop_column('file_mapper', 'timeline_file')
