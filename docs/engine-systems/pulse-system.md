---
título: "Sistema de Pulso"
categoría: "Sistemas del Motor"
versión: "1.0"
última_actualización: "2025-10-09"
autor: "Proyecto Runegram"
etiquetas: ["pulso", "temporización", "ticks", "automatización", "scheduler"]
documentos_relacionados:
  - "engine-systems/scripting-system.md"
  - "architecture/configuration.md"
referencias_código:
  - "src/services/pulse_service.py"
  - "gameconfig.toml"
estado: "actual"
---

# Pulse System

El Sistema de Pulse es el "corazón" temporal de Runegram. Ejecuta un "tick" cada 2 segundos (configurable), permitiendo que todos los sistemas basados en tiempo se sincronicen con el mismo heartbeat global.

## ¿Por Qué un Sistema de Pulse?

### Problemas del Enfoque Anterior (APScheduler Individual)

Antes del sistema de pulse, cada entidad (item, room, etc.) con tickers programaba su propio job en APScheduler:

```python
# Enfoque ANTIGUO (ya no se usa)
"tickers": [
    {
        "schedule": "*/2 * * * *",  # Expresión cron: cada 2 minutos
        "script": "script_espada_susurra",
        "category": "ambient"
    }
]
```

**Problemas:**
- ⚠️ **Escalabilidad**: Con 1000 items = 1000+ jobs individuales en APScheduler
- ⚠️ **Falta de sincronización**: Imposible coordinar timing preciso entre sistemas
- ⚠️ **Complejidad**: Expresiones cron son crípticas para diseñadores de contenido
- ⚠️ **Inflexibilidad**: Difícil pausar, reanudar, o razonar sobre timing relativo

### Ventajas del Sistema de Pulse

```python
# Enfoque NUEVO
"tick_scripts": [
    {
        "interval_ticks": 60,  # Cada 60 ticks (120s con tick=2s)
        "script": "script_espada_susurra",
        "category": "ambient",
        "permanent": True  # Se repite indefinidamente
    }
]
```

**Ventajas:**
- ✅ **Escalabilidad**: Un solo job global procesa todas las entidades
- ✅ **Sincronización**: Todos los sistemas operan en la misma timeline
- ✅ **Simplicidad**: "Cada 60 ticks" es más claro que `*/2 * * * *`
- ✅ **Flexibilidad**: Timing relativo, scripts one-shot, pausado futuro
- ✅ **Predictibilidad**: Orden de ejecución determinista

## Arquitectura

### Flujo de Ejecución

```
┌──────────────────────────────────────┐
│   pulse_service.scheduler            │
│   (APScheduler - Un solo job)        │
└────────────┬─────────────────────────┘
             │ Cada 2 segundos
             ▼
┌──────────────────────────────────────┐
│   _execute_global_pulse()            │
│   - Incrementa contador global       │
│   - Procesa todas las entidades      │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│   _process_items_tick_scripts()      │
│   - Itera todos los Items           │
│   - Verifica tick_scripts            │
└────────────┬─────────────────────────┘
             │ Por cada item con tick_scripts
             ▼
┌──────────────────────────────────────┐
│   _process_single_tick_script()      │
│   - Verifica si es momento de exec   │
│   - Filtra por online (ambient)      │
│   - Ejecuta script_service           │
│   - Actualiza tracking en tick_data  │
└──────────────────────────────────────┘
```

### Componentes Clave

#### 1. **Contador Global de Ticks**

```python
_global_tick_counter = 0  # Incrementa en cada pulse
```

- Se incrementa en cada ejecución del pulse
- Persiste en memoria durante la ejecución del bot
- **No persiste en BD**: Se resetea cuando el bot se reinicia

**Implicación**: Los tick_scripts pueden retrasarse ligeramente después de un reinicio, pero esto es aceptable para la mayoría de casos de uso (efectos ambient, clima, etc.).

#### 2. **Tracking en `tick_data` (JSONB)**

Cada Item tiene un campo `tick_data` que almacena el estado de sus tick_scripts:

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

**Qué almacena:**
- `last_executed_tick`: El tick global en que se ejecutó por última vez
- `has_executed`: Si se ha ejecutado alguna vez (importante para scripts one-shot)

#### 3. **Categorías de Scripts**

Los tick_scripts pueden tener diferentes categorías que afectan su comportamiento:

| Categoría | Descripción | Filtro de Online |
|-----------|-------------|------------------|
| `ambient` | Efectos ambientales, susurros, atmósfera | ✅ Solo jugadores online |
| `combat` | Sistema de combate (futuro) | ❌ Se ejecuta siempre |
| `system` | Sistemas globales (clima, día/noche) | ❌ Se ejecuta siempre |

## Uso para Diseñadores de Contenido

### Definir un Tick Script en un Prototipo

```python
# En game_data/item_prototypes.py

"espada_viviente": {
    "name": "una espada viviente",
    "description": "La hoja parece retorcerse...",
    "keywords": ["espada", "viviente"],
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
            "permanent": False  # Se ejecuta UNA SOLA VEZ
        }
    ]
}
```

### Parámetros de un Tick Script

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `interval_ticks` | int | ✅ Sí | Cada cuántos ticks se ejecuta |
| `script` | str | ✅ Sí | Nombre del script en `SCRIPT_REGISTRY` |
| `category` | str | ❌ No | `"ambient"` (default), `"combat"`, `"system"` |
| `permanent` | bool | ❌ No | `True` (default): se repite, `False`: una sola vez |

### Calcular interval_ticks

El intervalo del pulse se configura en `gameconfig.toml` bajo `[pulse] interval_seconds` (por defecto: 2 segundos).

Con la configuración por defecto (`interval_seconds = 2`):

| Tiempo Deseado | Cálculo | interval_ticks |
|----------------|---------|----------------|
| 10 segundos | 10 / 2 | 5 |
| 1 minuto | 60 / 2 | 30 |
| 2 minutos | 120 / 2 | 60 |
| 5 minutos | 300 / 2 | 150 |
| 1 hora | 3600 / 2 | 1800 |

**Fórmula**: `interval_ticks = segundos_deseados / interval_seconds`

**⚠️ IMPORTANTE:** Si modificas `interval_seconds` en `gameconfig.toml`, debes recalcular todos los `interval_ticks` en los prototipos para mantener el mismo timing.

## Uso para Desarrolladores del Motor

### Crear un Nuevo Script para Tick

1. **Escribir la función en `src/services/script_service.py`**:

```python
async def script_espada_despierta(session: AsyncSession, target: Item, character: Character, **kwargs):
    """
    Script que se ejecuta una vez cuando la espada se spawnea.
    """
    mensaje = f"<i>{target.get_name()} parece cobrar vida por primera vez...</i>"
    await broadcaster_service.send_message_to_character(character, mensaje)
```

2. **Registrar en `SCRIPT_REGISTRY`**:

```python
SCRIPT_REGISTRY = {
    # ... otros scripts ...
    "script_espada_despierta": script_espada_despierta,
}
```

3. **Usar en prototipo** (como se mostró arriba)

### Consultar el Tick Actual

```python
from src.services import pulse_service

current_tick = pulse_service.get_current_tick()
logging.info(f"Tick actual: {current_tick}")
```

### Configurar el Intervalo del Pulse

En `gameconfig.toml`:

```toml
[pulse]
interval_seconds = 2  # Por defecto: 2 segundos
```

Después de modificar, reiniciar el bot para aplicar cambios:
```bash
docker-compose restart bot
```

**Consideraciones al cambiar el intervalo:**
- ⚠️ Intervalos más cortos (1s) = más carga en BD y CPU
- ⚠️ Intervalos más largos (5s) = menos precisión temporal
- ⚠️ Cambiar este valor afecta todos los `interval_ticks` en prototipos
- ✅ 2 segundos es un buen balance entre precisión y performance

## Casos de Uso Futuros

El sistema de pulse está diseñado para soportar:

### 1. Sistema de Combate por Turnos

```python
# Futuro: Combate sincronizado
class CombatSystem:
    async def process_combat_round(self):
        # Se ejecuta cada 3 ticks (6 segundos)
        # Todos los combates procesan su turno simultáneamente
        pass
```

### 2. Sistema de Clima Dinámico

```python
# Futuro: Cambios de clima sincronizados en todo el mundo
"tick_scripts": [
    {
        "interval_ticks": 900,  # Cada 30 minutos
        "script": "script_cambiar_clima",
        "category": "system",
        "permanent": True
    }
]
```

### 3. Monstruos Errantes

```python
# Futuro: Spawning coordinado de mobs
"tick_scripts": [
    {
        "interval_ticks": 300,  # Cada 10 minutos
        "script": "script_spawn_mob_errante",
        "category": "system",
        "permanent": True
    }
]
```

### 4. Efectos Temporales en Combate

```python
# Futuro: Buff que dura exactamente 10 ticks
character.apply_buff("fuerza", duration_ticks=10)
```

## Limitaciones y Consideraciones

### 1. **El contador de ticks NO persiste**

Si el bot se reinicia, el contador vuelve a 0. Esto significa que los tick_scripts pueden ejecutarse antes/después de lo esperado tras un reinicio.

**Mitigación**: Aceptable para efectos ambient. Si necesitas persistencia exacta, considera usar timestamps en lugar de ticks.

### 2. **Performance con Muchas Entidades**

El pulse itera sobre TODAS las entidades en CADA tick. Con 10,000+ items, esto puede ser lento.

**Mitigación futura**:
- Índice de BD en campos relevantes
- Solo cargar entidades con `tick_scripts` no vacío
- Batch processing más eficiente

### 3. **Precisión Temporal**

Los ticks se ejecutan "aproximadamente" cada 2 segundos. Bajo carga alta, puede haber pequeños retrasos.

**Mitigación**: Para sistemas que requieren precisión absoluta, usar timestamps en lugar de ticks.

## Debugging

### Ver Logs del Pulse

El pulse loggea cada 30 ticks (60 segundos) para no saturar logs:

```
⏰ Global Pulse: Tick #30
⏰ Global Pulse: Tick #60
⏰ Global Pulse: Tick #90
```

Para debugging más detallado, cambiar en `pulse_service.py`:

```python
# Log cada tick (mucho más verboso)
if current_tick % 1 == 0:
    logging.debug(f"⏰ Global Pulse: Tick #{current_tick}")
```

### Verificar tick_data de un Item

```python
# En consola de BD o script
SELECT id, key, tick_data FROM items WHERE key = 'espada_viviente';

# Resultado:
# id | key              | tick_data
# ---+------------------+----------------------------------------
#  5 | espada_viviente  | {"script_0": {"last_executed_tick": 58, "has_executed": true}}
```

## Comparación con el Sistema Anterior

| Aspecto | Sistema Antiguo (ticker_service) | Sistema Nuevo (pulse_service) |
|---------|----------------------------------|-------------------------------|
| **Jobs en scheduler** | Uno por cada ticker | Uno global |
| **Expresión de timing** | Cron (`*/2 * * * *`) | Ticks (`60`) |
| **Escalabilidad** | ⚠️ O(n) jobs | ✅ O(1) jobs |
| **Sincronización** | ❌ No garantizada | ✅ Todos en la misma timeline |
| **Scripts one-shot** | ❌ No soportado | ✅ Soportado |
| **Timing relativo** | ❌ Difícil | ✅ Natural |
| **Debugging** | ⚠️ Múltiples jobs | ✅ Un solo flujo |

## Ver También

- [Scripting System](scripting-system.md) - Uso de scripts con pulse
- [Configuration](../architecture/configuration.md) - Configurar interval_seconds
