"""empty message

Revision ID: a4a949f6ce08
Revises: 829c2a47dd7f
Create Date: 2018-12-19 16:20:12.385000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'a4a949f6ce08'
down_revision = '829c2a47dd7f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(u'comment_ibfk_4', 'comment', type_='foreignkey')
    op.drop_column('comment', 'self_top_comment_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comment', sa.Column('self_top_comment_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.create_foreign_key(u'comment_ibfk_4', 'comment', 'comment', ['self_top_comment_id'], ['id'])
    # ### end Alembic commands ###
