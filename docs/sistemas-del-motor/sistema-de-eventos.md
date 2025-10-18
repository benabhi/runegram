---
título: "Sistema de Eventos"
categoría: "Sistemas del Motor"
última_actualización: "2025-10-17"
autor: "Proyecto Runegram"
etiquetas: ["eventos", "event-driven", "scripts", "hooks", "prioridades", "on_put", "on_take", "on_use", "on_enter", "on_leave", "on_spawn"]
documentos_relacionados:
  - "sistemas-del-motor/sistema-de-scripts.md"
  - "sistemas-del-motor/sistema-de-scheduling.md"
  - "sistemas-del-motor/sistema-de-estado.md"
  - "creacion-de-contenido/escritura-de-scripts.md"
  - "creacion-de-contenido/construccion-de-salas.md"
referencias_código:
  - "src/services/event_service.py"
  - "src/services/script_service.py"
  - "commands/player/movement.py"
  - "commands/admin/movement.py"
  - "commands/admin/building.py"
estado: "actual"
importancia: "crítica"
audiencia: "desarrollador"
---

# Sistema de Eventos

El Sistema de Eventos es el núcleo de la arquitectura **event-driven** de Runegram MUD. Permite que las acciones del jugador (y del sistema) disparen scripts de forma centralizada, sin que los comandos necesiten conocer qué scripts existen.

## Visión General

### Filosofía Event-Driven

En lugar de que cada comando ejecute scripts manualmente:

```python
# ❌ ANTIPATRÓN (scripts hardcodeados)
class CmdLook(Command):
    async def execute(self, character, session, message, args):
        # ... mostrar descripción ...

        # Hardcoded: el comando CONOCE los scripts
        if item.prototype.get("scripts", {}).get("on_look"):
            await script_service.execute_script(...)
```

El sistema de eventos desacopla comandos y scripts:

```python
# ✅ PATRÓN EVENT-DRIVEN (desacoplado)
class CmdLook(Command):
    async def execute(self, character, session, message, args):
        # ... mostrar descripción ...

        # El comando DISPARA un evento, sin conocer scripts
        result = await event_service.trigger_event(
            event_type=EventType.ON_LOOK,
            phase=EventPhase.AFTER,
            context=EventContext(
                session=session,
                character=character,
                target=item,
                room=room
            )
        )
```

### Beneficios

- ✅ **Desacoplamiento**: Comandos no conocen scripts
- ✅ **Extensibilidad**: Agregar scripts sin modificar comandos
- ✅ **Prioridades**: Control fino sobre orden de ejecución
- ✅ **Cancelación**: Scripts BEFORE pueden cancelar acciones
- ✅ **Hooks globales**: Sistemas del motor pueden escuchar eventos
- ✅ **Normalización**: Soporta formatos antiguos y nuevos automáticamente

## Componentes del Sistema

### 1. Event Service

**Archivo**: `src/services/event_service.py`
**Singleton**: `event_service`

Hub centralizado para manejo de eventos.

#### API Principal

```python
from src.services import event_service, EventType, EventPhase, EventContext, EventResult

# Disparar un evento
context = EventContext(
    session=session,
    character=character,
    target=item,
    room=room,
    extra={"cantidad": 5}  # Datos adicionales opcionales
)

result = await event_service.trigger_event(
    event_type=EventType.ON_GET,
    phase=EventPhase.BEFORE,
    context=context
)

# Verificar si la acción fue cancelada
if result.cancel_action:
    await message.answer(result.message or "La acción fue cancelada.")
    return
```

### 2. Event Types (Enum)

Tipos de eventos soportados:

```python
class EventType(Enum):
    # Items
    ON_LOOK = "on_look"
    ON_GET = "on_get"
    ON_DROP = "on_drop"
    ON_USE = "on_use"
    ON_OPEN = "on_open"
    ON_CLOSE = "on_close"
    ON_PUT = "on_put"
    ON_TAKE = "on_take"
    ON_SPAWN = "on_spawn"      # Generación de objetos
    ON_DESTROY = "on_destroy"

    # Rooms
    ON_ENTER = "on_enter"      # Entrada a salas
    ON_LEAVE = "on_leave"      # Salida de salas
    ON_ROOM_LOOK = "on_room_look"

    # Characters
    ON_LOGIN = "on_login"
    ON_LOGOUT = "on_logout"
    ON_DEATH = "on_death"
    ON_RESPAWN = "on_respawn"
    ON_LEVEL_UP = "on_level_up"

    # Combat (futuro)
    ON_ATTACK = "on_attack"
    ON_DEFEND = "on_defend"
    ON_DAMAGE = "on_damage"
    ON_KILL = "on_kill"
    ON_DIE = "on_die"
```

### 3. Event Phases (Enum)

Las fases determinan CUÁNDO se ejecutan los scripts:

```python
class EventPhase(Enum):
    BEFORE = "before"  # Antes de la acción (puede cancelar)
    AFTER = "after"    # Después de la acción
```

#### BEFORE vs AFTER

**BEFORE**: Validación y prevención
- ✅ Puede cancelar la acción retornando `False`
- ✅ Útil para checks de permisos, peso, espacio, etc.
- ✅ Se ejecuta ANTES de que ocurra la acción

**AFTER**: Efectos y notificaciones
- ❌ NO puede cancelar la acción
- ✅ Útil para efectos secundarios, notificaciones, logging
- ✅ Se ejecuta DESPUÉS de que ocurrió la acción

### 4. Event Context

Contenedor de información del evento:

```python
@dataclass
class EventContext:
    session: AsyncSession          # Sesión de BD
    character: Optional[Character] = None  # Quién dispara el evento
    target: Optional[Any] = None           # Entidad objetivo (Item, Room, etc.)
    room: Optional[Room] = None            # Sala donde ocurre
    extra: Dict[str, Any] = field(default_factory=dict)  # Datos adicionales
```

### 5. Event Result

Resultado de ejecutar un evento:

```python
@dataclass
class EventResult:
    success: bool                  # ¿Se ejecutó correctamente?
    cancel_action: bool = False    # ¿Cancelar la acción? (solo BEFORE)
    message: Optional[str] = None  # Mensaje opcional para el jugador
    data: Dict[str, Any] = field(default_factory=dict)  # Datos adicionales
```

## Uso en Comandos

### Patrón Básico

```python
class CmdExampleAction(Command):
    async def execute(self, character, session, message, args):
        # 1. Obtener entidades relevantes
        item = await find_item(...)
        room = character.room

        # 2. Disparar evento BEFORE (validación)
        context = EventContext(
            session=session,
            character=character,
            target=item,
            room=room
        )

        result_before = await event_service.trigger_event(
            event_type=EventType.ON_GET,
            phase=EventPhase.BEFORE,
            context=context
        )

        # 3. Verificar si fue cancelado
        if result_before.cancel_action:
            await message.answer(result_before.message or "No puedes hacer eso.")
            return

        # 4. Ejecutar la acción principal
        item.character_id = character.id
        await session.commit()

        # 5. Disparar evento AFTER (efectos)
        await event_service.trigger_event(
            event_type=EventType.ON_GET,
            phase=EventPhase.AFTER,
            context=context
        )

        # 6. Feedback al jugador
        await message.answer(f"Coges {item.get_name()}.")
```

### Ejemplo Real: CmdGet con Eventos

```python
class CmdGet(Command):
    names = ["coger", "tomar", "get"]

    async def execute(self, character, session, message, args):
        # ... búsqueda del item ...

        # Evento BEFORE: Verificar si puede coger el item
        context = EventContext(
            session=session,
            character=character,
            target=item,
            room=character.room
        )

        result_before = await event_service.trigger_event(
            event_type=EventType.ON_GET,
            phase=EventPhase.BEFORE,
            context=context
        )

        if result_before.cancel_action:
            await message.answer(result_before.message or "No puedes coger ese objeto.")
            return

        # Ejecutar acción
        item.room_id = None
        item.character_id = character.id
        await session.commit()

        # Evento AFTER: Efectos al coger
        await event_service.trigger_event(
            event_type=EventType.ON_GET,
            phase=EventPhase.AFTER,
            context=context
        )

        await message.answer(f"Coges {item.get_name()}.")
```

### Migración de Comandos Existentes

Esta sección documenta el patrón para migrar comandos que ejecutan scripts manualmente a usar el sistema de eventos.

#### Patrón de Migración BEFORE/AFTER

**Pasos para migrar un comando**:

1. **Identificar puntos de evento**: ¿Dónde se debería disparar BEFORE y AFTER?
2. **Agregar imports necesarios**: `event_service`, `EventType`, `EventPhase`, `EventContext`
3. **Crear EventContext**: Con session, character, target, room
4. **Disparar evento BEFORE**: Después de verificar locks, antes de la acción principal
5. **Verificar cancelación**: Si `result.cancel_action`, abortar
6. **Ejecutar acción principal**: Mover item, actualizar BD, etc.
7. **Disparar evento AFTER**: Después de la acción, antes del commit final

#### Ejemplo: Migración de CmdGet

**Antes (scripts hardcodeados)**:

```python
class CmdGet(Command):
    async def execute(self, character, session, message, args):
        # ... búsqueda del item ...

        # Verificar locks
        can_pass, error_message = await permission_service.can_execute(
            character, locks, access_type="get"
        )
        if not can_pass:
            await message.answer(error_message)
            return

        # Acción principal
        await item_service.move_item_to_character(session, item.id, character.id)

        # Mensajes
        await message.answer(f"Has cogido: {item.get_name()}")
```

**Después (sistema de eventos)**:

```python
from src.services import event_service, EventType, EventPhase, EventContext

class CmdGet(Command):
    async def execute(self, character, session, message, args):
        # ... búsqueda del item ...

        # Verificar locks
        can_pass, error_message = await permission_service.can_execute(
            character, locks, access_type="get"
        )
        if not can_pass:
            await message.answer(error_message)
            return

        # FASE BEFORE: Permite cancelar o modificar la acción de coger
        before_context = EventContext(
            session=session,
            character=character,
            target=item_to_get,
            room=character.room
        )

        before_result = await event_service.trigger_event(
            event_type=EventType.ON_GET,
            phase=EventPhase.BEFORE,
            context=before_context
        )

        # Si un script BEFORE cancela la acción, detener
        if before_result.cancel_action:
            await message.answer(before_result.message or "No puedes coger eso ahora.")
            return

        # Acción principal: mover item al inventario
        await item_service.move_item_to_character(session, item_to_get.id, character.id)

        # Mensajes
        await message.answer(f"Has cogido: {item_to_get.get_name()}")

        # FASE AFTER: Ejecutar efectos después de coger
        after_context = EventContext(
            session=session,
            character=character,
            target=item_to_get,
            room=character.room
        )

        await event_service.trigger_event(
            event_type=EventType.ON_GET,
            phase=EventPhase.AFTER,
            context=after_context
        )
```

#### Comandos Migrados

**ESTADO: COMPLETO** - Todos los comandos significativos han sido migrados al Sistema de Eventos.

| Comando | Archivo | EventType | Fases | Notas |
|---------|---------|-----------|-------|-------|
| `/mirar` | `commands/player/general.py` | `ON_LOOK` | BEFORE, AFTER | Migrado 2025-10-17 |
| `/coger` | `commands/player/interaction.py` | `ON_GET` | BEFORE, AFTER | Migrado 2025-10-17 |
| `/dejar` | `commands/player/interaction.py` | `ON_DROP` | BEFORE, AFTER | Migrado 2025-10-17 |
| `/meter` | `commands/player/interaction.py` | `ON_PUT` | BEFORE, AFTER | Migrado 2025-10-17 + extra container |
| `/sacar` | `commands/player/interaction.py` | `ON_TAKE` | BEFORE, AFTER | Migrado 2025-10-17 + extra container |
| `/usar` | `commands/player/interaction.py` | `ON_USE` | BEFORE, AFTER | Migrado 2025-10-17 (100% script-driven) |
| `/norte`, `/sur`, etc. | `commands/player/movement.py` | `ON_ENTER`, `ON_LEAVE` | BEFORE, AFTER | Migrado 2025-10-17 (10 direcciones) |
| `/teleport` | `commands/admin/movement.py` | `ON_ENTER`, `ON_LEAVE` | BEFORE, AFTER | Migrado 2025-10-17 + flag teleport |
| `/generarobjeto` | `commands/admin/building.py` | `ON_SPAWN` | BEFORE, AFTER | Migrado 2025-10-17 (nuevo evento) |
| `/destruirobjeto` | `commands/admin/building.py` | `ON_DESTROY` | BEFORE, AFTER | Migrado 2025-10-17 |

**Total: 10 comandos migrados** (20 direcciones de movimiento cuentan como 1 comando CmdMove)

#### Checklist de Migración

Antes de considerar completa la migración de un comando:

- [ ] Imports agregados: `event_service`, `EventType`, `EventPhase`, `EventContext`
- [ ] Evento BEFORE disparado después de verificar locks
- [ ] Cancelación verificada con `if result.cancel_action: return`
- [ ] Acción principal ejecutada solo si BEFORE no canceló
- [ ] Evento AFTER disparado después de la acción
- [ ] Mensajes de error usan `result.message` si está disponible
- [ ] Commits de sesión ocurren DESPUÉS de AFTER (para que scripts puedan modificar BD)

#### Características Especiales de Comandos Migrados

**CmdPut y CmdTake (Comandos de Contenedor)**:
- Pasan información adicional del contenedor en `extra={"container": container}`
- Permite que scripts reaccionen al contenedor específico usado
- Los scripts pueden acceder al contenedor mediante `context.extra.get("container")`

**CmdUse (Comando 100% Script-Driven)**:
- NO tiene "acción principal" - toda la lógica está en scripts ON_USE
- Escalable: Nuevos objetos usables solo requieren agregar scripts al prototipo
- No necesita modificarse para agregar nuevos tipos de objetos usables
- Captura el nombre del item ANTES de AFTER (por si scripts lo destruyen)
- Hace commit después de AFTER para persistir cambios de scripts
- Actualiza comandos de Telegram si el item otorgaba command sets
- Broadcasting incondicional (acción siempre visible)

## Ejemplos de Uso de Eventos por Tipo

### ON_PUT y ON_TAKE (Eventos de Contenedor)

Estos eventos se disparan cuando un jugador mete o saca objetos de contenedores. El contenedor está disponible en `context.extra["container"]`.

#### Ejemplo: Item que se resiste a ser guardado

```python
"espada_maldita": {
    "name": "una espada maldita",
    "description": "La hoja emite un brillo maligno...",
    "scripts": {
        "before_on_put": [{
            "script": "cancel_action(mensaje='La espada maldita se resiste a ser guardada')",
            "priority": 10
        }]
    }
}
```

#### Ejemplo: Contenedor que reacciona a objetos metidos

```python
"cofre_magico": {
    "name": "un cofre mágico",
    "is_container": True,
    "capacity": 10,
    "scripts": {
        "after_on_put": [{
            "script": "broadcast_room(mensaje='El cofre brilla al recibir un objeto')",
            "priority": 0
        }]
    }
}
```

#### Ejemplo: Item que purifica al sacarse de contenedor específico

```python
"arma_corrupta": {
    "name": "un arma corrupta",
    "scripts": {
        "after_on_take": [{
            "script": """
# Acceder al contenedor desde context.extra
container = context.extra.get('container')
if container and container.key == 'altar_purificador':
    # Cambiar estado del item
    await state_service.set_persistent(session, target, 'purificada', True)
    await broadcaster_service.send_message_to_character(
        character,
        '<i>El arma brilla intensamente al salir del altar. ¡Ha sido purificada!</i>'
    )
""",
            "priority": 0
        }]
    }
}
```

**Nota sobre context.extra**: Los scripts de ON_PUT y ON_TAKE pueden acceder al contenedor mediante `context.extra.get("container")`.

### ON_USE (Eventos de Uso)

El evento ON_USE es completamente script-driven. El comando `/usar` NO tiene acción principal - toda la lógica está en los scripts.

#### Ejemplo: Poción que cura

```python
"pocion_vida": {
    "name": "una poción de vida",
    "description": "Un frasco con líquido rojo brillante.",
    "scripts": {
        "after_on_use": [{
            "script": "global:curar_personaje(cantidad=50, mensaje='Te sientes revitalizado')",
            "priority": 0
        }]
    }
}
```

#### Ejemplo: Item consumible con usos limitados

```python
"pergamino_teleport": {
    "name": "un pergamino de teletransporte",
    "scripts": {
        "before_on_use": [{
            "script": """
# Verificar si tiene usos restantes
usos = await state_service.get_persistent(session, target, 'usos', default=3)
if usos <= 0:
    return False  # Cancelar acción
return True
""",
            "cancel_message": "El pergamino se desintegra. Ya no tiene más poder.",
            "priority": 10
        }],
        "after_on_use": [{
            "script": """
# Decrementar usos
usos = await state_service.get_persistent(session, target, 'usos', default=3)
await state_service.set_persistent(session, target, 'usos', usos - 1)

# Teletransportar a sala aleatoria
await global_scripts.teleport_aleatorio(session, character, target, room)

# Destruir item si era el último uso
if usos - 1 <= 0:
    await session.delete(target)
    await session.flush()
""",
            "priority": 0
        }]
    }
}
```

#### Ejemplo: Item que otorga habilidades temporales

```python
"elixir_fuerza": {
    "name": "un elixir de fuerza",
    "scripts": {
        "after_on_use": [{
            "script": """
# Otorgar buff temporal (30 minutos)
from datetime import timedelta
await state_service.set_transient(target, 'fuerza_aumentada', True, ttl=timedelta(minutes=30))

# Notificar jugador
await broadcaster_service.send_message_to_character(
    character,
    '<i>Sientes una oleada de fuerza sobrehumana recorrer tu cuerpo.</i>'
)

# Destruir item (consumible)
await session.delete(target)
await session.flush()
""",
            "priority": 0
        }]
    }
}
```

**Diseño de CmdUse**: Es 100% genérico. Nuevos objetos usables solo requieren definir scripts ON_USE en el prototipo. No necesitas modificar el comando.

### ON_ENTER y ON_LEAVE (Eventos de Movimiento)

Estos eventos se disparan cuando un jugador entra o sale de una sala. Permiten crear salas reactivas que responden al movimiento de jugadores.

#### Flujo de Eventos en Movimiento

Cuando un jugador se mueve de Sala A → Sala B:

1. **BEFORE ON_LEAVE** (Sala A) - Puede cancelar el movimiento
2. **AFTER ON_LEAVE** (Sala A) - Efectos al salir (si no fue cancelado)
3. **BEFORE ON_ENTER** (Sala B) - Puede cancelar la entrada
4. **AFTER ON_ENTER** (Sala B) - Efectos al entrar (si no fue cancelado)

#### Ejemplo: Sala que previene salida durante combate

```python
"arena_combate": {
    "name": "Arena de Combate",
    "description": "Un círculo de arena rodeado por gradas. No hay escapatoria durante el combate.",
    "scripts": {
        "before_on_leave": [{
            "script": """
# Verificar si el personaje está en combate
in_combat = await state_service.get_persistent(session, character, 'in_combat', default=False)
if in_combat:
    return False  # Cancelar movimiento
return True
""",
            "cancel_message": "¡No puedes huir del combate!",
            "priority": 10
        }]
    }
}
```

#### Ejemplo: Sala con trampa en la entrada

```python
"cueva_oscura": {
    "name": "Cueva Oscura",
    "description": "Una cueva húmeda y peligrosa. Algo cruje bajo tus pies...",
    "scripts": {
        "after_on_enter": [{
            "script": """
# Verificar si la trampa ya fue activada
trampa_activada = await state_service.get_persistent(session, room, 'trampa_activada', default=False)

if not trampa_activada:
    # Activar trampa (daño al personaje)
    character.attributes['hp'] = character.attributes.get('hp', 100) - 10
    await session.flush()

    # Marcar trampa como activada
    await state_service.set_persistent(session, room, 'trampa_activada', True)

    # Notificar a la sala
    await broadcaster_service.send_message_to_room(
        session=session,
        room_id=room.id,
        message_text='<i>¡Has activado una trampa! Pinchos emergen del suelo.</i>'
    )
""",
            "priority": 0
        }]
    }
}
```

#### Ejemplo: Sala con boss que inicia combate automáticamente

```python
"camara_dragon": {
    "name": "Cámara del Dragón",
    "description": "Una vasta cámara llena de tesoros. Un dragón inmenso yace dormido en el centro.",
    "scripts": {
        "after_on_enter": [{
            "script": """
# Verificar si el dragón ya fue derrotado
dragon_muerto = await state_service.get_persistent(session, room, 'dragon_muerto', default=False)

if not dragon_muerto:
    # Iniciar combate automáticamente
    await state_service.set_persistent(session, character, 'in_combat', True)
    await state_service.set_persistent(session, character, 'enemy', 'dragon_anciano')

    # Mensaje dramático
    await broadcaster_service.send_message_to_room(
        session=session,
        room_id=room.id,
        message_text='<b>El dragón abre un ojo. "Intruso..." ruge con voz atronadora.</b>'
    )
""",
            "priority": 0
        }]
    }
}
```

#### Diferencia: Movimiento Normal vs. Teletransporte

El comando `/teleport` (admin) usa los mismos eventos ON_ENTER/ON_LEAVE pero pasa un flag adicional en `extra`:

```python
# En CmdTeleport
extra = {"teleport": True}
```

Los scripts pueden detectar si el movimiento fue teletransporte:

```python
"sala_protegida": {
    "scripts": {
        "before_on_enter": [{
            "script": """
# Permitir teletransporte de admins, bloquear entrada normal
is_teleport = context.extra.get('teleport', False)
if not is_teleport:
    return False  # Bloquear entrada normal
return True  # Permitir teletransporte
""",
            "cancel_message": "Una barrera invisible bloquea la entrada.",
            "priority": 10
        }]
    }
}
```

**Nota sobre context.extra**: Todos los scripts de movimiento pueden acceder a `context.extra.get("teleport")` para diferenciar teletransporte de movimiento normal.

### ON_SPAWN (Evento de Generación)

El evento ON_SPAWN se dispara cuando un admin usa `/generarobjeto` para crear un objeto en el mundo.

#### Flujo de Eventos en Spawning

1. **BEFORE ON_SPAWN** - Puede cancelar la creación del objeto
2. Se crea el objeto en la base de datos
3. **AFTER ON_SPAWN** - Efectos después de crear el objeto

#### Ejemplo: Item que requiere condiciones especiales para spawnearse

```python
"reliquia_sagrada": {
    "name": "Reliquia Sagrada",
    "description": "Un artefacto de poder divino que solo puede manifestarse en lugares consagrados.",
    "scripts": {
        "before_on_spawn": [{
            "script": """
# Solo puede spawnearse en salas sagradas
es_sala_sagrada = room.has_tag('sagrado')
if not es_sala_sagrada:
    return False  # Cancelar spawning
return True
""",
            "cancel_message": "La Reliquia Sagrada solo puede manifestarse en lugares consagrados.",
            "priority": 10
        }]
    }
}
```

#### Ejemplo: Item que ejecuta inicialización especial al spawnearse

```python
"artefacto_antiguo": {
    "name": "Artefacto Antiguo",
    "description": "Un artefacto cubierto de runas misteriosas.",
    "scripts": {
        "after_on_spawn": [{
            "script": """
# Inicializar estado del artefacto
import random
poder = random.randint(50, 100)
await state_service.set_persistent(session, target, 'poder', poder)
await state_service.set_persistent(session, target, 'cargas', 10)

# Notificar poder inicial
await broadcaster_service.send_message_to_room(
    session=session,
    room_id=room.id,
    message_text=f'<i>El artefacto zumba con poder. Sientes que tiene un nivel de energía de {poder}.</i>'
)
""",
            "priority": 0
        }]
    }
}
```

**Dato Importante**: Los scripts BEFORE ON_SPAWN reciben el prototipo completo en `context.extra['prototype']` para poder tomar decisiones antes de que el objeto exista.

## Definición de Scripts en Prototipos

### Formato con Prioridades

```python
# En game_data/item_prototypes.py
"cofre_pesado": {
    "name": "un cofre pesado",
    "description": "Un cofre de hierro macizo...",
    "scripts": {
        "before_on_get": [
            {
                "script": "check_peso_maximo()",
                "priority": 10,  # Mayor prioridad = ejecuta primero
                "phase": "before",
                "cancel_message": "El cofre es demasiado pesado para levantarlo."
            },
            {
                "script": "check_fuerza_minima(fuerza_requerida=15)",
                "priority": 5,
                "phase": "before",
                "cancel_message": "No eres lo suficientemente fuerte para levantarlo."
            }
        ],
        "after_on_get": [
            {
                "script": "notificar_sala_pickup()",
                "priority": 0,
                "phase": "after"
            }
        ]
    }
}
```

### Formato Simple (Retrocompatible)

El sistema normaliza automáticamente el formato simple:

```python
# Formato simple (sigue funcionando)
"espada_magica": {
    "scripts": {
        "on_look": "script_notificar_brillo_magico(color=azul)"
    }
}

# Se convierte internamente a:
# "after_on_look": [{"script": "script_notificar_brillo_magico(color=azul)", "priority": 0}]
```

### Convenciones de Nomenclatura

Los eventos se nombran con el patrón: `{phase}_{event_type}`

| Event Type | Phase BEFORE | Phase AFTER |
|-----------|--------------|-------------|
| `ON_LOOK` | `before_on_look` | `after_on_look` |
| `ON_GET` | `before_on_get` | `after_on_get` |
| `ON_DROP` | `before_on_drop` | `after_on_drop` |
| `ON_PUT` | `before_on_put` | `after_on_put` |
| `ON_TAKE` | `before_on_take` | `after_on_take` |
| `ON_USE` | `before_on_use` | `after_on_use` |
| `ON_ENTER` | `before_on_enter` | `after_on_enter` |
| `ON_LEAVE` | `before_on_leave` | `after_on_leave` |
| `ON_SPAWN` | `before_on_spawn` | `after_on_spawn` |
| `ON_DESTROY` | `before_on_destroy` | `after_on_destroy` |

## Sistema de Prioridades

Los scripts con **mayor prioridad** se ejecutan **primero**.

### Orden de Ejecución

```python
"scripts": {
    "before_on_get": [
        {"script": "check_1()", "priority": 10},  # Ejecuta 1º
        {"script": "check_2()", "priority": 10},  # Ejecuta 2º (mismo priority)
        {"script": "check_3()", "priority": 5},   # Ejecuta 3º
        {"script": "check_4()", "priority": 0}    # Ejecuta 4º (último)
    ]
}
```

### Casos de Uso de Prioridades

**Alta prioridad (10+)**: Validaciones críticas
```python
{"script": "check_baneado()", "priority": 100}  # Verificar primero
{"script": "check_permisos_admin()", "priority": 50}
```

**Media prioridad (5-9)**: Validaciones de negocio
```python
{"script": "check_peso()", "priority": 10}
{"script": "check_espacio_inventario()", "priority": 9}
```

**Baja prioridad (0-4)**: Efectos secundarios
```python
{"script": "notificar_sala()", "priority": 1}
{"script": "log_accion()", "priority": 0}
```

## Cancelación de Acciones

Solo los scripts BEFORE pueden cancelar acciones.

### Retornar False en Script

```python
# En src/services/script_service.py
async def check_peso_maximo(session: AsyncSession, character: Character, target: Item, **kwargs):
    """
    Verifica si el personaje puede cargar el item.
    Retorna False para cancelar la acción.
    """
    peso_actual = sum(i.attributes.get("peso", 0) for i in character.items)
    peso_item = target.attributes.get("peso", 0)
    peso_maximo = character.attributes.get("peso_maximo", 100)

    if peso_actual + peso_item > peso_maximo:
        return False  # Cancela la acción

    return True  # Permite la acción
```

### Mensaje de Cancelación

```python
"before_on_get": [
    {
        "script": "check_peso_maximo()",
        "priority": 10,
        "cancel_message": "No puedes cargar más peso."  # Mensaje personalizado
    }
]
```

Si el script retorna `False`:
1. El `EventResult.cancel_action` será `True`
2. El comando debe verificar esto y abortar
3. Se muestra `cancel_message` al jugador

## Hooks Globales

Los hooks globales permiten que sistemas del motor escuchen TODOS los eventos de un tipo.

### Registrar un Hook Global

```python
from src.services import event_service, EventType

async def log_all_gets(phase: EventPhase, context: EventContext):
    """Hook que loggea todos los comandos /coger."""
    if phase == EventPhase.AFTER:
        logging.info(f"{context.character.name} cogió {context.target.get_name()}")

# Registrar el hook al iniciar el bot
event_service.register_global_hook(
    event_type=EventType.ON_GET,
    hook_func=log_all_gets
)
```

### Casos de Uso de Hooks

**Logging y Analytics**:
```python
async def track_item_pickups(phase, context):
    # Enviar métricas a analytics
    pass
```

**Sistema de Achievements**:
```python
async def check_achievement_pickup_legendary(phase, context):
    if context.target.has_tag("legendary"):
        # Otorgar achievement
        pass
```

**Sistema de Combate**:
```python
async def trigger_combat_on_attack(phase, context):
    # Iniciar combate cuando se dispara ON_ATTACK
    pass
```

## Normalización de Formatos

El event_service normaliza automáticamente scripts en diferentes formatos.

### Conversiones Automáticas

**String simple** → Lista con priority 0:
```python
# Entrada simple
"on_look": "script_brillo()"

# Normalizado internamente
"after_on_look": [{"script": "script_brillo()", "priority": 0, "phase": "after"}]
```

**Lista de strings** → Lista con priority 0:
```python
# Entrada simple
"on_get": ["script_1()", "script_2()"]

# Normalizado internamente
"after_on_get": [
    {"script": "script_1()", "priority": 0, "phase": "after"},
    {"script": "script_2()", "priority": 0, "phase": "after"}
]
```

**Lista con dicts** → Ya en formato completo:
```python
# Ya normalizado
"before_on_get": [
    {"script": "check()", "priority": 10, "phase": "before"}
]
```

## Mejores Prácticas

### 1. Usar BEFORE para Validaciones

```python
# ✅ CORRECTO: Validaciones en BEFORE
"before_on_get": [
    {"script": "check_permisos()", "priority": 10},
    {"script": "check_peso()", "priority": 9}
]

# ❌ INCORRECTO: Validaciones en AFTER (no pueden cancelar)
"after_on_get": [
    {"script": "check_permisos()"}  # Demasiado tarde, ya se ejecutó la acción
]
```

### 2. Usar AFTER para Efectos

```python
# ✅ CORRECTO: Efectos en AFTER
"after_on_get": [
    {"script": "notificar_sala()"},
    {"script": "activar_trampa()"},
    {"script": "log_accion()"}
]
```

### 3. Prioridades Lógicas

```python
# ✅ CORRECTO: Orden lógico de validaciones
"before_on_get": [
    {"script": "check_baneado()", "priority": 100},       # Primero
    {"script": "check_permisos_admin()", "priority": 50},
    {"script": "check_peso()", "priority": 10},
    {"script": "check_espacio_inventario()", "priority": 9}  # Último
]
```

### 4. Mensajes de Cancelación Descriptivos

```python
# ✅ CORRECTO: Mensaje claro
{
    "script": "check_llave()",
    "cancel_message": "El cofre está cerrado con llave. Necesitas la llave de bronce."
}

# ❌ INCORRECTO: Mensaje genérico
{
    "script": "check_llave()",
    "cancel_message": "No puedes hacer eso."
}
```

### 5. Mantener Scripts Pequeños y Enfocados

```python
# ✅ CORRECTO: Scripts específicos
"before_on_get": [
    {"script": "check_peso()"},
    {"script": "check_espacio()"},
    {"script": "check_permisos()"}
]

# ❌ INCORRECTO: Script monolítico
"before_on_get": [
    {"script": "check_todo()"}  # Hace demasiadas cosas
]
```

## Debugging

### Logs del Event Service

```python
# Los errores se loggean automáticamente
logging.exception(f"Error ejecutando script de evento {event_name}")
```

### Verificar Ejecución de Scripts

```python
# En scripts, agregar logging
async def mi_script(session, **context):
    logging.info(f"Ejecutando mi_script para {context['character'].name}")
    # ... lógica ...
```

### Verificar Cancelación

```python
result = await event_service.trigger_event(...)

if result.cancel_action:
    logging.info(f"Acción cancelada: {result.message}")
```

## Limitaciones

### 1. Scripts deben estar registrados

Los scripts referenciados en prototipos DEBEN existir en `SCRIPT_REGISTRY`.

```python
# En src/services/script_service.py
SCRIPT_REGISTRY = {
    "check_peso": check_peso,
    # ...
}
```

### 2. EventTypes son fijos

No se pueden agregar nuevos `EventType` sin modificar el enum en `event_service.py`.

### 3. No hay sandboxing

Los scripts tienen acceso completo a sesión de BD y contexto. Solo usar scripts confiables.

## Ver También

- [Sistema de Scripts](sistema-de-scripts.md) - Definición y ejecución de scripts
- [Sistema de Estado](sistema-de-estado.md) - Estado persistente/transiente para scripts
- [Sistema de Scheduling](sistema-de-scheduling.md) - Scheduling de scripts
- [Escritura de Scripts](../creacion-de-contenido/escritura-de-scripts.md) - Guía práctica
