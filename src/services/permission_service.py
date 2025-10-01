# src/services/permission_service.py
"""
Módulo de Servicio para la Gestión de Permisos y Locks.

Este servicio es el "guardián" de acceso a acciones en el juego. Interpreta
"lock strings" (cadenas de permisos) que se encuentran en varias entidades
del juego (comandos, salidas, objetos) y determina si un personaje tiene
permiso para realizar una acción.

El sistema está inspirado en Evennia y es extensible:
1. Un `lock_string` contiene una o más llamadas a funciones (ej: "rol(ADMIN) y tiene_objeto(llave)").
2. `can_execute` parsea este string.
3. Cada función de lock (ej: `rol()`) está registrada en `LOCK_FUNCTIONS`.
4. Para añadir un nuevo tipo de chequeo, solo hay que crear la función de
   chequeo y registrarla.
"""

import logging
import re
from src.models import Character

# --- Jerarquía de Roles ---
# Define el "poder" numérico de cada rol. Un rol superior hereda los
# permisos de todos los roles inferiores.
ROLE_HIERARCHY = {
    "JUGADOR": 1,
    "ADMIN": 2,
    "SUPERADMIN": 3,
}

# ==============================================================================
# SECCIÓN DE FUNCIONES DE LOCK
#
# Cada función aquí implementa una comprobación de permiso específica.
# Toman el personaje que intenta la acción y una lista de argumentos del
# lock string, y devuelven True si el personaje pasa el chequeo, False si no.
# ==============================================================================

def _lock_rol(character: Character, args: list[str]) -> bool:
    """
    Chequea si el rol del personaje es igual o superior al requerido.
    Ejemplo de uso en lock string: `rol(ADMIN)`
    """
    if not character or not character.account or not args:
        return False

    required_role = args[0].upper()
    user_role = character.account.role.upper()

    required_level = ROLE_HIERARCHY.get(required_role, 99) # Rol desconocido es muy alto
    user_level = ROLE_HIERARCHY.get(user_role, 0)

    return user_level >= required_level

def _lock_tiene_objeto(character: Character, args: list[str]) -> bool:
    """
    Chequea si el personaje lleva en su inventario un objeto con la clave dada.
    Ejemplo de uso en lock string: `tiene_objeto(llave_maestra)`
    """
    if not character or not args:
        return False

    item_key = args[0]
    # `any()` es una forma eficiente de comprobar si al menos un elemento cumple la condición.
    return any(item.key == item_key for item in character.items)

# ==============================================================================
# REGISTRO DE FUNCIONES DE LOCK
#
# Este diccionario mapea el nombre de la función en el lock string (en minúsculas)
# con la función de Python que implementa la lógica.
# ==============================================================================

LOCK_FUNCTIONS = {
    "rol": _lock_rol,
    "tiene_objeto": _lock_tiene_objeto,
    # Futuro: "habilidad": _lock_habilidad,
}

# ==============================================================================
# MOTOR DEL SERVICIO DE PERMISOS
# ==============================================================================

def _parse_lock_string(lock_string: str) -> list[tuple[str, list[str]]]:
    """
    Parsea un lock string en una lista de tuplas (nombre_funcion, [argumentos]).
    Ejemplo: "rol(ADMIN) y tiene_objeto(llave)" ->
             [('rol', ['ADMIN']), ('tiene_objeto', ['llave'])]
    """
    if not lock_string:
        return []

    # Regex para encontrar patrones como `nombre_funcion(argumento1, argumento2, ...)`
    func_pattern = re.compile(r"(\w+)\((.*?)\)")

    # Dividimos por ' y ' para manejar la lógica AND. La lógica OR requeriría un parser más complejo.
    parts = lock_string.lower().split(' y ')

    parsed_functions = []
    for part in parts:
        match = func_pattern.match(part.strip())
        if match:
            func_name, args_str = match.groups()
            # Dividimos los argumentos por coma, eliminando espacios extra.
            args = [arg.strip() for arg in args_str.split(',')]
            parsed_functions.append((func_name, args))
    return parsed_functions

async def can_execute(character: Character, lock_string: str) -> tuple[bool, str]:
    """
    Evalúa un `lock_string` contra un personaje para ver si puede pasar el lock.
    """
    try:
        # Un lock vacío significa que no hay restricciones.
        if not lock_string:
            return True, ""

        parsed_locks = _parse_lock_string(lock_string)
        if not parsed_locks and lock_string:
            logging.warning(f"Lock string mal formado y no parseable: '{lock_string}'")
            return False, "Error en la definición de permisos de esta acción."

        # Itera sobre cada función de lock parseada. Todas deben ser True.
        for func_name, args in parsed_locks:
            if func_name in LOCK_FUNCTIONS:
                lock_func = LOCK_FUNCTIONS[func_name]
                if not lock_func(character, args):
                    # Tan pronto como una función de lock falla, toda la cadena AND falla.
                    return False, f"Permiso denegado."
            else:
                logging.warning(f"Función de lock desconocida: '{func_name}' en el lock string: '{lock_string}'")
                return False, "Esa acción está bloqueada por una fuerza desconocida."

        # Si todas las funciones de lock devolvieron True, el personaje tiene permiso.
        return True, ""

    except Exception:
        logging.exception(f"Error crítico al procesar el lock_string: '{lock_string}'")
        # En caso de cualquier error inesperado, siempre fallamos de forma segura.
        return False, "Error interno al comprobar los permisos."