# src/services/permission_service.py
"""
Módulo de Servicio para la Gestión de Permisos y Locks.

Este servicio es el responsable de interpretar los "lock strings" (cadenas de
permisos) que se encuentran en varias entidades del juego (comandos, salidas,
objetos) y determinar si un personaje tiene permiso para realizar una acción.

Actualmente, solo implementa la función de lock `rol()`, pero está diseñado
para ser fácilmente expandible con funciones más complejas como `habilidad()`,
`tiene_objeto()`, etc.
"""

import logging
from src.models.character import Character


def _check_role(character: Character, required_role: str) -> bool:
    """
    Función de lock interna: Verifica si el personaje tiene el rol requerido.
    Compara de forma insensible a mayúsculas.
    """
    if not character or not character.account:
        return False
    return character.account.role.upper() == required_role.upper()


async def can_execute(character: Character, lock_string: str) -> tuple[bool, str]:
    """
    Evalúa un `lock_string` contra un personaje para ver si puede pasar el lock.

    Args:
        character (Character): El personaje que intenta la acción.
        lock_string (str): La cadena de permisos a evaluar (ej: "rol(ADMINISTRADOR)").

    Returns:
        tuple[bool, str]: Una tupla conteniendo:
                          - `True` si puede pasar, `False` si no.
                          - Una cadena con el mensaje de error si falla, o vacía si tiene éxito.
    """
    try:
        # Un lock vacío siempre se puede pasar. Es la forma de definir una acción "pública".
        if not lock_string:
            return True, ""

        # Por ahora, el parser es simple y solo soporta la lógica 'Y' (AND).
        # "rol(A) y tiene_objeto(B)" se divide en una lista de dos funciones.
        lock_functions = lock_string.lower().split(' y ')

        for func_str in lock_functions:
            # Futuro: Aquí iría un parser más avanzado para manejar funciones
            # con argumentos y operadores lógicos complejos.

            # Implementación actual: `rol(argumento)`
            if func_str.startswith('rol(') and func_str.endswith(')'):
                required_role = func_str[4:-1]
                if not _check_role(character, required_role):
                    return False, "No tienes el rango necesario para hacer eso."

            # Si encontramos una función de lock que no entendemos, por seguridad, denegamos el acceso.
            else:
                logging.warning(f"Función de lock desconocida encontrada: {func_str} en lock string: '{lock_string}'")
                return False, "Esa acción está bloqueada por una fuerza desconocida."

        # Si el personaje pasó todos los chequeos de la cadena, tiene permiso.
        return True, ""

    except Exception:
        logging.exception(f"Error al parsear el lock_string: '{lock_string}'")
        # En caso de cualquier error de parseo, siempre fallamos de forma segura.
        return False, "Error interno al comprobar los permisos."