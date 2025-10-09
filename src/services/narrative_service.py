# src/services/narrative_service.py
"""
Servicio de Narrativa (Narrative Service).

Este servicio proporciona mensajes narrativos evocativos aleatorios para diversos
eventos del juego, mejorando la inmersión y evitando la repetición de texto.

Centralizar los mensajes narrativos aquí ofrece varias ventajas:
1. **Variedad**: Cada evento puede tener múltiples descripciones, haciendo que
   el juego se sienta más dinámico y menos repetitivo.
2. **Inmersión**: Los mensajes evocativos refuerzan la atmósfera del mundo.
3. **Mantenibilidad**: Todos los mensajes narrativos se gestionan en un solo lugar
   (game_data/narrative_messages.py), facilitando su edición y expansión.
4. **Escalabilidad**: Agregar nuevos tipos de mensajes es trivial.

Uso típico:
    from src.services import narrative_service

    message = narrative_service.get_random_narrative(
        "item_spawn",
        item_name="una espada brillante"
    )
    # Resultado (aleatorio): "Una espada brillante se materializa con un destello."
"""

import random
import logging
from game_data.narrative_messages import NARRATIVE_MESSAGES


def get_random_narrative(message_type: str, **kwargs) -> str:
    """
    Obtiene un mensaje narrativo aleatorio del tipo especificado.

    Selecciona aleatoriamente un mensaje de la categoría especificada y lo formatea
    con las variables proporcionadas.

    Args:
        message_type (str): Tipo de mensaje narrativo (debe existir en NARRATIVE_MESSAGES).
                           Ejemplos: "item_spawn", "teleport_arrival", "character_suicide"
        **kwargs: Variables para formatear el mensaje usando str.format().
                 Las variables comunes incluyen:
                 - item_name: Nombre del objeto
                 - character_name: Nombre del personaje

    Returns:
        str: Mensaje narrativo formateado con las variables proporcionadas.

    Raises:
        ValueError: Si el message_type especificado no existe en NARRATIVE_MESSAGES.

    Examples:
        >>> get_random_narrative("item_spawn", item_name="una poción roja")
        '<i>Una poción roja aparece de la nada.</i>'

        >>> get_random_narrative("teleport_departure", character_name="Gandalf")
        '<i>Gandalf desaparece en un destello brillante.</i>'
    """
    if message_type not in NARRATIVE_MESSAGES:
        error_msg = (
            f"Tipo de mensaje narrativo '{message_type}' no existe. "
            f"Tipos disponibles: {', '.join(NARRATIVE_MESSAGES.keys())}"
        )
        logging.error(f"NARRATIVE_SERVICE: {error_msg}")
        raise ValueError(error_msg)

    # Obtener la lista de mensajes para este tipo
    messages = NARRATIVE_MESSAGES[message_type]

    if not messages:
        logging.warning(
            f"NARRATIVE_SERVICE: El tipo '{message_type}' existe pero no tiene mensajes definidos."
        )
        return "<i>Algo sucede.</i>"  # Fallback genérico

    # Seleccionar un mensaje aleatorio
    selected_message = random.choice(messages)

    # Formatear el mensaje con las variables proporcionadas
    try:
        formatted_message = selected_message.format(**kwargs)
        return formatted_message
    except KeyError as e:
        logging.error(
            f"NARRATIVE_SERVICE: Error al formatear mensaje tipo '{message_type}'. "
            f"Variable faltante: {e}. Mensaje: '{selected_message}'. "
            f"Variables proporcionadas: {kwargs}"
        )
        # Retornar el mensaje sin formatear como fallback
        return selected_message


def get_available_message_types() -> list[str]:
    """
    Obtiene una lista de todos los tipos de mensajes narrativos disponibles.

    Útil para debugging, documentación o validación.

    Returns:
        list[str]: Lista de tipos de mensajes disponibles.

    Example:
        >>> get_available_message_types()
        ['item_spawn', 'item_destroy_room', 'teleport_departure', ...]
    """
    return list(NARRATIVE_MESSAGES.keys())


def get_message_count(message_type: str) -> int:
    """
    Obtiene el número de variantes de mensajes disponibles para un tipo específico.

    Útil para estadísticas y asegurar que hay suficiente variedad.

    Args:
        message_type (str): Tipo de mensaje narrativo.

    Returns:
        int: Número de variantes disponibles. Retorna 0 si el tipo no existe.

    Example:
        >>> get_message_count("item_spawn")
        7
    """
    if message_type not in NARRATIVE_MESSAGES:
        return 0

    return len(NARRATIVE_MESSAGES[message_type])
