"""First migration

Revision ID: 92414c723d0b
Revises: 
Create Date: 2024-10-01 20:26:22.483893

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '92414c723d0b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.Unicode(length=100), nullable=False),
    sa.Column('email', sa.Unicode(length=100), nullable=False),
    sa.Column('first_name', sa.Unicode(length=100), nullable=False),
    sa.Column('last_name', sa.Unicode(length=100), nullable=False),
    sa.Column('password_hash', sa.Unicode(length=255), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('created_by', sa.Integer(), nullable=False),
    sa.Column('creation_date', sa.DateTime(), nullable=False),
    sa.Column('updated_by', sa.Integer(), nullable=True),
    sa.Column('update_date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    # ### end Alembic commands ###
