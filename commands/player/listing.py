# commands/player/listing.py
"""
Módulo de Comandos de Listados Completos.

Este archivo contiene comandos dedicados para mostrar listas completas de elementos
con soporte de paginación, permitiendo a los jugadores explorar listas largas de
forma eficiente en dispositivos móviles.
"""

import logging
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from commands.command import Command
from src.models import Character
from src.utils.pagination import paginate_list, format_pagination_footer
from src.templates import ICONS
from src.services import online_service
from src.config import settings


class CmdItems(Command):
    """Comando para listar todos los items de la sala actual con paginación."""
    names = ["items"]
    description = "Muestra todos los items de la sala. Uso: /items [página]"
    lock = ""

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        try:
            # Obtener número de página
            page = 1
            if args:
                try:
                    page = int(args[0])
                except ValueError:
                    await message.answer("Uso: /items [número de página]")
                    return

            room = character.room
            items = room.items

            if not items:
                await message.answer(f"<pre>{ICONS['look']} No hay nada en el suelo aquí.</pre>", parse_mode="HTML")
                return

            # Paginar items
            pagination = paginate_list(items, page=page, per_page=settings.pagination_items_per_page)

            # Construir output
            lines = [
                f"{ICONS['look']} <b>Todos los items en {room.name}</b>",
                "─────────────────────────────"
            ]

            for idx, item in enumerate(pagination['items'], start=pagination['start_index']):
                item_icon = item.prototype.get('display', {}).get('icon', ICONS['item'])
                item_name = item.get_name()
                lines.append(f"{idx}. {item_icon} {item_name}")

            # Agregar footer de paginación
            if pagination['total_pages'] > 1:
                lines.append(format_pagination_footer(
                    pagination['page'],
                    pagination['total_pages'],
                    '/items',
                    pagination['total_items']
                ))

            output = "<pre>" + "\n".join(lines) + "</pre>"
            await message.answer(output, parse_mode="HTML")

        except Exception:
            await message.answer("❌ Ocurrió un error al listar los items.")
            logging.exception(f"Fallo al ejecutar /items para {character.name}")


class CmdPersonajes(Command):
    """Comando para listar todos los personajes en la sala actual con paginación."""
    names = ["personajes"]
    description = "Muestra todos los personajes en la sala. Uso: /personajes [página]"
    lock = ""

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        try:
            # Obtener número de página
            page = 1
            if args:
                try:
                    page = int(args[0])
                except ValueError:
                    await message.answer("Uso: /personajes [número de página]")
                    return

            room = character.room

            # Filtrar para excluir al personaje que está mirando y jugadores desconectados
            active_characters = []
            for char in room.characters:
                if char.id != character.id and await online_service.is_character_online(char.id):
                    active_characters.append(char)

            if not active_characters:
                await message.answer(f"<pre>{ICONS['character']} Estás solo aquí.</pre>", parse_mode="HTML")
                return

            # Ordenar por nombre
            active_characters.sort(key=lambda c: c.name)

            # Paginar personajes
            pagination = paginate_list(active_characters, page=page, per_page=settings.pagination_items_per_page)

            # Construir output
            lines = [
                f"{ICONS['character']} <b>Personajes en {room.name}</b>",
                "─────────────────────────────"
            ]

            for idx, char in enumerate(pagination['items'], start=pagination['start_index']):
                lines.append(f"{idx}. {char.name}")

            # Agregar footer de paginación
            if pagination['total_pages'] > 1:
                lines.append(format_pagination_footer(
                    pagination['page'],
                    pagination['total_pages'],
                    '/personajes',
                    pagination['total_items']
                ))

            output = "<pre>" + "\n".join(lines) + "</pre>"
            await message.answer(output, parse_mode="HTML")

        except Exception:
            await message.answer("❌ Ocurrió un error al listar los personajes.")
            logging.exception(f"Fallo al ejecutar /personajes para {character.name}")


# Exportar comandos
LISTING_COMMANDS = [
    CmdItems(),
    CmdPersonajes(),
]
