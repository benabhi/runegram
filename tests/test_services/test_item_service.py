# tests/test_services/test_item_service.py
"""
Tests para el Item Service.

Este servicio maneja la creación y movimiento de objetos en el juego.
"""

import pytest
from src.services import item_service
from src.models import Item


@pytest.mark.critical
@pytest.mark.asyncio
class TestSpawnItem:
    """Tests para la función spawn_item_in_room()."""

    async def test_spawn_valid_item(self, db_session, sample_room):
        """
        Test: Debe crear una instancia de un prototipo válido.
        """
        # Usar un prototipo que sabemos que existe
        item_key = "espada_viviente"  # De item_prototypes.py

        item = await item_service.spawn_item_in_room(
            db_session,
            sample_room.id,
            item_key
        )

        assert item is not None
        assert item.key == item_key
        assert item.room_id == sample_room.id
        assert item.character_id is None
        assert item.parent_item_id is None

    async def test_spawn_invalid_item(self, db_session, sample_room):
        """
        Test: Debe fallar si el prototipo no existe.
        """
        invalid_key = "item_que_no_existe"

        with pytest.raises(ValueError) as exc_info:
            await item_service.spawn_item_in_room(
                db_session,
                sample_room.id,
                invalid_key
            )

        assert "No existe un prototipo" in str(exc_info.value)


@pytest.mark.critical
@pytest.mark.asyncio
class TestMoveItemToCharacter:
    """Tests para la función move_item_to_character()."""

    async def test_move_item_from_room_to_character(self, db_session, sample_item, sample_character):
        """
        Test: Debe mover un item del suelo al inventario de un personaje.
        """
        # El sample_item está en una sala por defecto
        original_room_id = sample_item.room_id

        await item_service.move_item_to_character(
            db_session,
            sample_item.id,
            sample_character.id
        )

        # Refrescar el item para ver los cambios
        await db_session.refresh(sample_item)

        assert sample_item.character_id == sample_character.id
        assert sample_item.room_id is None
        assert sample_item.parent_item_id is None


@pytest.mark.critical
@pytest.mark.asyncio
class TestMoveItemToRoom:
    """Tests para la función move_item_to_room()."""

    async def test_move_item_from_character_to_room(self, db_session, sample_character, sample_room):
        """
        Test: Debe mover un item del inventario al suelo de una sala.
        """
        # Crear un item en el inventario del personaje
        item = Item(key="test_item", character_id=sample_character.id)
        db_session.add(item)
        await db_session.commit()
        await db_session.refresh(item)

        assert item.character_id == sample_character.id

        # Mover a sala
        await item_service.move_item_to_room(
            db_session,
            item.id,
            sample_room.id
        )

        await db_session.refresh(item)

        assert item.room_id == sample_room.id
        assert item.character_id is None
        assert item.parent_item_id is None


@pytest.mark.critical
@pytest.mark.asyncio
class TestMoveItemToContainer:
    """Tests para la función move_item_to_container()."""

    async def test_move_item_into_container(self, db_session, sample_room):
        """
        Test: Debe mover un item dentro de un contenedor.
        """
        # Crear un contenedor
        container = Item(key="mochila_cuero", room_id=sample_room.id)
        db_session.add(container)

        # Crear un item suelto
        item = Item(key="espada_viviente", room_id=sample_room.id)
        db_session.add(item)

        await db_session.commit()
        await db_session.refresh(container)
        await db_session.refresh(item)

        # Meter el item en el contenedor
        await item_service.move_item_to_container(
            db_session,
            item.id,
            container.id
        )

        await db_session.refresh(item)

        assert item.parent_item_id == container.id
        assert item.room_id is None
        assert item.character_id is None


@pytest.mark.asyncio
class TestItemLocationExclusivity:
    """Tests para verificar que un item solo puede estar en una ubicación a la vez."""

    async def test_item_in_room_not_in_character(self, db_session, sample_item):
        """
        Test: Un item en una sala no debe estar en un inventario.
        """
        assert sample_item.room_id is not None
        assert sample_item.character_id is None
        assert sample_item.parent_item_id is None

    async def test_item_moves_clear_previous_location(self, db_session, sample_character, sample_item):
        """
        Test: Cuando un item se mueve, debe limpiarse su ubicación anterior.
        """
        # Inicialmente en sala
        original_room = sample_item.room_id
        assert original_room is not None

        # Mover a personaje
        await item_service.move_item_to_character(
            db_session,
            sample_item.id,
            sample_character.id
        )
        await db_session.refresh(sample_item)

        assert sample_item.character_id == sample_character.id
        assert sample_item.room_id is None  # Limpiado

        # Crear nuevo item y moverlo a contenedor
        new_item = Item(key="test_item", character_id=sample_character.id)
        db_session.add(new_item)
        await db_session.commit()
        await db_session.refresh(new_item)

        # Crear contenedor
        container = Item(key="mochila_cuero", character_id=sample_character.id)
        db_session.add(container)
        await db_session.commit()
        await db_session.refresh(container)

        # Mover a contenedor
        await item_service.move_item_to_container(
            db_session,
            new_item.id,
            container.id
        )
        await db_session.refresh(new_item)

        assert new_item.parent_item_id == container.id
        assert new_item.character_id is None  # Limpiado
        assert new_item.room_id is None  # Limpiado
