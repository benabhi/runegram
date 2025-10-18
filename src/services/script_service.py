# src/services/script_service.py
"""
Servicio de Ejecución de Scripts.

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

Características:
- Enhanced parser con soporte de argumentos complejos (strings con espacios, listas)
- Soporte de scripts globales con prefijo "global:"
- Integración con global_script_registry
"""

import re
import random
import logging
import shlex
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

    Enhanced Parser:
    - Soporta strings con espacios: script(msg="Hola mundo")
    - Soporta booleanos: script(activo=true)
    - Soporta números: script(cantidad=50)
    - Soporta listas: script(items=[espada,escudo])
    - Usa shlex para parsing robusto
    """
    # Detectar si es un script global (prefijo "global:")
    is_global = script_string.startswith("global:")
    if is_global:
        script_string = script_string[7:]  # Remover "global:"

    match = re.match(r"([\w:]+)\((.*)\)", script_string)
    if not match:
        # Si el script no tiene paréntesis, se asume que no tiene argumentos.
        return (script_string, {}), is_global

    name, args_str = match.groups()
    kwargs = {}

    if args_str:
        try:
            # Usar shlex para parsing robusto de argumentos
            tokens = shlex.split(args_str, posix=False)

            for token in tokens:
                if '=' not in token:
                    logging.warning(f"Argumento mal formado en '{script_string}': '{token}' (esperado clave=valor)")
                    continue

                key, value = token.split('=', 1)
                key = key.strip()
                value = value.strip()

                # Remover comillas si existen
                if (value.startswith('"') and value.endswith('"')) or \
                   (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]

                # Convertir tipos
                kwargs[key] = _parse_value(value)

        except Exception as e:
            logging.warning(f"Error parseando argumentos en '{script_string}': {e}")

    return (name, kwargs), is_global


def _parse_value(value: str):
    """
    Convierte un string a su tipo Python apropiado.

    Soporta:
    - Booleanos: true/false
    - Números: 123, 45.6
    - Listas: [item1,item2,item3]
    - Strings: cualquier otra cosa
    """
    # Booleanos
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False

    # Listas
    if value.startswith('[') and value.endswith(']'):
        items = value[1:-1].split(',')
        return [item.strip() for item in items if item.strip()]

    # Números
    try:
        if '.' in value:
            return float(value)
        return int(value)
    except ValueError:
        pass

    # String por defecto
    return value


async def execute_script(script_string: str, session: AsyncSession, **context):
    """
    El corazón del motor de scripts. Parsea el string, busca la función en
    el registro (local o global) y la ejecuta con el contexto proporcionado.

    Características:
    - Soporte de scripts globales con prefijo "global:"
    - Enhanced parser con argumentos complejos
    - Integración con global_script_registry

    Args:
        script_string (str): El string del script a ejecutar
            - Local: "script_name(arg=val)"
            - Global: "global:script_name(arg=val)"
        session (AsyncSession): La sesión de base de datos activa.
        **context: Un diccionario con las entidades relevantes al evento
                   (ej: `character`, `target`, `room`).

    Returns:
        Resultado del script (puede ser None, bool, o cualquier valor)
    """
    if not script_string:
        return

    (script_name, kwargs), is_global = _parse_script_string(script_string)

    # Scripts globales
    if is_global:
        from game_data.global_scripts import global_script_registry

        try:
            result = await global_script_registry.execute(
                name=script_name,
                context={**context, "session": session},
                params=kwargs
            )
            return result
        except Exception:
            logging.exception(f"Error ejecutando script global '{script_name}'")
            return None

    # Scripts locales
    if script_name in SCRIPT_REGISTRY:
        script_function = SCRIPT_REGISTRY[script_name]
        try:
            result = await script_function(session=session, **context, **kwargs)
            return result
        except Exception:
            logging.exception(f"Error ejecutando script local '{script_name}'")
            return None
    else:
        logging.warning(f"Script desconocido: '{script_name}' (no está en SCRIPT_REGISTRY ni en global_script_registry)")