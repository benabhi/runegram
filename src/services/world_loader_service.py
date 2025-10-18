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

from src.models import Room, Exit, Item
from game_data.room_prototypes import ROOM_PROTOTYPES
from game_data.item_prototypes import ITEM_PROTOTYPES

# Mapa de direcciones opuestas (referencia).
# NOTA: Ya no se usa para crear salidas automáticamente. Todas las salidas deben
# estar explícitamente definidas en ambas direcciones en los prototipos de sala.
OPPOSITE_DIRECTIONS = {
    "norte": "sur", "sur": "norte",
    "este": "oeste", "oeste": "este",
    "arriba": "abajo", "abajo": "arriba",
    "dentro": "fuera", "fuera": "dentro",
    "noreste": "suroeste", "suroeste": "noreste",
    "noroeste": "sureste", "sureste": "noroeste",
}

async def _sync_room_fixtures(session: AsyncSession, room_key_to_id_map: dict):
    """
    Sincroniza los fixtures (objetos de ambiente) definidos en las salas.

    Los fixtures son items que forman parte del ambiente de la sala y están
    definidos en el campo 'fixtures' del prototipo de sala. Esta función:

    1. Lee el campo 'fixtures' de cada sala en ROOM_PROTOTYPES.
    2. Para cada fixture definido, verifica si ya existe en la sala.
    3. Si no existe, lo crea. Si ya existe, lo mantiene (preserva script_state).

    Esta función es idempotente: no duplicará fixtures en reinicios.
    """
    logging.info("  -> Sincronizando fixtures de salas...")

    for room_key, room_data in ROOM_PROTOTYPES.items():
        fixture_keys = room_data.get("fixtures", [])
        if not fixture_keys:
            continue

        room_id = room_key_to_id_map.get(room_key)
        if not room_id:
            logging.warning(f"  -> Sala '{room_key}' no encontrada en mapa de IDs. Ignorando fixtures.")
            continue

        for item_key in fixture_keys:
            # Verificar que el prototipo existe
            if item_key not in ITEM_PROTOTYPES:
                logging.warning(f"  -> Fixture '{item_key}' no existe en ITEM_PROTOTYPES. Ignorando.")
                continue

            # Verificar si el fixture ya existe en esta sala
            result = await session.execute(
                select(Item).where(Item.key == item_key, Item.room_id == room_id)
            )
            existing_fixture = result.scalar_one_or_none()

            if existing_fixture:
                # Ya existe, mantenerlo (preserva script_state)
                logging.debug(f"  -> Fixture '{item_key}' ya existe en '{room_key}'. Manteniendo.")
            else:
                # Crear nuevo fixture
                new_fixture = Item(key=item_key, room_id=room_id)
                session.add(new_fixture)
                logging.info(f"  -> Creado fixture '{item_key}' en '{room_key}'.")


async def sync_world_from_prototypes(session: AsyncSession):
    """
    Sincroniza la base de datos con los prototipos de salas. Esta función es
    idempotente: se puede ejecutar de forma segura en cada arranque.

    Su lógica es:
    1. Crea/actualiza las salas.
    2. Borra todas las salidas existentes.
    3. Recrea todas las salidas tal como están definidas en los prototipos,
       aplicando los `locks` correspondientes. Todas las salidas deben estar
       explícitamente definidas en ambas direcciones en los prototipos.
    4. Sincroniza los fixtures (objetos de ambiente) de cada sala.
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

                    # Crear la salida tal como está definida en el prototipo.
                    # NOTA: Ya no creamos salidas de vuelta automáticamente.
                    # Todas las salidas deben estar explícitamente definidas en ambas
                    # direcciones en los prototipos de sala.
                    exit_forward = Exit(
                        name=direction.lower(),
                        from_room_id=from_room_id,
                        to_room_id=to_room_id,
                        locks=lock_string
                    )
                    session.add(exit_forward)
                else:
                    logging.warning(f"  -> La sala de destino '{to_room_key}' definida en la sala '{key}' no existe. Se ignora la salida.")

        # --- PASO 4: Sincronizar Fixtures de Salas ---
        await _sync_room_fixtures(session, room_key_to_id_map)

        await session.commit()
        logging.info("¡Sincronización del mundo completada!")
    except Exception:
        logging.exception("Error fatal durante la sincronización del mundo.")
        raise