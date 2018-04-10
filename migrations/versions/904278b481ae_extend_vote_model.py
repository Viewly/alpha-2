"""Extend Vote Model

Revision ID: 904278b481ae
Revises: 2d640e3991a4
Create Date: 2018-04-11 02:25:54.967395

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '904278b481ae'
down_revision = '2d640e3991a4'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('vote', sa.Column('delegated_amount', sa.Integer(), nullable=True))
    op.add_column('vote', sa.Column('token_amount', sa.Integer(), nullable=True))
    op.add_column('vote', sa.Column('weight', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('vote', 'weight')
    op.drop_column('vote', 'token_amount')
    op.drop_column('vote', 'delegated_amount')
