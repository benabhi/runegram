# src/services/permission_service.py
from src.models.character import Character


def _check_role(character: Character, required_role: str) -> bool:
    """Verifica si el personaje tiene el rol requerido."""
    return character.account.role.upper() == required_role.upper()


async def can_execute(character: Character, lock_string: str) -> tuple[bool, str]:
    """
    Verifica si un personaje puede pasar un lock.
    Devuelve una tupla: (puede_pasar, mensaje_de_error).
    """
    if not lock_string:
        return True, ""  # Un lock vacío siempre se puede pasar.

    # Lógica AND: todas las funciones de lock deben ser verdaderas.
    lock_functions = lock_string.lower().split(' y ')

    for func in lock_functions:
        # Por ahora, solo implementamos la función 'rol(argumento)'
        if func.startswith('rol(') and func.endswith(')'):
            required_role = func[4:-1]
            if not _check_role(character, required_role):
                # Devolvemos un mensaje de error específico
                return False, "No tienes el rango necesario."
        else:
            # Si encontramos una función de lock que no entendemos, por seguridad, fallamos.
            print(f"ADVERTENCIA: Función de lock desconocida: {func}")
            return False, "Esa acción está bloqueada por una fuerza desconocida."

    # Si el personaje pasó todos los chequeos de la cadena AND
    return True, ""