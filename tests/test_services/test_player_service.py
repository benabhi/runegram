# tests/test_services/test_player_service.py
"""
Tests para el Player Service.

Este servicio es crítico ya que maneja toda la lógica de creación y gestión
de cuentas y personajes.
"""

import pytest
from src.services import player_service
from src.models import Account, Character, Room


@pytest.mark.critical
@pytest.mark.asyncio
class TestGetOrCreateAccount:
    """Tests para la función get_or_create_account()."""

    async def test_create_new_account(self, db_session):
        """
        Test: Debe crear una nueva cuenta si no existe.
        """
        telegram_id = 123456789
        account = await player_service.get_or_create_account(db_session, telegram_id)

        assert account is not None
        assert account.telegram_id == telegram_id
        assert account.id is not None
        assert account.character is None  # No tiene personaje aún

    async def test_get_existing_account_without_character(self, db_session):
        """
        Test: Debe devolver una cuenta existente sin personaje.
        """
        # Crear cuenta previamente
        existing_account = Account(telegram_id=987654321)
        db_session.add(existing_account)
        await db_session.commit()

        # Intentar obtenerla
        account = await player_service.get_or_create_account(db_session, 987654321)

        assert account is not None
        assert account.id == existing_account.id
        assert account.telegram_id == 987654321

    async def test_get_existing_account_with_character(self, db_session, sample_character):
        """
        Test: Debe devolver una cuenta existente con personaje completamente cargado.
        """
        telegram_id = sample_character.account.telegram_id

        account = await player_service.get_or_create_account(db_session, telegram_id)

        assert account is not None
        assert account.character is not None
        assert account.character.name == sample_character.name
        # Verificar que las relaciones están cargadas
        assert hasattr(account.character, 'room')
        assert hasattr(account.character, 'items')


@pytest.mark.critical
@pytest.mark.asyncio
class TestCreateCharacter:
    """Tests para la función create_character()."""

    async def test_create_character_success(self, db_session, sample_room):
        """
        Test: Debe crear un personaje exitosamente para una cuenta nueva.
        """
        telegram_id = 111222333
        character_name = "NuevoHero"

        character = await player_service.create_character(
            db_session,
            telegram_id,
            character_name
        )

        assert character is not None
        assert character.name == character_name
        assert character.account_id is not None
        assert character.room_id == 1  # Sala de inicio (limbo)

    async def test_create_character_duplicate_name(self, db_session, sample_character):
        """
        Test: Debe fallar si el nombre ya está en uso.
        """
        telegram_id = 999888777
        duplicate_name = sample_character.name

        with pytest.raises(ValueError) as exc_info:
            await player_service.create_character(
                db_session,
                telegram_id,
                duplicate_name
            )

        assert "ya está en uso" in str(exc_info.value)

    async def test_create_character_account_already_has_character(self, db_session, sample_character):
        """
        Test: Debe fallar si la cuenta ya tiene un personaje.
        """
        telegram_id = sample_character.account.telegram_id

        with pytest.raises(ValueError) as exc_info:
            await player_service.create_character(
                db_session,
                telegram_id,
                "OtroNombre"
            )

        assert "Ya tienes un personaje" in str(exc_info.value)


@pytest.mark.critical
@pytest.mark.asyncio
class TestGetCharacterWithRelations:
    """Tests para la función get_character_with_relations_by_id()."""

    async def test_get_existing_character(self, db_session, sample_character):
        """
        Test: Debe obtener un personaje existente con todas sus relaciones.
        """
        character = await player_service.get_character_with_relations_by_id(
            db_session,
            sample_character.id
        )

        assert character is not None
        assert character.id == sample_character.id
        assert character.name == sample_character.name
        # Verificar que las relaciones críticas están cargadas
        assert hasattr(character, 'room')
        assert hasattr(character, 'account')
        assert hasattr(character, 'items')

    async def test_get_nonexistent_character(self, db_session):
        """
        Test: Debe devolver None si el personaje no existe.
        """
        character = await player_service.get_character_with_relations_by_id(
            db_session,
            99999  # ID que no existe
        )

        assert character is None


@pytest.mark.critical
@pytest.mark.asyncio
class TestTeleportCharacter:
    """Tests para la función teleport_character()."""

    async def test_teleport_to_valid_room(self, db_session, sample_character):
        """
        Test: Debe teletransportar un personaje a una sala válida.
        """
        # Crear una segunda sala
        new_room = Room(
            key="nueva_sala",
            name="Nueva Sala",
            description="Una sala de destino"
        )
        db_session.add(new_room)
        await db_session.commit()
        await db_session.refresh(new_room)

        original_room_id = sample_character.room_id

        # Teletransportar
        await player_service.teleport_character(
            db_session,
            sample_character.id,
            new_room.id
        )

        # Verificar que se movió
        await db_session.refresh(sample_character)
        assert sample_character.room_id == new_room.id
        assert sample_character.room_id != original_room_id

    async def test_teleport_to_invalid_room(self, db_session, sample_character):
        """
        Test: Debe fallar si la sala de destino no existe.
        """
        invalid_room_id = 99999

        with pytest.raises(ValueError) as exc_info:
            await player_service.teleport_character(
                db_session,
                sample_character.id,
                invalid_room_id
            )

        assert "no existe" in str(exc_info.value)
