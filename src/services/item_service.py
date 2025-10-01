# src/services/item_service.py
"""
Módulo de Servicio para la Gestión de Objetos (Items).

Este servicio encapsula la lógica de negocio para crear y manipular instancias
de objetos en el mundo del juego. Se encarga de la interacción directa con el
modelo `Item`.

Responsabilidades:
- Crear nuevas instancias de objetos a partir de prototipos (`spawn`).
- Mover objetos entre salas y los inventarios de los personajes.
"""

import logging
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.item import Item
from game_data.item_prototypes import ITEM_PROTOTYPES
from src.services import ticker_service


async def spawn_item_in_room(session: AsyncSession, room_id: int, item_key: str) -> Item:
    """
    Crea una instancia de un prototipo de objeto, la coloca en una sala
    y registra sus tickers.

    Args:
        session (AsyncSession): La sesión de base de datos activa.
        room_id (int): El ID de la sala donde se creará el objeto.
        item_key (str): La clave del prototipo del objeto a crear.

    Returns:
        Item: La nueva instancia del objeto `Item` creada.

    Raises:
        ValueError: Si la `item_key` no corresponde a ningún prototipo definido.
    """
    if item_key not in ITEM_PROTOTYPES:
        raise ValueError(f"No existe un prototipo de objeto con la clave '{item_key}'")

    try:
        # 1. Crear la instancia del modelo Item, vinculándola a la sala.
        new_item = Item(room_id=room_id, key=item_key)
        session.add(new_item)
        await session.commit()
        await session.refresh(new_item)

        # 2. Notificar al ticker_service para que programe los tickers de este nuevo objeto.
        await ticker_service.schedule_tickers_for_entity(new_item)

        return new_item
    except Exception:
        logging.exception(f"Error inesperado al intentar generar el objeto con clave '{item_key}' en la sala {room_id}")
        # Relanzamos la excepción para que la capa superior (el comando) la maneje.
        raise


async def move_item_to_character(session: AsyncSession, item_id: int, character_id: int):
    """
    Mueve un objeto desde una sala (o de ningún sitio) al inventario de un personaje.
    Actualiza el `room_id` a NULL y establece el `character_id`.
    """
    query = (
        update(Item)
        .where(Item.id == item_id)
        .values(room_id=None, character_id=character_id)
    )
    await session.execute(query)
    await session.commit()


async def move_item_to_room(session: AsyncSession, item_id: int, room_id: int):
    """
    Mueve un objeto desde el inventario de un personaje al suelo de una sala.
    Actualiza el `character_id` a NULL y establece el `room_id`.
    """
    query = (
        update(Item)
        .where(Item.id == item_id)
        .values(room_id=room_id, character_id=None)
    )
    await session.execute(query)
    await session.commit()