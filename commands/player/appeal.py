# commands/player/appeal.py
"""
Módulo del Comando de Apelación de Ban.

Este archivo contiene el comando que permite a los jugadores baneados
enviar UNA apelación para solicitar la revisión de su bloqueo.

El comando está disponible para cualquier usuario, pero solo funciona si:
- La cuenta está actualmente baneada
- No ha apelado anteriormente (solo se permite una apelación)

Cuando se envía una apelación, se notifica automáticamente a los administradores
en el canal de sistema.
"""

import logging
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from commands.command import Command
from src.models import Character
from src.services import ban_service, channel_service, player_service
from src.templates import ICONS


class CmdAppeal(Command):
    """
    Comando para apelar un ban de cuenta.

    Solo se permite UNA apelación por cuenta. Una vez enviada, el jugador
    debe esperar a que los administradores la revisen.

    Uso: /apelar <explicación de por qué debería ser desbaneado>
    """
    names = ["apelar", "appeal"]
    lock = ""  # Sin lock - cualquiera puede intentar apelar
    description = "Apelar un ban de cuenta (solo una vez)"

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        # Obtener cuenta (siempre debe existir porque dispatcher lo garantiza)
        account = await player_service.get_or_create_account(session, message.from_user.id)
        if not account:
            await message.answer("❌ Error al acceder a tu cuenta.")
            return

        # Validación: debe proporcionar texto de apelación
        if not args:
            await message.answer(
                "Uso: /apelar <tu explicación>\n\n"
                "Explica por qué crees que deberías ser desbaneado. "
                "Solo tienes UNA oportunidad de apelar."
            )
            return

        appeal_text = " ".join(args)

        try:
            # Intentar enviar apelación (el servicio validará todo)
            await ban_service.submit_appeal(
                session=session,
                account=account,
                appeal_text=appeal_text
            )

            # Confirmar al jugador
            await message.answer(
                "✅ <b>Tu apelación ha sido enviada correctamente.</b>\n\n"
                "Los administradores la revisarán pronto. Por favor, ten paciencia.\n\n"
                "⚠️ Recuerda: solo puedes apelar UNA vez.",
                parse_mode="HTML"
            )

            # Notificar a admins en canal de sistema
            char_name = character.name if character else f"Usuario {account.telegram_id}"

            notification = (
                f"{ICONS['appeal']} <b>Nueva apelación de ban</b>\n\n"
                f"<b>Jugador:</b> {char_name}\n"
                f"<b>Ver detalles:</b> /verapelacion {char_name if character else 'N/A'}\n\n"
                f"<i>Fragmento:</i> {appeal_text[:100]}..."
            )

            await channel_service.broadcast_to_channel(
                session=session,
                channel_key="sistema",
                message=notification
            )

            logging.info(f"Apelación enviada por {char_name} (Account ID: {account.id})")

        except ValueError as e:
            # Errores de validación (no está baneado, ya apeló, etc.)
            await message.answer(f"❌ {str(e)}")

        except Exception:
            await message.answer("❌ Ocurrió un error al enviar tu apelación. Intenta de nuevo más tarde.")
            logging.exception(f"Error al procesar apelación de Account ID {account.id}")


# Exportar lista de comandos
APPEAL_COMMANDS = [
    CmdAppeal(),
]
