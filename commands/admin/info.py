# commands/admin/info.py
"""
Módulo de Comandos Administrativos de Información.

Este archivo contiene comandos diseñados para que los administradores puedan
consultar el estado interno del juego. Son herramientas de solo lectura
que ayudan a supervisar, depurar y obtener una visión general del mundo
sin modificarlo.

Ejemplos futuros podrían incluir: /donde [jugador], /infoobjeto [id], etc.
"""

import logging
from aiogram import types
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from commands.command import Command
from src.models import Character, Room

class CmdListRooms(Command):
    """
    Comando que muestra una lista de todas las salas existentes en el mundo,
    incluyendo su ID, su clave de prototipo y su nombre.
    Soporta filtrado por categoría y tags.
    """
    names = ["listarsalas", "lsalas"]
    lock = "rol(ADMIN)"
    description = "Lista salas. Uso: /listarsalas [cat:X] [tag:Y,Z]"

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        """Ejecuta la consulta y formatea la lista de salas."""
        try:
            from src.services import tag_service
            from src.utils.paginated_output import send_paginated_list, parse_page_from_args, remove_page_from_args

            # Remover página de args para parsear solo filtros
            filter_args = remove_page_from_args(args)
            page = parse_page_from_args(args, default=1)

            all_rooms = []
            category_filter = None
            tag_filters = []

            if not filter_args:
                # Sin filtros, listar todas las salas
                result = await session.execute(select(Room).order_by(Room.id))
                all_rooms = result.scalars().all()
            else:
                # Parsear filtros (sintaxis cat:X tag:Y,Z)
                for arg in filter_args:
                    if arg.startswith("cat:"):
                        category_filter = arg.split(":", 1)[1]
                    elif arg.startswith("tag:"):
                        # Soportar múltiples tags separados por coma
                        tags = arg.split(":", 1)[1].split(",")
                        tag_filters.extend([t.strip() for t in tags])

                # Ejecutar búsqueda
                if category_filter:
                    all_rooms = await tag_service.find_rooms_by_category(session, category_filter)
                elif tag_filters:
                    all_rooms = await tag_service.find_rooms_by_tags_all(session, tag_filters)
                else:
                    result = await session.execute(select(Room).order_by(Room.id))
                    all_rooms = result.scalars().all()

            # Preparar parámetros para callbacks (abreviados para caber en 64 bytes)
            callback_params = {}
            if category_filter:
                callback_params['c'] = category_filter
            if tag_filters:
                callback_params['t'] = ",".join(tag_filters)

            # Enviar lista paginada con template y botones
            await send_paginated_list(
                message=message,
                items=all_rooms,
                page=page,
                template_name='room_list.html.j2',
                callback_action="pg_rooms",
                per_page=30,
                filters=bool(filter_args),
                cat=category_filter,
                tags=tag_filters,
                **callback_params  # Para preservar en botones
            )

        except Exception:
            # Captura cualquier error inesperado durante la consulta a la base de datos.
            await message.answer("❌ Ocurrió un error al intentar listar las salas.")
            logging.exception("Fallo al ejecutar /listarsalas")

class CmdExamineRoom(Command):
    """
    Comando para examinar información detallada de una sala por ID o key.
    """
    names = ["examinarsala", "exsala"]
    lock = "rol(ADMIN)"
    description = "Examina una sala por ID o key. Uso: /examinarsala <id o key>"

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        """Examina una sala por ID numérico o key de prototipo."""
        try:
            if not args:
                await message.answer("Uso: /examinarsala <id o key>\nEjemplo: /examinarsala 1 o /examinarsala plaza_central")
                return

            search_term = " ".join(args).lower()

            # Intentar primero como ID numérico
            room = None
            if search_term.isdigit():
                room_id = int(search_term)
                result = await session.execute(select(Room).where(Room.id == room_id))
                room = result.scalar_one_or_none()

            # Si no se encontró por ID, buscar por key
            if not room:
                result = await session.execute(select(Room).where(Room.key == search_term))
                room = result.scalar_one_or_none()

            if not room:
                await message.answer(f"❌ No se encontró ninguna sala con ID o key '{search_term}'.")
                return

            # Cargar relaciones necesarias
            await session.refresh(room, ['exits_from', 'items', 'characters'])
            
            # Cargar relaciones de salidas para mostrar nombres
            for exit_obj in room.exits_from:
                await session.refresh(exit_obj, ['to_room'])
            
            # Verificar estado online de personajes
            from src.services import online_service
            for char in room.characters:
                char.is_online = await online_service.is_character_online(char.id)
            
            # Usar template compacto específico para admin
            from src.templates import render_template
            response_text = render_template('room_examine.html.j2', room=room)
            
            await message.answer(response_text, parse_mode="HTML")

        except Exception:
            await message.answer("❌ Ocurrió un error al examinar la sala.")
            logging.exception(f"Fallo al ejecutar /examinarsala")


# Exportamos la lista de comandos de este módulo para que el dispatcher pueda importarla.
INFO_COMMANDS = [
    CmdListRooms(),
    CmdExamineRoom(),
]