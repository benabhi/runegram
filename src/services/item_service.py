# src/services/item_service.py

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.item import Item
from src.models.character import Character
from src.models.room import Room


async def create_item_in_room(session: AsyncSession, room_id: int, key: str, name: str, description: str) -> Item:
    """Crea una nueva instancia de un objeto y la coloca en una sala."""
    new_item = Item(
        room_id=room_id,
        key=key,
        name=name,
        description=description
    )
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