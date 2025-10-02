# src/services/validation_service.py
"""
Servicio de Validación de Integridad del Motor.

Este servicio proporciona validaciones críticas que se ejecutan durante el arranque
de la aplicación para detectar conflictos y errores de configuración en los datos
del juego que podrían causar comportamientos inesperados o bugs.

Filosofía:
- "Fail Fast": Es mejor detectar errores al arrancar que durante el juego.
- "Single Source of Truth": Cada identificador (alias de comando, key de prototipo)
  debe ser único en su dominio.
- Validaciones data-driven: Se validan prototipos, no código.

El sistema valida:
1. Unicidad de aliases de comandos (incluyendo canales dinámicos)
2. Unicidad de keys en prototipos de salas (rooms)
3. Unicidad de keys en prototipos de items
4. Más validaciones según sea necesario

Uso:
    from src.services import validation_service

    # Durante el arranque de la aplicación:
    validation_service.validate_all()  # Lanza ValidationError si hay problemas
"""

import logging
from typing import Dict, List, Set, Tuple
from collections import defaultdict

from game_data.room_prototypes import ROOM_PROTOTYPES
from game_data.item_prototypes import ITEM_PROTOTYPES
from game_data.channel_prototypes import CHANNEL_PROTOTYPES


class ValidationError(Exception):
    """Excepción lanzada cuando se detecta un error de validación crítico."""
    pass


def _collect_command_aliases() -> Dict[str, List[str]]:
    """
    Recopila todos los aliases de comandos de todos los CommandSets.

    Returns:
        Dict donde la clave es el alias y el valor es una lista de fuentes
        (ej: ["movement.norte", "movement.n", "channels.novato"]).
    """
    from src.handlers.player.dispatcher import COMMAND_SETS

    alias_to_sources = defaultdict(list)

    for set_name, commands in COMMAND_SETS.items():
        for cmd in commands:
            for alias in cmd.names:
                source = f"{set_name}.{cmd.names[0]}"  # ej: "movement.norte"
                alias_to_sources[alias].append(source)

    return alias_to_sources


def validate_command_aliases() -> List[str]:
    """
    Valida que no haya aliases de comandos duplicados.

    Returns:
        Lista de mensajes de error. Vacía si no hay problemas.
    """
    errors = []
    alias_to_sources = _collect_command_aliases()

    for alias, sources in alias_to_sources.items():
        if len(sources) > 1:
            sources_str = ", ".join(sources)
            errors.append(
                f"❌ Alias de comando duplicado: '/{alias}' está definido en: {sources_str}"
            )

    return errors


def validate_room_prototype_keys() -> List[str]:
    """
    Valida que no haya keys duplicadas en los prototipos de salas.

    Returns:
        Lista de mensajes de error. Vacía si no hay problemas.
    """
    errors = []
    seen_keys = set()

    for key in ROOM_PROTOTYPES.keys():
        if key in seen_keys:
            errors.append(f"❌ Key de sala duplicada: '{key}' aparece más de una vez en ROOM_PROTOTYPES")
        seen_keys.add(key)

    # Validación adicional: verificar que las salidas apunten a salas que existen
    for room_key, room_data in ROOM_PROTOTYPES.items():
        for direction, exit_data in room_data.get("exits", {}).items():
            # Soporte para formato simple (string) y formato con locks (dict)
            target_key = exit_data if isinstance(exit_data, str) else exit_data.get("to")

            if target_key and target_key not in ROOM_PROTOTYPES:
                errors.append(
                    f"❌ Salida inválida en sala '{room_key}': "
                    f"la dirección '{direction}' apunta a '{target_key}' que no existe"
                )

    return errors


def validate_item_prototype_keys() -> List[str]:
    """
    Valida que no haya keys duplicadas en los prototipos de items.

    Returns:
        Lista de mensajes de error. Vacía si no hay problemas.
    """
    errors = []
    seen_keys = set()

    for key in ITEM_PROTOTYPES.keys():
        if key in seen_keys:
            errors.append(f"❌ Key de item duplicada: '{key}' aparece más de una vez en ITEM_PROTOTYPES")
        seen_keys.add(key)

    return errors


def validate_channel_prototype_keys() -> List[str]:
    """
    Valida que no haya keys duplicadas en los prototipos de canales.

    Returns:
        Lista de mensajes de error. Vacía si no hay problemas.
    """
    errors = []
    seen_keys = set()

    for key in CHANNEL_PROTOTYPES.keys():
        if key in seen_keys:
            errors.append(f"❌ Key de canal duplicada: '{key}' aparece más de una vez en CHANNEL_PROTOTYPES")
        seen_keys.add(key)

    return errors


def validate_all() -> None:
    """
    Ejecuta todas las validaciones del sistema.

    Si se detecta algún error, lanza una ValidationError con todos los mensajes.
    Esta función debe ser llamada durante el arranque de la aplicación, antes
    de iniciar el bot.

    Raises:
        ValidationError: Si se detecta cualquier problema de validación.
    """
    logging.info("🔍 Ejecutando validaciones de integridad del motor...")

    all_errors = []

    # Validación 1: Aliases de comandos
    all_errors.extend(validate_command_aliases())

    # Validación 2: Keys de prototipos de salas
    all_errors.extend(validate_room_prototype_keys())

    # Validación 3: Keys de prototipos de items
    all_errors.extend(validate_item_prototype_keys())

    # Validación 4: Keys de prototipos de canales
    all_errors.extend(validate_channel_prototype_keys())

    if all_errors:
        error_message = "\n".join([
            "\n⚠️  ERRORES DE VALIDACIÓN DETECTADOS ⚠️",
            "=" * 60,
            *all_errors,
            "=" * 60,
            "\nCorrige estos errores antes de continuar."
        ])
        logging.error(error_message)
        raise ValidationError(error_message)

    logging.info("✅ Todas las validaciones pasaron correctamente.")


def get_validation_report() -> str:
    """
    Genera un reporte de validación sin lanzar excepciones.
    Útil para debugging o comandos administrativos.

    Returns:
        String con el reporte de validación.
    """
    lines = ["=== REPORTE DE VALIDACIÓN ===\n"]

    errors = []
    errors.extend(validate_command_aliases())
    errors.extend(validate_room_prototype_keys())
    errors.extend(validate_item_prototype_keys())
    errors.extend(validate_channel_prototype_keys())

    if errors:
        lines.append("❌ ERRORES ENCONTRADOS:\n")
        lines.extend([f"  {err}" for err in errors])
    else:
        lines.append("✅ No se encontraron errores.\n")

    # Estadísticas
    alias_count = len(_collect_command_aliases())
    room_count = len(ROOM_PROTOTYPES)
    item_count = len(ITEM_PROTOTYPES)
    channel_count = len(CHANNEL_PROTOTYPES)

    lines.append(f"\n📊 ESTADÍSTICAS:")
    lines.append(f"  • Aliases de comandos: {alias_count}")
    lines.append(f"  • Prototipos de salas: {room_count}")
    lines.append(f"  • Prototipos de items: {item_count}")
    lines.append(f"  • Prototipos de canales: {channel_count}")

    return "\n".join(lines)
