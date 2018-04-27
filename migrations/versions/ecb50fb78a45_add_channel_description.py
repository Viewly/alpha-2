"""Add Channel.description

Revision ID: ecb50fb78a45
Revises: 
Create Date: 2018-04-27 10:28:49.381844

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ecb50fb78a45'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('channel', sa.Column('description', sa.String(length=70), nullable=True))


def downgrade():
    op.drop_column('channel', 'description')
