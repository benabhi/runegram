---
título: "Sistema de Configuración de Runegram"
categoría: "Arquitectura"
audiencia: "desarrollador, administrador"
última_actualización: "2025-01-11"
autor: "Proyecto Runegram"
etiquetas: ["configuración", "toml", "pydantic", "env", "settings", "moderacion", "personajes", "paginacion"]
documentos_relacionados:
  - "../primeros-pasos/instalacion.md"
  - "../guia-de-administracion/migraciones-de-base-de-datos.md"
  - "../sistemas-del-motor/sistema-de-baneos.md"
referencias_código:
  - "src/config.py"
  - "gameconfig.toml"
  - ".env.example"
  - "game_data/channel_prototypes.py"
  - "src/services/ban_service.py"
  - "commands/admin/ban_management.py"
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

# --- Personajes ---
[characters]
# Longitud mínima del nombre del personaje
name_min_length = 3

# Longitud máxima del nombre del personaje
name_max_length = 15

# --- Sistema de Baneos y Moderación ---
[moderation]
# Canal donde se envían notificaciones de apelaciones de ban
# Si se deja vacío (""), las notificaciones se envían directamente a todos los admins
# Debe ser una key válida de CHANNEL_PROTOTYPES (ej: "moderacion", "sistema")
ban_appeal_channel = "moderacion"

# Longitud máxima de la razón del ban
ban_reason_max_length = 500

# Longitud máxima del texto de apelación
appeal_max_length = 1000

# Caracteres mostrados de vista previa de apelaciones en listados
appeal_preview_length = 100

# Número de cuentas baneadas por página en /listabaneados
banned_accounts_per_page = 10

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

#### Sección `[characters]`

| Variable | Tipo | Default | Descripción |
|----------|------|---------|-------------|
| `name_min_length` | int | 3 | Longitud mínima del nombre del personaje |
| `name_max_length` | int | 15 | Longitud máxima del nombre del personaje |

**Nota histórica:**

Esta sección resuelve una inconsistencia histórica en el código. Anteriormente:
- El modelo `Character` tenía hardcodeado `max_length=50` en el campo `name`
- El FSM de creación de personajes validaba con `max_length=15`

Ahora ambos usan el valor centralizado de `gameconfig.toml` (15 caracteres), garantizando consistencia.

**Uso en código:**
```python
from src.config import settings

# Validación en FSM de creación
if len(name) < settings.characters_name_min_length:
    await message.answer(f"El nombre debe tener al menos {settings.characters_name_min_length} caracteres.")

if len(name) > settings.characters_name_max_length:
    await message.answer(f"El nombre no puede exceder {settings.characters_name_max_length} caracteres.")
```

---

#### Sección `[moderation]`

| Variable | Tipo | Default | Descripción |
|----------|------|---------|-------------|
| `ban_appeal_channel` | str | "moderacion" | Canal donde se envían notificaciones de apelaciones de ban |
| `ban_reason_max_length` | int | 500 | Longitud máxima de la razón del ban |
| `appeal_max_length` | int | 1000 | Longitud máxima del texto de apelación |
| `appeal_preview_length` | int | 100 | Caracteres mostrados en vista previa de apelaciones |
| `banned_accounts_per_page` | int | 10 | Número de cuentas baneadas por página en `/listabaneados` |

**Comportamiento de `ban_appeal_channel`:**

1. **Canal configurado** (ej: `"moderacion"`):
   - Las notificaciones de apelaciones se envían al canal especificado
   - Solo administradores suscritos al canal las recibirán
   - Mantiene privacidad de las apelaciones

2. **Vacío** (`""`):
   - Las notificaciones se envían como **mensaje directo** a todos los administradores
   - Asegura que todos los admins sean notificados
   - Útil si no hay canal de moderación configurado

**Canal de moderación incluido:**

El proyecto incluye un canal `"moderacion"` preconfigurado en `game_data/channel_prototypes.py`:
- **Icon:** 🛡️
- **Lock:** `rol(ADMIN)` (solo administradores)
- **Default:** No activado por defecto (los admins deben activarlo con `/activarcanal moderacion`)

**Uso en código:**
```python
from src.config import settings
from game_data.channel_prototypes import CHANNEL_PROTOTYPES

# Validación de longitud de razón de ban
if len(reason) > settings.moderation_ban_reason_max_length:
    await message.answer(f"La razón no puede exceder {settings.moderation_ban_reason_max_length} caracteres.")

# Paginación en listado de baneados
per_page = settings.moderation_banned_accounts_per_page

# Notificación de apelaciones
channel_key = settings.moderation_ban_appeal_channel
if channel_key and channel_key in CHANNEL_PROTOTYPES:
    await channel_service.broadcast_to_channel(session, channel_key, notification)
else:
    # Fallback: enviar mensaje directo a todos los admins
    await notify_all_admins_directly(notification)
```

**Ver también:** [Sistema de Baneos](../sistemas-del-motor/sistema-de-baneos.md)

---

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
- [Guía de Instalación](../primeros-pasos/instalacion.md)
- [Migraciones de Base de Datos](../guia-de-administracion/migraciones-de-base-de-datos.md)

---

## 📝 Changelog

### 2025-01-11
- ✅ **Nueva sección `[characters]`**: Agregados `name_min_length` y `name_max_length` para validación centralizada
- ✅ **Corrección de inconsistencia histórica**: Resuelto conflicto entre límites hardcodeados (50 vs 15) para longitud de nombres
- ✅ **Expansión de `[moderation]`**: Agregados 4 nuevos campos configurables:
  - `ban_reason_max_length` (500)
  - `appeal_max_length` (1000)
  - `appeal_preview_length` (100)
  - `banned_accounts_per_page` (10)
- ✅ **Migración de hardcoded a configuración**: Todos los límites del sistema de baneos ahora son configurables
- ✅ **Documentación completa**: Ejemplos de uso en código para todas las nuevas configuraciones
- ✅ Documentación de paginación universal consolidada
- ✅ Explicación de diferencia entre `pagination` y `display_limits`
- ✅ Agregado sistema de configuración de notificaciones de apelaciones (`moderation.ban_appeal_channel`)
- ✅ Canal de moderación preconfigurado

### 2025-01-09
- ✅ Documentación inicial del sistema de configuración
