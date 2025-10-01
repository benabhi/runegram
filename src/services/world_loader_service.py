# src/services/world_loader_service.py
"""
Módulo de Servicio para la Carga del Mundo.

Este servicio es el responsable de construir y sincronizar el mundo estático del
juego (salas y salidas) con la base de datos. Se ejecuta una sola vez durante
el arranque de la aplicación.

Lee las definiciones de contenido desde `game_data/room_prototypes.py` y se
asegura de que el estado de la base de datos refleje fielmente esa "fuente de
la verdad".
"""

import logging
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import Room, Exit
from game_data.room_prototypes import ROOM_PROTOTYPES

# Mapa de direcciones opuestas para crear automáticamente las salidas bidireccionales.
OPPOSITE_DIRECTIONS = {
    "norte": "sur", "sur": "norte",
    "este": "oeste", "oeste": "este",
    "arriba": "abajo", "abajo": "arriba",
    "dentro": "fuera", "fuera": "dentro",
    "noreste": "suroeste", "suroeste": "noreste",
    "noroeste": "sureste", "sureste": "noroeste",
}

async def sync_world_from_prototypes(session: AsyncSession):
    """
    Sincroniza la base de datos con los prototipos de salas. Esta función es
    idempotente: se puede ejecutar de forma segura en cada arranque.

    Su lógica es:
    1. Crea/actualiza las salas.
    2. Borra todas las salidas existentes.
    3. Recrea todas las salidas, aplicando los `locks` definidos en los prototipos.
    """
    logging.info("Sincronizando el mundo estático desde los prototipos...")
    try:
        # --- PASO 1: Sincronizar Salas ---
        room_key_to_id_map = {}

        existing_rooms_query = await session.execute(select(Room))
        existing_rooms = {room.key: room for room in existing_rooms_query.scalars().all()}

        for key, data in ROOM_PROTOTYPES.items():
            room = existing_rooms.get(key)
            if not room:
                logging.info(f"  -> Creando sala '{key}'...")
                room = Room(key=key, name=data['name'], description=data['description'])
                session.add(room)
            else:
                room.name = data['name']
                room.description = data['description']

            await session.flush()
            room_key_to_id_map[key] = room.id

        # --- PASO 2: Limpiar Salidas Viejas ---
        logging.info("  -> Limpiando todas las salidas existentes para reconstruir...")
        await session.execute(delete(Exit))

        # --- PASO 3: Crear Salidas Nuevas con Locks ---
        for key, data in ROOM_PROTOTYPES.items():
            from_room_id = room_key_to_id_map[key]
            for direction, exit_data in data.get("exits", {}).items():
                # El prototipo ahora puede ser un string simple o un diccionario.
                if isinstance(exit_data, str):
                    to_room_key = exit_data
                    lock_string = ""
                elif isinstance(exit_data, dict):
                    to_room_key = exit_data.get("to")
                    lock_string = exit_data.get("locks", "")
                else:
                    continue # Ignorar formato incorrecto

                if to_room_key in room_key_to_id_map:
                    to_room_id = room_key_to_id_map[to_room_key]

                    # Crear la salida principal, incluyendo su lock.
                    exit_forward = Exit(
                        name=direction.lower(),
                        from_room_id=from_room_id,
                        to_room_id=to_room_id,
                        locks=lock_string
                    )
                    session.add(exit_forward)

                    # Crear la salida de vuelta automáticamente (sin lock por defecto).
                    opposite = OPPOSITE_DIRECTIONS.get(direction.lower())
                    if opposite:
                        # La salida de vuelta no hereda el lock, debe definirse explícitamente.
                        exit_backward = Exit(name=opposite, from_room_id=to_room_id, to_room_id=from_room_id)
                        session.add(exit_backward)
                else:
                    logging.warning(f"  -> La sala de destino '{to_room_key}' definida en la sala '{key}' no existe. Se ignora la salida.")

        await session.commit()
        logging.info("¡Sincronización del mundo completada!")
    except Exception:
        logging.exception("Error fatal durante la sincronización del mundo.")
        raise