# src/services/world_service.py
"""
Módulo de Servicio con Utilidades para el Mundo.

Este servicio contiene funciones de ayuda de bajo nivel para interactuar
con las entidades del mundo, principalmente el modelo `Room`.

A diferencia del `world_loader_service` que construye el mundo al arrancar,
las funciones aquí presentes son utilidades genéricas que pueden ser llamadas
desde otras partes del código, como los comandos.

NOTA: Varias funciones en este archivo (`create_room`, `link_rooms`) han quedado
obsoletas por el sistema de carga de mundo basado en prototipos, pero se
mantienen por si son de utilidad para futuras herramientas de administración
o para depuración.
"""

import logging
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.room import Room
from src.models.exit import Exit


async def get_room(session: AsyncSession, room_id: int) -> Room | None:
    """
    Busca y devuelve una sala por su ID numérico.

    Args:
        session (AsyncSession): La sesión de base de datos activa.
        room_id (int): El ID de la sala a buscar.

    Returns:
        Room | None: El objeto de la sala si se encuentra, de lo contrario None.
    """
    try:
        result = await session.execute(select(Room).where(Room.id == room_id))
        return result.scalar_one_or_none()
    except Exception:
        logging.exception(f"Error al buscar la sala con ID {room_id}")
        return None

# ==============================================================================
# Las siguientes funciones han sido mayormente reemplazadas por el sistema de
# carga de mundo (`world_loader_service`) y ya no se usan en el flujo principal.
# Se conservan para posible uso futuro en herramientas de administración.
# ==============================================================================

async def create_room(session: AsyncSession, name: str) -> Room:
    """
    (Obsoleto) Crea una nueva sala en la base de datos.
    """
    if not name:
        raise ValueError("El nombre de la sala no puede estar vacío.")
    new_room = Room(name=name)
    session.add(new_room)
    await session.commit()
    await session.refresh(new_room)
    return new_room

async def set_room_description(session: AsyncSession, room_id: int, description: str):
    """
    (Obsoleto) Actualiza la descripción de una sala existente.
    """
    query = update(Room).where(Room.id == room_id).values(description=description)
    await session.execute(query)
    await session.commit()

async def link_rooms(session: AsyncSession, from_room_id: int, direction: str, to_room_id: int, bidirectional: bool = True):
    """
    (Obsoleto) Crea una salida (y opcionalmente su opuesta) entre dos salas.
    """
    # Mapa de direcciones opuestas, duplicado aquí para que la función sea autónoma.
    OPPOSITE_DIRECTIONS = {
        "norte": "sur", "sur": "norte", "este": "oeste", "oeste": "este",
        "arriba": "abajo", "abajo": "arriba", "dentro": "fuera", "fuera": "dentro",
        "noreste": "suroeste", "suroeste": "noreste", "noroeste": "sureste", "sureste": "noroeste",
    }

    from_room = await get_room(session, from_room_id)
    to_room = await get_room(session, to_room_id)

    if not from_room or not to_room:
        raise ValueError("Una o ambas salas no existen.")

    direction_lower = direction.lower()
    new_exit = Exit(name=direction_lower, from_room_id=from_room_id, to_room_id=to_room_id)
    session.add(new_exit)

    if bidirectional:
        opposite_direction = OPPOSITE_DIRECTIONS.get(direction_lower)
        if opposite_direction:
            return_exit = Exit(name=opposite_direction, from_room_id=to_room_id, to_room_id=from_room_id)
            session.add(return_exit)

    await session.commit()