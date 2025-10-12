# 📋 ANÁLISIS Y PROPUESTA: SISTEMA DE LOCKS CONTEXTUALES PARA RUNEGRAM

> **Fecha de análisis**: 2025-01-11
> **Estado**: Análisis completo - Pendiente de aprobación e implementación
> **Inspiración**: Sistema de Locks de Evennia
> **Objetivo**: Extender el sistema de locks actual con funcionalidades contextuales

---

## 📑 TABLA DE CONTENIDOS

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Análisis del Sistema de Evennia](#análisis-del-sistema-de-evennia)
3. [Análisis del Sistema Actual de Runegram](#análisis-del-sistema-actual-de-runegram)
4. [Comparación de Diferencias Clave](#comparación-de-diferencias-clave)
5. [Propuesta: Locks Contextuales](#propuesta-locks-contextuales)
6. [Lock Functions Implementables](#lock-functions-implementables)
7. [Plan de Implementación Detallado](#plan-de-implementación-detallado)
8. [Archivos Afectados](#archivos-afectados)
9. [Ejemplos de Uso Práctico](#ejemplos-de-uso-práctico)
10. [Compatibilidad y Migración](#compatibilidad-y-migración)
11. [Testing](#testing)
12. [Decisiones Pendientes](#decisiones-pendientes)

---

## 🎯 RESUMEN EJECUTIVO

### Problema Identificado

El sistema de locks actual de Runegram es funcional pero limitado:
- ✅ **Funciona**: Evaluación booleana con AST, seguro y extensible
- ❌ **Limitado**: Un solo lock por entidad (comando, item, exit, canal)
- ❌ **No contextual**: No permite locks diferentes según la acción

**Ejemplo del problema actual**:
```python
# game_data/item_prototypes.py
"cofre_roble": {
    "locks": "rol(SUPERADMIN)",  # ¿Esto es para coger, abrir, o meter?
    "is_container": True
}
```

**Confusión semántica**:
- El lock actual se usa solo para el comando `/coger`
- Pero un contenedor tiene múltiples interacciones: `coger`, `abrir`, `meter`, `sacar`
- No hay forma de especificar locks diferentes para cada acción

### Solución Propuesta: Locks Contextuales

Inspirados en Evennia, proponemos un sistema de **locks con tipos de acceso** (access types):

```python
# PROPUESTA - Sistema contextual
"cofre_roble": {
    "locks": {
        "get": "rol(SUPERADMIN)",           # Solo SUPERADMIN puede cogerlo
        "open": "tiene_objeto(llave_roble)", # Cualquiera con llave puede abrirlo
        "put": "",                           # Todos pueden meter cosas
        "take": ""                           # Todos pueden sacar cosas
    },
    "is_container": True
}
```

### Beneficios Clave

1. **Claridad semántica**: Cada acción tiene su propio lock explícito
2. **Flexibilidad**: Diferentes permisos según la acción
3. **Compatibilidad**: Sistema actual sigue funcionando
4. **Extensibilidad**: Fácil agregar nuevos tipos de acceso
5. **Coherencia con Evennia**: Inspirado en sistemas MUD consolidados

### Factibilidad

**✅ MUY FACTIBLE** por las siguientes razones:

1. **Motor de evaluación reutilizable**: El `permission_service` actual ya tiene todo lo necesario
2. **Cambios localizados**: Solo afecta a puntos de verificación de permisos
3. **Backward compatible**: Lock string simple sigue funcionando como ahora
4. **Sin cambios en BD**: No requiere migraciones (locks ya es un campo flexible)

---

## 📖 ANÁLISIS DEL SISTEMA DE EVENNIA

### Filosofía General

Evennia usa un enfoque de **"lockdown"**: todo está bloqueado por defecto a menos que se permita explícitamente.

### Sintaxis de Locks

```python
access_type: [NOT] lockfunc1([arg1,...]) [AND|OR] [NOT] lockfunc2([arg1,...])
```

**Componentes**:
- `access_type`: El tipo de acción que controla (get, delete, edit, control, examine, etc.)
- `lockfunc`: Función de verificación (perm, attr, id, tag, etc.)
- Operadores: `AND`, `OR`, `NOT`

### Ejemplos de Evennia

```python
# Solo el objeto #34 puede borrar esto
"delete:id(34)"

# Cualquiera que no esté marcado como "very_weak" O sea Admin puede cogerlo
"get: not attr(very_weak) or perm(Admin)"

# Caja pesada que solo personajes fuertes pueden levantar
box.locks.add("get:attr_gt(strength, 50)")
```

### Access Types Comunes en Evennia

- `get`: Coger un objeto
- `drop`: Dejar un objeto
- `delete`: Borrar un objeto
- `edit`: Editar un objeto
- `control`: Control completo sobre un objeto
- `examine`: Ver información detallada
- `call`: Ejecutar un comando
- `msg`: Enviar mensaje a un objeto
- `puppet`: Controlar un objeto (como personaje)

### Características Clave de Evennia

1. **Múltiples locks por objeto**: Un objeto puede tener `get:`, `drop:`, `delete:`, etc.
2. **Mensajes personalizados**: `obj.db.get_err_msg = "No eres suficientemente fuerte"`
3. **Lock functions extensibles**: Sistema de plugins para agregar nuevas funciones
4. **Verificación centralizada**: `obj.access(accessing_obj, 'access_type')`

---

## 🔍 ANÁLISIS DEL SISTEMA ACTUAL DE RUNEGRAM

### Arquitectura Actual

**Archivo**: `src/services/permission_service.py`

#### Componentes

1. **Parser basado en AST**: Convierte lock string a árbol de sintaxis abstracta
2. **Evaluador (`LockEvaluator`)**: Recorre el árbol y evalúa resultado booleano
3. **Registro de funciones (`LOCK_FUNCTIONS`)**: Mapea nombres a implementaciones
4. **Función pública (`can_execute`)**: Interfaz de verificación

#### Lock Functions Actuales

```python
LOCK_FUNCTIONS = {
    "rol": _lock_rol,              # Verifica jerarquía de roles (JUGADOR < ADMIN < SUPERADMIN)
    "tiene_objeto": _lock_tiene_objeto,  # Verifica si tiene item en inventario
}
```

#### Sintaxis Soportada

```python
# Operadores booleanos
"rol(ADMIN)"
"rol(ADMIN) and tiene_objeto(llave)"
"rol(SUPERADMIN) or tiene_objeto(llave_maestra)"
"not rol(JUGADOR)"

# Agrupación con paréntesis
"(rol(ADMIN) and tiene_objeto(llave)) or rol(SUPERADMIN)"
```

### Uso Actual en el Código

#### 1. Comandos (Command.lock)

```python
# commands/command.py
class Command:
    lock: str = ""  # Lock string único por comando
```

**Verificación en dispatcher**:
```python
# src/handlers/player/dispatcher.py:216
can_run, error_message = await permission_service.can_execute(character, found_cmd.lock)
```

#### 2. Salidas (Exit.locks)

```python
# src/models/exit.py
class Exit(Base):
    locks = Column(String, nullable=False, default="")
```

**Verificación en movimiento**:
```python
# commands/player/movement.py:66
can_pass, error_message = await permission_service.can_execute(character, target_exit.locks)
```

#### 3. Items (prototipo["locks"])

```python
# game_data/item_prototypes.py
"cofre_roble": {
    "locks": "rol(SUPERADMIN)",  # Lock único
}
```

**Verificación en /coger**:
```python
# commands/player/interaction.py:245-246
lock_string = item_to_get.prototype.get("locks", "")
can_pass, error_message = await permission_service.can_execute(character, lock_string)
```

**Verificación en /meter y /sacar**:
```python
# commands/player/interaction.py:356-357 (meter)
# commands/player/interaction.py:436-437 (sacar)
lock_string = container.prototype.get("locks", "")
can_pass, _ = await permission_service.can_execute(character, lock_string)
```

#### 4. Salas (Room.locks)

```python
# src/models/room.py
class Room(Base):
    locks = Column(String, nullable=False, default="")
```

**Nota**: Actualmente NO se usa en el código, pero está preparado para futuras funcionalidades.

#### 5. Canales (prototipo["lock"] y prototipo["audience"])

```python
# game_data/channel_prototypes.py
"moderacion": {
    "lock": "rol(ADMIN)",      # Quién puede escribir
    "audience": "rol(ADMIN)"   # Quién puede recibir
}
```

**Verificación**:
```python
# src/services/channel_service.py
# Verifica lock para suscribirse y escribir
# Verifica audience para recibir mensajes
```

### Limitaciones Actuales

1. **Un solo lock por entidad**: No hay forma de diferenciar acciones
2. **Semántica implícita**: En items, el lock se usa solo para `/coger`, pero no está documentado
3. **No hay lock para contenedores específicos**: Meter/sacar reutilizan el mismo lock
4. **Mensajes de error genéricos**: No hay forma de personalizar mensajes por tipo de acción

---

## ⚖️ COMPARACIÓN DE DIFERENCIAS CLAVE

| Aspecto | Evennia | Runegram Actual | Propuesta Runegram |
|---------|---------|-----------------|-------------------|
| **Locks por entidad** | Múltiples (get, drop, delete, etc.) | Uno solo | Múltiples (locks dict) |
| **Sintaxis** | `access_type:lock_expr` | `lock_expr` | `{"access_type": "lock_expr"}` |
| **Parser** | Custom parser | AST de Python | AST de Python (sin cambios) |
| **Verificación** | `obj.access(who, 'type')` | `can_execute(who, lock_str)` | `can_execute(who, lock_str, access_type)` |
| **Mensajes error** | Personalizables por lock | Genéricos | Personalizables (futuro) |
| **Extensibilidad** | Plugin system | Registro manual | Registro manual |
| **Backward compat** | N/A | N/A | ✅ Lock string simple sigue funcionando |

### Diferencias Filosóficas

**Evennia**:
- Orientado a objetos puro (todo es un objeto con locks)
- Sistema más complejo y genérico
- Pensado para builders no programadores

**Runegram**:
- Híbrido: prototipos (TOML/Python) + instancias (BD)
- Sistema más simple y específico
- Pensado para desarrolladores que editan archivos Python

**Propuesta**:
- Mantener la simplicidad de Runegram
- Incorporar la claridad contextual de Evennia
- No sobre-ingenierizar: solo lo necesario

---

## 🚀 PROPUESTA: LOCKS CONTEXTUALES

### Concepto Central

Permitir que una entidad (item, exit, room) tenga **múltiples locks según el tipo de acceso**.

### Sintaxis Propuesta

#### Opción A: Diccionario de Locks (RECOMENDADA)

```python
# Prototipos
"cofre_roble": {
    "locks": {
        "get": "rol(SUPERADMIN)",           # Solo SUPERADMIN puede cogerlo (es muy pesado)
        "open": "tiene_objeto(llave_roble)", # Cualquiera con llave puede abrirlo
        "close": "tiene_objeto(llave_roble)", # Cualquiera con llave puede cerrarlo
        "put": "",                           # Todos pueden meter cosas (sin lock)
        "take": ""                           # Todos pueden sacar cosas (sin lock)
    },
    "is_container": True
}

# Exits
class Exit(Base):
    locks = Column(String, default="")  # Sigue siendo string, pero se parsea a JSON
```

**Ventajas**:
- Clara separación de acciones
- Fácil de leer y mantener
- Compatible con JSON (se puede guardar en BD como JSONB si se necesita)

**Desventajas**:
- Requiere modificar parseo de locks en código Python

#### Opción B: String con Prefijos (estilo Evennia)

```python
# Prototipos
"cofre_roble": {
    "locks": "get:rol(SUPERADMIN);open:tiene_objeto(llave_roble);put:;take:"
}
```

**Ventajas**:
- Similar a Evennia
- Se guarda fácilmente como string en BD

**Desventajas**:
- Menos legible en Python
- Requiere parser adicional para separar por `;` y `:`

### Recomendación: **Opción A (Diccionario)**

**Razones**:
1. Más pythónico y legible
2. Mejor integración con prototipos existentes
3. Validación más fácil (type hints)
4. Extensible con IDE autocompletion

### Compatibilidad hacia Atrás

**Problema**: El sistema actual usa lock como string simple.

**Solución**: Detección de tipo

```python
def normalize_locks(locks_input) -> dict[str, str]:
    """
    Normaliza locks a formato de diccionario.

    Soporta:
    - String simple (backward compat): "rol(ADMIN)" → {"default": "rol(ADMIN)"}
    - Diccionario: {"get": "...", "open": "..."} → sin cambios
    """
    if isinstance(locks_input, str):
        # Backward compatibility: string simple se convierte a "default"
        return {"default": locks_input}
    elif isinstance(locks_input, dict):
        return locks_input
    else:
        return {}
```

**Uso**:
```python
# Código antiguo (sigue funcionando)
"espada": {
    "locks": "rol(ADMIN)"  # Se convierte a {"default": "rol(ADMIN)"}
}

# Código nuevo (contextual)
"cofre": {
    "locks": {
        "get": "rol(SUPERADMIN)",
        "open": "tiene_objeto(llave)"
    }
}
```

### Access Types Propuestos para Runegram

#### Items

| Access Type | Descripción | Ejemplo |
|------------|-------------|---------|
| `get` | Coger del suelo | Solo fuertes pueden levantar objeto pesado |
| `drop` | Dejar en el suelo | No se puede soltar un objeto maldito |
| `put` | Meter en contenedor | Solo el dueño puede meter cosas |
| `take` | Sacar de contenedor | Solo con llave puedes sacar |
| `open` | Abrir contenedor | Necesitas llave o ser ladrón |
| `close` | Cerrar contenedor | Necesitas llave |
| `look` | Mirar detalles | Información oculta solo para magos |
| `use` | Usar objeto (futuro) | Solo guerreros pueden usar armas |
| `default` | Fallback genérico | Si no hay lock específico |

#### Exits

| Access Type | Descripción | Ejemplo |
|------------|-------------|---------|
| `traverse` | Atravesar salida | Solo admins pueden pasar |
| `look` | Ver descripción de salida | Puerta secreta invisible para no-rogues |
| `default` | Fallback genérico | Lock actual |

#### Rooms

| Access Type | Descripción | Ejemplo |
|------------|-------------|---------|
| `enter` | Entrar a la sala (futuro) | Solo miembros del gremio |
| `teleport_to` | Teletransportarse aquí | Solo admins |
| `look` | Ver descripción | Sala invisible |
| `default` | Fallback genérico | Lock de sala |

#### Commands

| Access Type | Descripción | Ejemplo |
|------------|-------------|---------|
| `execute` | Ejecutar comando | Lock actual |
| `default` | Fallback genérico | Mismo que execute |

**Nota**: Comandos probablemente no necesiten locks contextuales (solo `execute`), pero se mantiene la arquitectura consistente.

---

## 🔧 LOCK FUNCTIONS IMPLEMENTABLES

### Con lo que YA tenemos desarrollado

Estas lock functions se pueden implementar **inmediatamente** con los modelos y servicios existentes:

#### 1. **`en_sala(sala_key)` - Character está en sala específica**

```python
def _lock_en_sala(character: Character, args: list[str]) -> bool:
    """Verifica si el personaje está en una sala específica."""
    if not character or not character.room or not args:
        return False

    sala_key = args[0]
    return character.room.key == sala_key

# Uso
"locks": {
    "use": "en_sala(templo_sagrado)"  # Solo se puede usar en el templo
}
```

#### 2. **`en_categoria_sala(categoria)` - Character está en sala de categoría**

```python
def _lock_en_categoria_sala(character: Character, args: list[str]) -> bool:
    """Verifica si el personaje está en una sala de cierta categoría."""
    if not character or not character.room or not args:
        return False

    categoria = args[0]
    return character.room.category == categoria

# Uso
"locks": {
    "use": "en_categoria_sala(ciudad)"  # Solo en ciudades
}
```

#### 3. **`tiene_tag_sala(tag)` - Sala actual tiene tag**

```python
def _lock_tiene_tag_sala(character: Character, args: list[str]) -> bool:
    """Verifica si la sala actual tiene un tag específico."""
    if not character or not character.room or not args:
        return False

    tag = args[0]
    return tag in character.room.tags

# Uso
"locks": {
    "open": "tiene_tag_sala(magica)"  # Solo en salas mágicas
}
```

#### 4. **`cuenta_items(min_count)` - Tiene N o más items en inventario**

```python
def _lock_cuenta_items(character: Character, args: list[str]) -> bool:
    """Verifica si el personaje tiene al menos N items."""
    if not character or not args:
        return False

    min_count = int(args[0])
    return len(character.items) >= min_count

# Uso
"locks": {
    "get": "not cuenta_items(10)"  # Solo si tiene menos de 10 items
}
```

#### 5. **`tiene_item_categoria(categoria)` - Tiene item de categoría**

```python
def _lock_tiene_item_categoria(character: Character, args: list[str]) -> bool:
    """Verifica si el personaje tiene un item de cierta categoría."""
    if not character or not args:
        return False

    categoria = args[0]
    return any(item.category == categoria for item in character.items)

# Uso
"locks": {
    "traverse": "tiene_item_categoria(arma)"  # Debe estar armado
}
```

#### 6. **`tiene_item_tag(tag)` - Tiene item con tag específico**

```python
def _lock_tiene_item_tag(character: Character, args: list[str]) -> bool:
    """Verifica si el personaje tiene un item con un tag específico."""
    if not character or not args:
        return False

    tag = args[0]
    return any(tag in item.tags for item in character.items)

# Uso
"locks": {
    "open": "tiene_item_tag(magica)"  # Necesita item mágico
}
```

#### 7. **`es_owner(item)` - Es dueño del objeto (futuro)**

```python
def _lock_es_owner(character: Character, args: list[str]) -> bool:
    """
    Verifica si el personaje es dueño de un objeto.

    Nota: Requiere agregar campo 'owner_id' a Item en el futuro.
    """
    # Por ahora retorna True (placeholder)
    # Implementación real requiere:
    # - Agregar Item.owner_id (ForeignKey a Character)
    # - Migración de BD
    return True

# Uso futuro
"locks": {
    "take": "es_owner(self)"  # Solo el dueño puede sacar sus cosas
}
```

#### 8. **`online()` - Character está conectado**

```python
async def _lock_online(character: Character, args: list[str]) -> bool:
    """Verifica si el personaje está actualmente conectado."""
    if not character:
        return False

    from src.services import online_service
    return await online_service.is_character_online(character.id)

# Uso (para locks dinámicos en el futuro)
"locks": {
    "look": "online()"  # Solo personajes conectados
}
```

**Nota**: Esta función es **async**, lo que requiere modificar el sistema de evaluación. Ver "Decisiones Pendientes".

#### 9. **`suscrito_canal(canal_key)` - Suscrito a canal**

```python
def _lock_suscrito_canal(character: Character, args: list[str]) -> bool:
    """Verifica si el personaje está suscrito a un canal."""
    if not character or not args:
        return False

    canal_key = args[0]
    # Requiere acceso a CharacterSetting
    # Por ahora placeholder
    return False  # TODO: implementar cuando sea necesario

# Uso futuro
"locks": {
    "enter": "suscrito_canal(gremio_magos)"  # Solo miembros del gremio
}
```

### Lock Functions que requieren desarrollo futuro

Estas requieren sistemas que aún no existen:

#### 10. **`attr(nombre)` y `attr_gt(nombre, valor)` - Atributos de personaje**

**Requiere**: Sistema de atributos/stats (fuerza, inteligencia, etc.)

```python
# Futuro
"locks": {
    "get": "attr_gt(fuerza, 50)",  # Solo si fuerza > 50
    "use": "attr(tiene_magia)"      # Solo si tiene atributo 'tiene_magia'
}
```

#### 11. **`habilidad(nombre, nivel)` - Nivel de habilidad**

**Requiere**: Sistema de habilidades/skills

```python
# Futuro
"locks": {
    "open": "habilidad(lockpicking, 30)",  # Nivel 30+ en ganzúa
    "use": "habilidad(magia_arcana, 50)"   # Nivel 50+ en magia
}
```

#### 12. **`quest_completada(quest_id)` - Quest completada**

**Requiere**: Sistema de quests

```python
# Futuro
"locks": {
    "traverse": "quest_completada(rescate_princesa)"
}
```

#### 13. **`faccion(faccion_nombre)` - Miembro de facción**

**Requiere**: Sistema de facciones

```python
# Futuro
"locks": {
    "enter": "faccion(gremio_ladrones)"
}
```

### Resumen de Implementabilidad

| Lock Function | Estado | Prioridad | Requiere |
|--------------|--------|-----------|----------|
| `en_sala()` | ✅ Listo | Alta | Nada |
| `en_categoria_sala()` | ✅ Listo | Media | Nada |
| `tiene_tag_sala()` | ✅ Listo | Media | Nada |
| `cuenta_items()` | ✅ Listo | Media | Nada |
| `tiene_item_categoria()` | ✅ Listo | Alta | Nada |
| `tiene_item_tag()` | ✅ Listo | Alta | Nada |
| `es_owner()` | ⏳ Parcial | Media | Campo Item.owner_id |
| `online()` | ⏳ Async | Baja | Soporte async en evaluator |
| `suscrito_canal()` | ⏳ Parcial | Baja | Acceso a CharacterSetting |
| `attr()` / `attr_gt()` | ❌ Futuro | Baja | Sistema de atributos |
| `habilidad()` | ❌ Futuro | Baja | Sistema de habilidades |
| `quest_completada()` | ❌ Futuro | Baja | Sistema de quests |
| `faccion()` | ❌ Futuro | Baja | Sistema de facciones |

---

## 📂 PLAN DE IMPLEMENTACIÓN DETALLADO

### Fase 1: Refactorización del Sistema de Locks (CORE)

**Objetivo**: Soportar locks contextuales sin romper funcionalidad existente.

#### 1.1. Modificar `permission_service.py`

**Cambios en la firma de `can_execute`**:

```python
# ANTES
async def can_execute(character: Character, lock_string: str) -> tuple[bool, str]:
    """Evalúa un lock_string contra un personaje."""

# DESPUÉS
async def can_execute(
    character: Character,
    locks: str | dict[str, str],  # Acepta string o dict
    access_type: str = "default"  # Tipo de acceso a verificar
) -> tuple[bool, str]:
    """
    Evalúa un lock contra un personaje para un tipo de acceso específico.

    Args:
        character: Personaje que intenta la acción
        locks: Lock string simple O diccionario de locks contextuales
        access_type: Tipo de acceso a verificar (get, open, traverse, etc.)

    Returns:
        (puede_ejecutar, mensaje_error)
    """
```

**Implementación**:

```python
async def can_execute(
    character: Character,
    locks: str | dict[str, str],
    access_type: str = "default"
) -> tuple[bool, str]:
    """Evalúa un lock contra un personaje."""

    # 1. Normalizar locks a diccionario
    if isinstance(locks, str):
        # Backward compatibility: string simple
        if not locks:  # Lock vacío = sin restricción
            return True, ""
        locks_dict = {"default": locks}
    elif isinstance(locks, dict):
        locks_dict = locks
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

    # 4. Evaluar el lock string (código existente)
    try:
        tree = ast.parse(lock_string, mode='eval')
        evaluator = LockEvaluator(character)
        result = evaluator.visit(tree.body)

        if result:
            return True, ""
        else:
            return False, "Permiso denegado."

    except SyntaxError:
        logging.error(f"Error de sintaxis en lock: '{lock_string}'")
        return False, "Error en la definición de permisos."
    except Exception:
        logging.exception(f"Error al evaluar lock: '{lock_string}'")
        return False, "Error interno al comprobar permisos."
```

#### 1.2. Agregar nuevas Lock Functions

**Archivo**: `src/services/permission_service.py`

```python
# Después de las funciones existentes (_lock_rol, _lock_tiene_objeto)

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
    """Verifica si el personaje tiene al menos N items."""
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

# Actualizar el registro
LOCK_FUNCTIONS = {
    "rol": _lock_rol,
    "tiene_objeto": _lock_tiene_objeto,
    # Nuevas funciones
    "en_sala": _lock_en_sala,
    "en_categoria_sala": _lock_en_categoria_sala,
    "tiene_tag_sala": _lock_tiene_tag_sala,
    "cuenta_items": _lock_cuenta_items,
    "tiene_item_categoria": _lock_tiene_item_categoria,
    "tiene_item_tag": _lock_tiene_item_tag,
}
```

### Fase 2: Actualizar Comandos de Interacción

**Objetivo**: Usar locks contextuales en comandos que interactúan con items.

#### 2.1. Modificar `/coger` (CmdGet)

**Archivo**: `commands/player/interaction.py:245-249`

```python
# ANTES
lock_string = item_to_get.prototype.get("locks", "")
can_pass, error_message = await permission_service.can_execute(character, lock_string)

# DESPUÉS
locks = item_to_get.prototype.get("locks", "")
can_pass, error_message = await permission_service.can_execute(
    character,
    locks,
    access_type="get"  # 🆕 Especificamos el tipo de acceso
)
```

#### 2.2. Modificar `/meter` (CmdPut)

**Archivo**: `commands/player/interaction.py:356-360`

```python
# ANTES
lock_string = container.prototype.get("locks", "")
can_pass, _ = await permission_service.can_execute(character, lock_string)

# DESPUÉS
locks = container.prototype.get("locks", "")
can_pass, error_message = await permission_service.can_execute(
    character,
    locks,
    access_type="put"  # 🆕 Meter en contenedor
)

# Mensaje personalizado
if not can_pass:
    await message.answer(error_message or f"No puedes meter cosas en {container.get_name()}.")
    return
```

#### 2.3. Modificar `/sacar` (CmdTake)

**Archivo**: `commands/player/interaction.py:436-440`

```python
# ANTES
lock_string = container.prototype.get("locks", "")
can_pass, _ = await permission_service.can_execute(character, lock_string)

# DESPUÉS
locks = container.prototype.get("locks", "")
can_pass, error_message = await permission_service.can_execute(
    character,
    locks,
    access_type="take"  # 🆕 Sacar de contenedor
)

# Mensaje personalizado
if not can_pass:
    await message.answer(error_message or f"No puedes sacar cosas de {container.get_name()}.")
    return
```

#### 2.4. Modificar `/dejar` (CmdDrop) - Futuro

**Archivo**: `commands/player/interaction.py:277-321`

**Nota**: Actualmente `/dejar` no verifica locks. En el futuro se podría agregar:

```python
# FUTURO (si se desea)
locks = item_to_drop.prototype.get("locks", "")
can_pass, error_message = await permission_service.can_execute(
    character,
    locks,
    access_type="drop"
)

if not can_pass:
    await message.answer(error_message or "No puedes soltar este objeto.")
    return
```

#### 2.5. Modificar `/mirar` item (CmdLook) - Futuro

**Archivo**: `commands/player/general.py`

**Nota**: Para items con información oculta.

```python
# FUTURO (si se desea)
locks = item.prototype.get("locks", "")
can_pass, _ = await permission_service.can_execute(
    character,
    locks,
    access_type="look"
)

if not can_pass:
    # Mostrar descripción genérica en lugar de la completa
    await message.answer("No logras discernir nada especial sobre eso.")
    return
```

### Fase 3: Actualizar Movimiento (Exits)

**Objetivo**: Usar access_type "traverse" para salidas.

#### 3.1. Modificar CmdMove

**Archivo**: `commands/player/movement.py:66-71`

```python
# ANTES
can_pass, error_message = await permission_service.can_execute(character, target_exit.locks)

# DESPUÉS
can_pass, error_message = await permission_service.can_execute(
    character,
    target_exit.locks,
    access_type="traverse"  # 🆕 Atravesar salida
)
```

**Nota**: Como Exit.locks es un campo String en BD, por ahora seguirá siendo string simple. En el futuro se podría migrar a JSONB si se necesitan locks contextuales para exits (ej: "traverse" vs "look").

### Fase 4: Actualizar Prototipos de Items

**Objetivo**: Usar locks contextuales en prototipos de ejemplo.

#### 4.1. Modificar `game_data/item_prototypes.py`

```python
# ANTES
"cofre_roble": {
    "name": "un cofre de roble",
    "keywords": ["cofre", "roble"],
    "description": "Un pesado cofre de madera de roble con refuerzos de hierro. Está cerrado.",
    "category": "contenedor",
    "tags": ["cofre", "fijo", "madera", "cerrado"],
    "is_container": True,
    "capacity": 20,
    "locks": "rol(SUPERADMIN)",  # ¿Para qué acción?
    "display": {
        "icon": "📦",
    }
},

# DESPUÉS (locks contextuales)
"cofre_roble": {
    "name": "un cofre de roble",
    "keywords": ["cofre", "roble"],
    "description": "Un pesado cofre de madera de roble con refuerzos de hierro. Está cerrado.",
    "category": "contenedor",
    "tags": ["cofre", "fijo", "madera", "cerrado"],
    "is_container": True,
    "capacity": 20,
    "locks": {
        "get": "rol(SUPERADMIN)",  # Solo SUPERADMIN puede cogerlo (muy pesado)
        "put": "",                  # Todos pueden meter cosas (sin lock)
        "take": "",                 # Todos pueden sacar cosas (sin lock)
        # Futuro: "open": "tiene_objeto(llave_roble)"
    },
    "display": {
        "icon": "📦",
    }
},
```

#### 4.2. Agregar Nuevos Ejemplos

```python
# Puerta con llave (futuro cuando tengamos sistema de open/close)
"puerta_hierro": {
    "name": "una pesada puerta de hierro",
    "keywords": ["puerta", "hierro"],
    "description": "Una imponente puerta de hierro forjado. Parece necesitar una llave especial.",
    "category": "puerta",
    "tags": ["puerta", "fijo", "cerrada"],
    "is_container": False,
    "locks": {
        "get": "rol(SUPERADMIN)",  # No se puede coger
        # Futuro: "open": "tiene_objeto(llave_hierro) or rol(ADMIN)"
    },
    "display": {
        "icon": "🚪",
    }
},

# Objeto mágico que solo pueden usar magos
"baston_arcano": {
    "name": "un bastón arcano",
    "keywords": ["baston", "arcano", "magico"],
    "description": "Un bastón que pulsa con energía mágica.",
    "category": "arma",
    "tags": ["magica", "baston", "dos_manos"],
    "locks": {
        "get": "",  # Cualquiera puede cogerlo
        "use": "tiene_item_tag(mago)"  # Solo quien tenga un item con tag "mago"
    },
    "display": {
        "icon": "🪄",
    }
},

# Objeto que solo se puede coger en cierta sala
"reliquia_sagrada": {
    "name": "una reliquia sagrada",
    "keywords": ["reliquia", "sagrada"],
    "description": "Un objeto de poder divino que solo puede ser tocado en lugares sagrados.",
    "category": "quest",
    "tags": ["quest", "unica", "sagrada"],
    "locks": {
        "get": "en_categoria_sala(templo) or rol(ADMIN)",
        "drop": "en_categoria_sala(templo) or rol(ADMIN)"
    },
    "display": {
        "icon": "✨",
    }
},
```

### Fase 5: Testing

**Objetivo**: Verificar que todo funciona correctamente.

#### 5.1. Tests Unitarios para `permission_service`

**Archivo**: `tests/test_services/test_permission_service.py`

```python
import pytest
from src.services import permission_service
from src.models import Character, Account, Room

@pytest.mark.asyncio
async def test_locks_contextuales_dict():
    """Verifica que locks como diccionario funcionen correctamente."""
    character = create_test_character()

    locks = {
        "get": "rol(ADMIN)",
        "open": "",  # Sin restricción
        "take": "tiene_objeto(llave)"
    }

    # get: requiere ADMIN (character es JUGADOR)
    can_get, _ = await permission_service.can_execute(character, locks, "get")
    assert can_get == False

    # open: sin restricción
    can_open, _ = await permission_service.can_execute(character, locks, "open")
    assert can_open == True

    # take: requiere objeto (no lo tiene)
    can_take, _ = await permission_service.can_execute(character, locks, "take")
    assert can_take == False

@pytest.mark.asyncio
async def test_backward_compatibility_string():
    """Verifica que locks como string simple sigan funcionando."""
    character = create_test_character()

    lock_string = "rol(ADMIN)"

    # Debería funcionar con access_type="default"
    can_pass, _ = await permission_service.can_execute(character, lock_string, "default")
    assert can_pass == False

    # Debería funcionar sin especificar access_type
    can_pass, _ = await permission_service.can_execute(character, lock_string)
    assert can_pass == False

@pytest.mark.asyncio
async def test_nuevas_lock_functions():
    """Verifica que las nuevas lock functions funcionen."""
    character = create_test_character_in_room("plaza_central")

    # en_sala
    can_pass, _ = await permission_service.can_execute(character, {"get": "en_sala(plaza_central)"}, "get")
    assert can_pass == True

    # cuenta_items
    # TODO: agregar items al character de prueba
    can_pass, _ = await permission_service.can_execute(character, {"get": "cuenta_items(5)"}, "get")
    assert can_pass == False  # No tiene 5 items
```

#### 5.2. Tests de Integración

**Casos de prueba manuales**:

1. **Coger objeto con lock contextual**:
   - Crear cofre con `locks: {"get": "rol(ADMIN)"}`
   - Como JUGADOR: `/coger cofre` → Debe denegar
   - Como ADMIN: `/coger cofre` → Debe permitir

2. **Meter/sacar con locks diferentes**:
   - Crear cofre con `locks: {"put": "rol(ADMIN)", "take": ""}`
   - Como JUGADOR: `/meter espada en cofre` → Debe denegar
   - Como JUGADOR: `/sacar espada de cofre` → Debe permitir (si hay espada)
   - Como ADMIN: `/meter espada en cofre` → Debe permitir

3. **Backward compatibility**:
   - Usar objeto con `locks: "rol(ADMIN)"` (string simple)
   - Verificar que `/coger` siga funcionando como antes

4. **Nuevas lock functions**:
   - Crear objeto con `locks: {"get": "en_sala(biblioteca)"}`
   - Verificar que solo se pueda coger en la biblioteca

---

## 📂 ARCHIVOS AFECTADOS

### Modificaciones (CORE)

| Archivo | Cambios | Prioridad | Complejidad |
|---------|---------|-----------|-------------|
| `src/services/permission_service.py` | Agregar soporte dict, nuevas lock functions | 🔴🔴🔴 CRÍTICO | Media |
| `commands/player/interaction.py` | Actualizar `/coger`, `/meter`, `/sacar` con access_type | 🔴🔴🔴 CRÍTICO | Baja |
| `commands/player/movement.py` | Actualizar `CmdMove` con access_type="traverse" | 🔴🔴 Alta | Baja |
| `game_data/item_prototypes.py` | Convertir locks a formato dict (ejemplos) | 🔴🔴 Alta | Baja |

### Documentación

| Archivo | Cambios | Prioridad |
|---------|---------|-----------|
| `docs/sistemas-del-motor/sistema-de-permisos.md` | Agregar sección de locks contextuales | 🔴🔴🔴 CRÍTICO |
| `docs/creacion-de-contenido/creacion-de-items.md` | Actualizar ejemplos con locks contextuales | 🔴🔴 Alta |
| `CLAUDE.md` | Agregar locks contextuales a filosofía | 🔴 Media |
| `README.md` | Mencionar locks contextuales si es relevante | 🔴 Baja |

### Testing

| Archivo | Cambios | Prioridad |
|---------|---------|-----------|
| `tests/test_services/test_permission_service.py` | Agregar tests para locks contextuales | 🔴🔴🔴 CRÍTICO |
| `tests/test_commands/` (futuro) | Tests de integración para comandos | 🔴🔴 Alta |

### Sin Cambios (por ahora)

- `src/models/*.py` - No requiere cambios en BD
- `alembic/` - No requiere migraciones
- `commands/admin/*` - No afectados inicialmente
- `src/services/channel_service.py` - Ya usa locks, compatible

---

## 💡 EJEMPLOS DE USO PRÁCTICO

### Ejemplo 1: Cofre con Llave

```python
# game_data/item_prototypes.py

"llave_cofre_magico": {
    "name": "una llave de cristal",
    "keywords": ["llave", "cristal"],
    "description": "Una llave hecha de cristal translúcido que emite un suave brillo.",
    "category": "llave",
    "tags": ["llave", "magica"],
    "display": {"icon": "🔑"}
},

"cofre_magico": {
    "name": "un cofre mágico",
    "keywords": ["cofre", "magico"],
    "description": "Un cofre ornamentado con runas brillantes. Está cerrado con un mecanismo mágico.",
    "category": "contenedor",
    "tags": ["cofre", "magico", "fijo"],
    "is_container": True,
    "capacity": 10,
    "locks": {
        "get": "rol(SUPERADMIN)",  # Demasiado pesado para cogerlo
        "put": "tiene_objeto(llave_cofre_magico)",  # Necesitas llave para meter
        "take": "tiene_objeto(llave_cofre_magico)"  # Necesitas llave para sacar
    },
    "display": {"icon": "📦"}
}
```

**Flujo de juego**:
```
> /mirar
📍 BIBLIOTECA ARCANA
Una antigua biblioteca llena de libros polvorientos.

Objetos en el suelo:
    - 📦 un cofre mágico
    - 🔑 una llave de cristal

> /coger cofre
❌ Permiso denegado.

> /coger llave
✅ Has cogido: una llave de cristal

> /meter espada en cofre
✅ Guardas una espada en un cofre mágico.

> /dejar llave
✅ Has dejado: una llave de cristal

> /sacar espada de cofre
❌ Permiso denegado.
```

### Ejemplo 2: Objeto que Solo Funciona en Ciertas Salas

```python
# game_data/item_prototypes.py

"orbe_de_teletransporte": {
    "name": "un orbe de teletransporte",
    "keywords": ["orbe", "teletransporte"],
    "description": "Un orbe mágico que brilla con energía. Solo funciona en lugares de poder.",
    "category": "magico",
    "tags": ["magico", "unico", "teletransporte"],
    "locks": {
        "get": "",  # Cualquiera puede cogerlo
        "use": "tiene_tag_sala(nodo_magico) or rol(ADMIN)"  # Solo en salas mágicas
    },
    "display": {"icon": "🔮"}
}

# game_data/room_prototypes.py

"torre_mago": {
    "name": "Torre del Mago",
    "description": "La cima de una torre antigua. Energía mágica fluye en el aire.",
    "category": "dungeon",
    "tags": ["magica", "nodo_magico"],  # 🆕 Tag especial
}
```

**Flujo de juego**:
```
> /usar orbe
❌ Permiso denegado.

> /norte
[te mueves a Torre del Mago]

> /usar orbe
✅ El orbe brilla intensamente...
```

### Ejemplo 3: Contenedor Personal

```python
# game_data/item_prototypes.py

"mochila_personal": {
    "name": "tu mochila personal",
    "keywords": ["mochila", "personal"],
    "description": "Una mochila encantada que solo tú puedes abrir.",
    "category": "contenedor",
    "tags": ["contenedor", "personal", "magica"],
    "is_container": True,
    "capacity": 20,
    "locks": {
        "get": "",  # Cualquiera puede cogerla del suelo
        "put": "",  # El dueño puede meter (futuro: usar es_owner)
        "take": "", # El dueño puede sacar (futuro: usar es_owner)
        # Futuro cuando tengamos Item.owner_id:
        # "put": "es_owner(self) or rol(ADMIN)",
        # "take": "es_owner(self) or rol(ADMIN)"
    },
    "display": {"icon": "🎒"}
}
```

### Ejemplo 4: Salida Restringida

```python
# En código de creación de exits (futuro)

# Exit con locks contextuales (requiere migrar Exit.locks a JSONB)
exit_sala_secreta = Exit(
    name="pasadizo_oculto",
    from_room_id=biblioteca.id,
    to_room_id=sala_secreta.id,
    locks={
        "traverse": "tiene_item_tag(mago) or rol(ADMIN)",  # Solo magos
        "look": "tiene_item_tag(detective)"  # Solo detectives ven la pista
    }
)
```

**Flujo de juego**:
```
> /mirar
📍 BIBLIOTECA ANTIGUA
[descripción...]

Salidas visibles:
    - norte
    - sur

[Si tienes item con tag "detective"]

Salidas visibles:
    - norte
    - sur
    - pasadizo_oculto (oculto) 👁️ Solo lo ves si tienes tag

> /pasadizo_oculto
❌ Esa salida está bloqueada.

[Consigues un bastón mágico con tag "mago"]

> /pasadizo_oculto
✅ Atraviesas el pasadizo oculto...
```

---

## 🔄 COMPATIBILIDAD Y MIGRACIÓN

### Estrategia de Compatibilidad hacia Atrás

**Principio**: TODO el contenido existente debe seguir funcionando sin cambios.

#### Fase de Transición

1. **Locks simples siguen funcionando**:
   ```python
   # Esto sigue siendo válido
   "espada": {
       "locks": "rol(ADMIN)"  # String simple
   }
   ```

2. **Locks contextuales son opcionales**:
   ```python
   # Esto también es válido (nuevo formato)
   "espada": {
       "locks": {
           "get": "rol(ADMIN)",
           "use": "rol(GUERRERO)"
       }
   }
   ```

3. **Conversión automática en runtime**:
   - String simple → `{"default": "string"}`
   - Dict → sin cambios
   - Vacío → `{}`

#### Migración Gradual de Contenido

**No se requiere migrar todo de golpe**. Se puede hacer progresivamente:

```python
# Fase 1: Prototipos críticos (cofres, puertas)
"cofre_roble": {
    "locks": {  # 🆕 Migrado a dict
        "get": "rol(SUPERADMIN)",
        "put": "",
        "take": ""
    }
}

# Fase 2: Otros prototipos siguen con string
"espada_simple": {
    "locks": "rol(ADMIN)"  # ✅ Sigue siendo string, funciona igual
}
```

### Plan de Migración de BD (NO REQUERIDO)

**Importante**: Esta propuesta **NO requiere migraciones de base de datos**.

**Razón**:
- `Room.locks` ya es `String` (puede ser string o JSON string)
- `Exit.locks` ya es `String` (puede ser string o JSON string)
- Items usan prototipos (Python dict, no BD)
- Comandos usan atributo de clase (no BD)

**Si en el futuro se quisiera guardar locks en BD como JSONB**:

```python
# Migración futura (opcional, para mejor performance)
# alembic/versions/XXXX_locks_to_jsonb.py

def upgrade():
    # Room.locks: String → JSONB
    op.alter_column('rooms', 'locks',
                    type_=JSONB,
                    postgresql_using='locks::jsonb')

    # Exit.locks: String → JSONB
    op.alter_column('exits', 'locks',
                    type_=JSONB,
                    postgresql_using='locks::jsonb')

def downgrade():
    # Revertir a String
    op.alter_column('rooms', 'locks', type_=String)
    op.alter_column('exits', 'locks', type_=String)
```

**Decisión**: Postergar esto hasta que sea realmente necesario. Por ahora, JSON como string es suficiente.

---

## 🧪 TESTING

### Tests Unitarios

**Archivo**: `tests/test_services/test_permission_service.py`

#### Test Suite: Locks Contextuales

```python
import pytest
from src.services import permission_service
from src.models import Character, Account, Room, Item
from sqlalchemy.ext.asyncio import AsyncSession

class TestLocksContextuales:
    """Tests para el sistema de locks contextuales."""

    @pytest.mark.asyncio
    async def test_dict_locks_access_type_especifico(self):
        """Verifica que los locks con access_type específico funcionen."""
        character = create_mock_character(role="JUGADOR")

        locks = {
            "get": "rol(ADMIN)",
            "open": "",
            "put": "rol(ADMIN)"
        }

        # get: ADMIN required, character is JUGADOR
        can_get, msg = await permission_service.can_execute(character, locks, "get")
        assert can_get == False
        assert "denegado" in msg.lower()

        # open: no restriction
        can_open, msg = await permission_service.can_execute(character, locks, "open")
        assert can_open == True
        assert msg == ""

        # put: ADMIN required
        can_put, msg = await permission_service.can_execute(character, locks, "put")
        assert can_put == False

    @pytest.mark.asyncio
    async def test_dict_locks_fallback_default(self):
        """Verifica que si no existe access_type, usa 'default'."""
        character = create_mock_character(role="JUGADOR")

        locks = {
            "default": "rol(ADMIN)",
            "open": ""
        }

        # get: no existe, usa default
        can_get, _ = await permission_service.can_execute(character, locks, "get")
        assert can_get == False

        # open: existe específico (vacío = sin restricción)
        can_open, _ = await permission_service.can_execute(character, locks, "open")
        assert can_open == True

    @pytest.mark.asyncio
    async def test_backward_compat_string_simple(self):
        """Verifica que string simple siga funcionando (backward compatibility)."""
        character = create_mock_character(role="JUGADOR")

        lock_string = "rol(ADMIN)"

        # Sin especificar access_type (default)
        can_pass, _ = await permission_service.can_execute(character, lock_string)
        assert can_pass == False

        # Especificando access_type (debería usar el string como default)
        can_pass, _ = await permission_service.can_execute(character, lock_string, "get")
        assert can_pass == False

    @pytest.mark.asyncio
    async def test_lock_vacio_siempre_permite(self):
        """Verifica que lock vacío siempre permita acceso."""
        character = create_mock_character(role="JUGADOR")

        # String vacío
        can_pass, _ = await permission_service.can_execute(character, "")
        assert can_pass == True

        # Dict con access_type vacío
        can_pass, _ = await permission_service.can_execute(character, {"get": ""}, "get")
        assert can_pass == True

        # Dict vacío
        can_pass, _ = await permission_service.can_execute(character, {})
        assert can_pass == True
```

#### Test Suite: Nuevas Lock Functions

```python
class TestNuevasLockFunctions:
    """Tests para las nuevas lock functions."""

    @pytest.mark.asyncio
    async def test_en_sala(self):
        """Verifica lock function en_sala()."""
        room = create_mock_room(key="plaza_central")
        character = create_mock_character(room=room)

        # Character está en plaza_central
        locks = {"get": "en_sala(plaza_central)"}
        can_pass, _ = await permission_service.can_execute(character, locks, "get")
        assert can_pass == True

        # Character NO está en biblioteca
        locks = {"get": "en_sala(biblioteca)"}
        can_pass, _ = await permission_service.can_execute(character, locks, "get")
        assert can_pass == False

    @pytest.mark.asyncio
    async def test_en_categoria_sala(self):
        """Verifica lock function en_categoria_sala()."""
        room = create_mock_room(category="ciudad")
        character = create_mock_character(room=room)

        # Character está en sala de categoría "ciudad"
        locks = {"get": "en_categoria_sala(ciudad)"}
        can_pass, _ = await permission_service.can_execute(character, locks, "get")
        assert can_pass == True

        # Character NO está en "dungeon"
        locks = {"get": "en_categoria_sala(dungeon)"}
        can_pass, _ = await permission_service.can_execute(character, locks, "get")
        assert can_pass == False

    @pytest.mark.asyncio
    async def test_tiene_tag_sala(self):
        """Verifica lock function tiene_tag_sala()."""
        room = create_mock_room(tags=["magica", "sagrada"])
        character = create_mock_character(room=room)

        # Sala tiene tag "magica"
        locks = {"use": "tiene_tag_sala(magica)"}
        can_pass, _ = await permission_service.can_execute(character, locks, "use")
        assert can_pass == True

        # Sala NO tiene tag "oscura"
        locks = {"use": "tiene_tag_sala(oscura)"}
        can_pass, _ = await permission_service.can_execute(character, locks, "use")
        assert can_pass == False

    @pytest.mark.asyncio
    async def test_cuenta_items(self):
        """Verifica lock function cuenta_items()."""
        character = create_mock_character()

        # Agregar 3 items al character
        add_mock_items(character, count=3)

        # Character tiene >= 2 items
        locks = {"get": "cuenta_items(2)"}
        can_pass, _ = await permission_service.can_execute(character, locks, "get")
        assert can_pass == True

        # Character NO tiene >= 10 items
        locks = {"get": "cuenta_items(10)"}
        can_pass, _ = await permission_service.can_execute(character, locks, "get")
        assert can_pass == False

    @pytest.mark.asyncio
    async def test_tiene_item_categoria(self):
        """Verifica lock function tiene_item_categoria()."""
        character = create_mock_character()

        # Agregar espada (categoría "arma")
        add_mock_item(character, category="arma")

        # Character tiene item de categoría "arma"
        locks = {"traverse": "tiene_item_categoria(arma)"}
        can_pass, _ = await permission_service.can_execute(character, locks, "traverse")
        assert can_pass == True

        # Character NO tiene item de categoría "armadura"
        locks = {"traverse": "tiene_item_categoria(armadura)"}
        can_pass, _ = await permission_service.can_execute(character, locks, "traverse")
        assert can_pass == False

    @pytest.mark.asyncio
    async def test_tiene_item_tag(self):
        """Verifica lock function tiene_item_tag()."""
        character = create_mock_character()

        # Agregar bastón con tag "magica"
        add_mock_item(character, tags=["magica", "unica"])

        # Character tiene item con tag "magica"
        locks = {"use": "tiene_item_tag(magica)"}
        can_pass, _ = await permission_service.can_execute(character, locks, "use")
        assert can_pass == True

        # Character NO tiene item con tag "maldita"
        locks = {"use": "tiene_item_tag(maldita)"}
        can_pass, _ = await permission_service.can_execute(character, locks, "use")
        assert can_pass == False
```

### Tests de Integración (Manual)

**Checklist de verificación**:

1. ✅ **Coger objeto con lock contextual**
   - Crear cofre con `"locks": {"get": "rol(ADMIN)"}`
   - Verificar que JUGADOR no pueda cogerlo
   - Verificar que ADMIN sí pueda

2. ✅ **Meter/sacar con locks diferentes**
   - Crear cofre con `"locks": {"put": "rol(ADMIN)", "take": ""}`
   - Verificar que JUGADOR no pueda meter
   - Verificar que JUGADOR sí pueda sacar

3. ✅ **Backward compatibility con string**
   - Usar espada con `"locks": "rol(ADMIN)"`
   - Verificar que `/coger` funcione igual que antes

4. ✅ **Nuevas lock functions**
   - Crear objeto con `"locks": {"get": "en_sala(biblioteca)"}`
   - Verificar que solo se pueda coger en biblioteca

5. ✅ **Lock vacío = sin restricción**
   - Crear objeto con `"locks": ""`
   - Verificar que todos puedan cogerlo
   - Crear objeto con `"locks": {"get": ""}`
   - Verificar que todos puedan cogerlo

6. ✅ **Mensajes de error**
   - Verificar que mensajes de error sean apropiados
   - Verificar que "Permiso denegado" aparezca cuando corresponda

---

## ❓ DECISIONES PENDIENTES

### 1. ¿Locks Asíncronos?

**Problema**: La lock function `online()` requiere llamada async a Redis.

**Opciones**:

**A) Soporte async en evaluator (COMPLEJO)**
- Modificar `LockEvaluator` para soportar funciones async
- Todas las lock functions deben ser async
- Mayor complejidad

**B) Descartar lock functions async (SIMPLE)**
- No implementar `online()` como lock function
- Mantener evaluator síncrono
- Menor complejidad

**Recomendación**: **Opción B** por ahora. Si se necesita verificar online, hacerlo fuera del sistema de locks.

### 2. ¿Migrar BD a JSONB?

**Problema**: Actualmente Room.locks y Exit.locks son String. ¿Migrar a JSONB para locks contextuales?

**Opciones**:

**A) Migrar a JSONB**
- Mejor para queries complejas en BD
- Validación de estructura en BD
- Requiere migración

**B) Mantener String (con JSON serializado)**
- Sin migraciones
- Parsing en Python
- Más simple

**Recomendación**: **Opción B** por ahora. Migrar a JSONB solo si se necesita query locks desde BD (poco probable).

### 3. ¿Mensajes de Error Personalizados?

**Problema**: Evennia permite mensajes de error personalizados por lock. ¿Implementar?

**Ejemplo Evennia**:
```python
box.db.get_err_msg = "No eres suficientemente fuerte para levantar esto."
```

**Opciones**:

**A) Implementar mensajes personalizados**
```python
"cofre_roble": {
    "locks": {
        "get": "rol(SUPERADMIN)",
        "put": "tiene_objeto(llave_roble)"
    },
    "lock_messages": {
        "get": "El cofre es demasiado pesado para levantarlo.",
        "put": "El cofre está cerrado con llave."
    }
}
```

**B) Mantener mensajes genéricos**
- "Permiso denegado"
- Más simple

**Recomendación**: **Opción A en el futuro**, pero no crítico para MVP. Por ahora, usar mensajes genéricos.

### 4. ¿Access Type para Comandos?

**Problema**: ¿Los comandos necesitan locks contextuales?

**Análisis**:
- Comandos típicamente tienen un solo tipo de acción: "ejecutar"
- No hay necesidad de múltiples access types por comando
- Lock simple es suficiente

**Recomendación**: **NO implementar** locks contextuales para comandos. Mantener `Command.lock` como string simple.

### 5. ¿Validación de Access Types?

**Problema**: ¿Validar que los access types sean válidos (get, open, put, etc.)?

**Opciones**:

**A) Lista cerrada de access types válidos**
```python
VALID_ACCESS_TYPES = {
    "item": ["get", "drop", "put", "take", "open", "close", "look", "use"],
    "exit": ["traverse", "look"],
    "room": ["enter", "teleport_to", "look"],
}
```

**B) Libre (cualquier string)**
- Más flexible
- Sin validación

**Recomendación**: **Opción B** por flexibilidad. Si se usa un access type inválido, simplemente no matchea y usa "default".

### 6. ¿Item.owner_id?

**Problema**: La lock function `es_owner()` requiere campo `owner_id` en Item.

**Opciones**:

**A) Implementar ahora**
- Agregar `Item.owner_id` (ForeignKey a Character)
- Migración de BD
- Sistema de ownership completo

**B) Postergar para futuro**
- Implementar solo cuando se necesite ownership
- Por ahora, placeholder que retorna True

**Recomendación**: **Opción B**. No es crítico para MVP. Implementar cuando haya sistema de ownership real.

---

## 📊 RESUMEN DE PRIORIDADES

### CRÍTICO (Implementar primero)

1. ✅ Modificar `permission_service.can_execute()` para soportar dict
2. ✅ Agregar 6 nuevas lock functions básicas
3. ✅ Actualizar comandos de interacción (/coger, /meter, /sacar)
4. ✅ Actualizar documentación del sistema de permisos
5. ✅ Tests unitarios para locks contextuales

### ALTA PRIORIDAD (Implementar después)

1. ✅ Migrar prototipos de ejemplo a locks contextuales
2. ✅ Actualizar comando de movimiento (CmdMove)
3. ✅ Documentar guía de creación de items con locks contextuales
4. ✅ Tests de integración manuales

### MEDIA PRIORIDAD (Futuro cercano)

1. ⏳ Mensajes de error personalizados por access type
2. ⏳ Lock function `es_owner()` completa (requiere Item.owner_id)
3. ⏳ Agregar access type "look" para items con info oculta
4. ⏳ Agregar access type "drop" para items que no se pueden soltar

### BAJA PRIORIDAD (Futuro lejano)

1. ❌ Migrar Room.locks y Exit.locks a JSONB en BD
2. ❌ Lock functions async (ej: online())
3. ❌ Validación estricta de access types
4. ❌ Sistema de ownership completo

---

## 🎯 CONCLUSIÓN

### ¿Tiene Sentido en Nuestro Juego?

**Sí, ABSOLUTAMENTE**. Por las siguientes razones:

1. **Claridad semántica**: Los contenedores tienen múltiples acciones (coger, meter, sacar, abrir). Un solo lock es insuficiente.

2. **Flexibilidad de diseño**: Permite crear mecánicas interesantes:
   - Cofres que todos pueden usar pero solo algunos pueden mover
   - Objetos que solo funcionan en ciertos lugares
   - Contenedores personales que solo el dueño puede abrir

3. **Escalabilidad**: Cuando agreguemos sistemas de combate, habilidades, quests, etc., necesitaremos locks más sofisticados.

4. **Coherencia con Evennia**: Nos inspiramos en un sistema probado y consolidado.

### ¿Es Factible?

**Sí, MUY FACTIBLE**:

- ✅ Motor de evaluación ya existe (AST-based)
- ✅ Sin cambios en BD (backward compatible)
- ✅ Cambios localizados en pocos archivos
- ✅ Implementación incremental posible
- ✅ No rompe funcionalidad existente

### Esfuerzo Estimado

**4-6 horas de trabajo** (incluyendo testing y documentación):

- 2h: Modificar `permission_service.py` + nuevas lock functions
- 1h: Actualizar comandos de interacción
- 1h: Migrar prototipos de ejemplo
- 1h: Tests unitarios
- 1h: Documentación

### Riesgos

**BAJOS**:

1. **Backward compatibility**: Mitigado con detección de tipo (string vs dict)
2. **Complejidad para diseñadores**: Mitigado con buenos ejemplos y documentación
3. **Performance**: Impacto mínimo (evaluación sigue siendo O(1) por lock)

### Recomendación Final

**✅ IMPLEMENTAR** el sistema de locks contextuales.

**Razones**:
- Beneficios claros superan el esfuerzo
- Factibilidad técnica alta
- Riesgos bajos y mitigables
- Alineado con la visión del proyecto

**Plan de Acción**:
1. Aprobar esta propuesta
2. Implementar Fase 1 (CORE)
3. Testing exhaustivo
4. Implementar Fase 2-4 progresivamente
5. Documentar y comunicar cambios

---

**Versión**: 1.0
**Fecha**: 2025-01-11
**Autor**: Análisis para Proyecto Runegram
**Estado**: 📋 Pendiente de aprobación e implementación
**Próximo paso**: Revisión y decisión de stakeholders
