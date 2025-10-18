---
título: "Sistema de Scripts"
categoría: "Sistemas del Motor"
última_actualización: "2025-10-17"
autor: "Proyecto Runegram"
etiquetas: ["scripts", "eventos", "scheduling", "automatización"]
documentos_relacionados:
  - "sistemas-del-motor/sistema-de-eventos.md"
  - "sistemas-del-motor/sistema-de-scheduling.md"
  - "sistemas-del-motor/sistema-de-estado.md"
  - "sistemas-del-motor/sistema-de-prototipos.md"
  - "creacion-de-contenido/escritura-de-scripts.md"
referencias_código:
  - "src/services/script_service.py"
  - "src/services/event_service.py"
  - "src/services/scheduler_service.py"
  - "src/services/state_service.py"
estado: "actual"
importancia: "crítica"
---

# Sistema de Scripts

El Sistema de Scripts es el puente que conecta el **Contenido** del juego (prototipos en `game_data/`) con la **Lógica** del motor (servicios en `src/services/`). Permite que objetos, salas y el mundo tengan comportamiento dinámico.

## Características Actuales

- ✅ **Event-driven architecture** (`event_service`)
- ✅ **Hybrid scheduling** (`scheduler_service` con tick + cron)
- ✅ **State management** (`state_service` persistente + transiente)
- ✅ **Prioridades** en scripts de eventos
- ✅ **Cancelación de acciones** (scripts BEFORE)
- ✅ **Hooks globales** para sistemas del motor
- ✅ **Retrocompatibilidad** completa con formatos anteriores

## Arquitectura

El sistema de scripts se compone de **4 servicios principales**:

```
┌─────────────────────────────────────────────────────────────┐
│                    SISTEMA DE SCRIPTS                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐ │
│  │ event_service  │  │ scheduler_     │  │ state_       │ │
│  │                │  │ service        │  │ service      │ │
│  │ • Eventos      │  │ • Tick scripts │  │ • Persistente│ │
│  │ • BEFORE/AFTER │  │ • Cron scripts │  │ • Transiente │ │
│  │ • Prioridades  │  │ • Híbrido      │  │ • Cooldowns  │ │
│  └────────────────┘  └────────────────┘  └──────────────┘ │
│           │                   │                    │        │
│           └───────────────────┴────────────────────┘        │
│                              │                              │
│                   ┌──────────▼──────────┐                  │
│                   │   script_service    │                  │
│                   │                     │                  │
│                   │ • SCRIPT_REGISTRY   │                  │
│                   │ • execute_script()  │                  │
│                   └─────────────────────┘                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1. script_service (Core)

El servicio central que:
- Registra funciones de script (`SCRIPT_REGISTRY`)
- Parsea script strings (`"script_name(arg=valor)"`)
- Ejecuta scripts de forma segura
- Proporciona contexto de ejecución

**Archivo**: `src/services/script_service.py`

### 2. event_service

Event Hub para scripts reactivos:
- Eventos BEFORE/AFTER
- Sistema de prioridades
- Cancelación de acciones
- Hooks globales

Ver: [Sistema de Eventos](sistema-de-eventos.md)

### 3. scheduler_service

Scheduler híbrido para scripts proactivos:
- Tick-based (retrocompatible)
- Cron-based (calendario real)
- Scripts globales vs por jugador

Ver: [Sistema de Scheduling](sistema-de-scheduling.md)

### 4. state_service

Gestión de estado para scripts:
- Estado persistente (PostgreSQL JSONB)
- Estado transiente (Redis con TTL)
- Helpers para cooldowns

Ver: [Sistema de Estado](sistema-de-estado.md)

## Script Service (Core)

### SCRIPT_REGISTRY

Diccionario que mapea nombres de script a funciones:

```python
# En src/services/script_service.py

SCRIPT_REGISTRY = {
    "script_notificar_brillo_magico": script_notificar_brillo_magico,
    "script_espada_susurra_secreto": script_espada_susurra_secreto,
    "check_peso_maximo": check_peso_maximo,
    "script_curacion_menor": script_curacion_menor,
    # ...
}
```

### Anatomía de una Función de Script

```python
async def script_ejemplo(
    session: AsyncSession,      # Sesión de BD (SIEMPRE)
    character: Character = None, # Quien dispara el evento (opcional)
    target: Any = None,          # Entidad objetivo (opcional)
    room: Room = None,           # Sala donde ocurre (opcional)
    **kwargs                     # Argumentos adicionales
):
    """
    Descripción del script.

    Args en kwargs:
        - arg1: Descripción
        - arg2: Descripción
    """
    # Obtener argumentos
    valor = kwargs.get("arg1", default_value)

    # Lógica del script
    # ...

    # Retornar True/False si es un script BEFORE
    return True  # Permite la acción
    # return False  # Cancela la acción
```

### Ejecutar un Script

```python
from src.services import script_service

result = await script_service.execute_script(
    script_string="script_ejemplo(arg1=valor1, arg2=42)",
    session=session,
    character=character,
    target=item,
    room=room
)
```

## Tipos de Scripts

### 1. Scripts de Eventos (Reactivos)

Se disparan cuando ocurre una acción del jugador.

**Eventos soportados**:
- `on_look`, `on_get`, `on_drop`, `on_use`
- `on_put`, `on_take`, `on_open`, `on_close`
- `on_enter`, `on_leave`, `on_room_look`
- Y más (ver `EventType` en `event_service.py`)

**Formato con prioridades**:
```python
"espada_magica": {
    "scripts": {
        "before_on_get": [
            {
                "script": "check_fuerza_minima(fuerza_requerida=10)",
                "priority": 10,
                "phase": "before",
                "cancel_message": "No eres lo suficientemente fuerte."
            }
        ],
        "after_on_get": [
            {
                "script": "notificar_brillo_magico(color=azul)",
                "priority": 0,
                "phase": "after"
            }
        ]
    }
}
```

**Formato simple** (retrocompatible):
```python
"espada_magica": {
    "scripts": {
        "on_look": "script_notificar_brillo_magico(color=azul)"
    }
}
```

Ver: [Sistema de Eventos](sistema-de-eventos.md) para detalles completos.

### 2. Scripts de Scheduling (Proactivos)

Se ejecutan automáticamente basados en tiempo.

#### Tick Scripts (Retrocompatible)

Basados en intervalos de ticks:

```python
"espada_viviente": {
    "tick_scripts": [
        {
            "interval_ticks": 60,  # Cada 60 ticks (120s)
            "script": "script_susurrar_secreto",
            "category": "ambient",
            "permanent": True
        }
    ]
}
```

#### Scheduled Scripts (Cron)

Basados en calendario real:

```python
"campana_ciudad": {
    "scheduled_scripts": [
        {
            "schedule": "0 12 * * *",  # Diario a las 12:00
            "script": "script_sonar_campanadas",
            "global": True,  # Ejecuta una sola vez
            "category": "ambient",
            "permanent": True
        }
    ]
}
```

Ver: [Sistema de Scheduling](sistema-de-scheduling.md) para detalles completos.

## Scripts con Estado

Los scripts pueden almacenar y recuperar estado usando `state_service`.

### Estado Persistente (sobrevive reinicios)

```python
async def script_usar_pocion_limitada(session, target, character, **kwargs):
    """Poción con 3 usos."""
    usos = await state_service.get_persistent(
        session=session,
        entity=target,
        key="usos_restantes",
        default=3
    )

    if usos <= 0:
        await message.answer("La poción está vacía.")
        return

    # Usar poción
    character.attributes["vida"] += 50

    # Decrementar usos
    await state_service.decrement_persistent(
        session=session,
        entity=target,
        key="usos_restantes",
        min_value=0
    )

    await session.commit()
```

### Estado Transiente (cooldowns)

```python
async def script_habilidad_con_cooldown(session, target, character, **kwargs):
    """Habilidad con cooldown de 1 minuto."""
    from datetime import timedelta

    # Verificar cooldown
    if await state_service.is_on_cooldown(target, "habilidad_especial"):
        segundos = await state_service.get_cooldown_remaining(target, "habilidad_especial")
        await message.answer(f"Debes esperar {segundos}s.")
        return

    # Ejecutar habilidad
    # ...

    # Establecer cooldown
    await state_service.set_cooldown(
        entity=target,
        cooldown_name="habilidad_especial",
        duration=timedelta(minutes=1)
    )
```

Ver: [Sistema de Estado](sistema-de-estado.md) para detalles completos.

## Flujo de Ejecución Completo

### Ejemplo: Comando /coger con Sistema de Scripts

```
1. Jugador ejecuta: /coger espada

2. CmdGet.execute() dispara evento BEFORE
   ↓
   event_service.trigger_event(ON_GET, BEFORE, context)
   ↓
   Ejecuta scripts "before_on_get" en orden de prioridad:
   - check_peso_maximo() [priority: 10]
   - check_permisos() [priority: 5]
   ↓
   Si algún script retorna False → Cancelar acción

3. Si no fue cancelado, ejecutar acción principal:
   - item.character_id = character.id
   - await session.commit()

4. CmdGet.execute() dispara evento AFTER
   ↓
   event_service.trigger_event(ON_GET, AFTER, context)
   ↓
   Ejecuta scripts "after_on_get":
   - notificar_sala()
   - activar_trampa()
   - log_accion()

5. Feedback al jugador
```

## Crear un Nuevo Script

### Paso 1: Escribir la Función

```python
# En src/services/script_service.py

async def script_activar_trampa(
    session: AsyncSession,
    target: Item,
    character: Character,
    room: Room,
    **kwargs
):
    """
    Activa una trampa cuando se coge el item.
    """
    danio = kwargs.get("danio", 10)

    # Aplicar daño
    character.attributes["vida"] -= danio

    # Notificar
    mensaje = f"<i>¡Una trampa se activa y {character.name} recibe {danio} puntos de daño!</i>"
    await broadcaster_service.send_message_to_room(
        session=session,
        room_id=room.id,
        message_text=mensaje
    )

    await session.commit()
```

### Paso 2: Registrar la Función

```python
# En src/services/script_service.py

SCRIPT_REGISTRY = {
    # ... otros scripts ...
    "script_activar_trampa": script_activar_trampa,
}
```

### Paso 3: Usar en Prototipo

```python
# En game_data/item_prototypes.py

"idolo_maldito": {
    "name": "un ídolo maldito",
    "description": "Una figura dorada que emana maldad...",
    "scripts": {
        "after_on_get": [
            {
                "script": "script_activar_trampa(danio=20)",
                "priority": 0,
                "phase": "after"
            }
        ]
    }
}
```

## Mejores Prácticas

### 1. Nomenclatura de Scripts

```python
# ✅ CORRECTO: Nombres descriptivos
script_espada_susurra_secreto
check_peso_maximo
notificar_brillo_magico

# ❌ INCORRECTO: Nombres genéricos
script_1
do_thing
handler
```

### 2. Usar BEFORE para Validaciones

```python
# ✅ CORRECTO
"before_on_get": [
    {"script": "check_peso()"},
    {"script": "check_permisos()"}
]

# ❌ INCORRECTO: Validaciones en AFTER (no pueden cancelar)
"after_on_get": [
    {"script": "check_peso()"}  # Demasiado tarde
]
```

### 3. Documentar Scripts

```python
async def script_ejemplo(session, **kwargs):
    """
    Descripción clara de qué hace el script.

    Args en kwargs:
        - danio (int): Cantidad de daño a aplicar
        - color (str): Color del efecto visual

    Retorna:
        bool: True si permite la acción (scripts BEFORE)
    """
```

### 4. Manejo de Errores

```python
async def script_con_errores(session, **kwargs):
    """Script robusto con manejo de errores."""
    try:
        valor = kwargs.get("valor_requerido")
        if not valor:
            logging.warning("Script llamado sin valor_requerido")
            return

        # Lógica del script
        # ...

    except Exception:
        logging.exception("Error en script_con_errores")
        # No propagar la excepción (para no romper el flujo)
```

### 5. Separar Lógica Compleja

```python
# ✅ CORRECTO: Scripts pequeños y enfocados
async def check_peso():
    # Solo verificar peso
    pass

async def check_espacio_inventario():
    # Solo verificar espacio
    pass

# ❌ INCORRECTO: Script monolítico
async def check_todo():
    # Hace demasiadas cosas
    pass
```

## Retrocompatibilidad

El sistema es 100% retrocompatible. No es necesario migrar scripts anteriores.

### Formatos Anteriores Siguen Funcionando

```python
# Formato anterior - Sigue funcionando perfectamente
"espada": {
    "scripts": {
        "on_look": "script_brillo()"
    },
    "tick_scripts": [
        {
            "interval_ticks": 60,
            "script": "script_susurro()"
        }
    ]
}
```

### Migrar al Formato Nuevo es Opcional

Para aprovechar las funcionalidades completas:

```python
# Formato con prioridades y fases
"espada": {
    "scripts": {
        "before_on_get": [
            {"script": "check_fuerza()", "priority": 10, "cancel_message": "..."}
        ],
        "after_on_look": [
            {"script": "script_brillo()", "priority": 0}
        ]
    },
    "tick_scripts": [...],  # Sin cambios
    "scheduled_scripts": [  # Formato cron
        {"schedule": "0 12 * * *", "script": "...", "global": True}
    ]
}
```

## Debugging

### Ver Scripts Ejecutados

```python
# Agregar logging en scripts
async def mi_script(session, **kwargs):
    logging.info(f"Ejecutando mi_script con kwargs: {kwargs}")
    # ...
```

### Verificar Registro de Scripts

```python
# En script_service.py
logging.info(f"Scripts registrados: {list(SCRIPT_REGISTRY.keys())}")
```

### Probar Scripts Manualmente

```python
# En un comando de admin
result = await script_service.execute_script(
    script_string="mi_script(arg=valor)",
    session=session,
    character=character,
    target=item
)

await message.answer(f"Resultado: {result}")
```

## Limitaciones

### 1. Sin Sandboxing Real

Los scripts tienen acceso completo a sesión de BD y contexto. Solo usar scripts confiables.

### 2. Scripts Deben Estar Registrados

Scripts referenciados en prototipos DEBEN existir en `SCRIPT_REGISTRY`.

### 3. Parsing Simple

El parser de scripts es básico. Argumentos complejos pueden requerir escaping.

### 4. Sin Type Safety

Los argumentos no son validados. Scripts deben manejar valores incorrectos.

## Ver También

- [Sistema de Eventos](sistema-de-eventos.md) - Event-driven architecture completa
- [Sistema de Scheduling](sistema-de-scheduling.md) - Tick y cron scripts
- [Sistema de Estado](sistema-de-estado.md) - Estado persistente y transiente
- [Escritura de Scripts](../creacion-de-contenido/escritura-de-scripts.md) - Guía práctica
- [Sistema de Prototipos](sistema-de-prototipos.md) - Definir scripts en prototipos
