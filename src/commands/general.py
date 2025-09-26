# src/commands/general.py
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from src.commands.command import Command
from src.models.character import Character
from src.utils.presenters import show_current_room


class CmdLook(Command):
    names = ["mirar", "m"]
    lock = ""

    async def execute(
        self,
        character: Character,
        session: AsyncSession,
        message: types.Message,
        args: list[str]
    ):
        await show_current_room(message)


class CmdSay(Command):
    names = ["decir", "'"]
    lock = ""

    async def execute(
        self,
        character: Character,
        session: AsyncSession,
        message: types.Message,
        args: list[str]
    ):
        if not args:
            await message.answer("¿Qué quieres decir?")
            return

        say_text = " ".join(args)
        # Por ahora, solo le devolvemos el mensaje a él.
        # En el futuro, un broadcaster lo enviaría a todos en la sala.
        await message.answer(f"Dices: {say_text}")


class CmdInventory(Command):
    names = ["inventario", "inv", "i"]
    lock = ""

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
            items_list = [f" - {item.name}" for item in inventory]
            items_str = "\n".join(items_list)
            response = f"<b>Llevas lo siguiente:</b>\n{items_str}"

        await message.answer(f"<pre>{response}</pre>", parse_mode="HTML")


# --- Lista de Comandos para el CommandSet "General" ---
GENERAL_COMMANDS = [
    CmdLook(),
    CmdSay(),
    CmdInventory(),
]