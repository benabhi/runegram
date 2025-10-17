# src/services/world_service.py
"""
Módulo de Servicio con Utilidades para el Mundo.

Este servicio contiene funciones de ayuda de bajo nivel para interactuar
con las entidades del mundo, principalmente el modelo `Room`.

A diferencia del `world_loader_service` que construye el mundo al arrancar,
las funciones aquí presentes son utilidades genéricas que pueden ser llamadas
desde otras partes del código, como los comandos.
"""

import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.room import Room


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