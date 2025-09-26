# src/services/world_service.py

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.room import Room

async def get_room(session: AsyncSession, room_id: int) -> Room | None:
    """Busca y devuelve una sala por su ID."""
    result = await session.execute(select(Room).where(Room.id == room_id))
    return result.scalar_one_or_none()

async def create_room(session: AsyncSession, name: str) -> Room:
    """Crea una nueva sala en la base de datos."""
    if not name:
        raise ValueError("El nombre de la sala no puede estar vacío.")

    new_room = Room(name=name)
    session.add(new_room)
    await session.commit()
    await session.refresh(new_room)
    return new_room

async def set_room_description(session: AsyncSession, room_id: int, description: str):
    """Actualiza la descripción de una sala existente."""
    query = update(Room).where(Room.id == room_id).values(description=description)
    await session.execute(query)
    await session.commit()

async def link_rooms(session: AsyncSession, from_room_id: int, direction: str, to_room_id: int):
    """Crea una salida desde una sala hacia otra."""
    from_room = await get_room(session, from_room_id)
    to_room = await get_room(session, to_room_id)

    if not from_room or not to_room:
        raise ValueError("Una o ambas salas no existen.")

    # Copiamos el diccionario de salidas para que SQLAlchemy detecte el cambio
    new_exits = dict(from_room.exits)
    new_exits[direction.lower()] = to_room_id

    # Actualizamos la sala con el nuevo diccionario de salidas
    query = update(Room).where(Room.id == from_room_id).values(exits=new_exits)
    await session.execute(query)
    await session.commit()