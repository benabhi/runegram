# src/commands/player/character.py
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from commands.command import Command
from src.models.character import Character
from src.services import player_service

class CmdCreateCharacter(Command):
    names = ["crearpersonaje"]
    lock = ""

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        if character:
            return await message.answer("Ya tienes un personaje.")

        character_name = " ".join(args)
        if not character_name or len(character_name) > 50:
            return await message.answer("Por favor, proporciona un nombre válido (máx 50 caracteres). Uso: /crearpersonaje [nombre]")

        try:
            new_char = await player_service.create_character(session, message.from_user.id, character_name)
            await message.answer(
                f"¡Tu personaje, {new_char.name}, ha sido creado con éxito!\n"
                "Ahora estás listo para explorar el mundo de Runegram. ¡Envía /start para comenzar!"
            )
        except ValueError as e:
            await message.answer(f"No se pudo crear el personaje: {e}")
        except Exception as e:
            await message.answer("Ocurrió un error inesperado al crear tu personaje.")
            print(f"Error en CmdCreateCharacter: {e}")

# --- Exportación del Command Set ---
CHARACTER_COMMANDS = [CmdCreateCharacter()]