# src/services/permission_service.py
"""
Módulo de Servicio para la Gestión de Permisos y Locks.

Este servicio es el "guardián" de acceso a acciones en el juego. Interpreta
"lock strings" (cadenas de permisos) para determinar si un personaje tiene
permiso, utilizando el módulo `ast` de Python para un parseo seguro y potente.

El sistema es extensible y soporta lógica booleana compleja:
1. Un `lock_string` es una expresión similar a Python (ej: "rol(ADMIN) or (tiene_objeto(llave) and not rol(SUPERADMIN))").
2. `ast.parse` convierte el string en un árbol de sintaxis abstracta (AST) de forma segura.
3. La clase `LockEvaluator` (un `ast.NodeVisitor`) recorre el árbol y evalúa el resultado.
4. Las funciones de lock (ej: `rol()`) están registradas en `LOCK_FUNCTIONS`.

Versión 2.0 - Sistema de Locks Contextuales:
- Soporte para locks contextuales (diccionarios por access_type)
- Soporte para lock functions asíncronas
- Sistema de mensajes de error personalizados (lock_messages)
- Backward compatible con lock strings simples
"""

import logging
import ast # Módulo para parsear la sintaxis de Python de forma segura
import inspect
from typing import Callable, Awaitable
from src.models import Character

# --- Jerarquía de Roles ---
ROLE_HIERARCHY = {
    "JUGADOR": 1,
    "ADMIN": 2,
    "SUPERADMIN": 3,
}

# ==============================================================================
# SECCIÓN DE FUNCIONES DE LOCK
#
# Estas funciones no cambian. Siguen siendo los bloques de construcción
# de nuestra lógica de permisos.
# ==============================================================================

def _lock_rol(character: Character, args: list[str]) -> bool:
    """Chequea si el rol del personaje es igual o superior al requerido."""
    if not character or not character.account or not args:
        return False

    required_role = args[0].upper()
    user_role = character.account.role.upper()

    required_level = ROLE_HIERARCHY.get(required_role, 99)
    user_level = ROLE_HIERARCHY.get(user_role, 0)

    return user_level >= required_level

def _lock_tiene_objeto(character: Character, args: list[str]) -> bool:
    """Chequea si el personaje lleva en su inventario un objeto con la clave dada."""
    if not character or not args:
        return False

    item_key = args[0]
    return any(item.key == item_key for item in character.items)

def _lock_en_sala(character: Character, args: list[str]) -> bool:
    """Verifica si el personaje está en una sala específica."""
    if not character or not character.room or not args:
        return False

    sala_key = args[0]
    return character.room.key == sala_key

def _lock_en_categoria_sala(character: Character, args: list[str]) -> bool:
    """Verifica si el personaje está en una sala de cierta categoría."""
    if not character or not character.room or not args:
        return False

    categoria = args[0]
    return character.room.category == categoria

def _lock_tiene_tag_sala(character: Character, args: list[str]) -> bool:
    """Verifica si la sala actual tiene un tag específico."""
    if not character or not character.room or not args:
        return False

    tag = args[0]
    return tag in character.room.tags

def _lock_cuenta_items(character: Character, args: list[str]) -> bool:
    """Verifica si el personaje tiene al menos N items en inventario."""
    if not character or not args:
        return False

    try:
        min_count = int(args[0])
        return len(character.items) >= min_count
    except ValueError:
        return False

def _lock_tiene_item_categoria(character: Character, args: list[str]) -> bool:
    """Verifica si el personaje tiene un item de cierta categoría."""
    if not character or not args:
        return False

    categoria = args[0]
    return any(item.category == categoria for item in character.items)

def _lock_tiene_item_tag(character: Character, args: list[str]) -> bool:
    """Verifica si el personaje tiene un item con un tag específico."""
    if not character or not args:
        return False

    tag = args[0]
    return any(tag in item.tags for item in character.items)

async def _lock_online(character: Character, args: list[str]) -> bool:
    """
    Verifica si el personaje está actualmente conectado.

    Esta es una lock function asíncrona que requiere acceso a Redis.
    """
    if not character:
        return False

    from src.services import online_service
    return await online_service.is_character_online(character.id)

# ==============================================================================
# REGISTRO DE FUNCIONES DE LOCK
# ==============================================================================

LOCK_FUNCTIONS = {
    "rol": _lock_rol,
    "tiene_objeto": _lock_tiene_objeto,
    "en_sala": _lock_en_sala,
    "en_categoria_sala": _lock_en_categoria_sala,
    "tiene_tag_sala": _lock_tiene_tag_sala,
    "cuenta_items": _lock_cuenta_items,
    "tiene_item_categoria": _lock_tiene_item_categoria,
    "tiene_item_tag": _lock_tiene_item_tag,
    "online": _lock_online,  # Función asíncrona
}

# ==============================================================================
# MOTOR DEL SERVICIO DE PERMISOS (BASADO EN AST)
# ==============================================================================

class LockEvaluator(ast.NodeVisitor):
    """
    Un visitante de nodos AST que evalúa un lock string de forma segura.
    Recorre el árbol de sintaxis y calcula el resultado booleano final.

    Versión 2.0: Soporta lock functions asíncronas.
    """
    def __init__(self, character: Character):
        self.character = character

    async def visit_BoolOp(self, node: ast.BoolOp):
        """Maneja operadores `and` y `or` con soporte async."""
        # Evaluamos cada sub-expresión (pueden ser async)
        sub_results = []
        for value in node.values:
            result = self.visit(value)
            # Si el resultado es una corrutina, esperarlo
            if inspect.iscoroutine(result):
                result = await result
            sub_results.append(result)

        if isinstance(node.op, ast.And):
            return all(sub_results)
        elif isinstance(node.op, ast.Or):
            return any(sub_results)
        return False

    async def visit_UnaryOp(self, node: ast.UnaryOp):
        """Maneja el operador `not` con soporte async."""
        if isinstance(node.op, ast.Not):
            result = self.visit(node.operand)
            # Si el resultado es una corrutina, esperarlo
            if inspect.iscoroutine(result):
                result = await result
            return not result
        return False

    async def visit_Call(self, node: ast.Call):
        """Maneja las llamadas a funciones de lock (ej: `rol(...)`) con soporte async."""
        func_name = node.func.id.lower()
        if func_name in LOCK_FUNCTIONS:
            # Evaluamos los argumentos (que también son nodos AST)
            args = []
            for arg in node.args:
                result = self.visit(arg)
                if inspect.iscoroutine(result):
                    result = await result
                args.append(result)

            lock_func = LOCK_FUNCTIONS[func_name]

            # Verificar si la función es asíncrona
            if inspect.iscoroutinefunction(lock_func):
                return await lock_func(self.character, args)
            else:
                return lock_func(self.character, args)

        logging.warning(f"Función de lock desconocida llamada: {func_name}")
        return False # Falla de forma segura si la función no está registrada.

    def visit_Constant(self, node: ast.Constant):
        """Maneja valores constantes como strings o números."""
        return node.value

    def visit_Name(self, node: ast.Name) -> str:
        """
        Maneja nombres/identificadores. Los tratamos como strings.
        Esto permite escribir `rol(ADMIN)` en lugar de `rol('ADMIN')`.
        """
        return node.id

    def generic_visit(self, node):
        """
        Método de captura para cualquier tipo de nodo no soportado.
        Esto es una medida de seguridad crucial para prevenir la ejecución
        de código no deseado (bucles, asignaciones, etc.).
        """
        raise TypeError(f"Construcción no soportada en lock string: {type(node).__name__}")

async def can_execute(
    character: Character,
    locks: str | dict[str, str],
    access_type: str = "default",
    lock_messages: dict[str, str] | None = None
) -> tuple[bool, str]:
    """
    Evalúa un lock contra un personaje para un tipo de acceso específico.

    Versión 2.0 - Sistema de Locks Contextuales:
    - Soporta locks como string simple (backward compatible)
    - Soporta locks como diccionario contextual por access_type
    - Soporta mensajes de error personalizados
    - Soporta lock functions asíncronas

    Args:
        character: Personaje que intenta la acción
        locks: Lock string simple O diccionario de locks contextuales
               Ejemplos:
               - String: "rol(ADMIN)"
               - Dict: {"get": "rol(ADMIN)", "open": "tiene_objeto(llave)"}
        access_type: Tipo de acceso a verificar (get, open, put, take, traverse, etc.)
                    Default: "default"
        lock_messages: Diccionario opcional de mensajes de error personalizados
                      Ejemplo: {"get": "El cofre es demasiado pesado."}

    Returns:
        tuple[bool, str]: (puede_ejecutar, mensaje_error)
                         - (True, "") si pasa el lock
                         - (False, "mensaje") si falla

    Ejemplos:
        >>> # Lock simple (backward compatible)
        >>> can_pass, msg = await can_execute(char, "rol(ADMIN)")

        >>> # Lock contextual
        >>> locks = {"get": "rol(ADMIN)", "open": "tiene_objeto(llave)"}
        >>> can_pass, msg = await can_execute(char, locks, "get")

        >>> # Con mensajes personalizados
        >>> locks = {"get": "rol(SUPERADMIN)"}
        >>> messages = {"get": "El cofre es demasiado pesado para levantarlo."}
        >>> can_pass, msg = await can_execute(char, locks, "get", messages)
    """
    # 1. Normalizar locks a diccionario
    if isinstance(locks, str):
        # Backward compatibility: string simple se convierte a "default"
        if not locks:  # Lock vacío = sin restricción
            return True, ""
        locks_dict = {"default": locks}
    elif isinstance(locks, dict):
        locks_dict = locks
    elif locks is None:
        # None se trata como sin lock
        return True, ""
    else:
        # Tipo inválido, denegar por seguridad
        logging.error(f"Tipo de lock inválido: {type(locks)}")
        return False, "Error en la configuración de permisos."

    # 2. Obtener el lock string para el access_type
    # Primero intenta el tipo específico, luego "default"
    lock_string = locks_dict.get(access_type) or locks_dict.get("default", "")

    # 3. Lock vacío = sin restricción
    if not lock_string:
        return True, ""

    # 4. Evaluar el lock string (con soporte async)
    try:
        # Parsear el string a un árbol AST. `mode='eval'` espera una sola expresión.
        tree = ast.parse(lock_string, mode='eval')

        # Crear una instancia de nuestro evaluador con el contexto del personaje.
        evaluator = LockEvaluator(character)

        # Visitar el árbol para obtener el resultado booleano (ahora async)
        result = evaluator.visit(tree.body)

        # Si el resultado es una corrutina, esperarlo
        if inspect.iscoroutine(result):
            result = await result

        if result:
            return True, ""
        else:
            # 5. Mensaje de error personalizado o genérico
            if lock_messages and access_type in lock_messages:
                error_message = lock_messages[access_type]
            else:
                error_message = "Permiso denegado."

            return False, error_message

    except SyntaxError:
        logging.error(f"Error de sintaxis en el lock string: '{lock_string}'")
        return False, "Error en la definición de permisos de esta acción."
    except Exception:
        logging.exception(f"Error inesperado al evaluar el lock string: '{lock_string}'")
        return False, "Error interno al comprobar los permisos."