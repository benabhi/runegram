# src/services/world_loader_service.py
import logging
# --- ¡Importación clave añadida! ---
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import Room, Exit
from game_data.room_prototypes import ROOM_PROTOTYPES

# Mapa de direcciones opuestas para conexiones bidireccionales
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
    Sincroniza la base de datos con los prototipos de salas.
    Es idempotente: crea salas si no existen y las actualiza si existen.
    """
    logging.info(" sincronizando el mundo desde los prototipos...")

    # Paso 1: Sincronizar todas las salas para asegurar que existen y obtener sus IDs.
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

    # Paso 2: Limpiar salidas viejas. Es más fácil borrarlas y recrearlas.
    logging.info("  -> Limpiando todas las salidas existentes para reconstruir...")

    # --- LÍNEA CORREGIDA ---
    # La forma correcta de borrar todos los registros de una tabla es usando la instrucción `delete()`.
    await session.execute(delete(Exit))
    # --- FIN DE LA CORRECCIÓN ---

    # Paso 3: Crear todas las salidas de nuevo.
    for key, data in ROOM_PROTOTYPES.items():
        from_room_id = room_key_to_id_map[key]
        for direction, to_room_key in data.get("exits", {}).items():
            if to_room_key in room_key_to_id_map:
                to_room_id = room_key_to_id_map[to_room_key]

                exit_forward = Exit(name=direction.lower(), from_room_id=from_room_id, to_room_id=to_room_id)
                session.add(exit_forward)

                opposite = OPPOSITE_DIRECTIONS.get(direction.lower())
                if opposite:
                    exit_backward = Exit(name=opposite, from_room_id=to_room_id, to_room_id=from_room_id)
                    session.add(exit_backward)
            else:
                logging.warning(f"  -> La sala de destino '{to_room_key}' definida en '{key}' no existe.")

    await session.commit()
    logging.info("¡Sincronización del mundo completada!")