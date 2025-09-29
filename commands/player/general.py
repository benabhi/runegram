# src/commands/player/general.py
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from commands.command import Command
from src.models.character import Character
from src.utils.presenters import show_current_room

class CmdLook(Command):
    names = ["mirar", "m", "l"]
    lock = ""

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        await show_current_room(message)

class CmdSay(Command):
    names = ["decir", "'"]
    lock = ""

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        if not args:
            return await message.answer("¿Qué quieres decir?")
        say_text = " ".join(args)
        await message.answer(f"Dices: {say_text}")

class CmdInventory(Command):
    names = ["inventario", "inv", "i"]
    lock = ""

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        inventory = character.items
        if not inventory:
            response = "No llevas nada."
        else:
            items_list = [f" - {item.name}" for item in inventory]
            items_str = "\n".join(items_list)
            response = f"<b>Llevas lo siguiente:</b>\n{items_str}"
        await message.answer(f"<pre>{response}</pre>", parse_mode="HTML")

class CmdHelp(Command):
    names = ["ayuda", "help"]
    lock = ""

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        help_text = (
            "<b>Comandos Básicos de Runegram</b>\n"
            "---------------------------------\n"
            "/mirar - Muestra la descripción de tu entorno.\n"
            "/inventario - Muestra los objetos que llevas.\n"
            "/decir [mensaje] - Hablas a la gente en tu misma sala.\n"
            "/coger [objeto] - Recoges un objeto del suelo.\n"
            "/dejar [objeto] - Dejas un objeto que llevas.\n\n"
            "Para moverte, usa /norte, /sur, etc."
        )
        await message.answer(f"<pre>{help_text}</pre>", parse_mode="HTML")

# --- Exportación del Command Set ---
GENERAL_COMMANDS = [CmdLook(), CmdSay(), CmdInventory(), CmdHelp()]