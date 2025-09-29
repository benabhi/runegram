# src/commands/player/general.py
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from commands.command import Command
from src.models.character import Character
from src.utils.presenters import show_current_room
from src.services import script_service

class CmdLook(Command):
    names = ["mirar", "m", "l"]
    lock = ""

    async def execute(
        self,
        character: Character,
        session: AsyncSession,
        message: types.Message,
        args: list[str]
    ):
        # Si no hay argumentos, simplemente miramos la sala.
        if not args:
            await show_current_room(message)
            # Disparamos el evento on_look de la sala (futuro)
            return

        target_name = " ".join(args).lower()
        found_target = None

        # 1. Buscar en los objetos de la sala
        for item in character.room.items:
            if target_name in item.get_keywords() or target_name in item.get_name().lower():
                found_target = item
                break

        # 2. Si no se encontró, buscar en el inventario del personaje
        if not found_target:
            for item in character.items:
                if target_name in item.get_keywords() or target_name in item.get_name().lower():
                    found_target = item
                    break

        # Futuro: 3. Buscar otros personajes en la sala
        # Futuro: 4. Buscar NPCs en la sala

        if not found_target:
            return await message.answer("No ves eso por aquí.")

        # Mostramos la descripción del objeto encontrado.
        await message.answer(f"<pre>{found_target.get_description()}</pre>", parse_mode="HTML")

        # DISPARAMOS EL EVENTO ON_LOOK
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