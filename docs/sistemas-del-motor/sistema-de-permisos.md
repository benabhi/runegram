---
título: "Sistema de Permisos (Locks)"
categoría: "Sistemas del Motor"
última_actualización: "2025-01-16"
autor: "Proyecto Runegram"
etiquetas: ["permisos", "locks", "seguridad", "roles", "contextuales"]
documentos_relacionados:
  - "sistemas-del-motor/sistema-de-comandos.md"
  - "sistemas-del-motor/sistema-de-prototipos.md"
  - "creacion-de-contenido/creacion-de-items.md"
referencias_código:
  - "src/services/permission_service.py"
  - "commands/player/interaction.py"
  - "commands/player/movement.py"
estado: "actual"
importancia: "crítica"
notas_de_version: "CmdDrop ahora verifica locks con access_type='drop'"
---

# Sistema de Permisos (Locks)

El Sistema de Permisos, o sistema de `locks`, es el "guardián" de Runegram. Es un motor de reglas potente y extensible que determina si un personaje (`Character`) tiene permiso para realizar una acción determinada, como usar un comando, pasar por una salida o coger un objeto.

El diseño está inspirado en los sistemas de `locks` de frameworks de MUDs avanzados como Evennia y se basa en tres pilares: **`lock strings` expresivos**, **locks contextuales por tipo de acción**, y un **motor de evaluación seguro con soporte async**.

## Características Principales

El sistema ofrece las siguientes características:

✅ **Locks Contextuales**: Diferentes restricciones según el tipo de acción (get, put, take, traverse, etc.)
✅ **Lock Functions Asíncronas**: Soporte para funciones de lock que requieren acceso a Redis u otras operaciones async
✅ **Mensajes de Error Personalizados**: Define mensajes específicos para cada tipo de lock
✅ **9 Lock Functions**: Funciones de lock para casos de uso avanzados
✅ **Backward Compatible**: Mantiene compatibilidad total con locks string simples

## 1. Arquitectura General

El sistema se compone de cuatro partes principales, todas encapsuladas en `src/services/permission_service.py`:

1.  **El Parser (basado en `ast`):** El corazón del sistema. En lugar de un parser manual, se utiliza el módulo `ast` (Abstract Syntax Tree) de Python para convertir de forma segura un `lock string` en un árbol de sintaxis que representa su estructura lógica.

2.  **El Evaluador (`LockEvaluator`):** Una clase que "camina" por el árbol de sintaxis generado por `ast` y evalúa el resultado booleano final. Es una caja de arena segura que solo permite ejecutar operadores lógicos (`and`, `or`, `not`) y llamadas a funciones de `lock` pre-aprobadas. **Versión 2.0: Ahora soporta funciones asíncronas.**

3.  **El Registro de Funciones de Lock (`LOCK_FUNCTIONS`):** Un diccionario que mapea los nombres de las funciones permitidas en un `lock string` (ej: `rol`) a las funciones de Python reales que implementan la lógica de comprobación (ej: `_lock_rol`). Puede incluir tanto funciones síncronas como asíncronas.

4.  **Sistema de Access Types (Nuevo en v2.0):** Permite definir locks diferentes según el tipo de acción que se intenta realizar sobre un objeto o entidad (ej: `get`, `put`, `take`, `traverse`, `open`).

## 2. El `Lock String`

Un `lock string` es una cadena de texto que define una o más condiciones que deben cumplirse. Gracias al uso de `ast`, la sintaxis es muy similar a una expresión booleana de Python.

### Operadores Soportados

*   **`and`**: Ambas condiciones deben ser verdaderas.
*   **`or`**: Al menos una de las condiciones debe ser verdadera.
*   **`not`**: Niega el resultado de una condición.
*   **`()`**: Permite agrupar condiciones para controlar el orden de evaluación.

### Funciones de Lock Disponibles

El sistema implementa 9 funciones de `lock` que cubren casos de uso comunes:

#### Funciones Basadas en Roles

*   **`rol(ROL)`**: Comprueba si el rol del personaje es igual o superior al `ROL` especificado.
    *   **Jerarquía:** `SUPERADMIN > ADMIN > JUGADOR`.
    *   Un `SUPERADMIN` pasará las comprobaciones de `rol(ADMIN)` y `rol(JUGADOR)`.
    *   **Ejemplo:** `rol(ADMIN)`
    *   **Tipo:** Síncrona

#### Funciones Basadas en Inventario

*   **`tiene_objeto(clave_prototipo)`**: Comprueba si el personaje lleva un objeto con la `key` especificada en su inventario.
    *   **Ejemplo:** `tiene_objeto(llave_maestra)`
    *   **Tipo:** Síncrona

*   **`cuenta_items(N)`**: Verifica si el personaje tiene al menos N items en su inventario.
    *   **Ejemplo:** `cuenta_items(5)` → Requiere 5 o más items
    *   **Tipo:** Síncrona

*   **`tiene_item_categoria(categoria)`**: Verifica si el personaje tiene al menos un item de la categoría especificada.
    *   **Ejemplo:** `tiene_item_categoria(arma)`
    *   **Tipo:** Síncrona

*   **`tiene_item_tag(tag)`**: Verifica si el personaje tiene al menos un item con el tag especificado.
    *   **Ejemplo:** `tiene_item_tag(magico)`
    *   **Tipo:** Síncrona

#### Funciones Basadas en Ubicación

*   **`en_sala(sala_key)`**: Verifica si el personaje está en una sala específica.
    *   **Ejemplo:** `en_sala(plaza_central)`
    *   **Tipo:** Síncrona

*   **`en_categoria_sala(categoria)`**: Verifica si el personaje está en una sala de cierta categoría.
    *   **Ejemplo:** `en_categoria_sala(templo)`
    *   **Tipo:** Síncrona

*   **`tiene_tag_sala(tag)`**: Verifica si la sala actual tiene un tag específico.
    *   **Ejemplo:** `tiene_tag_sala(sagrado)`
    *   **Tipo:** Síncrona

#### Funciones de Estado

*   **`online()`**: Verifica si el personaje está actualmente conectado.
    *   **Ejemplo:** `online()` → Solo permite acción si el personaje está activo
    *   **Tipo:** Asíncrona (requiere acceso a Redis)
    *   **Nota:** Esta es la primera lock function asíncrona del sistema

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

# Nuevas lock functions (v2.0)

# Solo si está en una sala específica O es admin
"en_sala(templo_sagrado) or rol(ADMIN)"

# Solo si tiene menos de 10 items (usando NOT con cuenta_items)
"not cuenta_items(10)"

# Solo si tiene un arma equipada Y está en zona de combate
"tiene_item_categoria(arma) and tiene_tag_sala(zona_combate)"

# Solo si está online (útil para interacciones entre jugadores)
"online()"

# Combinación compleja: en templo O (tiene arma sagrada Y está online)
"en_categoria_sala(templo) or (tiene_item_tag(sagrado) and online())"
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

## 4. Sistema de Locks Contextuales

El sistema soporta **locks contextuales**, que permiten definir diferentes restricciones según el tipo de acción que se intenta realizar.

### ¿Qué son los Locks Contextuales?

Tradicionalmente, un objeto tenía un único lock que se aplicaba a todas las acciones. Los locks contextuales permiten especificar restricciones diferentes según el **access type** (tipo de acceso).

### Access Types Disponibles

Los access types son strings que identifican el tipo de acción. Los más comunes son:

- **`get`**: Coger un objeto del suelo o sala
- **`drop`**: Dejar un objeto en el suelo
- **`put`**: Meter un objeto dentro de un contenedor
- **`take`**: Sacar un objeto de un contenedor
- **`open`**: Abrir un contenedor cerrado
- **`traverse`**: Atravesar una salida/puerta
- **`use`**: Usar un objeto
- **`default`**: Valor por defecto si no hay access type específico

### Sintaxis: String Simple vs Diccionario

#### Backward Compatibility - String Simple

Los locks string simples siguen funcionando exactamente igual que antes:

```python
# Lock simple (se aplica a TODAS las acciones)
"locks": "rol(ADMIN)"
```

Este lock se convierte internamente a `{"default": "rol(ADMIN)"}` y se aplica cuando no hay un lock específico para el access type solicitado.

#### Locks Contextuales - Diccionario

Para locks contextuales, usa un diccionario donde cada clave es un access type:

```python
# Locks contextuales (diferentes restricciones por acción)
"locks": {
    "get": "rol(SUPERADMIN)",      # Solo SUPERADMIN puede cogerlo
    "put": "",                       # Todos pueden meter cosas
    "take": "tiene_objeto(llave)"   # Necesita llave para sacar
}
```

### Ejemplo Práctico: Cofre con Locks Contextuales

```python
# game_data/item_prototypes.py

"cofre_magico": {
    "name": "un cofre mágico",
    "keywords": ["cofre", "magico"],
    "description": "Un cofre ornamentado con runas brillantes.",
    "is_container": True,
    "capacity": 10,

    # Locks contextuales
    "locks": {
        "get": "rol(SUPERADMIN)",              # Demasiado pesado para cogerlo
        "put": "tiene_objeto(llave_magica)",   # Necesita llave para meter
        "take": "tiene_objeto(llave_magica)"   # Necesita llave para sacar
    },

    # Mensajes de error personalizados (opcional)
    "lock_messages": {
        "get": "El cofre está encantado y firmemente fijado al suelo.",
        "put": "El cofre está sellado con magia. Necesitas la llave mágica.",
        "take": "El cofre está sellado con magia. Necesitas la llave mágica."
    }
}
```

### Mensajes de Error Personalizados

El parámetro `lock_messages` permite definir mensajes de error específicos para cada access type:

```python
"lock_messages": {
    "get": "Mensaje personalizado cuando falla el lock 'get'",
    "put": "Mensaje personalizado cuando falla el lock 'put'",
    "take": "Mensaje personalizado cuando falla el lock 'take'"
}
```

Si no se proporciona un mensaje personalizado, se usa el mensaje genérico: `"Permiso denegado."`

### Uso en Código

```python
from src.services import permission_service

# Lock simple (backward compatible)
can_pass, error_msg = await permission_service.can_execute(
    character,
    "rol(ADMIN)"
)

# Lock contextual con access type
locks = {
    "get": "rol(ADMIN)",
    "open": "tiene_objeto(llave)"
}

can_pass, error_msg = await permission_service.can_execute(
    character,
    locks,
    access_type="get"  # Verifica el lock para "get"
)

# Lock contextual con mensajes personalizados
lock_messages = {
    "get": "El cofre es demasiado pesado para levantarlo."
}

can_pass, error_msg = await permission_service.can_execute(
    character,
    locks,
    access_type="get",
    lock_messages=lock_messages
)

# Si falla, error_msg contendrá el mensaje personalizado
```

### Fallback a "default"

Si se solicita un access type que no existe en el diccionario de locks, el sistema busca la clave `"default"`:

```python
"locks": {
    "default": "rol(ADMIN)",  # Se usa para cualquier access type no especificado
    "open": ""                 # Excepto "open" que tiene lock vacío (sin restricción)
}
```

### Casos de Uso Comunes

#### Contenedor Fijo pero Accesible

```python
"cofre_roble": {
    "locks": {
        "get": "rol(SUPERADMIN)",  # No se puede coger (fijo)
        "put": "",                  # Todos pueden meter cosas
        "take": ""                  # Todos pueden sacar cosas
    }
}
```

#### Contenedor con Llave

```python
"cofre_cerrado": {
    "locks": {
        "get": "rol(SUPERADMIN)",              # Fijo
        "put": "tiene_objeto(llave_cofre)",    # Necesita llave
        "take": "tiene_objeto(llave_cofre)"    # Necesita llave
    }
}
```

#### Objeto que Solo se Puede Coger en Ciertas Salas

```python
"reliquia_sagrada": {
    "locks": {
        "get": "en_categoria_sala(templo) or rol(ADMIN)",
        "drop": "en_categoria_sala(templo) or rol(ADMIN)"
    },
    "lock_messages": {
        "get": "La reliquia rechaza tu toque. Solo puede ser recogida en un lugar sagrado.",
        "drop": "La reliquia rechaza ser abandonada aquí. Debe permanecer en un lugar sagrado."
    }
}
```

#### Salida/Puerta con Lock

```python
# En room_prototypes.py o Exit model
exit = {
    "name": "norte",
    "to_room": "sala_secreta",
    "locks": {
        "traverse": "tiene_objeto(llave_torre) or rol(ADMIN)"
    }
}
```

## 5. Cómo Extender el Sistema

Añadir una nueva función de `lock` es un proceso de tres pasos:

### Función Síncrona

```python
# En src/services/permission_service.py

def _lock_habilidad(character: Character, args: list[str]) -> bool:
    """Verifica si el personaje tiene cierta habilidad con nivel mínimo."""
    if not character or not args:
        return False

    skill_name = args[0]
    min_level = int(args[1]) if len(args) > 1 else 1

    # Lógica de verificación (ejemplo)
    skill_level = character.attributes.get(f"skill_{skill_name}", 0)
    return skill_level >= min_level

# Registrar la función
LOCK_FUNCTIONS = {
    # ... funciones existentes ...
    "habilidad": _lock_habilidad,
}
```

### Función Asíncrona

Si tu lock function necesita acceso a la base de datos, Redis, o cualquier operación asíncrona:

```python
# En src/services/permission_service.py

async def _lock_tiene_quest(character: Character, args: list[str]) -> bool:
    """
    Verifica si el personaje ha completado una quest específica.
    Esta es una lock function asíncrona que requiere acceso a BD.
    """
    if not character or not args:
        return False

    quest_name = args[0]

    # Operación asíncrona (ejemplo)
    from src.services import quest_service
    return await quest_service.has_completed_quest(character.id, quest_name)

# Registrar la función asíncrona
LOCK_FUNCTIONS = {
    # ... funciones existentes ...
    "tiene_quest": _lock_tiene_quest,  # Función asíncrona
}
```

El `LockEvaluator` detecta automáticamente si una función es asíncrona y la maneja apropiadamente usando `await`.

### Usar en Contenido

Una vez registrada, la función de lock está disponible inmediatamente en todos los prototipos:

```python
# game_data/item_prototypes.py

"espada_legendaria": {
    "locks": {
        "get": "habilidad(espadas, 10) or rol(ADMIN)"
    }
}

"recompensa_quest": {
    "locks": {
        "get": "tiene_quest(salvar_aldea)"
    }
}
```

Este diseño hace que el Sistema de Permisos sea una de las herramientas más potentes y escalables del motor de Runegram.

## Resumen de Características

**Características del Sistema:**
- ✅ Sistema de locks contextuales por access_type
- ✅ Soporte para lock functions asíncronas
- ✅ Mensajes de error personalizados por access type
- ✅ 9 lock functions disponibles
- ✅ Backward compatible con locks string simples

**Migración:**
- Los locks string simples siguen funcionando sin cambios
- Para aprovechar locks contextuales, convierte el lock a diccionario
- Para mensajes personalizados, añade campo `lock_messages` en prototipos

**Archivos Relevantes:**
- `src/services/permission_service.py` - Core del sistema
- `commands/player/interaction.py` - Usa access types (get, drop, put, take)
- `commands/player/movement.py` - Usa access type (traverse)
- `game_data/item_prototypes.py` - Ejemplos de locks contextuales

## Ver También

- [Sistema de Comandos](sistema-de-comandos.md) - Uso de locks en comandos
- [Sistema de Prototipos](sistema-de-prototipos.md) - Uso de locks en prototipos
- [Creación de Items](../creacion-de-contenido/creacion-de-items.md) - Ejemplos prácticos de locks
- [Construcción de Salas](../creacion-de-contenido/construccion-de-salas.md) - Locks en salidas/puertas
