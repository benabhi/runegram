# src/services/state_service.py
"""
Servicio de Manejo de Estado para Sistema de Scripts.

Gestiona estado persistente (PostgreSQL) y transiente (Redis) para scripts.

Responsabilidades:
1. Estado persistente en JSONB (sobrevive reinicios).
2. Estado transiente en Redis (cooldowns, flags temporales).
3. API unificada para acceso a ambos tipos de estado.
4. Soporte para expiración automática de estados transientes.
5. Namespace por entidad para evitar colisiones.
"""

from typing import Any, Dict, Optional, Union
from datetime import datetime, timedelta
import logging
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified
import redis.asyncio as redis

from src.models import Item, Room, Character
from src.config import settings


class StateService:
    """
    Gestiona estado para scripts de forma unificada.

    Dos tipos de estado:
    1. **Persistente** (PostgreSQL JSONB):
       - Sobrevive reinicios del bot
       - Guardado en columna `script_state`
       - Ejemplo: quest progress, items creados, stats modificados

    2. **Transiente** (Redis):
       - Se pierde al reiniciar
       - Ideal para cooldowns, buffs temporales, flags
       - Soporte de TTL (expiración automática)

    Ejemplo de uso:
        # Estado persistente
        await state_service.set_persistent(
            session=session,
            entity=item,
            key="uses_remaining",
            value=3
        )

        # Estado transiente con TTL
        await state_service.set_transient(
            entity=item,
            key="on_cooldown",
            value=True,
            ttl=timedelta(minutes=5)
        )
    """

    def __init__(self):
        """Inicializa el cliente de Redis."""
        self.redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            decode_responses=False  # Manejamos serialización manualmente
        )

    # =================== ESTADO PERSISTENTE (PostgreSQL) ===================

    async def get_persistent(
        self,
        session: AsyncSession,
        entity: Union[Item, Room, Character],
        key: str,
        default: Any = None
    ) -> Any:
        """
        Obtiene un valor del estado persistente.

        Args:
            session: Sesión de BD
            entity: Entidad (Item, Room, Character)
            key: Clave del estado
            default: Valor por defecto si no existe

        Returns:
            Valor almacenado o default
        """
        if not hasattr(entity, 'script_state') or entity.script_state is None:
            return default

        return entity.script_state.get(key, default)

    async def set_persistent(
        self,
        session: AsyncSession,
        entity: Union[Item, Room, Character],
        key: str,
        value: Any
    ):
        """
        Establece un valor en el estado persistente.

        Args:
            session: Sesión de BD
            entity: Entidad (Item, Room, Character)
            key: Clave del estado
            value: Valor a almacenar (debe ser JSON-serializable)
        """
        # Inicializar script_state si no existe
        if not hasattr(entity, 'script_state') or entity.script_state is None:
            entity.script_state = {}

        # Establecer valor
        entity.script_state[key] = value

        # Marcar como modificado para SQLAlchemy (JSONB)
        flag_modified(entity, "script_state")

        logging.debug(
            f"Estado persistente actualizado: {entity.__class__.__name__}#{entity.id} "
            f"[{key}] = {value}"
        )

    async def delete_persistent(
        self,
        session: AsyncSession,
        entity: Union[Item, Room, Character],
        key: str
    ):
        """
        Elimina una clave del estado persistente.

        Args:
            session: Sesión de BD
            entity: Entidad (Item, Room, Character)
            key: Clave a eliminar
        """
        if not hasattr(entity, 'script_state') or entity.script_state is None:
            return

        if key in entity.script_state:
            del entity.script_state[key]
            flag_modified(entity, "script_state")

    async def get_all_persistent(
        self,
        session: AsyncSession,
        entity: Union[Item, Room, Character]
    ) -> Dict[str, Any]:
        """
        Obtiene todo el estado persistente de una entidad.

        Returns:
            Diccionario completo de script_state
        """
        if not hasattr(entity, 'script_state') or entity.script_state is None:
            return {}

        return dict(entity.script_state)

    async def clear_persistent(
        self,
        session: AsyncSession,
        entity: Union[Item, Room, Character]
    ):
        """
        Limpia completamente el estado persistente de una entidad.
        """
        entity.script_state = {}
        flag_modified(entity, "script_state")

    # =================== ESTADO TRANSIENTE (Redis) ===================

    def _make_redis_key(
        self,
        entity: Union[Item, Room, Character],
        key: str
    ) -> str:
        """
        Genera clave de Redis con namespace por entidad.

        Formato: script_state:{entity_type}:{entity_id}:{key}
        Ejemplo: script_state:item:42:on_cooldown
        """
        entity_type = entity.__class__.__name__.lower()
        return f"script_state:{entity_type}:{entity.id}:{key}"

    async def get_transient(
        self,
        entity: Union[Item, Room, Character],
        key: str,
        default: Any = None
    ) -> Any:
        """
        Obtiene un valor del estado transiente (Redis).

        Args:
            entity: Entidad (Item, Room, Character)
            key: Clave del estado
            default: Valor por defecto si no existe

        Returns:
            Valor almacenado o default
        """
        redis_key = self._make_redis_key(entity, key)

        try:
            value_json = await self.redis_client.get(redis_key)

            if value_json is None:
                return default

            # Deserializar JSON
            value = json.loads(value_json)
            return value

        except Exception:
            logging.exception(f"Error obteniendo estado transiente: {redis_key}")
            return default

    async def set_transient(
        self,
        entity: Union[Item, Room, Character],
        key: str,
        value: Any,
        ttl: Optional[timedelta] = None
    ):
        """
        Establece un valor en el estado transiente (Redis).

        Args:
            entity: Entidad (Item, Room, Character)
            key: Clave del estado
            value: Valor a almacenar (debe ser JSON-serializable)
            ttl: Tiempo de vida (opcional). Si se omite, no expira.
        """
        redis_key = self._make_redis_key(entity, key)

        try:
            # Serializar a JSON
            value_json = json.dumps(value)

            # Establecer en Redis con TTL opcional
            if ttl:
                await self.redis_client.setex(
                    redis_key,
                    int(ttl.total_seconds()),
                    value_json
                )
            else:
                await self.redis_client.set(redis_key, value_json)

            logging.debug(
                f"Estado transiente actualizado: {entity.__class__.__name__}#{entity.id} "
                f"[{key}] = {value} (TTL: {ttl})"
            )

        except Exception:
            logging.exception(f"Error estableciendo estado transiente: {redis_key}")

    async def delete_transient(
        self,
        entity: Union[Item, Room, Character],
        key: str
    ):
        """
        Elimina una clave del estado transiente.

        Args:
            entity: Entidad (Item, Room, Character)
            key: Clave a eliminar
        """
        redis_key = self._make_redis_key(entity, key)

        try:
            await self.redis_client.delete(redis_key)
        except Exception:
            logging.exception(f"Error eliminando estado transiente: {redis_key}")

    async def exists_transient(
        self,
        entity: Union[Item, Room, Character],
        key: str
    ) -> bool:
        """
        Verifica si existe una clave en el estado transiente.

        Útil para verificar cooldowns.

        Returns:
            True si la clave existe (y no ha expirado)
        """
        redis_key = self._make_redis_key(entity, key)

        try:
            exists = await self.redis_client.exists(redis_key)
            return bool(exists)
        except Exception:
            logging.exception(f"Error verificando existencia transiente: {redis_key}")
            return False

    async def get_ttl(
        self,
        entity: Union[Item, Room, Character],
        key: str
    ) -> Optional[int]:
        """
        Obtiene el TTL restante de una clave transiente.

        Returns:
            Segundos restantes, o None si no existe o no tiene TTL
        """
        redis_key = self._make_redis_key(entity, key)

        try:
            ttl = await self.redis_client.ttl(redis_key)

            # -2 = no existe, -1 = sin expiración
            if ttl == -2 or ttl == -1:
                return None

            return ttl

        except Exception:
            logging.exception(f"Error obteniendo TTL: {redis_key}")
            return None

    # =================== UTILIDADES ===================

    async def increment_persistent(
        self,
        session: AsyncSession,
        entity: Union[Item, Room, Character],
        key: str,
        amount: int = 1
    ) -> int:
        """
        Incrementa un contador en el estado persistente.

        Args:
            session: Sesión de BD
            entity: Entidad
            key: Clave del contador
            amount: Cantidad a incrementar (default: 1)

        Returns:
            Nuevo valor del contador
        """
        current = await self.get_persistent(session, entity, key, default=0)
        new_value = current + amount
        await self.set_persistent(session, entity, key, new_value)
        return new_value

    async def decrement_persistent(
        self,
        session: AsyncSession,
        entity: Union[Item, Room, Character],
        key: str,
        amount: int = 1,
        min_value: Optional[int] = None
    ) -> int:
        """
        Decrementa un contador en el estado persistente.

        Args:
            session: Sesión de BD
            entity: Entidad
            key: Clave del contador
            amount: Cantidad a decrementar (default: 1)
            min_value: Valor mínimo permitido (opcional)

        Returns:
            Nuevo valor del contador
        """
        current = await self.get_persistent(session, entity, key, default=0)
        new_value = current - amount

        if min_value is not None and new_value < min_value:
            new_value = min_value

        await self.set_persistent(session, entity, key, new_value)
        return new_value

    async def set_cooldown(
        self,
        entity: Union[Item, Room, Character],
        cooldown_name: str,
        duration: timedelta
    ):
        """
        Helper para establecer un cooldown transiente.

        Args:
            entity: Entidad
            cooldown_name: Nombre del cooldown
            duration: Duración del cooldown
        """
        await self.set_transient(
            entity=entity,
            key=f"cooldown_{cooldown_name}",
            value=True,
            ttl=duration
        )

    async def is_on_cooldown(
        self,
        entity: Union[Item, Room, Character],
        cooldown_name: str
    ) -> bool:
        """
        Helper para verificar si un cooldown está activo.

        Args:
            entity: Entidad
            cooldown_name: Nombre del cooldown

        Returns:
            True si el cooldown está activo
        """
        return await self.exists_transient(entity, f"cooldown_{cooldown_name}")

    async def get_cooldown_remaining(
        self,
        entity: Union[Item, Room, Character],
        cooldown_name: str
    ) -> Optional[int]:
        """
        Obtiene el tiempo restante de un cooldown.

        Returns:
            Segundos restantes, o None si no está en cooldown
        """
        return await self.get_ttl(entity, f"cooldown_{cooldown_name}")


# Instancia singleton
state_service = StateService()
