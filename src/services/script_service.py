# src/services/script_service.py
import re
import random
import logging  # <-- Importamos logging
from sqlalchemy.ext.asyncio import AsyncSession

# Importamos los modelos de datos con los que los scripts interactuarán
from src.models.character import Character
from src.models.item import Item
from src.models.room import Room

# Importamos el servicio centralizado para enviar mensajes
from src.services import broadcaster_service


# ==============================================================================
# SECCIÓN 1: DEFINICIONES DE LAS FUNCIONES DE SCRIPT
# ==============================================================================

async def script_notificar_brillo_magico(session: AsyncSession, character: Character, target: Item, **kwargs):
    """
    Script de evento: Notifica al jugador que un objeto brilla al ser mirado.
    """
    color = kwargs.get("color", "una luz misteriosa")
    message = f"🌟 Al fijar tu vista en {target.get_name()}, notas que emite un suave brillo de color {color}."

    await broadcaster_service.send_message_to_character(character, message)


async def script_espada_susurra_secreto(session: AsyncSession, target: Item, character: Character, **kwargs):
    """
    Script de ticker: Hace que un objeto emita un susurro a un personaje específico
    que está activo en la misma sala.
    """
    secretos = [
        "El tesoro se encuentra bajo la sombra del roble marchito...",
        "La llave oxidada no abre una puerta, sino un corazón...",
        "Cuidado con el que no proyecta sombra...",
    ]
    secreto_elegido = random.choice(secretos)

    mensaje = f"<i>Un susurro escalofriante parece emanar de {target.get_name()}: \"{secreto_elegido}\"</i>"

    # Ahora enviamos el mensaje solo al personaje del contexto, que ya sabemos que está activo.
    await broadcaster_service.send_message_to_character(character, mensaje)


# ==============================================================================
# SECCIÓN 2: EL MOTOR DE SCRIPTS
# ==============================================================================

SCRIPT_REGISTRY = {
    "script_notificar_brillo_magico": script_notificar_brillo_magico,
    "script_espada_susurra_secreto": script_espada_susurra_secreto,
}

def _parse_script_string(script_string: str) -> tuple[str, dict]:
    """
    Parsea un string de script como 'nombre_script(key1=val1, key2=val2)'
    y devuelve el nombre y un diccionario de argumentos.
    """
    match = re.match(r"(\w+)\((.*)\)", script_string)
    if not match:
        return script_string, {}

    name, args_str = match.groups()
    kwargs = {}
    if args_str:
        try:
            kwargs = dict(arg.strip().split('=') for arg in args_str.split(','))
        except ValueError:
            print(f"ADVERTENCIA: Argumentos de script mal formados en '{script_string}'. Ignorando argumentos.")
    return name, kwargs


async def execute_script(script_string: str, session: AsyncSession, **context):
    """
    El corazón del motor de scripts.
    """
    if not script_string:
        return

    script_name, kwargs = _parse_script_string(script_string)

    if script_name in SCRIPT_REGISTRY:
        script_function = SCRIPT_REGISTRY[script_name]
        try:
            await script_function(session=session, **context, **kwargs)
        except Exception as e:
            # --- MEJORA DE LOGGING ---
            # Usamos logging.exception para obtener un traceback completo en los logs de Docker.
            logging.exception(f"Ocurrió un error al ejecutar el script '{script_name}'")
    else:
        logging.warning(f"ADVERTENCIA: Se intentó ejecutar un script desconocido: '{script_name}'")