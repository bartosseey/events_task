"""fix

Revision ID: 9b2f10ac9ae7
Revises: e81e82b4ec68
Create Date: 2024-10-05 10:52:43.763746

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9b2f10ac9ae7'
down_revision = 'e81e82b4ec68'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('participant_meals_on_event', schema=None) as batch_op:
        batch_op.drop_constraint('participant_meals_on_event_event_id_fkey', type_='foreignkey')
        batch_op.drop_column('event_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('participant_meals_on_event', schema=None) as batch_op:
        batch_op.add_column(sa.Column('event_id', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.create_foreign_key('participant_meals_on_event_event_id_fkey', 'events', ['event_id'], ['id'])

    # ### end Alembic commands ###
