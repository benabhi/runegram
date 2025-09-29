# src/services/world_service.py

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.room import Room
from src.models.exit import Exit # <-- Importa el nuevo modelo

# Mapa de direcciones opuestas para conexiones bidireccionales
OPPOSITE_DIRECTIONS = {
    "norte": "sur", "sur": "norte",
    "este": "oeste", "oeste": "este",
    "arriba": "abajo", "abajo": "arriba",
    "dentro": "fuera", "fuera": "dentro",
    "noreste": "suroeste", "suroeste": "noreste",
    "noroeste": "sureste", "sureste": "noroeste",
}

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

async def link_rooms(session: AsyncSession, from_room_id: int, direction: str, to_room_id: int, bidirectional: bool = True):
    """Crea una salida (y opcionalmente su opuesta) entre dos salas."""
    from_room = await get_room(session, from_room_id)
    to_room = await get_room(session, to_room_id)

    if not from_room or not to_room:
        raise ValueError("Una o ambas salas no existen.")

    # Crear la salida principal
    direction_lower = direction.lower()
    new_exit = Exit(name=direction_lower, from_room_id=from_room_id, to_room_id=to_room_id)
    session.add(new_exit)

    # Crear la salida de vuelta si es bidireccional
    if bidirectional:
        opposite_direction = OPPOSITE_DIRECTIONS.get(direction_lower)
        if opposite_direction:
            return_exit = Exit(name=opposite_direction, from_room_id=to_room_id, to_room_id=from_room_id)
            session.add(return_exit)

    await session.commit()