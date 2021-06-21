"""empty message

Revision ID: e026dd5d3bbc
Revises: a599b9afcb7b
Create Date: 2021-06-10 23:20:10.888190

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e026dd5d3bbc'
down_revision = 'a599b9afcb7b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venue', sa.Column('seeking_description', sa.String(length=500), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venue', 'seeking_description')
    # ### end Alembic commands ###