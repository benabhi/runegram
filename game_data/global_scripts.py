# game_data/global_scripts.py
"""
Registro de Scripts Globales Reutilizables para Sistema de Scripts v2.0.

Los scripts globales son funciones Python que pueden ser invocadas desde prototipos
con parámetros validados, facilitando la reutilización y mantenimiento.

Estructura de un Script Global:
- Nombre único que se usa desde prototipos
- Función async que recibe contexto estándar + parámetros personalizados
- Validación de parámetros con tipos esperados
- Documentación clara de parámetros y comportamiento

Ejemplo de uso en prototipo:
    "scripts": {
        "after_on_use": "global:curar_personaje(cantidad=50, mensaje='Te sientes mejor')"
    }
"""

from typing import Any, Dict, Callable, List
from dataclasses import dataclass
import logging

from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class GlobalScriptDefinition:
    """
    Definición de un script global reutilizable.
    """
    name: str                           # Nombre único del script
    function: Callable                  # Función async a ejecutar
    params: Dict[str, type]             # Parámetros esperados con sus tipos
    description: str                    # Descripción del script
    category: str = "utility"           # Categoría (utility, combat, narrative, etc.)


class GlobalScriptRegistry:
    """
    Registro centralizado de scripts globales.

    Permite registrar, validar y ejecutar scripts globales con parámetros.
    """

    def __init__(self):
        self._scripts: Dict[str, GlobalScriptDefinition] = {}

    def register(
        self,
        name: str,
        function: Callable,
        params: Dict[str, type],
        description: str,
        category: str = "utility"
    ):
        """
        Registra un script global.

        Args:
            name: Nombre único del script (ej: "curar_personaje")
            function: Función async que implementa el script
            params: Dict con nombres de parámetros y sus tipos
            description: Descripción del script
            category: Categoría del script
        """
        if name in self._scripts:
            logging.warning(f"Script global '{name}' ya está registrado. Se sobrescribirá.")

        self._scripts[name] = GlobalScriptDefinition(
            name=name,
            function=function,
            params=params,
            description=description,
            category=category
        )

        logging.info(f"Script global registrado: {name} (categoría: {category})")

    def get(self, name: str) -> GlobalScriptDefinition | None:
        """Obtiene un script global por nombre."""
        return self._scripts.get(name)

    def exists(self, name: str) -> bool:
        """Verifica si un script global existe."""
        return name in self._scripts

    def list_all(self) -> List[GlobalScriptDefinition]:
        """Lista todos los scripts globales registrados."""
        return list(self._scripts.values())

    def list_by_category(self, category: str) -> List[GlobalScriptDefinition]:
        """Lista scripts globales por categoría."""
        return [s for s in self._scripts.values() if s.category == category]

    async def execute(
        self,
        name: str,
        context: Dict[str, Any],
        params: Dict[str, Any]
    ) -> Any:
        """
        Ejecuta un script global con validación de parámetros.

        Args:
            name: Nombre del script
            context: Contexto de ejecución (session, character, target, room, etc.)
            params: Parámetros del script

        Returns:
            Resultado del script

        Raises:
            ValueError: Si el script no existe o los parámetros son inválidos
        """
        script_def = self.get(name)

        if not script_def:
            raise ValueError(f"Script global '{name}' no encontrado")

        # Validar parámetros
        self._validate_params(script_def, params)

        # Ejecutar script
        try:
            result = await script_def.function(**context, **params)
            return result
        except Exception as e:
            logging.exception(f"Error ejecutando script global '{name}'")
            raise

    def _validate_params(
        self,
        script_def: GlobalScriptDefinition,
        params: Dict[str, Any]
    ):
        """
        Valida que los parámetros coincidan con los esperados.

        Raises:
            ValueError: Si faltan parámetros o los tipos no coinciden
        """
        # Verificar parámetros requeridos
        for param_name, param_type in script_def.params.items():
            if param_name not in params:
                raise ValueError(
                    f"Script '{script_def.name}' requiere parámetro '{param_name}'"
                )

            # Validar tipo
            value = params[param_name]
            if not isinstance(value, param_type):
                raise ValueError(
                    f"Script '{script_def.name}': parámetro '{param_name}' debe ser {param_type.__name__}, "
                    f"se recibió {type(value).__name__}"
                )

        # Advertir sobre parámetros extra (no bloquear)
        extra_params = set(params.keys()) - set(script_def.params.keys())
        if extra_params:
            logging.warning(
                f"Script '{script_def.name}' recibió parámetros no esperados: {extra_params}"
            )


# ============================================================================
# INSTANCIA GLOBAL
# ============================================================================

global_script_registry = GlobalScriptRegistry()


# ============================================================================
# SCRIPTS GLOBALES - UTILITY
# ============================================================================

async def script_curar_personaje(
    session: AsyncSession,
    character: Any,
    cantidad: int = 10,
    mensaje: str = "Te sientes mejor."
):
    """
    Cura HP de un personaje.

    Args:
        session: Sesión de BD
        character: Personaje a curar
        cantidad: HP a restaurar
        mensaje: Mensaje a mostrar
    """
    from src.services import broadcaster_service

    # TODO: Cuando exista sistema de stats, actualizar HP aquí
    # character.hp = min(character.hp + cantidad, character.max_hp)

    # Notificar al jugador
    from src.bot import bot
    if hasattr(character, 'account') and character.account:
        await bot.send_message(
            character.account.telegram_id,
            f"<i>{mensaje}</i>",
            parse_mode="HTML"
        )

    # Notificar a la sala
    if hasattr(character, 'room') and character.room:
        await broadcaster_service.send_message_to_room(
            session=session,
            room_id=character.room.id,
            message_text=f"<i>{character.name} parece sentirse mejor.</i>",
            exclude_character_id=character.id
        )

    logging.info(f"Script global 'curar_personaje': {character.name} curado {cantidad} HP")


async def script_danar_personaje(
    session: AsyncSession,
    character: Any,
    cantidad: int = 5,
    mensaje: str = "¡Te duele!"
):
    """
    Daña HP de un personaje.

    Args:
        session: Sesión de BD
        character: Personaje a dañar
        cantidad: HP a quitar
        mensaje: Mensaje a mostrar
    """
    from src.services import broadcaster_service

    # TODO: Cuando exista sistema de stats, actualizar HP aquí
    # character.hp = max(character.hp - cantidad, 0)

    # Notificar al jugador
    from src.bot import bot
    if hasattr(character, 'account') and character.account:
        await bot.send_message(
            character.account.telegram_id,
            f"<i>{mensaje}</i>",
            parse_mode="HTML"
        )

    # Notificar a la sala
    if hasattr(character, 'room') and character.room:
        await broadcaster_service.send_message_to_room(
            session=session,
            room_id=character.room.id,
            message_text=f"<i>{character.name} parece herido.</i>",
            exclude_character_id=character.id
        )

    logging.info(f"Script global 'danar_personaje': {character.name} dañado {cantidad} HP")


async def script_teleport_aleatorio(
    session: AsyncSession,
    character: Any,
    mensaje: str = "¡Sientes una extraña energía que te transporta!"
):
    """
    Teleporta a un personaje a una sala aleatoria.

    Args:
        session: Sesión de BD
        character: Personaje a teleportar
        mensaje: Mensaje a mostrar
    """
    from sqlalchemy import select, func
    from src.models import Room
    from src.services import broadcaster_service, narrative_service

    # Obtener sala aleatoria
    query = select(Room).order_by(func.random()).limit(1)
    result = await session.execute(query)
    random_room = result.scalar_one_or_none()

    if not random_room:
        logging.warning("No hay salas disponibles para teleport aleatorio")
        return

    old_room = character.room

    # Notificar salida
    departure_msg = narrative_service.get_random_narrative(
        "teleport_departure",
        character_name=character.name
    )
    await broadcaster_service.send_message_to_room(
        session=session,
        room_id=old_room.id,
        message_text=departure_msg,
        exclude_character_id=character.id
    )

    # Teleportar
    character.room_id = random_room.id

    # Notificar llegada
    arrival_msg = narrative_service.get_random_narrative(
        "teleport_arrival",
        character_name=character.name
    )
    await broadcaster_service.send_message_to_room(
        session=session,
        room_id=random_room.id,
        message_text=arrival_msg,
        exclude_character_id=character.id
    )

    # Notificar al jugador
    from src.bot import bot
    if hasattr(character, 'account') and character.account:
        await bot.send_message(
            character.account.telegram_id,
            f"<i>{mensaje}</i>",
            parse_mode="HTML"
        )

    await session.commit()
    logging.info(f"Script global 'teleport_aleatorio': {character.name} → {random_room.name}")


async def script_spawn_item(
    session: AsyncSession,
    room: Any,
    item_key: str,
    mensaje: str = ""
):
    """
    Spawna un item en una sala.

    Args:
        session: Sesión de BD
        room: Sala donde spawnar
        item_key: Key del prototipo de item
        mensaje: Mensaje opcional a mostrar
    """
    from src.models import Item
    from src.services import broadcaster_service, narrative_service
    from game_data.item_prototypes import ITEM_PROTOTYPES

    # Verificar que el prototipo existe
    if item_key not in ITEM_PROTOTYPES:
        logging.warning(f"Script global 'spawn_item': prototipo '{item_key}' no existe")
        return

    # Crear item
    new_item = Item(key=item_key, room_id=room.id)
    session.add(new_item)
    await session.flush()  # Para obtener el ID

    # Mensaje narrativo
    item_name = new_item.get_name()
    narrative_msg = narrative_service.get_random_narrative(
        "item_spawn",
        item_name=item_name
    )

    # Notificar a la sala
    await broadcaster_service.send_message_to_room(
        session=session,
        room_id=room.id,
        message_text=narrative_msg
    )

    # Mensaje adicional si se proporcionó
    if mensaje:
        await broadcaster_service.send_message_to_room(
            session=session,
            room_id=room.id,
            message_text=f"<i>{mensaje}</i>"
        )

    await session.commit()
    logging.info(f"Script global 'spawn_item': {item_key} spawneado en {room.name}")


# ============================================================================
# REGISTRO DE SCRIPTS GLOBALES
# ============================================================================

def register_all_global_scripts():
    """
    Registra todos los scripts globales en el registry.

    Debe llamarse al iniciar el bot (en run.py).
    """
    # Utility
    global_script_registry.register(
        name="curar_personaje",
        function=script_curar_personaje,
        params={"cantidad": int, "mensaje": str},
        description="Cura HP de un personaje",
        category="utility"
    )

    global_script_registry.register(
        name="danar_personaje",
        function=script_danar_personaje,
        params={"cantidad": int, "mensaje": str},
        description="Daña HP de un personaje",
        category="utility"
    )

    global_script_registry.register(
        name="teleport_aleatorio",
        function=script_teleport_aleatorio,
        params={"mensaje": str},
        description="Teleporta a un personaje a una sala aleatoria",
        category="utility"
    )

    global_script_registry.register(
        name="spawn_item",
        function=script_spawn_item,
        params={"item_key": str, "mensaje": str},
        description="Spawna un item en una sala",
        category="utility"
    )

    logging.info(f"✅ {len(global_script_registry.list_all())} scripts globales registrados")
