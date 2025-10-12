# src/services/ban_service.py
"""
Módulo de Servicio para la Gestión de Baneos y Apelaciones.

Este servicio encapsula toda la lógica de negocio relacionada con el sistema de
baneos de cuentas, incluyendo:
- Baneos permanentes y temporales
- Sistema de apelaciones (una oportunidad por cuenta)
- Verificación automática de expiración de baneos
- Auditoría completa (quién, cuándo, por qué)

Responsabilidades:
1. Banear y desbanear cuentas con validaciones robustas
2. Gestionar apelaciones de ban con límite de una por cuenta
3. Verificar estado de ban considerando expiración temporal
4. Proporcionar listados paginados de cuentas baneadas
5. Logging exhaustivo de todas las operaciones para auditoría
"""

import logging
from datetime import datetime
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.account import Account
from src.models.character import Character
from src.config import settings


async def is_account_banned(session: AsyncSession, account: Account) -> bool:
    """
    Verifica si una cuenta está actualmente baneada.

    Considera baneos temporales: si ban_expires_at existe y ha pasado,
    automáticamente desbanea la cuenta.

    Args:
        session: Sesión de base de datos activa
        account: Cuenta a verificar

    Returns:
        True si la cuenta está baneada, False en caso contrario
    """
    try:
        # Si no está marcada como baneada, retornar False directamente
        if not account.is_banned:
            return False

        # Verificar si el ban ha expirado (baneos temporales)
        if account.ban_expires_at:
            now = datetime.utcnow()
            if now >= account.ban_expires_at:
                # El ban ha expirado, desbanear automáticamente
                logging.info(
                    f"Ban expirado para cuenta {account.id}. "
                    f"Fecha de expiración: {account.ban_expires_at}. "
                    "Desbaneando automáticamente."
                )
                await _auto_unban_expired(session, account)
                return False

        # La cuenta está baneada y el ban no ha expirado
        return True

    except Exception:
        logging.exception(f"Error al verificar estado de ban para cuenta {account.id}")
        # En caso de error, asumir que NO está baneada (fail-safe)
        return False


async def _auto_unban_expired(session: AsyncSession, account: Account) -> None:
    """
    Función auxiliar interna para desbanear automáticamente cuentas
    cuyo ban temporal ha expirado.

    Args:
        session: Sesión de base de datos activa
        account: Cuenta a desbanear automáticamente
    """
    try:
        account.is_banned = False
        account.ban_reason = None
        account.banned_at = None
        account.banned_by_account_id = None
        account.ban_expires_at = None
        # Mantener has_appealed y appeal_text para historial

        await session.commit()

        logging.info(f"Cuenta {account.id} desbaneada automáticamente por expiración")

    except Exception:
        await session.rollback()
        logging.exception(f"Error al desbanear automáticamente cuenta {account.id}")


async def ban_account(
    session: AsyncSession,
    character: Character,
    reason: str,
    banned_by_account_id: int,
    expires_at: Optional[datetime] = None
) -> None:
    """
    Banea una cuenta asociada a un personaje.

    Aplica un ban permanente o temporal con razón obligatoria y auditoría
    completa. Registra quién aplicó el ban y cuándo.

    Args:
        session: Sesión de base de datos activa
        character: Personaje cuya cuenta será baneada
        reason: Razón del ban (obligatoria, máximo 500 caracteres)
        banned_by_account_id: ID de la cuenta del admin que ejecuta el ban
        expires_at: Fecha de expiración (None = permanente, datetime = temporal)

    Raises:
        ValueError: Si la cuenta ya está baneada
        ValueError: Si la razón está vacía o excede 500 caracteres
        RuntimeError: Si ocurre un error durante el baneo
    """
    try:
        # Obtener la cuenta asociada al personaje
        account = character.account

        # Validaciones
        if await is_account_banned(session, account):
            raise ValueError(f"La cuenta de {character.name} ya está baneada.")

        if not reason or not reason.strip():
            raise ValueError("Debes proporcionar una razón para el ban.")

        if len(reason) > settings.moderation_ban_reason_max_length:
            raise ValueError(
                f"La razón del ban no puede exceder {settings.moderation_ban_reason_max_length} caracteres."
            )

        # Aplicar el ban
        now = datetime.utcnow()
        account.is_banned = True
        account.ban_reason = reason.strip()
        account.banned_at = now
        account.banned_by_account_id = banned_by_account_id
        account.ban_expires_at = expires_at

        await session.commit()

        # Logging detallado para auditoría
        ban_type = "temporal" if expires_at else "permanente"
        expiry_info = f" (expira: {expires_at})" if expires_at else ""
        logging.info(
            f"Ban {ban_type} aplicado a cuenta {account.id} (personaje: {character.name}). "
            f"Razón: '{reason}'. Aplicado por cuenta {banned_by_account_id}.{expiry_info}"
        )

    except ValueError:
        # Propagar ValueError sin hacer rollback (son errores de validación)
        raise
    except Exception:
        await session.rollback()
        logging.exception(f"Error al banear cuenta de {character.name}")
        raise RuntimeError("Error crítico al aplicar el ban.")


async def unban_account(session: AsyncSession, character: Character) -> None:
    """
    Quita el ban de una cuenta asociada a un personaje.

    Limpia todos los campos relacionados con el ban, incluyendo los campos
    de apelación (has_appealed, appeal_text, appealed_at). Esto permite que
    el jugador pueda apelar nuevamente si es baneado en el futuro.

    Args:
        session: Sesión de base de datos activa
        character: Personaje cuya cuenta será desbaneada

    Raises:
        ValueError: Si la cuenta no está baneada
        RuntimeError: Si ocurre un error durante el desbaneo
    """
    try:
        account = character.account

        # Validación
        if not account.is_banned:
            raise ValueError(f"La cuenta de {character.name} no está baneada.")

        # Guardar razón original para logging
        original_reason = account.ban_reason
        ban_type = "temporal" if account.ban_expires_at else "permanente"

        # Quitar el ban y resetear campos de apelación
        # Esto permite que el jugador pueda apelar nuevamente si es baneado de nuevo
        account.is_banned = False
        account.ban_reason = None
        account.banned_at = None
        account.banned_by_account_id = None
        account.ban_expires_at = None
        account.has_appealed = False
        account.appeal_text = None
        account.appealed_at = None

        await session.commit()

        # Logging detallado
        logging.info(
            f"Ban {ban_type} removido de cuenta {account.id} (personaje: {character.name}). "
            f"Razón original: '{original_reason}'."
        )

    except ValueError:
        raise
    except Exception:
        await session.rollback()
        logging.exception(f"Error al desbanear cuenta de {character.name}")
        raise RuntimeError("Error crítico al quitar el ban.")


async def submit_appeal(
    session: AsyncSession,
    account: Account,
    appeal_text: str
) -> None:
    """
    Registra una apelación de ban.

    Permite al jugador baneado enviar UNA apelación con su explicación.
    Solo se permite una apelación por cuenta (has_appealed).

    Args:
        session: Sesión de base de datos activa
        account: Cuenta baneada que apela
        appeal_text: Texto de la apelación (máximo 1000 caracteres)

    Raises:
        ValueError: Si la cuenta no está baneada
        ValueError: Si ya apeló anteriormente
        ValueError: Si el texto está vacío o excede 1000 caracteres
        RuntimeError: Si ocurre un error al guardar la apelación
    """
    try:
        # Validaciones
        if not account.is_banned:
            raise ValueError("No puedes apelar porque tu cuenta no está baneada.")

        if account.has_appealed:
            raise ValueError("Ya has enviado una apelación anteriormente. Solo se permite una.")

        if not appeal_text or not appeal_text.strip():
            raise ValueError("Debes proporcionar un texto para tu apelación.")

        if len(appeal_text) > settings.moderation_appeal_max_length:
            raise ValueError(
                f"La apelación no puede exceder {settings.moderation_appeal_max_length} caracteres."
            )

        # Registrar apelación
        now = datetime.utcnow()
        account.has_appealed = True
        account.appeal_text = appeal_text.strip()
        account.appealed_at = now

        await session.commit()

        # Logging
        logging.info(
            f"Apelación registrada para cuenta {account.id}. "
            f"Texto: '{appeal_text[:50]}...'"
        )

    except ValueError:
        raise
    except Exception:
        await session.rollback()
        logging.exception(f"Error al registrar apelación para cuenta {account.id}")
        raise RuntimeError("Error crítico al guardar la apelación.")


async def get_banned_accounts(
    session: AsyncSession,
    page: int = 1,
    per_page: int = None
) -> tuple[list[Account], int]:
    """
    Obtiene lista paginada de cuentas baneadas.

    Retorna solo cuentas actualmente baneadas (is_banned = True),
    verificando expiración de baneos temporales automáticamente.

    Args:
        session: Sesión de base de datos activa
        page: Número de página (1-indexed)
        per_page: Cantidad de resultados por página

    Returns:
        Tupla con (lista de cuentas baneadas, total de cuentas baneadas)
    """
    try:
        # Usar valor por defecto desde configuración si no se especifica
        if per_page is None:
            per_page = settings.moderation_banned_accounts_per_page

        # Verificar y expirar baneos temporales antes de consultar
        await check_and_expire_bans(session)

        # Calcular offset
        offset = (page - 1) * per_page

        # Query principal con relaciones cargadas
        query = (
            select(Account)
            .where(Account.is_banned == True)
            .options(
                selectinload(Account.character),
                selectinload(Account.banned_by).selectinload(Account.character)
            )
            .order_by(Account.banned_at.desc())
            .limit(per_page)
            .offset(offset)
        )

        result = await session.execute(query)
        banned_accounts = result.scalars().all()

        # Contar total de baneados
        count_query = select(func.count()).select_from(Account).where(Account.is_banned == True)
        count_result = await session.execute(count_query)
        total_count = count_result.scalar()

        return list(banned_accounts), total_count

    except Exception:
        logging.exception("Error al obtener lista de cuentas baneadas")
        return [], 0


async def get_account_ban_info(
    session: AsyncSession,
    character: Character
) -> dict:
    """
    Obtiene información completa del ban de una cuenta.

    Retorna un diccionario con todos los detalles del ban y apelación
    si existen.

    Args:
        session: Sesión de base de datos activa
        character: Personaje cuya cuenta se consulta

    Returns:
        Diccionario con:
        - is_banned (bool): Si está baneada
        - is_temporary (bool): Si es ban temporal
        - reason (str|None): Razón del ban
        - banned_at (datetime|None): Fecha del ban
        - banned_by_name (str|None): Nombre del admin que baneó
        - expires_at (datetime|None): Fecha de expiración (si aplica)
        - has_appealed (bool): Si ha apelado
        - appeal_text (str|None): Texto de apelación
        - appealed_at (datetime|None): Fecha de apelación
    """
    try:
        account = character.account

        # Cargar relación banned_by si existe
        if account.banned_by_account_id:
            query = (
                select(Account)
                .where(Account.id == account.id)
                .options(selectinload(Account.banned_by).selectinload(Account.character))
            )
            result = await session.execute(query)
            account = result.scalar_one()

        # Obtener nombre del admin que baneó
        banned_by_name = None
        if account.banned_by and account.banned_by.character:
            banned_by_name = account.banned_by.character.name

        return {
            "is_banned": account.is_banned,
            "is_temporary": account.ban_expires_at is not None,
            "reason": account.ban_reason,
            "banned_at": account.banned_at,
            "banned_by_name": banned_by_name,
            "expires_at": account.ban_expires_at,
            "has_appealed": account.has_appealed,
            "appeal_text": account.appeal_text,
            "appealed_at": account.appealed_at
        }

    except Exception:
        logging.exception(f"Error al obtener info de ban para {character.name}")
        return {
            "is_banned": False,
            "is_temporary": False,
            "reason": None,
            "banned_at": None,
            "banned_by_name": None,
            "expires_at": None,
            "has_appealed": False,
            "appeal_text": None,
            "appealed_at": None
        }


async def check_and_expire_bans(session: AsyncSession) -> int:
    """
    Verifica y expira automáticamente todos los baneos temporales que
    han alcanzado su fecha de expiración.

    Esta función debe ser llamada periódicamente (ej: por el pulse global)
    o antes de operaciones críticas de verificación de ban.

    Args:
        session: Sesión de base de datos activa

    Returns:
        Cantidad de cuentas desbaneadas automáticamente
    """
    try:
        now = datetime.utcnow()

        # Buscar cuentas con ban expirado
        query = (
            select(Account)
            .where(
                Account.is_banned == True,
                Account.ban_expires_at != None,
                Account.ban_expires_at <= now
            )
        )

        result = await session.execute(query)
        expired_accounts = result.scalars().all()

        # Desbanear cada una
        count = 0
        for account in expired_accounts:
            account.is_banned = False
            account.ban_reason = None
            account.banned_at = None
            account.banned_by_account_id = None
            account.ban_expires_at = None
            count += 1

        if count > 0:
            await session.commit()
            logging.info(f"Desbaneadas automáticamente {count} cuentas por expiración de ban")

        return count

    except Exception:
        await session.rollback()
        logging.exception("Error al verificar y expirar baneos temporales")
        return 0
