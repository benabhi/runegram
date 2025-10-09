# src/services/item_service.py
"""
Módulo de Servicio para la Gestión de Objetos (Items).

Este servicio encapsula la lógica de negocio para crear y manipular instancias
de objetos en el mundo del juego. Se encarga de la interacción directa con el
modelo `Item`.

Responsabilidades:
- Crear nuevas instancias de objetos a partir de prototipos (`spawn`).
- Mover objetos entre salas, inventarios de personajes y contenedores.
"""

import logging
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.item import Item
from game_data.item_prototypes import ITEM_PROTOTYPES


async def spawn_item_in_room(session: AsyncSession, room_id: int, item_key: str) -> Item:
    """
    Crea una instancia de un prototipo de objeto y la coloca en una sala.

    Los tick_scripts se procesan automáticamente por el pulse_service global.
    """
    if item_key not in ITEM_PROTOTYPES:
        raise ValueError(f"No existe un prototipo de objeto con la clave '{item_key}'")

    try:
        new_item = Item(room_id=room_id, key=item_key)
        session.add(new_item)
        await session.commit()
        await session.refresh(new_item)
        return new_item
    except Exception:
        logging.exception(f"Error inesperado al generar el objeto con clave '{item_key}'")
        raise


async def move_item_to_character(session: AsyncSession, item_id: int, character_id: int):
    """
    Mueve un objeto al inventario de un personaje, quitándolo de cualquier
    otra ubicación (sala o contenedor).
    """
    query = (
        update(Item)
        .where(Item.id == item_id)
        .values(room_id=None, character_id=character_id, parent_item_id=None)
    )
    await session.execute(query)
    await session.commit()


async def move_item_to_room(session: AsyncSession, item_id: int, room_id: int):
    """
    Mueve un objeto al suelo de una sala, quitándolo de cualquier
    otra ubicación (inventario o contenedor).
    """
    query = (
        update(Item)
        .where(Item.id == item_id)
        .values(room_id=room_id, character_id=None, parent_item_id=None)
    )
    await session.execute(query)
    await session.commit()


async def move_item_to_container(session: AsyncSession, item_id: int, container_id: int):
    """
    Mueve un objeto al interior de otro objeto (contenedor), quitándolo de
    cualquier otra ubicación (sala o inventario).
    """
    query = (
        update(Item)
        .where(Item.id == item_id)
        .values(room_id=None, character_id=None, parent_item_id=container_id)
    )
    await session.execute(query)
    await session.commit()


async def delete_item(session: AsyncSession, item_id: int) -> Item:
    """
    Elimina permanentemente un objeto del juego.

    Args:
        session: Sesión de base de datos activa
        item_id: ID del objeto a eliminar

    Returns:
        Item: El objeto eliminado (antes de ser eliminado, para obtener información)

    Raises:
        ValueError: Si el objeto no existe

    Notas:
        - Si el objeto es un contenedor, los items dentro quedarán huérfanos
          (sin parent_item_id) y deberán ser manejados por el llamador.
        - El objeto se elimina permanentemente de la base de datos.
    """
    # Obtener el objeto antes de eliminarlo para retornar información
    item = await session.get(Item, item_id)

    if not item:
        raise ValueError(f"No existe un objeto con el ID '{item_id}'")

    try:
        # Si es un contenedor, eliminar referencia de los items contenidos
        # (opcional: podrías querer moverlos al suelo o inventario)
        if item.prototype.get("is_container"):
            # Actualizar items contenidos para que queden sin parent
            await session.execute(
                update(Item)
                .where(Item.parent_item_id == item_id)
                .values(parent_item_id=None)
            )

        # Eliminar el objeto
        await session.delete(item)
        await session.commit()

        logging.info(f"Objeto eliminado: {item.get_name()} (ID: {item_id})")
        return item

    except Exception:
        logging.exception(f"Error inesperado al eliminar el objeto con ID '{item_id}'")
        raise