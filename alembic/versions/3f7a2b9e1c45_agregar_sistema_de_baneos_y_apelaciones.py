"""Agregar sistema de baneos y apelaciones a modelo Account

Revision ID: 3f7a2b9e1c45
Revises: f638e27bd1ff
Create Date: 2025-01-11 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3f7a2b9e1c45'
down_revision = 'f638e27bd1ff'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### Sistema de Baneos ###

    # Campo is_banned con índice para búsquedas rápidas
    op.add_column('accounts', sa.Column('is_banned', sa.Boolean(), server_default='false', nullable=False))
    op.create_index(op.f('ix_accounts_is_banned'), 'accounts', ['is_banned'], unique=False)

    # Razón del ban (máximo 500 caracteres)
    op.add_column('accounts', sa.Column('ban_reason', sa.String(length=500), nullable=True))

    # Fecha y hora del ban
    op.add_column('accounts', sa.Column('banned_at', sa.DateTime(), nullable=True))

    # ID del administrador que aplicó el ban (FK auto-referencial)
    op.add_column('accounts', sa.Column('banned_by_account_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_accounts_banned_by_account_id',
        'accounts', 'accounts',
        ['banned_by_account_id'], ['id']
    )

    # Fecha de expiración del ban (None = permanente, datetime = temporal)
    op.add_column('accounts', sa.Column('ban_expires_at', sa.DateTime(), nullable=True))

    # ### Sistema de Apelaciones ###

    # Indica si el usuario ya apeló (solo una oportunidad)
    op.add_column('accounts', sa.Column('has_appealed', sa.Boolean(), server_default='false', nullable=False))

    # Texto de la apelación (máximo 1000 caracteres)
    op.add_column('accounts', sa.Column('appeal_text', sa.String(length=1000), nullable=True))

    # Fecha y hora de la apelación
    op.add_column('accounts', sa.Column('appealed_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    # Eliminar campos en orden inverso
    op.drop_column('accounts', 'appealed_at')
    op.drop_column('accounts', 'appeal_text')
    op.drop_column('accounts', 'has_appealed')
    op.drop_column('accounts', 'ban_expires_at')
    op.drop_constraint('fk_accounts_banned_by_account_id', 'accounts', type_='foreignkey')
    op.drop_column('accounts', 'banned_by_account_id')
    op.drop_column('accounts', 'banned_at')
    op.drop_column('accounts', 'ban_reason')
    op.drop_index(op.f('ix_accounts_is_banned'), table_name='accounts')
    op.drop_column('accounts', 'is_banned')
