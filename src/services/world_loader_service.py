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
    1. Crea las salas que no existen y actualiza los datos de las que sí existen.
    2. Borra por completo todas las salidas existentes.
    3. Recrea todas las salidas basándose en las definiciones actuales.
    """
    logging.info("Sincronizando el mundo estático desde los prototipos...")
    try:
        # --- PASO 1: Sincronizar Salas ---
        # Se asegura de que todas las salas definidas en los prototipos existan en la BD
        # y actualiza su nombre/descripción. Guarda un mapa de `key` a `id` para el siguiente paso.
        room_key_to_id_map = {}

        # Obtenemos todas las salas existentes de la BD para compararlas.
        existing_rooms_query = await session.execute(select(Room))
        existing_rooms = {room.key: room for room in existing_rooms_query.scalars().all()}

        for key, data in ROOM_PROTOTYPES.items():
            room = existing_rooms.get(key)
            if not room:
                # La sala no existe en la BD, la creamos.
                logging.info(f"  -> Creando sala '{key}'...")
                room = Room(key=key, name=data['name'], description=data['description'])
                session.add(room)
            else:
                # La sala ya existe, actualizamos sus datos por si cambiaron.
                room.name = data['name']
                room.description = data['description']

            # `flush` envía los cambios a la BD sin cerrar la transacción, lo que
            # nos permite obtener el ID de las nuevas salas antes del commit final.
            await session.flush()
            room_key_to_id_map[key] = room.id

        # --- PASO 2: Limpiar Salidas Viejas ---
        # Es más simple y seguro borrar todas las salidas y recrearlas que intentar
        # parchear las existentes. Esto asegura que las salidas eliminadas de los
        # prototipos también se eliminen de la BD.
        logging.info("  -> Limpiando todas las salidas existentes para reconstruir...")
        await session.execute(delete(Exit))

        # --- PASO 3: Crear Salidas Nuevas ---
        # Itera de nuevo sobre los prototipos y crea las filas en la tabla `exits`.
        for key, data in ROOM_PROTOTYPES.items():
            from_room_id = room_key_to_id_map[key]
            for direction, to_room_key in data.get("exits", {}).items():
                if to_room_key in room_key_to_id_map:
                    to_room_id = room_key_to_id_map[to_room_key]

                    # Crear la salida principal (ej: A -> B, "norte")
                    exit_forward = Exit(name=direction.lower(), from_room_id=from_room_id, to_room_id=to_room_id)
                    session.add(exit_forward)

                    # Crear la salida de vuelta automáticamente (ej: B -> A, "sur")
                    opposite = OPPOSITE_DIRECTIONS.get(direction.lower())
                    if opposite:
                        exit_backward = Exit(name=opposite, from_room_id=to_room_id, to_room_id=from_room_id)
                        session.add(exit_backward)
                else:
                    logging.warning(f"  -> La sala de destino '{to_room_key}' definida en la sala '{key}' no existe. Se ignora la salida.")

        await session.commit()
        logging.info("¡Sincronización del mundo completada!")
    except Exception:
        # Un fallo aquí es crítico para el arranque del bot.
        logging.exception("Error fatal durante la sincronización del mundo.")
        # Relanzamos la excepción para que la función on_startup la capture y detenga el bot.
        raise