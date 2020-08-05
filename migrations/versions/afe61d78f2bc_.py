"""empty message

Revision ID: afe61d78f2bc
Revises: b81f2d7639e9
Create Date: 2020-08-04 16:05:44.470448

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'afe61d78f2bc'
down_revision = 'b81f2d7639e9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artists', sa.Column('past_shows_count', sa.Integer(), nullable=True))
    op.add_column('artists', sa.Column('upcoming_shows_count', sa.Integer(), nullable=True))
    op.add_column('venues', sa.Column('past_shows_count', sa.Integer(), nullable=True))
    op.add_column('venues', sa.Column('upcoming_shows_count', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venues', 'upcoming_shows_count')
    op.drop_column('venues', 'past_shows_count')
    op.drop_column('artists', 'upcoming_shows_count')
    op.drop_column('artists', 'past_shows_count')
    # ### end Alembic commands ###