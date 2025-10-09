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
            from src.utils.paginated_output import send_paginated_simple, parse_page_from_args

            # Obtener número de página
            page = parse_page_from_args(args, default=1)

            room = character.room
            items = room.items

            if not items:
                await message.answer(f"{ICONS['look']} No hay nada en el suelo aquí.")
                return

            # Función de formato para cada item
            def format_item(item):
                item_icon = item.prototype.get('display', {}).get('icon', ICONS['item'])
                return f"{item_icon} {item.get_name()}"

            # Enviar lista paginada con botones
            await send_paginated_simple(
                message=message,
                items=items,
                page=page,
                callback_action="pg_items",
                format_func=format_item,
                header=f"Todos los items en {room.name}",
                per_page=settings.pagination_items_per_page,
                icon=ICONS['look']
            )

        except Exception:
            await message.answer("❌ Ocurrió un error al listar los items.")
            logging.exception(f"Fallo al ejecutar /items para {character.name}")


class CmdCharacters(Command):
    """Comando para listar todos los personajes en la sala actual con paginación."""
    names = ["personajes"]
    description = "Muestra todos los personajes en la sala. Uso: /personajes [página]"
    lock = ""

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        try:
            from src.utils.paginated_output import send_paginated_simple, parse_page_from_args

            # Obtener número de página
            page = parse_page_from_args(args, default=1)

            room = character.room

            # Filtrar para excluir al personaje que está mirando y jugadores desconectados
            active_characters = []
            for char in room.characters:
                if char.id != character.id and await online_service.is_character_online(char.id):
                    active_characters.append(char)

            if not active_characters:
                await message.answer(f"{ICONS['character']} Estás solo aquí.")
                return

            # Ordenar por nombre
            active_characters.sort(key=lambda c: c.name)

            # Enviar lista paginada con botones
            await send_paginated_simple(
                message=message,
                items=active_characters,
                page=page,
                callback_action="pg_chars",
                format_func=lambda c: c.name,
                header=f"Personajes en {room.name}",
                per_page=settings.pagination_items_per_page,
                icon=ICONS['character']
            )

        except Exception:
            await message.answer("❌ Ocurrió un error al listar los personajes.")
            logging.exception(f"Fallo al ejecutar /personajes para {character.name}")


# Exportar comandos
LISTING_COMMANDS = [
    CmdItems(),
    CmdCharacters(),
]
