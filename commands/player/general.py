# commands/player/general.py
from aiogram import types
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from commands.command import Command
from src.models.character import Character
from src.utils.presenters import show_current_room
from src.services import script_service, online_service

class CmdLook(Command):
    names = ["mirar", "m", "l"]
    lock = ""
    description = "Observa tu entorno o un objeto/personaje específico."

    async def execute(
        self,
        character: Character,
        session: AsyncSession,
        message: types.Message,
        args: list[str]
    ):
        if not args:
            await show_current_room(message)
            return

        target_name = " ".join(args).lower()
        found_target = None

        for item in character.room.items:
            if target_name in item.get_keywords() or target_name in item.get_name().lower():
                found_target = item
                break

        if not found_target:
            for item in character.items:
                if target_name in item.get_keywords() or target_name in item.get_name().lower():
                    found_target = item
                    break

        if not found_target:
            return await message.answer("No ves eso por aquí.")

        await message.answer(f"<pre>{found_target.get_description()}</pre>", parse_mode="HTML")

        if "on_look" in found_target.prototype.get("scripts", {}):
            await script_service.execute_script(
                script_string=found_target.prototype["scripts"]["on_look"],
                session=session,
                character=character,
                target=found_target
            )

class CmdSay(Command):
    names = ["decir", "'"]
    lock = ""
    description = "Habla con las personas que están en tu misma sala."

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        if not args:
            return await message.answer("¿Qué quieres decir?")
        say_text = " ".join(args)
        await message.answer(f"Dices: {say_text}")

class CmdInventory(Command):
    names = ["inventario", "inv", "i"]
    lock = ""
    description = "Muestra los objetos que llevas en tu inventario."

    async def execute(
        self,
        character: Character,
        session: AsyncSession,
        message: types.Message,
        args: list[str]
    ):
        inventory = character.items
        if not inventory:
            response = "No llevas nada."
        else:
            items_list = [f" - {item.get_name()}" for item in inventory]
            items_str = "\n".join(items_list)
            response = f"<b>Llevas lo siguiente:</b>\n{items_str}"

        await message.answer(f"<pre>{response}</pre>", parse_mode="HTML")

class CmdHelp(Command):
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
            "/quien - Muestra quién está conectado.\n\n"
            "Para moverte, usa /norte, /sur, etc."
        )
        await message.answer(f"<pre>{help_text}</pre>", parse_mode="HTML")

class CmdWho(Command):
    names = ["quien", "who"]
    lock = ""
    description = "Muestra una lista de los jugadores conectados."

    async def execute(
        self,
        character: Character,
        session: AsyncSession,
        message: types.Message,
        args: list[str]
    ):
        """Muestra una lista de los jugadores actualmente en línea."""

        online_characters = await online_service.get_online_characters(session)

        if not online_characters:
            return await message.answer("Eres la única alma aventurera en este mundo ahora mismo.")

        # Excluimos al propio jugador de la cuenta si solo hay una persona
        if len(online_characters) == 1 and online_characters[0].id == character.id:
            return await message.answer("Eres la única alma aventurera en este mundo ahora mismo.")

        response_lines = [f"<b>Hay {len(online_characters)} aventureros en Runegram:</b>"]
        for char in sorted(online_characters, key=lambda c: c.name):
            response_lines.append(f"- {char.name}")

        response_text = "\n".join(response_lines)
        await message.answer(f"<pre>{response_text}</pre>", parse_mode="HTML")


# --- Exportación del Command Set (Actualizado) ---
GENERAL_COMMANDS = [CmdLook(), CmdSay(), CmdInventory(), CmdHelp(), CmdWho()]