# commands/player/character.py
"""
Módulo de Comandos para la Gestión del Personaje.

Este archivo contiene los comandos que permiten a los jugadores gestionar
el ciclo de vida de su personaje en el juego.

Comandos disponibles:
- `/crearpersonaje`: Crea un nuevo personaje (primer comando para nuevos jugadores)
- `/suicidio`: Elimina permanentemente el personaje actual
"""

import logging
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from commands.command import Command
from src.models.character import Character
from src.services import player_service, command_service

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
            await message.answer(
                "❌ Ya tienes un personaje creado.\n"
                "Si quieres eliminarlo y crear uno nuevo, usa: /suicidio CONFIRMAR"
            )
            return

        # 2. Validar el nombre proporcionado por el usuario.
        character_name = " ".join(args)
        if not character_name or len(character_name) > 50:
            await message.answer("Por favor, proporciona un nombre válido (máx 50 caracteres). Uso: /crearpersonaje [nombre]")
            return

        try:
            # 3. Llamar al servicio que contiene la lógica de negocio para la creación.
            new_char = await player_service.create_character(session, message.from_user.id, character_name)

            # 3.1. Marcar el personaje como online inmediatamente
            from src.services import online_service
            await online_service.update_last_seen(session, new_char)

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


class CmdSuicide(Command):
    """
    Comando para que un jugador elimine permanentemente su personaje.

    ⚠️ ADVERTENCIA: Esta acción es IRREVERSIBLE y eliminará:
    - El personaje y su nombre
    - Todo su inventario
    - Todas sus configuraciones
    - Cualquier progreso en el juego

    Requiere confirmación explícita mediante el argumento "CONFIRMAR".
    """
    names = ["suicidio", "borrarpersonaje", "eliminarpersonaje"]
    description = "Elimina permanentemente tu personaje (irreversible)."
    lock = ""

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        """
        Gestiona la eliminación permanente del personaje actual.

        Requiere que el jugador escriba "CONFIRMAR" para evitar eliminaciones accidentales.
        """
        # 1. Verificar que el jugador tiene un personaje
        if not character:
            await message.answer("No tienes un personaje que eliminar.")
            return

        # 2. Verificar confirmación
        confirmation = " ".join(args).upper()
        if confirmation != "CONFIRMAR":
            await message.answer(
                "⚠️ <b>ADVERTENCIA: Esta acción es IRREVERSIBLE</b>\n\n"
                f"Estás a punto de eliminar permanentemente a <b>{character.name}</b>.\n\n"
                "Esto eliminará:\n"
                "• Tu personaje y su nombre\n"
                "• Todo tu inventario\n"
                "• Todas tus configuraciones\n"
                "• Todo tu progreso en el juego\n\n"
                "Si estás seguro de que quieres hacer esto, escribe:\n"
                "<code>/suicidio CONFIRMAR</code>",
                parse_mode="HTML"
            )
            return

        # 3. Guardar información antes de eliminar
        character_name = character.name
        account = character.account

        try:
            # 4. Eliminar el personaje
            await player_service.delete_character(session, character)

            # 5. Actualizar comandos de Telegram (sin personaje ya solo puede crear)
            # Para hacer esto, necesitamos obtener la cuenta actualizada
            from src.services import player_service as ps
            updated_account = await ps.get_or_create_account(session, message.from_user.id)

            if updated_account.character is None:
                # Actualizar comandos para reflejar que no hay personaje
                await command_service.update_telegram_commands(None, updated_account)

            # 6. Actualizar comandos de Telegram para mostrar /crearpersonaje
            from src.services import command_service
            await command_service.update_telegram_commands(account=character.account)

            # 7. Enviar confirmación
            await message.answer(
                f"💀 <b>{character_name}</b> ha sido eliminado permanentemente.\n\n"
                "Tu cuenta sigue activa, pero ya no tienes un personaje.\n\n"
                "Para volver a jugar, crea un nuevo personaje con:\n"
                "<code>/crearpersonaje [nombre]</code>",
                parse_mode="HTML"
            )

        except RuntimeError as e:
            # Error durante la eliminación
            await message.answer(
                "❌ Ocurrió un error al intentar eliminar tu personaje.\n"
                "Por favor, contacta a un administrador."
            )
            logging.error(f"Error en /suicidio para {character_name}: {e}")
        except Exception:
            # Error inesperado
            await message.answer(
                "❌ Ocurrió un error inesperado.\n"
                "Tu personaje podría no haber sido eliminado. Por favor, contacta a un administrador."
            )
            logging.exception(f"Error inesperado en /suicidio para {character_name}")


# Exportamos la lista de comandos de este módulo.
CHARACTER_COMMANDS = [
    CmdCreateCharacter(),
    CmdSuicide(),
]