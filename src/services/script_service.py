# src/services/script_service.py
"""
Módulo de Servicio para la Ejecución de Scripts.

Este servicio actúa como el "traductor" entre el contenido del juego (definido
como strings en los archivos de prototipos) y la lógica del motor (código Python).
Permite que los diseñadores de contenido invoquen funcionalidades del motor
sin necesidad de escribir código.

Funciona con un sistema de registro:
1.  Las funciones de script se definen en este archivo.
2.  Se registran en el diccionario `SCRIPT_REGISTRY` con un nombre único.
3.  Los archivos de prototipos en `game_data` usan ese nombre para referirse a ellas.
4.  El método `execute_script` se encarga de parsear el string, buscar la
    función en el registro y ejecutarla con el contexto adecuado.
"""

import re
import random
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.character import Character
from src.models.item import Item
from src.models.room import Room
from src.services import broadcaster_service


# ==============================================================================
# SECCIÓN 1: DEFINICIONES DE LAS FUNCIONES DE SCRIPT
#
# Cada función aquí es una "habilidad" que el motor ofrece a los diseñadores
# de contenido. Deben ser genéricas y reutilizables.
# ==============================================================================

async def script_notificar_brillo_magico(session: AsyncSession, character: Character, target: Item, **kwargs):
    """
    Script de evento: Notifica al jugador que un objeto brilla al ser mirado.

    - Disparador Típico: `on_look` en un prototipo de objeto.
    - Contexto Esperado: `character` (quien mira), `target` (el objeto mirado).
    - Argumentos: `color` (str, opcional) - el color del brillo.
    """
    color = kwargs.get("color", "una luz misteriosa")
    message = f"🌟 Al fijar tu vista en {target.get_name()}, notas que emite un suave brillo de color {color}."
    await broadcaster_service.send_message_to_character(character, message)


async def script_espada_susurra_secreto(session: AsyncSession, target: Item, character: Character, **kwargs):
    """
    Script de ticker: Hace que un objeto emita un susurro a un personaje activo
    que se encuentre en la misma sala.

    - Disparador Típico: `tickers` en un prototipo de objeto.
    - Contexto Esperado: `target` (el objeto que susurra), `character` (el jugador que escucha).
    - Argumentos: Ninguno.
    """
    secretos = [
        "El tesoro se encuentra bajo la sombra del roble marchito...",
        "La llave oxidada no abre una puerta, sino un corazón...",
        "Cuidado con el que no proyecta sombra...",
    ]
    secreto_elegido = random.choice(secretos)
    mensaje = f"<i>Un susurro escalofriante parece emanar de {target.get_name()}: \"{secreto_elegido}\"</i>"
    await broadcaster_service.send_message_to_character(character, mensaje)


# ==============================================================================
# SECCIÓN 2: REGISTRO DE SCRIPTS
#
# Este diccionario es el puente entre los nombres de los scripts (strings)
# y las funciones de Python reales. Para que un script pueda ser llamado
# desde `game_data`, DEBE estar registrado aquí.
# ==============================================================================

SCRIPT_REGISTRY = {
    "script_notificar_brillo_magico": script_notificar_brillo_magico,
    "script_espada_susurra_secreto": script_espada_susurra_secreto,
    # Futuros scripts se añadirían aquí.
}


# ==============================================================================
# SECCIÓN 3: EL MOTOR DE EJECUCIÓN
#
# Lógica interna del servicio para interpretar y ejecutar los scripts.
# ==============================================================================

def _parse_script_string(script_string: str) -> tuple[str, dict]:
    """
    Parsea un string de script como 'nombre(clave=valor, ...)' y devuelve
    el nombre de la función y un diccionario de argumentos.

    Limitación actual: solo soporta argumentos simples de tipo `clave=valor`.
    """
    match = re.match(r"(\w+)\((.*)\)", script_string)
    if not match:
        # Si el script no tiene paréntesis, se asume que no tiene argumentos.
        return script_string, {}

    name, args_str = match.groups()
    kwargs = {}
    if args_str:
        try:
            kwargs = dict(arg.strip().split('=') for arg in args_str.split(','))
        except ValueError:
            logging.warning(f"Argumentos de script mal formados en '{script_string}'. Ignorando argumentos.")
    return name, kwargs


async def execute_script(script_string: str, session: AsyncSession, **context):
    """
    El corazón del motor de scripts. Parsea el string, busca la función en
    el registro y la ejecuta con el contexto proporcionado.

    Args:
        script_string (str): El string del script a ejecutar (ej: "mi_script(arg=val)").
        session (AsyncSession): La sesión de base de datos activa.
        **context: Un diccionario con las entidades relevantes al evento
                   (ej: `character`, `target`, `room`).
    """
    if not script_string:
        return

    script_name, kwargs = _parse_script_string(script_string)

    if script_name in SCRIPT_REGISTRY:
        script_function = SCRIPT_REGISTRY[script_name]
        try:
            # Ejecutamos la función encontrada, pasando el contexto y los argumentos parseados.
            await script_function(session=session, **context, **kwargs)
        except Exception:
            # Si un script falla, registramos el error con un traceback completo
            # pero no detenemos la ejecución del resto del juego.
            logging.exception(f"Ocurrió un error al ejecutar el script '{script_name}'")
    else:
        logging.warning(f"ADVERTENCIA: Se intentó ejecutar un script desconocido: '{script_name}'")