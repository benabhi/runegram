# alembic/script.py.mako

"""Add character_creation to default command_sets

Revision ID: f638e27bd1ff
Revises: c89c472e9f7b
Create Date: 2025-10-04 20:47:18.016240+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f638e27bd1ff'
down_revision = 'c89c472e9f7b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Actualizar el server_default de la columna command_sets
    op.alter_column(
        'characters',
        'command_sets',
        server_default='["general", "character_creation", "interaction", "movement", "channels", "dynamic_channels", "settings"]'
    )

    # 2. Actualizar personajes existentes: agregar "character_creation" si no lo tienen
    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE characters
        SET command_sets = jsonb_insert(
            command_sets::jsonb,
            '{1}',
            '"character_creation"'::jsonb,
            true
        )
        WHERE NOT (command_sets::jsonb ? 'character_creation')
    """))


def downgrade() -> None:
    # 1. Restaurar el server_default anterior
    op.alter_column(
        'characters',
        'command_sets',
        server_default='["general", "interaction", "movement", "channels", "dynamic_channels", "settings"]'
    )

    # 2. Eliminar "character_creation" de personajes existentes
    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE characters
        SET command_sets = (
            SELECT jsonb_agg(elem)
            FROM jsonb_array_elements_text(command_sets::jsonb) AS elem
            WHERE elem != 'character_creation'
        )
        WHERE command_sets::jsonb ? 'character_creation'
    """))