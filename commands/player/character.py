# commands/player/character.py
"""
Módulo de Comandos para la Gestión del Personaje.

Este archivo contiene los comandos que permiten a los jugadores gestionar
el ciclo de vida de su personaje en el juego.

El comando principal aquí es `/crearpersonaje`, que es el primer comando que
un nuevo jugador debe usar para entrar al mundo de Runegram.

Futuros comandos como `/borrarpersonaje` o `/descripcion` también pertenecerían
a este módulo.
"""

import logging
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from commands.command import Command
from src.models.character import Character
from src.services import player_service

class CmdCreateCharacter(Command):
    """
    Comando para que un nuevo usuario cree su personaje.
    """
    names = ["crearpersonaje"]
    description = "Crea tu personaje para empezar a jugar."
    lock = ""

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        """
        Gestiona la lógica de creación de un nuevo personaje.
        """
        # 1. Comprobar si el jugador ya tiene un personaje.
        # El objeto 'character' solo es None si la cuenta no tiene un personaje asociado.
        if character:
            await message.answer("Ya tienes un personaje.")
            return

        # 2. Validar el nombre proporcionado por el usuario.
        character_name = " ".join(args)
        if not character_name or len(character_name) > 50:
            await message.answer("Por favor, proporciona un nombre válido (máx 50 caracteres). Uso: /crearpersonaje [nombre]")
            return

        try:
            # 3. Llamar al servicio que contiene la lógica de negocio para la creación.
            new_char = await player_service.create_character(session, message.from_user.id, character_name)

            # 4. Enviar un mensaje de éxito al jugador.
            await message.answer(
                f"¡Tu personaje, {new_char.name}, ha sido creado con éxito!\n"
                "Ahora estás listo para explorar el mundo de Runegram. ¡Envía /start para comenzar!"
            )
        except ValueError as e:
            # Captura errores de negocio específicos lanzados por `player_service`,
            # como "El nombre ya está en uso".
            await message.answer(f"No se pudo crear el personaje: {e}")
        except Exception:
            # Captura cualquier otro error inesperado durante el proceso de creación.
            # Gracias al `logging.exception`, veremos el traceback completo en los logs
            # del contenedor, lo que es vital para depurar errores sutiles de la base de datos.
            await message.answer("Ocurrió un error inesperado al crear tu personaje.")
            logging.exception(f"Error finalizando la creación del personaje para {message.from_user.id}")

# Exportamos la lista de comandos de este módulo.
CHARACTER_COMMANDS = [
    CmdCreateCharacter(),
]