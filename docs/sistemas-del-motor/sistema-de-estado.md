---
título: "Sistema de Estado"
categoría: "Sistemas del Motor"
última_actualización: "2025-10-17"
autor: "Proyecto Runegram"
etiquetas: ["estado", "persistencia", "redis", "cooldowns", "scripts"]
documentos_relacionados:
  - "sistemas-del-motor/sistema-de-scripts.md"
  - "sistemas-del-motor/sistema-de-eventos.md"
  - "creacion-de-contenido/escritura-de-scripts.md"
referencias_código:
  - "src/services/state_service.py"
estado: "actual"
importancia: "alta"
audiencia: "desarrollador"
---

# Sistema de Estado

El Sistema de Estado proporciona una API unificada para que scripts puedan almacenar y recuperar estado de dos formas: **persistente** (PostgreSQL) y **transiente** (Redis).

## Visión General

### ¿Por Qué Dos Tipos de Estado?

**Estado Persistente** (PostgreSQL JSONB):
- ✅ Sobrevive reinicios del bot
- ✅ Ideal para progreso de quests, contadores permanentes
- ✅ Almacenado en columna `script_state` (JSONB)
- ⚠️ Más lento (requiere commit a BD)

**Estado Transiente** (Redis):
- ✅ Rápido y eficiente
- ✅ Soporte de TTL (expiración automática)
- ✅ Ideal para cooldowns, buffs temporales, flags
- ❌ Se pierde al reiniciar el bot

### Filosofía del Sistema

Los scripts necesitan recordar información:
- ¿Cuántas veces se usó este item?
- ¿Cuándo fue la última vez que se activó?
- ¿El jugador ya completó esta quest?
- ¿El buff está activo?

El `state_service` proporciona una API simple para ambos casos.

## Estado Persistente (PostgreSQL)

### Estructura de Datos

La columna `script_state` es un campo JSONB que permite almacenar cualquier estructura JSON:

```python
# Ejemplo de script_state en un Item
item.script_state = {
    "usos_restantes": 3,
    "ultima_activacion": "2025-10-17T12:00:00Z",
    "quest_completada": True,
    "contador_victorias": 15,
    "custom_data": {
        "nivel": 5,
        "experiencia": 1250
    }
}
```

### API de Estado Persistente

#### Obtener Valor

```python
from src.services import state_service

valor = await state_service.get_persistent(
    session=session,
    entity=item,  # Item, Room o Character
    key="usos_restantes",
    default=10  # Valor por defecto si no existe
)
# valor = 3 (o 10 si no existía)
```

#### Establecer Valor

```python
await state_service.set_persistent(
    session=session,
    entity=item,
    key="usos_restantes",
    value=5
)

# IMPORTANTE: Hacer commit después
await session.commit()
```

#### Eliminar Valor

```python
await state_service.delete_persistent(
    session=session,
    entity=item,
    key="usos_restantes"
)

await session.commit()
```

#### Obtener Todo el Estado

```python
todo_el_estado = await state_service.get_all_persistent(
    session=session,
    entity=item
)
# Retorna: {"usos_restantes": 3, "quest_completada": True, ...}
```

#### Limpiar Todo el Estado

```python
await state_service.clear_persistent(
    session=session,
    entity=item
)

await session.commit()
```

### Helpers para Contadores

#### Incrementar

```python
nuevo_valor = await state_service.increment_persistent(
    session=session,
    entity=item,
    key="contador_usos",
    amount=1  # Default: 1
)
# Si era 5, ahora es 6

await session.commit()
```

#### Decrementar

```python
nuevo_valor = await state_service.decrement_persistent(
    session=session,
    entity=item,
    key="cargas_restantes",
    amount=1,
    min_value=0  # No bajar de 0
)
# Si era 3, ahora es 2 (nunca negativo)

await session.commit()
```

### Ejemplo: Item con Usos Limitados

```python
# En un script
async def script_usar_pocion(session: AsyncSession, target: Item, character: Character, **kwargs):
    """
    Poción de curación con 3 usos.
    """
    # Obtener usos restantes
    usos = await state_service.get_persistent(
        session=session,
        entity=target,
        key="usos_restantes",
        default=3  # Empieza con 3 usos
    )

    if usos <= 0:
        await broadcaster_service.send_message_to_character(
            character,
            "La poción está vacía."
        )
        return

    # Curar al personaje
    character.attributes["vida"] += 50

    # Decrementar usos
    nuevo_usos = await state_service.decrement_persistent(
        session=session,
        entity=target,
        key="usos_restantes",
        min_value=0
    )

    await session.commit()

    if nuevo_usos == 0:
        await broadcaster_service.send_message_to_character(
            character,
            "Has usado la última carga de la poción."
        )
```

## Estado Transiente (Redis)

### API de Estado Transiente

#### Obtener Valor

```python
valor = await state_service.get_transient(
    entity=item,
    key="buff_activo",
    default=False
)
```

#### Establecer Valor (con TTL)

```python
from datetime import timedelta

await state_service.set_transient(
    entity=item,
    key="buff_fuerza",
    value=True,
    ttl=timedelta(minutes=5)  # Expira en 5 minutos
)
```

#### Establecer Valor (sin TTL)

```python
await state_service.set_transient(
    entity=item,
    key="flag_temporal",
    value={"datos": "importantes"}
    # Sin ttl = no expira (pero se pierde al reiniciar)
)
```

#### Eliminar Valor

```python
await state_service.delete_transient(
    entity=item,
    key="buff_fuerza"
)
```

#### Verificar Existencia

```python
existe = await state_service.exists_transient(
    entity=item,
    key="buff_fuerza"
)
# True si existe (y no ha expirado)
```

#### Obtener TTL Restante

```python
segundos_restantes = await state_service.get_ttl(
    entity=item,
    key="buff_fuerza"
)
# Retorna segundos restantes, o None si no existe/no tiene TTL
```

### Namespace de Redis

Las claves en Redis usan el formato:
```
script_state:{entity_type}:{entity_id}:{key}
```

Ejemplos:
```
script_state:item:42:cooldown_uso
script_state:character:15:buff_fuerza
script_state:room:8:trampa_activada
```

## Sistema de Cooldowns

El state_service incluye helpers específicos para cooldowns (muy común en scripts).

### Establecer Cooldown

```python
from datetime import timedelta

await state_service.set_cooldown(
    entity=item,
    cooldown_name="uso",
    duration=timedelta(minutes=5)
)
```

Internamente crea: `cooldown_{cooldown_name}` con TTL automático.

### Verificar Cooldown

```python
en_cooldown = await state_service.is_on_cooldown(
    entity=item,
    cooldown_name="uso"
)

if en_cooldown:
    segundos = await state_service.get_cooldown_remaining(
        entity=item,
        cooldown_name="uso"
    )
    await message.answer(f"Debes esperar {segundos}s antes de usar esto de nuevo.")
    return
```

### Ejemplo: Item con Cooldown

```python
async def script_espada_especial(session: AsyncSession, target: Item, character: Character, **kwargs):
    """
    Espada con habilidad especial (cooldown de 1 minuto).
    """
    from datetime import timedelta

    # Verificar cooldown
    if await state_service.is_on_cooldown(target, "habilidad_especial"):
        segundos = await state_service.get_cooldown_remaining(target, "habilidad_especial")
        await broadcaster_service.send_message_to_character(
            character,
            f"Debes esperar {segundos}s antes de usar la habilidad especial de nuevo."
        )
        return

    # Ejecutar habilidad
    await broadcaster_service.send_message_to_room(
        session=session,
        room_id=character.room_id,
        message_text=f"<i>{character.name} desata el poder de {target.get_name()}!</i>"
    )

    # Establecer cooldown
    await state_service.set_cooldown(
        entity=target,
        cooldown_name="habilidad_especial",
        duration=timedelta(minutes=1)
    )
```

## Cuándo Usar Cada Tipo

### Usar Estado Persistente (PostgreSQL)

✅ Progreso de quests
✅ Contadores de victorias/derrotas
✅ Items consumibles con usos limitados
✅ Estado que debe sobrevivir reinicios
✅ Datos importantes que no pueden perderse

### Usar Estado Transiente (Redis)

✅ Cooldowns de habilidades
✅ Buffs/debuffs temporales
✅ Flags temporales (trampa activada, puerta abierta)
✅ Cache de datos (datos que se pueden recalcular)
✅ Datos que expiran automáticamente

## Uso en Scripts

### Ejemplo Completo: Poción con Cooldown y Usos

```python
async def script_usar_pocion_magica(
    session: AsyncSession,
    target: Item,
    character: Character,
    **kwargs
):
    """
    Poción mágica:
    - 5 usos (persistente)
    - Cooldown de 30 segundos entre usos (transiente)
    """
    from datetime import timedelta

    # 1. Verificar cooldown (transiente)
    if await state_service.is_on_cooldown(target, "uso"):
        segundos = await state_service.get_cooldown_remaining(target, "uso")
        await broadcaster_service.send_message_to_character(
            character,
            f"La poción aún está enfriándose. Espera {segundos}s."
        )
        return

    # 2. Verificar usos restantes (persistente)
    usos = await state_service.get_persistent(
        session=session,
        entity=target,
        key="usos_restantes",
        default=5
    )

    if usos <= 0:
        await broadcaster_service.send_message_to_character(
            character,
            "La poción está vacía."
        )
        return

    # 3. Ejecutar efecto
    vida_recuperada = 50
    character.attributes["vida"] = min(
        character.attributes.get("vida", 100) + vida_recuperada,
        character.attributes.get("vida_maxima", 100)
    )

    # 4. Actualizar estado persistente (usos)
    nuevo_usos = await state_service.decrement_persistent(
        session=session,
        entity=target,
        key="usos_restantes",
        min_value=0
    )

    # 5. Establecer cooldown transiente
    await state_service.set_cooldown(
        entity=target,
        cooldown_name="uso",
        duration=timedelta(seconds=30)
    )

    await session.commit()

    # 6. Feedback
    mensaje = f"Bebes {target.get_name()} y recuperas {vida_recuperada} puntos de vida."
    if nuevo_usos > 0:
        mensaje += f" Quedan {nuevo_usos} usos."
    else:
        mensaje += " La poción está vacía."

    await broadcaster_service.send_message_to_character(character, mensaje)
```

### Ejemplo: Sistema de Quest

```python
async def script_iniciar_quest_dragon(
    session: AsyncSession,
    target: Item,  # PNJ que da la quest
    character: Character,
    **kwargs
):
    """
    Inicia la quest del dragón.
    """
    # Verificar si ya completó la quest (persistente)
    completada = await state_service.get_persistent(
        session=session,
        entity=character,
        key="quest_dragon_completada",
        default=False
    )

    if completada:
        await broadcaster_service.send_message_to_character(
            character,
            "Ya has completado esta quest."
        )
        return

    # Verificar si ya tiene la quest activa (persistente)
    activa = await state_service.get_persistent(
        session=session,
        entity=character,
        key="quest_dragon_activa",
        default=False
    )

    if activa:
        await broadcaster_service.send_message_to_character(
            character,
            "Ya tienes esta quest activa."
        )
        return

    # Iniciar quest
    await state_service.set_persistent(
        session=session,
        entity=character,
        key="quest_dragon_activa",
        value=True
    )

    await state_service.set_persistent(
        session=session,
        entity=character,
        key="quest_dragon_progreso",
        value={"dragones_derrotados": 0, "objetivo": 5}
    )

    await session.commit()

    await broadcaster_service.send_message_to_character(
        character,
        "Has aceptado la Quest del Dragón. Debes derrotar 5 dragones."
    )
```

## Migración de Base de Datos (Pendiente)

**IMPORTANTE**: Para usar estado persistente, es necesario agregar la columna `script_state` a los modelos.

### Modelos a Actualizar

Agregar a `src/models/item.py`, `src/models/room.py`, `src/models/character.py`:

```python
from sqlalchemy import Column, JSONB

script_state = Column(JSONB, nullable=True, default=dict)
```

### Crear Migración

```bash
docker exec -it runegram-bot-1 alembic revision --autogenerate -m "Add script_state for Scripts system"
docker exec -it runegram-bot-1 alembic upgrade head
```

Hasta que se ejecute la migración, el estado persistente NO funcionará (pero el transiente sí).

## Mejores Prácticas

### 1. Valores por Defecto Sensatos

```python
# ✅ CORRECTO: Siempre proveer default
usos = await state_service.get_persistent(
    session=session,
    entity=item,
    key="usos_restantes",
    default=3
)

# ❌ INCORRECTO: Sin default (retorna None)
usos = await state_service.get_persistent(
    session=session,
    entity=item,
    key="usos_restantes"
)
if usos is None:  # Código innecesario
    usos = 3
```

### 2. Commit Después de Persistente

```python
# ✅ CORRECTO: Commit después de set_persistent
await state_service.set_persistent(session, item, "key", value)
await session.commit()

# ❌ INCORRECTO: Sin commit (cambios se pierden)
await state_service.set_persistent(session, item, "key", value)
```

### 3. TTL Apropiados para Cooldowns

```python
# ✅ CORRECTO: TTL realista
await state_service.set_cooldown(item, "habilidad", timedelta(minutes=5))

# ❌ INCORRECTO: TTL demasiado largo (usa persistente)
await state_service.set_cooldown(item, "buff", timedelta(days=30))  # Mejor en persistente
```

### 4. Nombres de Keys Descriptivos

```python
# ✅ CORRECTO: Claves descriptivas
await state_service.set_persistent(session, item, "quest_dragon_completada", True)
await state_service.set_cooldown(item, "habilidad_especial", timedelta(minutes=1))

# ❌ INCORRECTO: Claves ambiguas
await state_service.set_persistent(session, item, "flag", True)
await state_service.set_cooldown(item, "cd", timedelta(minutes=1))
```

### 5. Estructuras JSON para Datos Complejos

```python
# ✅ CORRECTO: Estructura JSON anidada
await state_service.set_persistent(
    session, character, "quest_progreso",
    {
        "dragones_derrotados": 3,
        "objetivo": 5,
        "recompensa_reclamada": False,
        "tiempo_inicio": "2025-10-17T12:00:00Z"
    }
)

# ❌ INCORRECTO: Múltiples claves sueltas
await state_service.set_persistent(session, character, "dragones_derrotados", 3)
await state_service.set_persistent(session, character, "objetivo", 5)
await state_service.set_persistent(session, character, "recompensa", False)
# ... mejor agrupado en una estructura
```

## Debugging

### Ver Estado Persistente en BD

```sql
-- Ver script_state de un item
SELECT id, key, script_state FROM items WHERE id = 42;

-- Ver todos los items con estado
SELECT id, key, script_state FROM items WHERE script_state IS NOT NULL;
```

### Ver Estado Transiente en Redis

```bash
# Conectar a Redis
docker exec -it runegram-redis-1 redis-cli

# Ver todas las claves de script_state
KEYS script_state:*

# Ver valor de una clave específica
GET script_state:item:42:cooldown_uso

# Ver TTL
TTL script_state:item:42:cooldown_uso
```

### Logging en Scripts

```python
# Loggear accesos a estado
valor = await state_service.get_persistent(session, item, "usos")
logging.debug(f"Item {item.id} tiene {valor} usos restantes")

# Loggear cambios de estado
await state_service.set_persistent(session, item, "usos", nuevo_valor)
logging.info(f"Item {item.id} ahora tiene {nuevo_valor} usos")
```

## Limitaciones

### 1. script_state Requiere Migración

La columna `script_state` debe agregarse a los modelos antes de usar estado persistente.

### 2. Estado Transiente No Persiste

Redis se limpia al reiniciar. No usar para datos críticos.

### 3. Sin Validación de Esquema

El campo `script_state` acepta cualquier JSON. Es responsabilidad de los scripts mantener consistencia.

### 4. Sin Transacciones en Redis

Las operaciones Redis no son transaccionales con PostgreSQL. Si un commit falla, el estado transiente ya cambió.

## Ver También

- [Sistema de Scripts](sistema-de-scripts.md) - Definición de scripts
- [Sistema de Eventos](sistema-de-eventos.md) - Event-driven architecture
- [Escritura de Scripts](../creacion-de-contenido/escritura-de-scripts.md) - Guía práctica
