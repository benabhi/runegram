# commands/player/appeal.py
"""
Módulo del Comando de Apelación de Ban.

Este archivo contiene el comando que permite a los jugadores baneados
enviar UNA apelación para solicitar la revisión de su bloqueo.

El comando está disponible para cualquier usuario, pero solo funciona si:
- La cuenta está actualmente baneada
- No ha apelado anteriormente (solo se permite una apelación)

Cuando se envía una apelación, se notifica automáticamente a los administradores:
- Si hay un canal configurado en gameconfig.toml (moderation.ban_appeal_channel),
  se envía la notificación a ese canal.
- Si no hay canal configurado o está vacío, se envía mensaje directo a todos
  los administradores (ADMIN y SUPERADMIN) online.
"""

import logging
from aiogram import types
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from commands.command import Command
from src.models import Character, Account
from src.services import ban_service, channel_service, player_service
from src.templates import ICONS
from src.config import settings
from src.bot.bot import bot
from game_data.channel_prototypes import CHANNEL_PROTOTYPES


async def _notify_admins_of_appeal(
    session: AsyncSession,
    player_name: str,
    appeal_text: str,
    character: Character = None
) -> None:
    """
    Notifica a los administradores sobre una nueva apelación de ban.

    Dependiendo de la configuración en gameconfig.toml:
    - Si hay un canal configurado (moderation.ban_appeal_channel), envía al canal
    - Si no hay canal o está vacío, envía mensaje directo a todos los admins

    Args:
        session: Sesión de base de datos activa
        player_name: Nombre del jugador que apeló
        appeal_text: Texto de la apelación
        character: Personaje del jugador (puede ser None)
    """
    # Construir mensaje de notificación (sin <pre>, es notificación privada/directa)
    notification = (
        f"{ICONS['appeal']} <b>Nueva apelación de ban</b>\n\n"
        f"<b>Jugador:</b> {player_name}\n"
        f"<b>Ver detalles:</b> /verapelacion {player_name if character else 'N/A'}\n\n"
        f"<i>Fragmento:</i> {appeal_text[:100]}..."
    )

    # Leer configuración del canal
    channel_key = settings.moderation_ban_appeal_channel

    # Si hay canal configurado y existe en prototipos, usar canal
    if channel_key and channel_key in CHANNEL_PROTOTYPES:
        try:
            await channel_service.broadcast_to_channel(
                session=session,
                channel_key=channel_key,
                message=notification
            )
            logging.info(f"Notificación de apelación enviada al canal '{channel_key}'")
            return
        except Exception:
            logging.exception(f"Error al enviar notificación al canal '{channel_key}', usando fallback")
            # Si falla, continuar con el fallback de mensajes directos

    # Fallback: Enviar mensaje directo a todos los administradores
    try:
        # Obtener todas las cuentas con rol ADMIN o SUPERADMIN
        query = select(Account).where(Account.role.in_(["ADMIN", "SUPERADMIN"]))
        result = await session.execute(query)
        admin_accounts = result.scalars().all()

        if not admin_accounts:
            logging.warning("No se encontraron administradores para notificar apelación")
            return

        # Enviar mensaje directo a cada admin
        sent_count = 0
        for admin_account in admin_accounts:
            try:
                await bot.send_message(
                    chat_id=admin_account.telegram_id,
                    text=notification,
                    parse_mode="HTML"
                )
                sent_count += 1
            except Exception as e:
                logging.warning(
                    f"No se pudo enviar notificación al admin {admin_account.telegram_id}: {e}"
                )

        logging.info(
            f"Notificación de apelación enviada directamente a {sent_count}/{len(admin_accounts)} admins"
        )

    except Exception:
        logging.exception("Error al notificar admins sobre apelación")


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

            # Notificar a admins según configuración
            char_name = character.name if character else f"Usuario {account.telegram_id}"
            await _notify_admins_of_appeal(session, char_name, appeal_text, character)

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
