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

class CmdListarSalas(Command):
    """
    Comando que muestra una lista de todas las salas existentes en el mundo,
    incluyendo su ID, su clave de prototipo y su nombre.
    Soporta filtrado por categoría y tags.
    """
    names = ["listarsalas", "lsalas"]
    lock = "rol(ADMIN)"
    description = "Lista salas. Uso: /listarsalas [category:X] [tag:Y]"

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        """Ejecuta la consulta y formatea la lista de salas."""
        try:
            from src.services import tag_service

            all_rooms = []

            if not args:
                # Sin filtros, listar todas las salas
                result = await session.execute(select(Room).order_by(Room.id))
                all_rooms = result.scalars().all()
            else:
                # Parsear filtros
                category_filter = None
                tag_filters = []

                for arg in args:
                    if arg.startswith("category:"):
                        category_filter = arg.split(":", 1)[1]
                    elif arg.startswith("tag:"):
                        tag_filters.append(arg.split(":", 1)[1])

                # Ejecutar búsqueda
                if category_filter:
                    all_rooms = await tag_service.find_rooms_by_category(session, category_filter)
                elif tag_filters:
                    all_rooms = await tag_service.find_rooms_by_tags_all(session, tag_filters)
                else:
                    result = await session.execute(select(Room).order_by(Room.id))
                    all_rooms = result.scalars().all()

            if not all_rooms:
                await message.answer("No se encontraron salas con esos criterios.")
                return

            # 2. Construir el mensaje de respuesta línea por línea.
            response_lines = ["<b>Lista de Salas del Mundo:</b>"]
            for room in all_rooms[:30]:  # Límite de 30 salas
                # Agregar category y tags si existen
                category_str = f" [cat: {room.category}]" if room.category else ""
                tags_str = f" [tags: {', '.join(room.tags)}]" if room.tags else ""
                response_lines.append(f"ID: {room.id:<4} | Key: {room.key:<20} | {room.name}{category_str}{tags_str}")

            if len(all_rooms) > 30:
                response_lines.append(f"\n... y {len(all_rooms) - 30} salas más.")

            body = "\n".join(response_lines)

            # 3. Envolver el cuerpo completo en una etiqueta <pre> para asegurar
            #    un formato de monoespaciado y una alineación perfecta de las columnas.
            response_text = f"<pre>{body}</pre>"

            await message.answer(response_text, parse_mode="HTML")

        except Exception:
            # Captura cualquier error inesperado durante la consulta a la base de datos.
            await message.answer("❌ Ocurrió un error al intentar listar las salas.")
            logging.exception("Fallo al ejecutar /listarsalas")

class CmdExaminarSala(Command):
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

            # Construir información detallada
            response_lines = [
                f"<b>╔══ Información de Sala ══╗</b>",
                f"<b>ID:</b> {room.id}",
                f"<b>Key:</b> {room.key or 'N/A'}",
                f"<b>Nombre:</b> {room.name}",
                f"<b>Descripción:</b> {room.description[:100]}..." if len(room.description) > 100 else f"<b>Descripción:</b> {room.description}",
                f"<b>Locks:</b> {room.locks or 'Ninguno'}",
            ]

            # Salidas
            if room.exits_from:
                exits_info = []
                for exit_obj in room.exits_from:
                    exits_info.append(f"  • {exit_obj.name} → Sala ID {exit_obj.to_room_id}")
                response_lines.append(f"<b>Salidas:</b>\n" + "\n".join(exits_info))
            else:
                response_lines.append(f"<b>Salidas:</b> Ninguna")

            # Objetos en la sala
            if room.items:
                items_info = [f"  • {item.get_name()} (ID: {item.id})" for item in room.items]
                response_lines.append(f"<b>Objetos:</b> ({len(room.items)})\n" + "\n".join(items_info))
            else:
                response_lines.append(f"<b>Objetos:</b> Ninguno")

            # Personajes en la sala
            if room.characters:
                chars_info = [f"  • {char.name} (ID: {char.id})" for char in room.characters]
                response_lines.append(f"<b>Personajes:</b> ({len(room.characters)})\n" + "\n".join(chars_info))
            else:
                response_lines.append(f"<b>Personajes:</b> Ninguno")

            response_text = f"<pre>{chr(10).join(response_lines)}</pre>"
            await message.answer(response_text, parse_mode="HTML")

        except Exception:
            await message.answer("❌ Ocurrió un error al examinar la sala.")
            logging.exception(f"Fallo al ejecutar /examinarsala")


# Exportamos la lista de comandos de este módulo para que el dispatcher pueda importarla.
INFO_COMMANDS = [
    CmdListarSalas(),
    CmdExaminarSala(),
]