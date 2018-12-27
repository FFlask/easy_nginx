"""empty message

Revision ID: 4aae50ec5f26
Revises: 5beabc167b4a
Create Date: 2018-12-24 17:16:30.170000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4aae50ec5f26'
down_revision = '5beabc167b4a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('private_msg',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('src_user_id', sa.Integer(), nullable=True),
    sa.Column('dst_user_id', sa.Integer(), nullable=True),
    sa.Column('msg', sa.TEXT(), nullable=True),
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['dst_user_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['src_user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_private_msg_id'), 'private_msg', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_private_msg_id'), table_name='private_msg')
    op.drop_table('private_msg')
    # ### end Alembic commands ###