# commands/player/general.py
"""
Módulo de Comandos Generales del Jugador.

Este archivo agrupa los comandos más básicos y fundamentales que un jugador
utiliza para interactuar con el mundo y obtener información esencial sobre su
entorno y su personaje.

Estos comandos están disponibles para todos los jugadores en todo momento.
"""

import logging
from aiogram import types
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from commands.command import Command
from src.models.character import Character
from src.utils.presenters import show_current_room
from src.services import script_service, online_service

class CmdLook(Command):
    """
    Comando para observar el entorno actual (la sala) o un objeto o
    personaje específico dentro de ella.
    """
    names = ["mirar", "m", "l"]
    lock = ""
    description = "Observa tu entorno o un objeto/personaje específico."

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        try:
            # Si no se proporcionan argumentos, el jugador mira la sala.
            if not args:
                await show_current_room(message)
                return

            target_name = " ".join(args).lower()
            found_target = None

            # 1. Buscar en los objetos de la sala.
            if character.room.items:
                for item in character.room.items:
                    if target_name in item.get_keywords() or target_name in item.get_name().lower():
                        found_target = item
                        break

            # 2. Si no se encontró, buscar en el inventario del personaje.
            if not found_target and character.items:
                for item in character.items:
                    if target_name in item.get_keywords() or target_name in item.get_name().lower():
                        found_target = item
                        break

            # Futuro: 3. Buscar otros personajes en la sala.
            # Futuro: 4. Buscar NPCs en la sala.

            if not found_target:
                await message.answer("No ves eso por aquí.")
                return

            # Mostramos la descripción del objeto encontrado.
            await message.answer(f"<pre>{found_target.get_description()}</pre>", parse_mode="HTML")

            # Finalmente, disparamos el evento on_look si el objeto tiene un script asociado.
            if "on_look" in found_target.prototype.get("scripts", {}):
                await script_service.execute_script(
                    script_string=found_target.prototype["scripts"]["on_look"],
                    session=session,
                    character=character,
                    target=found_target
                )
        except Exception:
            await message.answer("❌ Ocurrió un error al intentar mirar.")
            logging.exception(f"Fallo al ejecutar /mirar para {character.name}")

class CmdSay(Command):
    """
    Comando para que el personaje hable a otros en la misma sala.
    """
    names = ["decir", "'"]
    lock = ""
    description = "Habla con las personas que están en tu misma sala."

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        if not args:
            await message.answer("¿Qué quieres decir?")
            return

        # Futuro: Este mensaje debería ser transmitido a otros jugadores en la sala.
        say_text = " ".join(args)
        await message.answer(f"Dices: {say_text}")

class CmdInventory(Command):
    """
    Comando para mostrar al jugador los objetos que lleva en su inventario.
    """
    names = ["inventario", "inv", "i"]
    lock = ""
    description = "Muestra los objetos que llevas en tu inventario."

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        try:
            inventory = character.items
            if not inventory:
                response = "No llevas nada."
            else:
                items_list = [f" - {item.get_name()}" for item in inventory]
                items_str = "\n".join(items_list)
                response = f"<b>Llevas lo siguiente:</b>\n{items_str}"

            await message.answer(f"<pre>{response}</pre>", parse_mode="HTML")
        except Exception:
            await message.answer("❌ Ocurrió un error al mostrar tu inventario.")
            logging.exception(f"Fallo al ejecutar /inventario para {character.name}")

class CmdHelp(Command):
    """
    Comando para mostrar un mensaje de ayuda básico con los comandos principales.
    """
    names = ["ayuda", "help"]
    lock = ""
    description = "Muestra una lista con los comandos básicos del juego."

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        help_text = (
            "<b>Comandos Básicos de Runegram</b>\n"
            "---------------------------------\n"
            "/mirar - Muestra la descripción de tu entorno.\n"
            "/inventario - Muestra los objetos que llevas.\n"
            "/decir [mensaje] - Hablas a la gente en tu misma sala.\n"
            "/coger [objeto] - Recoges un objeto del suelo.\n"
            "/dejar [objeto] - Dejas un objeto que llevas.\n"
            "/quien - Muestra quién está conectado.\n"
            "/canales - Gestiona tus suscripciones a canales.\n\n"
            "Para moverte, usa /norte, /sur, etc."
        )
        await message.answer(f"<pre>{help_text}</pre>", parse_mode="HTML")

class CmdWho(Command):
    """
    Comando social que muestra una lista de todos los personajes que
    están actualmente conectados al juego.
    """
    names = ["quien", "who"]
    lock = ""
    description = "Muestra una lista de los jugadores conectados."

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        try:
            online_characters = await online_service.get_online_characters(session)

            # Si la lista está vacía o solo contiene al jugador actual, se muestra
            # un mensaje indicando que está solo.
            if not online_characters or (len(online_characters) == 1 and online_characters[0].id == character.id):
                await message.answer("Eres la única alma aventurera en este mundo ahora mismo.")
                return

            response_lines = [f"<b>Hay {len(online_characters)} aventureros en Runegram:</b>"]
            # Ordenamos la lista alfabéticamente por nombre para una visualización clara.
            for char in sorted(online_characters, key=lambda c: c.name):
                response_lines.append(f"- {char.name}")

            response_text = "\n".join(response_lines)
            await message.answer(f"<pre>{response_text}</pre>", parse_mode="HTML")
        except Exception:
            await message.answer("❌ Ocurrió un error al obtener la lista de jugadores.")
            logging.exception(f"Fallo al ejecutar /quien para {character.name}")

# Exportamos la lista de comandos de este módulo.
GENERAL_COMMANDS = [
    CmdLook(),
    CmdSay(),
    CmdInventory(),
    CmdHelp(),
    CmdWho(),
]