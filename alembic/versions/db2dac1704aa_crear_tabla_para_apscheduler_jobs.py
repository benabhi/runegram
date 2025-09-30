"""Crear tabla para apscheduler jobs

Revision ID: db2dac1704aa
Revises: cdb486941d55
Create Date: <LA FECHA SE GENERA AUTOMÁTICAMENTE>

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'db2dac1704aa'
down_revision = 'cdb486941d55'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Crea la tabla 'apscheduler_jobs' con el esquema exacto que espera
    la librería APScheduler para su SQLAlchemyJobStore.
    """
    op.create_table(
        'apscheduler_jobs',
        sa.Column('id', sa.Unicode(191), primary_key=True),
        sa.Column('next_run_time', sa.Float(25), index=True),
        sa.Column('job_state', sa.LargeBinary, nullable=False)
    )


def downgrade() -> None:
    """
    Elimina la tabla 'apscheduler_jobs' si se revierte la migración.
    """
    op.drop_table('apscheduler_jobs')