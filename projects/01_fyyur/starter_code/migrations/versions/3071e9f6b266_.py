"""empty message

Revision ID: 3071e9f6b266
Revises: 8b59da19ea7f
Create Date: 2021-01-01 20:10:06.937404

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3071e9f6b266'
down_revision = '8b59da19ea7f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'genres')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('genres', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    # ### end Alembic commands ###