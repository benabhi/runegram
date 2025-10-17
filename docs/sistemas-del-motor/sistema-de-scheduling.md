---
título: "Sistema de Scheduling"
categoría: "Sistemas del Motor"
versión: "2.0"
última_actualización: "2025-10-17"
autor: "Proyecto Runegram"
etiquetas: ["scheduling", "temporización", "ticks", "cron", "automatización", "scheduler"]
documentos_relacionados:
  - "sistemas-del-motor/sistema-de-scripts.md"
  - "sistemas-del-motor/sistema-de-eventos.md"
  - "arquitectura/configuracion.md"
referencias_código:
  - "src/services/scheduler_service.py"
  - "gameconfig.toml"
estado: "actual"
importancia: "crítica"
---

# Sistema de Scheduling (v2.0)

El Sistema de Scheduling es el "corazón" temporal de Runegram. Gestiona la ejecución programada de scripts mediante un sistema híbrido que soporta **tick-based scheduling** (v1.0) y **cron-based scheduling** (v2.0).

**IMPORTANTE**: Este servicio **reemplaza completamente** al antiguo `pulse_service.py` (eliminado), manteniendo 100% de retrocompatibilidad con el sistema de ticks existente.

## Visión General

### Arquitectura Híbrida

El `scheduler_service` combina tres tipos de scheduling:

1. **Tick-based** (v1.0): Intervalos basados en ticks (mantiene compatibilidad)
2. **Cron-based** (v2.0 - nuevo): Expresiones cron de calendario real
3. **Timestamp-based** (v2.0 - futuro): Eventos únicos en fecha/hora específica

### ¿Por Qué un Sistema Híbrido?

**Ventajas del sistema de ticks** (mantiene sistema original):
- ✅ Sincronización perfecta entre sistemas
- ✅ Timing relativo fácil de razonar
- ✅ Simple para diseñadores ("cada 60 ticks")
- ✅ Escalable (un solo job global)

**Ventajas del sistema cron** (nuevo en v2.0):
- ✅ Eventos basados en calendario real
- ✅ "Todos los días a las 12:00" sin calcular ticks
- ✅ Sintaxis estándar reconocible
- ✅ Scripts globales (ejecuta una sola vez vs por jugador)

## Componentes del Sistema

### 1. Scheduler Service

**Archivo**: `src/services/scheduler_service.py`
**Singleton**: `scheduler_service`

#### Métodos Públicos

```python
from src.services import scheduler_service

# Iniciar scheduler (llamado en run.py)
scheduler_service.start()

# Detener scheduler (shutdown ordenado)
scheduler_service.shutdown()

# Obtener tick actual
current_tick = scheduler_service.get_current_tick()

# Acceder a APScheduler interno
scheduler_service.scheduler.add_job(...)
```

#### Jobs Internos

El scheduler gestiona 3 jobs automáticamente:

1. **`tick_pulse`**: Ejecuta cada 2s (configurable) - procesa tick_scripts
2. **`cron_processor`**: Ejecuta cada minuto - procesa cron scripts
3. **`cron_reload`**: Ejecuta cada 5 min - recarga cache de cron scripts

### 2. Tick-based Scheduling (v1.0 - Retrocompatible)

Mantiene el sistema de pulse original sin cambios.

#### Definición en Prototipos

```python
# En game_data/item_prototypes.py
"espada_viviente": {
    "tick_scripts": [
        {
            "interval_ticks": 60,  # Cada 60 ticks (120s con tick=2s)
            "script": "script_espada_susurra_secreto",
            "category": "ambient",
            "permanent": True  # Se repite indefinidamente
        },
        {
            "interval_ticks": 1,  # Al primer tick después de spawnearse
            "script": "script_espada_despierta",
            "category": "ambient",
            "permanent": False  # Una sola vez
        }
    ]
}
```

#### Parámetros de tick_scripts

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `interval_ticks` | int | ✅ Sí | Cada cuántos ticks se ejecuta |
| `script` | str | ✅ Sí | Nombre del script en `SCRIPT_REGISTRY` |
| `category` | str | ❌ No | `"ambient"` (default), `"combat"`, `"system"` |
| `permanent` | bool | ❌ No | `True` (default): se repite, `False`: una sola vez |

#### Calcular interval_ticks

Con configuración por defecto (`interval_seconds = 2`):

| Tiempo Deseado | Cálculo | interval_ticks |
|----------------|---------|----------------|
| 10 segundos | 10 / 2 | 5 |
| 1 minuto | 60 / 2 | 30 |
| 2 minutos | 120 / 2 | 60 |
| 5 minutos | 300 / 2 | 150 |
| 1 hora | 3600 / 2 | 1800 |

**Fórmula**: `interval_ticks = segundos_deseados / interval_seconds`

### 3. Cron-based Scheduling (v2.0 - Nuevo)

Permite scheduling basado en expresiones cron estándar.

#### Definición en Prototipos

```python
# En game_data/item_prototypes.py
"campana_de_la_torre": {
    "scheduled_scripts": [
        {
            "schedule": "0 12 * * *",  # Diario a las 12:00 UTC
            "script": "script_sonar_campanadas_mediodia",
            "permanent": True,
            "global": True,  # Ejecuta UNA SOLA VEZ (no por jugador)
            "category": "ambient"
        },
        {
            "schedule": "0 */4 * * *",  # Cada 4 horas
            "script": "script_cambiar_clima",
            "permanent": True,
            "global": False,  # Ejecuta por cada jugador online
            "category": "system"
        }
    ]
}
```

#### Parámetros de scheduled_scripts

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `schedule` | str | ✅ Sí | Expresión cron (formato estándar) |
| `script` | str | ✅ Sí | Nombre del script en `SCRIPT_REGISTRY` |
| `permanent` | bool | ❌ No | `True` (default): se repite, `False`: una sola vez |
| `global` | bool | ❌ No | `True`: ejecuta una vez, `False` (default): por jugador |
| `category` | str | ❌ No | `"ambient"` (default), `"combat"`, `"system"` |

#### Sintaxis de Expresiones Cron

Formato: `minuto hora día_mes mes día_semana`

**Ejemplos comunes**:
```
0 12 * * *      # Diario a las 12:00
*/30 * * * *    # Cada 30 minutos
0 0 * * 0       # Domingos a medianoche
0 9-17 * * 1-5  # Lunes a Viernes, de 9 a 17 horas
```

Ver: [Crontab Guru](https://crontab.guru/) para ayuda con expresiones cron

#### Scripts Globales vs Por Jugador

**`global: true`** - Ejecuta UNA SOLA VEZ:
```python
"scheduled_scripts": [
    {
        "schedule": "0 12 * * *",
        "script": "script_anuncio_global",
        "global": True  # Se ejecuta una vez, no por cada jugador
    }
]
```

**`global: false`** - Ejecuta POR CADA JUGADOR ONLINE:
```python
"scheduled_scripts": [
    {
        "schedule": "0 8 * * *",
        "script": "script_entrega_recompensa_diaria",
        "global": False  # Se ejecuta para cada jugador
    }
]
```

### 4. Tracking y Estado

#### tick_data (JSONB)

Los tick_scripts usan `item.tick_data` para almacenar estado:

```python
item.tick_data = {
    "script_0": {
        "last_executed_tick": 58,
        "has_executed": True
    },
    "script_1": {
        "last_executed_tick": 120,
        "has_executed": False
    }
}
```

#### Cron Scripts Cache

El scheduler mantiene un cache interno de cron scripts que se recarga cada 5 minutos automáticamente. Esto permite agregar nuevos cron scripts sin reiniciar el bot.

## Flujo de Ejecución

### Tick-based (v1.0)

```
┌──────────────────────────────────────┐
│   scheduler_service.scheduler        │
│   (APScheduler - Job: tick_pulse)    │
└────────────┬─────────────────────────┘
             │ Cada 2 segundos
             ▼
┌──────────────────────────────────────┐
│   _execute_tick_pulse()              │
│   - Incrementa contador global       │
│   - Procesa tick_scripts             │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│   _process_tick_scripts()            │
│   - Query OPTIMIZADA (solo items     │
│     con tick_scripts)                │
│   - Itera items con scripts          │
└────────────┬─────────────────────────┘
             │ Por cada script
             ▼
┌──────────────────────────────────────┐
│   _process_single_tick_script()      │
│   - Verifica intervalo               │
│   - Filtra online (ambient)          │
│   - Ejecuta script_service           │
│   - Actualiza tick_data              │
└──────────────────────────────────────┘
```

### Cron-based (v2.0)

```
┌──────────────────────────────────────┐
│   scheduler_service.scheduler        │
│   (APScheduler - Job: cron_processor)│
└────────────┬─────────────────────────┘
             │ Cada minuto
             ▼
┌──────────────────────────────────────┐
│   _process_cron_scripts()            │
│   - Itera cache de cron scripts      │
│   - Verifica con croniter            │
└────────────┬─────────────────────────┘
             │ Por cada script a ejecutar
             ▼
┌──────────────────────────────────────┐
│   _execute_cron_script()             │
│   - Carga entidad                    │
│   - Si global: ejecuta una vez       │
│   - Si por jugador: itera online     │
│   - Ejecuta script_service           │
└──────────────────────────────────────┘
```

## Categorías de Scripts

Los scripts pueden tener diferentes categorías que afectan su comportamiento:

| Categoría | Descripción | Filtro de Online |
|-----------|-------------|------------------|
| `ambient` | Efectos ambientales, susurros, atmósfera | ✅ Solo jugadores online |
| `combat` | Sistema de combate (futuro) | ❌ Se ejecuta siempre |
| `system` | Sistemas globales (clima, día/noche) | ❌ Se ejecuta siempre |

## Uso para Diseñadores de Contenido

### ¿Cuándo usar tick_scripts?

✅ Efectos que deben sincronizarse con otros sistemas
✅ Timing relativo ("60 ticks después de X")
✅ Intervalos cortos (< 5 minutos)
✅ Scripts que cambian frecuentemente

### ¿Cuándo usar scheduled_scripts (cron)?

✅ Eventos basados en calendario real
✅ "Todos los días a las 12:00"
✅ Intervalos largos (horas, días)
✅ Scripts globales (una ejecución para todos)

### Ejemplos de Uso

#### Espada que Susurra Periódicamente (tick_scripts)

```python
"espada_susurrante": {
    "name": "una espada susurrante",
    "description": "La hoja parece murmurar palabras incomprensibles...",
    "tick_scripts": [
        {
            "interval_ticks": 150,  # Cada 5 minutos
            "script": "script_susurrar_secreto",
            "category": "ambient",
            "permanent": True
        }
    ]
}
```

#### Campana que Suena al Mediodía (scheduled_scripts)

```python
"campana_ciudad": {
    "name": "la campana de la ciudad",
    "description": "Una enorme campana de bronce...",
    "scheduled_scripts": [
        {
            "schedule": "0 12 * * *",  # Diario a las 12:00
            "script": "script_sonar_campanadas",
            "global": True,  # Solo una vez, no por cada jugador
            "category": "ambient",
            "permanent": True
        }
    ]
}
```

#### Sistema de Recompensas Diarias (scheduled_scripts)

```python
"libro_de_tareas": {
    "name": "un libro de tareas diarias",
    "description": "Un libro mágico que se actualiza cada día...",
    "scheduled_scripts": [
        {
            "schedule": "0 0 * * *",  # Medianoche
            "script": "script_renovar_tareas_diarias",
            "global": False,  # Por cada jugador online
            "category": "system",
            "permanent": True
        }
    ]
}
```

## Uso para Desarrolladores del Motor

### Migración desde pulse_service

Si estabas usando `pulse_service`, la migración es transparente:

```python
# ANTES (pulse_service - eliminado)
from src.services import pulse_service

pulse_service.initialize_pulse_system()
current_tick = pulse_service.get_current_tick()
pulse_service.scheduler.add_job(...)
pulse_service.shutdown_pulse_system()

# DESPUÉS (scheduler_service - nuevo)
from src.services import scheduler_service

scheduler_service.start()
current_tick = scheduler_service.get_current_tick()
scheduler_service.scheduler.add_job(...)
scheduler_service.shutdown()
```

### Crear Scripts para Scheduling

Los scripts se definen en `src/services/script_service.py`:

```python
async def script_sonar_campanadas(session: AsyncSession, target: Item, **kwargs):
    """
    Script global que suena campanadas a las 12:00.
    """
    execution_time = kwargs.get("execution_time")  # datetime del cron

    # Enviar mensaje a todos los jugadores online
    mensaje = "<i>Escuchas las campanadas de la torre sonar doce veces.</i>"

    # ... lógica para broadcast ...
```

### Configuración del Intervalo de Ticks

En `gameconfig.toml`:

```toml
[pulse]
interval_seconds = 2  # Por defecto: 2 segundos
```

**Consideraciones al cambiar el intervalo**:
- ⚠️ Intervalos más cortos (1s) = más carga
- ⚠️ Intervalos más largos (5s) = menos precisión
- ⚠️ Cambiar este valor afecta todos los `interval_ticks` en prototipos
- ✅ 2 segundos es un buen balance

## Optimizaciones v2.0

### 1. Query Optimizada para tick_scripts

```python
# Solo carga items QUE TIENEN tick_scripts
query = select(Item).where(
    Item.prototype['tick_scripts'].astext.is_not(None)
)
```

### 2. Cache de Cron Scripts

Los cron scripts se cargan una vez y se cachean, reduciendo queries a BD.

### 3. Recarga Automática

El cache se recarga cada 5 minutos, permitiendo agregar nuevos scripts sin reiniciar.

## Limitaciones y Consideraciones

### 1. El contador de ticks NO persiste

Si el bot se reinicia, el contador vuelve a 0. Los tick_scripts pueden ejecutarse antes/después de lo esperado tras un reinicio.

**Mitigación**: Aceptable para efectos ambient. Para persistencia exacta, usar cron scripts.

### 2. Cron Scripts requieren croniter

Para usar cron scripts, instalar dependencia opcional:

```bash
pip install croniter
```

Si no está instalado, los cron scripts se ignoran (con log de error).

### 3. Precisión de Cron Scripts

Los cron scripts se verifican cada minuto. Eventos con precisión < 1 minuto no son soportados (usar tick_scripts).

### 4. Zona Horaria

Los cron scripts usan UTC. Tener en cuenta al definir horarios.

## Debugging

### Ver Logs del Scheduler

```
✅ Scheduler Service iniciado (Tick + Cron + Timestamp).
⏰ Global Pulse: Tick #30
⏰ Global Pulse: Tick #60
📅 Cron scripts cache actualizado: 5 entidades.
```

### Verificar tick_data

```sql
SELECT id, key, tick_data FROM items WHERE key = 'espada_viviente';
```

### Verificar Cron Scripts en Cache

Los cron scripts se loggean al cargar:

```
📅 Cron scripts cache actualizado: 5 entidades.
```

## Ver También

- [Sistema de Scripts](sistema-de-scripts.md) - Uso de scripts con scheduling
- [Sistema de Eventos](sistema-de-eventos.md) - Event-driven architecture v2.0
- [Configuración](../arquitectura/configuracion.md) - Configurar interval_seconds
