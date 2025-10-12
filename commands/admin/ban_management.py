# commands/admin/ban_management.py
"""
Módulo de Comandos Administrativos para la Gestión de Baneos.

Este archivo contiene comandos que permiten a los administradores gestionar el
sistema de baneos, incluyendo:
- Banear cuentas (permanente o temporal)
- Desbanear cuentas
- Listar cuentas baneadas con paginación
- Ver detalles de apelaciones

Todos estos comandos requieren permisos de ADMIN o superior.
"""

import logging
import math
from datetime import datetime, timedelta
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from commands.command import Command
from src.models import Character, Account
from src.services import ban_service
from src.services.permission_service import ROLE_HIERARCHY
from src.templates import ICONS
from src.config import settings


class CmdBan(Command):
    """
    Comando para banear una cuenta permanentemente o temporalmente.

    Uso:
    - /banear <nombre> <razón> - Ban permanente
    - /banear <nombre> <días> <razón> - Ban temporal por X días
    """
    names = ["banear", "ban"]
    lock = "rol(ADMIN)"
    description = "Banea una cuenta. Uso: /banear <nombre> <días?> <razón>"

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        if len(args) < 2:
            await message.answer(
                "Uso:\n"
                "• /banear <nombre> <razón> - Ban permanente\n"
                "• /banear <nombre> <días> <razón> - Ban temporal"
            )
            return

        target_name = args[0]

        # Intentar parsear segundo argumento como días
        ban_days = None
        reason_start_idx = 1

        try:
            ban_days = int(args[1])
            reason_start_idx = 2

            if ban_days <= 0:
                await message.answer("❌ El número de días debe ser mayor a 0.")
                return

            if len(args) < 3:
                await message.answer("❌ Debes proporcionar una razón para el ban temporal.")
                return

        except ValueError:
            # No es un número, entonces es parte de la razón
            ban_days = None
            reason_start_idx = 1

        reason = " ".join(args[reason_start_idx:])

        if not reason.strip():
            await message.answer("❌ Debes proporcionar una razón para el ban.")
            return

        try:
            # Buscar personaje por nombre (case-insensitive)
            query = select(Character).where(Character.name.ilike(target_name))
            result = await session.execute(query)
            target_char = result.scalar_one_or_none()

            if not target_char:
                await message.answer(f"❌ No se encontró un personaje con el nombre '{target_name}'.")
                return

            # Obtener cuenta del personaje
            target_account = await session.get(Account, target_char.account_id)
            if not target_account:
                await message.answer("❌ Error: El personaje no tiene una cuenta asociada.")
                return

            # Validación: No permitir banear a admins o superadmins
            target_role = target_account.role.upper()
            acting_role = character.account.role.upper()

            # Verificar jerarquía de roles
            if target_role in ROLE_HIERARCHY and acting_role in ROLE_HIERARCHY:
                if ROLE_HIERARCHY[target_role] >= ROLE_HIERARCHY.get(acting_role, 0):
                    await message.answer(f"❌ No puedes banear a un {target_role}.")
                    return

            # Calcular fecha de expiración si es ban temporal
            expires_at = None
            if ban_days:
                expires_at = datetime.utcnow() + timedelta(days=ban_days)

            # Aplicar el ban
            await ban_service.ban_account(
                session=session,
                character=target_char,
                reason=reason,
                banned_by_account_id=character.account_id,
                expires_at=expires_at
            )

            # Feedback al admin
            ban_type = f"temporal ({ban_days} días)" if ban_days else "permanente"
            expiry_info = f"\n<b>Expira:</b> {expires_at.strftime('%Y-%m-%d %H:%M UTC')}" if expires_at else ""

            await message.answer(
                f"✅ Cuenta de <b>{target_char.name}</b> baneada ({ban_type}).\n"
                f"<b>Razón:</b> {reason}{expiry_info}",
                parse_mode="HTML"
            )

            logging.info(
                f"Admin {character.name} (ID: {character.account_id}) baneó a "
                f"{target_char.name} (ID: {target_account.id}). "
                f"Tipo: {ban_type}. Razón: '{reason}'"
            )

        except ValueError as e:
            await message.answer(f"❌ {str(e)}")
        except Exception:
            await message.answer("❌ Ocurrió un error al intentar banear la cuenta.")
            logging.exception(f"Error al ejecutar /banear para '{target_name}'")


class CmdUnban(Command):
    """
    Comando para quitar el ban de una cuenta.
    """
    names = ["desbanear", "unban"]
    lock = "rol(ADMIN)"
    description = "Quita el ban de una cuenta. Uso: /desbanear <nombre>"

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        if len(args) != 1:
            await message.answer("Uso: /desbanear <nombre_personaje>")
            return

        target_name = args[0]

        try:
            # Buscar personaje por nombre
            query = select(Character).where(Character.name.ilike(target_name))
            result = await session.execute(query)
            target_char = result.scalar_one_or_none()

            if not target_char:
                await message.answer(f"❌ No se encontró un personaje con el nombre '{target_name}'.")
                return

            # Desbanear
            await ban_service.unban_account(session, target_char)

            await message.answer(f"✅ Cuenta de <b>{target_char.name}</b> desbaneada correctamente.", parse_mode="HTML")

            logging.info(
                f"Admin {character.name} (ID: {character.account_id}) desbaneó a "
                f"{target_char.name} (ID: {target_char.account_id})"
            )

        except ValueError as e:
            await message.answer(f"❌ {str(e)}")
        except Exception:
            await message.answer("❌ Ocurrió un error al intentar desbanear la cuenta.")
            logging.exception(f"Error al ejecutar /desbanear para '{target_name}'")


class CmdListBanned(Command):
    """
    Comando para listar todas las cuentas baneadas con paginación.
    """
    names = ["listabaneados", "bans", "banned"]
    lock = "rol(ADMIN)"
    description = "Lista cuentas baneadas. Uso: /listabaneados [página]"

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        # Parsear número de página
        page = 1
        if args:
            try:
                page = int(args[0])
                if page < 1:
                    page = 1
            except ValueError:
                await message.answer("❌ El número de página debe ser un número válido.")
                return

        try:
            # Obtener cuentas baneadas con paginación (usa config por defecto)
            banned_accounts, total_count = await ban_service.get_banned_accounts(
                session=session,
                page=page
                # per_page usa el default de settings.moderation_banned_accounts_per_page
            )

            per_page = settings.moderation_banned_accounts_per_page

            if total_count == 0:
                await message.answer("✅ No hay cuentas baneadas actualmente.")
                return

            # Calcular total de páginas
            total_pages = math.ceil(total_count / per_page)

            # Validar página
            if page > total_pages:
                await message.answer(f"❌ Solo hay {total_pages} página(s). Usa /listabaneados {total_pages}")
                return

            # Construir mensaje
            output = "<pre>"
            output += f"CUENTAS BANEADAS (Página {page}/{total_pages})\n"
            output += f"Total: {total_count}\n\n"

            for account in banned_accounts:
                # Nombre del personaje
                char_name = account.character.name if account.character else "Sin personaje"

                # Tipo de ban
                if account.ban_expires_at:
                    ban_type_icon = ICONS['temporary']
                    ban_type_label = "Temporal"
                else:
                    ban_type_icon = ICONS['permanent']
                    ban_type_label = "Permanente"

                # Admin que baneó
                banned_by_name = "Desconocido"
                if account.banned_by and account.banned_by.character:
                    banned_by_name = account.banned_by.character.name

                # Fecha del ban
                banned_date = account.banned_at.strftime('%Y-%m-%d') if account.banned_at else "N/A"

                # Indicador de apelación
                appeal_status = f" {ICONS['appeal']}" if account.has_appealed else ""

                output += f"    - {char_name} ({ban_type_icon} {ban_type_label}){appeal_status}\n"
                output += f"      Razón: {account.ban_reason}\n"
                output += f"      Por: {banned_by_name} | Fecha: {banned_date}\n"

                if account.ban_expires_at:
                    output += f"      Expira: {account.ban_expires_at.strftime('%Y-%m-%d %H:%M UTC')}\n"

                output += "\n"

            # Agregar navegación si hay múltiples páginas
            if total_pages > 1:
                output += "───────────────\n"
                if page > 1:
                    output += f"◀️ /listabaneados {page - 1}  "
                if page < total_pages:
                    output += f"▶️ /listabaneados {page + 1}"

            output += "</pre>"
            await message.answer(output, parse_mode="HTML")

        except Exception:
            await message.answer("❌ Ocurrió un error al obtener la lista de baneados.")
            logging.exception("Error al ejecutar /listabaneados")


class CmdViewAppeal(Command):
    """
    Comando para ver la apelación de un jugador baneado.
    """
    names = ["verapelacion", "verap"]
    lock = "rol(ADMIN)"
    description = "Ver apelación de un jugador. Uso: /verapelacion <nombre>"

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        if len(args) != 1:
            await message.answer("Uso: /verapelacion <nombre_personaje>")
            return

        target_name = args[0]

        try:
            # Buscar personaje por nombre
            query = select(Character).where(Character.name.ilike(target_name))
            result = await session.execute(query)
            target_char = result.scalar_one_or_none()

            if not target_char:
                await message.answer(f"❌ No se encontró un personaje con el nombre '{target_name}'.")
                return

            # Obtener información del ban
            ban_info = await ban_service.get_account_ban_info(session, target_char)

            if not ban_info["is_banned"]:
                await message.answer(f"❌ La cuenta de {target_char.name} no está baneada.")
                return

            if not ban_info["has_appealed"]:
                await message.answer(f"ℹ️ {target_char.name} aún no ha enviado una apelación.")
                return

            # Construir mensaje con información completa
            output = "<pre>"
            output += f"{ICONS['appeal']} APELACIÓN DE {target_char.name.upper()}\n\n"

            output += "INFORMACIÓN DEL BAN:\n"
            if ban_info["is_temporary"]:
                ban_type_icon = ICONS['temporary']
                ban_type = "Temporal"
            else:
                ban_type_icon = ICONS['permanent']
                ban_type = "Permanente"

            output += f"    - Tipo: {ban_type_icon} {ban_type}\n"
            output += f"    - Razón: {ban_info['reason']}\n"

            if ban_info["banned_by_name"]:
                output += f"    - Baneado por: {ban_info['banned_by_name']}\n"

            if ban_info["banned_at"]:
                output += f"    - Fecha: {ban_info['banned_at'].strftime('%Y-%m-%d %H:%M UTC')}\n"

            if ban_info["expires_at"]:
                output += f"    - Expira: {ban_info['expires_at'].strftime('%Y-%m-%d %H:%M UTC')}\n"

            output += "\nAPELACIÓN:\n"
            output += f"    - Fecha: {ban_info['appealed_at'].strftime('%Y-%m-%d %H:%M UTC')}\n"
            output += f"    - Texto:\n      {ban_info['appeal_text']}\n\n"
            output += "───────────────\n"
            output += f"Para desbanear: /desbanear {target_char.name}"
            output += "</pre>"

            await message.answer(output, parse_mode="HTML")

        except Exception:
            await message.answer("❌ Ocurrió un error al obtener la apelación.")
            logging.exception(f"Error al ejecutar /verapelacion para '{target_name}'")


# Exportar lista de comandos
BAN_MANAGEMENT_COMMANDS = [
    CmdBan(),
    CmdUnban(),
    CmdListBanned(),
    CmdViewAppeal(),
]
