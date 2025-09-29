# src/services/item_service.py

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.item import Item
# No necesitamos Character y Room aquí directamente
# from src.models.character import Character
# from src.models.room import Room
from game_data.item_prototypes import ITEM_PROTOTYPES


async def spawn_item_in_room(session: AsyncSession, room_id: int, item_key: str) -> Item:
    """
    Crea una instancia de un prototipo de objeto y la coloca en una sala.
    """
    if item_key not in ITEM_PROTOTYPES:
        raise ValueError(f"No existe un prototipo de objeto con la clave '{item_key}'")

    # Creamos una nueva instancia de Item, solo guardando la key y su ubicación.
    new_item = Item(room_id=room_id, key=item_key)
    session.add(new_item)
    await session.commit()
    await session.refresh(new_item)
    return new_item


async def move_item_to_character(session: AsyncSession, item_id: int, character_id: int):
    """Mueve un objeto desde una sala al inventario de un personaje."""
    query = update(Item).where(Item.id == item_id).values(
        room_id=None,
        character_id=character_id
    )
    await session.execute(query)
    await session.commit()


async def move_item_to_room(session: AsyncSession, item_id: int, room_id: int):
    """Mueve un objeto desde el inventario de un personaje a una sala."""
    query = update(Item).where(Item.id == item_id).values(
        room_id=room_id,
        character_id=None
    )
    await session.execute(query)
    await session.commit()