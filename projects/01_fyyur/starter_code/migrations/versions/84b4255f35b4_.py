"""empty message

Revision ID: 84b4255f35b4
Revises: ec96748b2300
Create Date: 2021-01-05 21:18:14.776786

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '84b4255f35b4'
down_revision = 'ec96748b2300'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Artist', 'name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.create_unique_constraint(None, 'Artist', ['name'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'Artist', type_='unique')
    op.alter_column('Artist', 'name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###
