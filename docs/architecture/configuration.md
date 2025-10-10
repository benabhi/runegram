---
título: "Sistema de Configuración de Runegram"
categoría: "Arquitectura"
audiencia: "desarrollador, administrador"
versión: "1.0"
última_actualización: "2025-01-09"
autor: "Proyecto Runegram"
etiquetas: ["configuración", "toml", "pydantic", "env", "settings"]
documentos_relacionados:
  - "getting-started/quick-start.md"
  - "admin-guide/database-migrations.md"
referencias_código:
  - "src/config.py"
  - "gameconfig.toml"
  - ".env.example"
estado: "actual"
importancia: "crítica"
---

# Sistema de Configuración de Runegram

## Filosofía de Configuración

Runegram utiliza un **sistema de configuración híbrido** que separa claramente:

1. **Credenciales sensibles** (`.env`) - Tokens, passwords, secretos
2. **Configuración del juego** (`gameconfig.toml`) - Comportamiento, límites, tiempos

Esta separación permite:
- ✅ **Seguridad**: `.env` nunca se sube a Git
- ✅ **Versionado**: `gameconfig.toml` SÍ está en Git y comparte configuración del juego
- ✅ **Facilidad**: Modificar comportamiento sin editar código Python
- ✅ **Validación**: Pydantic valida ambas fuentes automáticamente

---

## Archivo: `.env` (Credenciales Sensibles)

### Ubicación
`/runegram/.env`

### Propósito
Contiene tokens, passwords y otras credenciales que **NUNCA** deben subirse a Git.

### Variables Requeridas

```bash
# ===============================================================
#          Archivo de Configuración de Entorno para Runegram
# ===============================================================

# --- Configuración del Superadministrador ---
SUPERADMIN_TELEGRAM_ID=1234567890

# --- Telegram ---
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# --- Base de Datos (PostgreSQL) ---
POSTGRES_USER=runegram
POSTGRES_PASSWORD=runegram
POSTGRES_DB=runegram_db
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# --- Caché y Estados (Redis) ---
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
```

### Variables Explicadas

| Variable | Tipo | Descripción |
|----------|------|-------------|
| `SUPERADMIN_TELEGRAM_ID` | int | ID de Telegram del usuario con rol SUPERADMIN |
| `BOT_TOKEN` | string | Token de autenticación de @BotFather |
| `POSTGRES_USER` | string | Usuario de PostgreSQL |
| `POSTGRES_PASSWORD` | string | Password de PostgreSQL |
| `POSTGRES_DB` | string | Nombre de la base de datos |
| `POSTGRES_HOST` | string | Host de PostgreSQL (en Docker: nombre del servicio) |
| `POSTGRES_PORT` | int | Puerto de PostgreSQL (default: 5432) |
| `REDIS_HOST` | string | Host de Redis (en Docker: nombre del servicio) |
| `REDIS_PORT` | int | Puerto de Redis (default: 6379) |
| `REDIS_DB` | int | Número de base de datos Redis (0-15) |

---

## Archivo: `gameconfig.toml` (Configuración del Juego)

### Ubicación
`/runegram/gameconfig.toml`

### Propósito
Contiene toda la configuración de comportamiento del juego que **SÍ puede estar en Git**.

### Formato TOML

TOML (Tom's Obvious, Minimal Language) es un formato de configuración:
- ✅ Legible por humanos
- ✅ Estricto con tipos de datos
- ✅ Soporta secciones anidadas
- ✅ Permite comentarios

### Estructura Completa

```toml
# ============================================================================
#                    RUNEGRAM - Configuración del Juego
# ============================================================================

# --- Sistema de Presencia (Online/Offline) ---
[online]
# Tiempo de inactividad (en minutos) antes de marcar jugador como offline
threshold_minutes = 5

# TTL en Redis para el timestamp last_seen (en días)
last_seen_ttl_days = 7

# TTL en Redis para el flag offline_notified (en días)
offline_notified_ttl_days = 1

# --- Sistema de Pulse Global ---
[pulse]
# Intervalo del pulse en segundos (cada cuántos segundos ejecuta un tick)
# IMPORTANTE: Cambiar este valor afecta la conversión de ticks a tiempo real
# en todos los scripts que usan interval_ticks
interval_seconds = 2

# --- Paginación Universal ---
# TODOS los listados usan este valor como límite por página
# Cuando una lista excede este valor, automáticamente se activa
# la paginación con navegación por comandos y botones inline
[pagination]
# Items por página en TODOS los listados
items_per_page = 30

# --- Límites de Visualización (solo para comandos con truncado) ---
# Estos valores aplican SOLO a comandos que muestran previsualizaciones
# y tienen alternativas dedicadas para ver listados completos
[display_limits]
# Máximo de items mostrados en /mirar (sala) antes de truncar
# (el jugador puede usar /items para ver listado completo con paginación)
max_room_items = 10

# Máximo de personajes mostrados en /mirar (sala)
# (el jugador puede usar /personajes para ver listado completo con paginación)
max_room_characters = 10

# --- Gameplay General ---
[gameplay]
# Habilitar modo debug (logs extra, comandos de testing)
debug_mode = false
```

### Configuraciones Explicadas

#### Sección `[online]`

| Variable | Tipo | Default | Descripción |
|----------|------|---------|-------------|
| `threshold_minutes` | int | 5 | Minutos de inactividad antes de marcar offline |
| `last_seen_ttl_days` | int | 7 | Días que Redis mantiene el timestamp last_seen |
| `offline_notified_ttl_days` | int | 1 | Días que Redis mantiene el flag offline_notified |

**Uso en código:**
```python
from src.config import settings

# Como timedelta
timeout = settings.online_threshold  # timedelta(minutes=5)

# Como valor raw
minutes = settings.online_threshold_minutes  # int: 5
```

#### Sección `[pulse]`

| Variable | Tipo | Default | Descripción |
|----------|------|---------|-------------|
| `interval_seconds` | int | 2 | Segundos entre cada tick del pulse global |

**⚠️ IMPORTANTE:** Cambiar `interval_seconds` afecta la conversión de ticks a tiempo real en TODOS los `tick_scripts` de prototipos.

**Ejemplo:**
- Con `interval_seconds = 2` y `interval_ticks = 30` → script ejecuta cada 60 segundos
- Si cambias a `interval_seconds = 5` y `interval_ticks = 30` → script ejecuta cada 150 segundos

**Uso en código:**
```python
from src.config import settings

scheduler.add_job(
    pulse_function,
    'interval',
    seconds=settings.pulse_interval_seconds
)
```

#### Sección `[pagination]`

| Variable | Tipo | Default | Descripción |
|----------|------|---------|-------------|
| `items_per_page` | int | 30 | Items por página en TODOS los listados con paginación automática |

**Filosofía de Paginación Unificada:**

Runegram usa un **único valor** de paginación para TODOS los listados. Cuando una lista excede este límite, se activa automáticamente:
- ✅ Botones inline de navegación (⬅️ ➡️)
- ✅ Comandos de paginación (`/comando 2` para página 2)
- ✅ Indicador de página actual

**Comandos con paginación automática:**
- `/inventario` - Activa paginación si tienes >30 items
- `/inventario [contenedor]` - Activa paginación si el contenedor tiene >30 items
- `/quien` - Activa paginación si hay >30 jugadores online
- `/items [página]` - Siempre usa paginación
- `/personajes [página]` - Siempre usa paginación
- `/listarsalas` (admin) - Siempre usa paginación
- `/listaritems` (admin) - Siempre usa paginación

**Uso en código:**
```python
from src.config import settings

# Paginación simple con send_paginated_simple
await send_paginated_simple(
    message=message,
    items=items,
    page=page,
    callback_action="pg_inv",
    format_func=lambda item: f"{item.get_name()}",
    header="Tu Inventario",
    per_page=settings.pagination_items_per_page
)
```

#### Sección `[display_limits]`

**⚠️ Importante:** Estos límites aplican SOLO a comandos con **truncado** (que muestran "... y X más items"). Los comandos sin alternativas (como `/inventario`, `/quien`) usan paginación automática en su lugar.

| Variable | Tipo | Default | Descripción |
|----------|------|---------|-------------|
| `max_room_items` | int | 10 | Items mostrados en `/mirar` (sala) antes de truncar |
| `max_room_characters` | int | 10 | Personajes mostrados en `/mirar` (sala) |

**Comandos afectados (con truncado):**
- `/mirar` (sala) - Muestra máximo 10 items/personajes y dice "... y X más" (el jugador puede usar `/items` o `/personajes` para ver todos)

**Comandos que YA NO usan estos límites:**
- ❌ `/inventario` - Ahora usa paginación automática (`pagination.items_per_page`)
- ❌ `/quien` - Ahora usa paginación automática (`pagination.items_per_page`)
- ❌ `/inventario [contenedor]` - Ahora usa paginación automática

**Uso en código:**
```python
from src.config import settings

# Solo para comandos con truncado (como /mirar sala)
if len(items) > settings.display_limits_max_room_items:
    truncated = items[:settings.display_limits_max_room_items]
    remaining = len(items) - settings.display_limits_max_room_items
    # Mostrar: "... y {remaining} más items. Usa /items para verlos todos."
```

#### Sección `[gameplay]`

| Variable | Tipo | Default | Descripción |
|----------|------|---------|-------------|
| `debug_mode` | bool | false | Habilita logs extra y comandos de testing |

**Uso futuro:**
```python
from src.config import settings

if settings.gameplay_debug_mode:
    logging.debug("Información extra de debug...")
    # Habilitar comandos especiales de testing
```

---

## Cómo Modificar la Configuración

### 1. Modificar Credenciales (.env)

**NO subir cambios a Git.**

```bash
# Editar .env
nano .env

# Reiniciar el bot para aplicar cambios
docker-compose restart bot
```

### 2. Modificar Configuración del Juego (gameconfig.toml)

**SÍ puedes subir cambios a Git.**

```bash
# Editar gameconfig.toml
nano gameconfig.toml

# Reiniciar el bot para aplicar cambios
docker-compose restart bot

# Commitear cambios
git add gameconfig.toml
git commit -m "Ajustado tiempo de desconexión a 10 minutos"
git push
```

---

## Agregar Nueva Configuración

### Paso 1: Editar `gameconfig.toml`

```toml
[combat]
# Tiempo máximo de combate en segundos
max_combat_duration = 300
```

### Paso 2: Editar `src/config.py`

```python
class Settings(BaseSettings):
    # ... campos existentes ...

    # Sistema de Combate
    combat_max_combat_duration: int = 300
```

La convención es: `[seccion]_nombre_campo`

### Paso 3: Usar en código

```python
from src.config import settings

if combat_duration > settings.combat_max_combat_duration:
    await end_combat(character)
```

---

## Validación de Configuración

Pydantic valida automáticamente:
- ✅ Tipos de datos correctos (int, str, bool)
- ✅ Valores requeridos presentes
- ✅ Formato correcto

**Si falta una configuración crítica:**
```
ValidationError: field required (type=value_error.missing)
```

**Si el tipo es incorrecto:**
```
ValidationError: value is not a valid integer (type=type_error.integer)
```

El bot **NO arrancará** si hay errores de validación, asegurando que no se ejecute con configuración incorrecta.

---

## Valores por Defecto

Si `gameconfig.toml` no existe o falta una configuración, se usan los valores por defecto definidos en `src/config.py`:

```python
class Settings(BaseSettings):
    online_threshold_minutes: int = 5  # Default aquí
```

Esto permite arrancar el bot sin `gameconfig.toml` para testing o desarrollo inicial.

---

## Mejores Prácticas

### DO ✅

- **Documentar configuraciones nuevas** en este archivo
- **Usar nombres descriptivos** en TOML (ej: `threshold_minutes`, no `t`)
- **Incluir comentarios** explicativos en `gameconfig.toml`
- **Commitear gameconfig.toml** a Git (es configuración compartida)
- **Usar settings en lugar de constantes** hardcodeadas en código

### DON'T ❌

- **NUNCA subir .env a Git** (credenciales sensibles)
- **No hardcodear valores** que deberían ser configurables
- **No usar variables mágicas** sin contexto (ej: `if x > 300`)
- **No modificar .env en producción** sin backup

---

## Troubleshooting

### Bot no arranca después de modificar configuración

1. **Verificar sintaxis TOML:**
   ```bash
   python -c "import toml; toml.load('gameconfig.toml')"
   ```

2. **Verificar logs de Pydantic:**
   ```bash
   docker-compose logs bot | grep -i validation
   ```

3. **Verificar que .env existe:**
   ```bash
   ls -la .env
   ```

### Cambios no se aplican

1. **Reiniciar el bot:**
   ```bash
   docker-compose restart bot
   ```

2. **Verificar que editaste el archivo correcto:**
   ```bash
   cat gameconfig.toml | grep -A2 "\[online\]"
   ```

### Errores de tipos

```python
# ❌ Incorrecto
threshold_minutes = "5"  # String, debería ser int

# ✅ Correcto
threshold_minutes = 5  # Int
```

---

## Referencias

- **Especificación TOML:** https://toml.io/
- **Pydantic Settings:** https://docs.pydantic.dev/usage/settings/
- **Python dotenv:** https://github.com/theskumar/python-dotenv

---

**Documentación Relacionada:**
- [Guía de Instalación](../getting-started/installation.md)
- [Migraciones de Base de Datos](../admin-guide/database-migrations.md)
