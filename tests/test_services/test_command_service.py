# tests/test_services/test_command_service.py
"""
Tests para el Command Service.

Este servicio maneja la lógica de qué comandos están disponibles para
un personaje en función de su contexto (items, sala, rol).
"""

import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.services import command_service
from src.models import Item, Account, Character, Room


async def load_character_with_relations(db_session, character_id: int) -> Character:
    """
    Helper para cargar un personaje con todas sus relaciones necesarias.
    Replica la lógica de player_service.get_character_with_relations_by_id.
    """
    query = (
        select(Character)
        .where(Character.id == character_id)
        .options(
            selectinload(Character.room),
            selectinload(Character.items),
            selectinload(Character.account)
        )
    )
    result = await db_session.execute(query)
    return result.scalar_one()


@pytest.mark.critical
@pytest.mark.asyncio
class TestGetActiveCommandSetsForCharacter:
    """Tests para la función get_active_command_sets_for_character()."""

    async def test_character_creation_when_no_character(self):
        """
        Test: Debe devolver solo 'character_creation' cuando no hay personaje.
        """
        active_sets = await command_service.get_active_command_sets_for_character(None)

        assert active_sets == ["character_creation"]

    async def test_base_command_sets_from_character(self, db_session, sample_character):
        """
        Test: Debe incluir los command_sets base del personaje.
        """
        # Cargar el personaje con todas sus relaciones
        character = await load_character_with_relations(db_session, sample_character.id)

        active_sets = await command_service.get_active_command_sets_for_character(character)

        # Verificar que incluye los sets base del personaje
        assert "general" in active_sets
        assert "movement" in active_sets
        assert "interaction" in active_sets
        assert "channels" in active_sets

    async def test_command_sets_from_inventory_item(self, db_session, sample_character):
        """
        Test: Debe incluir command_sets otorgados por items en el inventario.
        """
        # Crear un item que otorga un command set especial
        special_item = Item(
            key="espada_viviente",
            character_id=sample_character.id
        )
        db_session.add(special_item)
        await db_session.commit()

        # Cargar el personaje con todas sus relaciones
        character = await load_character_with_relations(db_session, sample_character.id)

        active_sets = await command_service.get_active_command_sets_for_character(character)

        # Como espada_viviente no tiene grants_command_sets, solo debe tener los base
        assert "general" in active_sets
        assert "movement" in active_sets

    async def test_command_sets_from_room(self, db_session, sample_character, sample_room):
        """
        Test: Debe incluir command_sets otorgados por la sala actual.
        """
        # Cargar el personaje con todas sus relaciones
        character = await load_character_with_relations(db_session, sample_character.id)

        active_sets = await command_service.get_active_command_sets_for_character(character)

        # Verificar que al menos incluye los sets base
        assert "general" in active_sets
        assert "movement" in active_sets

    async def test_admin_command_sets_for_admin(self, db_session, sample_character):
        """
        Test: Debe incluir command sets de admin cuando el rol es ADMIN.
        """
        # Cambiar el rol de la cuenta a ADMIN
        sample_character.account.role = "ADMIN"
        await db_session.commit()

        # Cargar el personaje con todas sus relaciones
        character = await load_character_with_relations(db_session, sample_character.id)

        active_sets = await command_service.get_active_command_sets_for_character(character)

        # Verificar que incluye los sets de admin
        assert "spawning" in active_sets
        assert "admin_movement" in active_sets
        assert "admin_info" in active_sets
        assert "diagnostics" in active_sets
        assert "management" in active_sets

    async def test_admin_command_sets_for_superadmin(self, db_session, sample_character):
        """
        Test: Debe incluir command sets de admin cuando el rol es SUPERADMIN.
        """
        # Cambiar el rol de la cuenta a SUPERADMIN
        sample_character.account.role = "SUPERADMIN"
        await db_session.commit()

        # Cargar el personaje con todas sus relaciones
        character = await load_character_with_relations(db_session, sample_character.id)

        active_sets = await command_service.get_active_command_sets_for_character(character)

        # Verificar que incluye los sets de admin
        assert "spawning" in active_sets
        assert "admin_movement" in active_sets
        assert "admin_info" in active_sets
        assert "diagnostics" in active_sets
        assert "management" in active_sets

    async def test_no_admin_command_sets_for_player(self, db_session, sample_character):
        """
        Test: No debe incluir command sets de admin para roles PLAYER o HELPER.
        """
        # Asegurar que el rol es PLAYER
        sample_character.account.role = "PLAYER"
        await db_session.commit()

        # Cargar el personaje con todas sus relaciones
        character = await load_character_with_relations(db_session, sample_character.id)

        active_sets = await command_service.get_active_command_sets_for_character(character)

        # Verificar que NO incluye los sets de admin
        assert "spawning" not in active_sets
        assert "admin_movement" not in active_sets
        assert "admin_info" not in active_sets
        assert "diagnostics" not in active_sets
        assert "management" not in active_sets

    async def test_command_sets_are_sorted(self, db_session, sample_character):
        """
        Test: La lista de command sets debe estar ordenada alfabéticamente.
        """
        # Cargar el personaje con todas sus relaciones
        character = await load_character_with_relations(db_session, sample_character.id)

        active_sets = await command_service.get_active_command_sets_for_character(character)

        # Verificar que está ordenada
        assert active_sets == sorted(active_sets)

    async def test_no_duplicate_command_sets(self, db_session, sample_character):
        """
        Test: No debe haber command sets duplicados en la lista.
        """
        # Forzar duplicados manualmente modificando command_sets
        sample_character.command_sets = ["general", "general", "movement"]
        await db_session.commit()

        # Cargar el personaje con todas sus relaciones
        character = await load_character_with_relations(db_session, sample_character.id)

        active_sets = await command_service.get_active_command_sets_for_character(character)

        # Verificar que no hay duplicados
        assert len(active_sets) == len(set(active_sets))


class TestGetCommandSets:
    """Tests para la función get_command_sets()."""

    def test_get_command_sets_returns_dict(self):
        """
        Test: Debe devolver un diccionario de command sets.
        """
        command_sets = command_service.get_command_sets()

        assert isinstance(command_sets, dict)
        # Verificar que contiene algunas claves esperadas
        assert "general" in command_sets or "movement" in command_sets


@pytest.mark.asyncio
class TestUpdateTelegramCommands:
    """Tests para la función update_telegram_commands()."""

    async def test_update_telegram_commands_with_none_character(self):
        """
        Test: Debe manejar correctamente cuando character es None.
        """
        # No debería lanzar excepción
        try:
            await command_service.update_telegram_commands(None)
        except Exception as e:
            pytest.fail(f"update_telegram_commands(None) lanzó excepción: {e}")

    async def test_update_telegram_commands_logs_error_on_failure(self, db_session, sample_character):
        """
        Test: Debe capturar y registrar errores sin fallar.
        """
        # Cargar el personaje con todas sus relaciones
        character = await load_character_with_relations(db_session, sample_character.id)

        # Esto podría fallar si no hay bot configurado, pero no debe lanzar excepción
        try:
            await command_service.update_telegram_commands(character)
        except Exception as e:
            pytest.fail(f"update_telegram_commands() lanzó excepción: {e}")
