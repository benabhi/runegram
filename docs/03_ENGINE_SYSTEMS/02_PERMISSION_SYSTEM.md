# Sistema de Permisos (Locks)

El Sistema de Permisos, o sistema de `locks`, es el "guardián" de Runegram. Es un motor de reglas potente y extensible que determina si un personaje (`Character`) tiene permiso para realizar una acción determinada, como usar un comando, pasar por una salida o coger un objeto.

El diseño está inspirado en los sistemas de `locks` de frameworks de MUDs avanzados como Evennia y se basa en dos pilares: **`lock strings` expresivos** y un **motor de evaluación seguro**.

## 1. Arquitectura General

El sistema se compone de tres partes principales, todas encapsuladas en `src/services/permission_service.py`:

1.  **El Parser (basado en `ast`):** El corazón del sistema. En lugar de un parser manual, se utiliza el módulo `ast` (Abstract Syntax Tree) de Python para convertir de forma segura un `lock string` en un árbol de sintaxis que representa su estructura lógica.
2.  **El Evaluador (`LockEvaluator`):** Una clase que "camina" por el árbol de sintaxis generado por `ast` y evalúa el resultado booleano final. Es una caja de arena segura que solo permite ejecutar operadores lógicos (`and`, `or`, `not`) y llamadas a funciones de `lock` pre-aprobadas.
3.  **El Registro de Funciones de Lock (`LOCK_FUNCTIONS`):** Un diccionario que mapea los nombres de las funciones permitidas en un `lock string` (ej: `rol`) a las funciones de Python reales que implementan la lógica de comprobación (ej: `_lock_rol`).

## 2. El `Lock String`

Un `lock string` es una cadena de texto que define una o más condiciones que deben cumplirse. Gracias al uso de `ast`, la sintaxis es muy similar a una expresión booleana de Python.

### Operadores Soportados

*   **`and`**: Ambas condiciones deben ser verdaderas.
*   **`or`**: Al menos una de las condiciones debe ser verdadera.
*   **`not`**: Niega el resultado de una condición.
*   **`()`**: Permite agrupar condiciones para controlar el orden de evaluación.

### Funciones de Lock Disponibles

Actualmente, el sistema implementa las siguientes funciones de `lock`:

*   **`rol(ROL)`**: Comprueba si el rol del personaje es igual o superior al `ROL` especificado.
    *   **Jerarquía:** `SUPERADMIN > ADMIN > JUGADOR`.
    *   Un `SUPERADMIN` pasará las comprobaciones de `rol(ADMIN)` y `rol(JUGADOR)`.
    *   **Ejemplo:** `rol(ADMIN)`

*   **`tiene_objeto(clave_prototipo)`**: Comprueba si el personaje lleva un objeto con la `key` especificada en su inventario.
    *   **Ejemplo:** `tiene_objeto(llave_maestra)`

### Ejemplos de `Lock Strings` Complejos

```python
# Solo un ADMIN o superior puede pasar.
"rol(ADMIN)"

# El personaje debe llevar la llave de la torre en su inventario.
"tiene_objeto(llave_torre)"

# Debe ser un ADMIN Y llevar la llave.
"rol(ADMIN) and tiene_objeto(llave_torre)"

# Debe ser un SUPERADMIN O llevar la llave especial.
"rol(SUPERADMIN) or tiene_objeto(llave_especial)"

# Cualquiera puede pasar, EXCEPTO los JUGADORES (es decir, solo ADMINS y superiores).
"not rol(JUGADOR)"

# Un lock complejo: debe ser un ADMIN que lleve la llave, O ser un SUPERADMIN.
"(rol(ADMIN) and tiene_objeto(llave_gremio)) or rol(SUPERADMIN)"
```

## 3. Flujo de Evaluación de un Permiso

Cuando una parte del juego necesita comprobar un permiso (ej: el `dispatcher` para un comando, o `CmdMove` para una salida), se llama a `permission_service.can_execute(character, lock_string)`.

1.  **Parseo:** `ast.parse(lock_string, mode='eval')` convierte el string en un árbol de nodos. Si la sintaxis es inválida, se lanza un `SyntaxError`.
2.  **Creación del Evaluador:** Se crea una instancia de `LockEvaluator`, pasándole el objeto `character` que intenta la acción. Este `character` es el contexto contra el cual se evaluarán todas las condiciones.
3.  **Recorrido del Árbol:** El método `evaluator.visit(tree)` comienza a "caminar" por el árbol.
    *   Si encuentra un nodo `BoolOp` (`and`/`or`), evalúa recursivamente sus hijos y combina los resultados.
    *   Si encuentra un nodo `UnaryOp` (`not`), evalúa recursivamente su operando y niega el resultado.
    *   Si encuentra un nodo `Call` (una función como `rol(...)`), busca el nombre (`rol`) en el registro `LOCK_FUNCTIONS`. Si lo encuentra, ejecuta la función de Python correspondiente (`_lock_rol`), pasándole el `character` y los argumentos parseados. Si no lo encuentra, devuelve `False`.
    *   Cualquier otro tipo de nodo (asignaciones, bucles, etc.) no está permitido y lanzará un `TypeError`, lo que garantiza la seguridad del sistema.
4.  **Resultado:** La función `can_execute` devuelve una tupla `(True, "")` si el resultado final es verdadero, o `(False, "Mensaje de error")` si es falso.

## 4. Cómo Extender el Sistema

Añadir un nuevo tipo de `lock` (ej: `habilidad(magia)>10`) es un proceso de tres pasos:

1.  **Crear la Lógica:** Escribir una nueva función de chequeo en `permission_service.py`, similar a `_lock_rol`. Esta función recibiría `character` y una lista de argumentos (`["magia>10"]`).
2.  **Registrar la Función:** Añadir la nueva función al diccionario `LOCK_FUNCTIONS` con su nombre en minúsculas.
    ```python
    LOCK_FUNCTIONS = {
        # ...
        "habilidad": _lock_habilidad,
    }
    ```
3.  **Usar en Contenido:** ¡Listo! Ahora los diseñadores pueden empezar a escribir `lock strings` como `"habilidad(magia)>10"` en sus prototipos.

Este diseño hace que el Sistema de Permisos sea una de las herramientas más potentes y escalables del motor de Runegram.