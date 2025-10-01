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
"""

import logging
import ast # Módulo para parsear la sintaxis de Python de forma segura
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

# ==============================================================================
# REGISTRO DE FUNCIONES DE LOCK
# ==============================================================================

LOCK_FUNCTIONS = {
    "rol": _lock_rol,
    "tiene_objeto": _lock_tiene_objeto,
}

# ==============================================================================
# MOTOR DEL SERVICIO DE PERMISOS (BASADO EN AST)
# ==============================================================================

class LockEvaluator(ast.NodeVisitor):
    """
    Un visitante de nodos AST que evalúa un lock string de forma segura.
    Recorre el árbol de sintaxis y calcula el resultado booleano final.
    """
    def __init__(self, character: Character):
        self.character = character

    def visit_BoolOp(self, node: ast.BoolOp) -> bool:
        """Maneja operadores `and` y `or`."""
        # Obtenemos los resultados de cada sub-expresión.
        sub_results = [self.visit(value) for value in node.values]
        if isinstance(node.op, ast.And):
            return all(sub_results)
        elif isinstance(node.op, ast.Or):
            return any(sub_results)
        return False

    def visit_UnaryOp(self, node: ast.UnaryOp) -> bool:
        """Maneja el operador `not`."""
        if isinstance(node.op, ast.Not):
            return not self.visit(node.operand)
        return False

    def visit_Call(self, node: ast.Call) -> bool:
        """Maneja las llamadas a funciones de lock (ej: `rol(...)`)."""
        func_name = node.func.id.lower()
        if func_name in LOCK_FUNCTIONS:
            # Evaluamos los argumentos (que también son nodos AST).
            args = [self.visit(arg) for arg in node.args]
            lock_func = LOCK_FUNCTIONS[func_name]
            return lock_func(self.character, args)

        logging.warning(f"Función de lock desconocida llamada: {func_name}")
        return False # Falla de forma segura si la función no está registrada.

    def visit_Constant(self, node: ast.Constant) -> any:
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

async def can_execute(character: Character, lock_string: str) -> tuple[bool, str]:
    """
    Evalúa un `lock_string` contra un personaje para ver si puede pasar el lock.
    """
    if not lock_string:
        return True, ""

    try:
        # 1. Parsear el string a un árbol AST. `mode='eval'` espera una sola expresión.
        tree = ast.parse(lock_string, mode='eval')

        # 2. Crear una instancia de nuestro evaluador con el contexto del personaje.
        evaluator = LockEvaluator(character)

        # 3. Visitar el árbol para obtener el resultado booleano.
        result = evaluator.visit(tree.body)

        if result:
            return True, ""
        else:
            return False, "Permiso denegado."

    except SyntaxError:
        logging.error(f"Error de sintaxis en el lock string: '{lock_string}'")
        return False, "Error en la definición de permisos de esta acción."
    except Exception as e:
        logging.exception(f"Error inesperado al evaluar el lock string: '{lock_string}'")
        return False, "Error interno al comprobar los permisos."