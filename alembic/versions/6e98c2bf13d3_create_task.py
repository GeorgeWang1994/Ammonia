"""create task

Revision ID: 6e98c2bf13d3
Revises: 
Create Date: 2019-05-12 11:31:14.365810

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6e98c2bf13d3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('task',
    sa.Column('task_id', sa.String(length=50), nullable=False, comment='任务id'),
    sa.Column('status', sa.Enum('START', 'PROCESSING', 'FINISH', name='taskstatuschoice'), nullable=False, comment='任务当前的状态'),
    sa.Column('result', sa.String(length=200), nullable=True, comment='任务执行的结果'),
    sa.Column('_traceback', sa.TEXT(), nullable=True, comment='报错信息'),
    sa.Column('create_time', sa.DATETIME(), nullable=False, comment='创建时间'),
    sa.Column('modified_time', sa.DATETIME(), nullable=False, comment='修改时间'),
    sa.PrimaryKeyConstraint('task_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('task')
    # ### end Alembic commands ###
