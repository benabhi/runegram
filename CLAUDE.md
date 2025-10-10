# CLAUDE.md - Guía de Desarrollo para Runegram MUD

## 🎯 Visión del Proyecto

**Runegram** es un motor de juego de rol textual multijugador (MUD - Multi-User Dungeon) diseñado específicamente para ser jugado a través de Telegram. El objetivo final es crear un **juego masivo completamente funcional** con sistemas de combate, habilidades, economía, y una experiencia rica e inmersiva optimizada para dispositivos móviles.

---

## 📋 Principios Fundamentales

### 1. Separación Motor vs. Contenido

Esta es la filosofía arquitectónica más importante del proyecto:

- **Motor (`src/`)**: Código genérico en **inglés** que no conoce la semántica del juego
  - Define sistemas, servicios, modelos y lógica de negocio
  - Es reutilizable y abstracto
  - No sabe qué es una "espada", solo maneja objetos `Item`

- **Contenido (`game_data/`, `commands/`)**: Datos y definiciones en **español**
  - Define qué objetos existen, qué hacen los comandos específicos
  - Describe el mundo, las salas, los prototipos
  - Es específico del juego y fácilmente modificable

**Regla de Oro**: Al agregar funcionalidad, pregúntate: "¿Esto es parte del motor o del contenido?" Mantén esta separación estricta.

### 2. Optimización para Telegram Mobile

#### Limitaciones a Considerar
- **Pantallas pequeñas**: Textos concisos pero descriptivos
- **Interacción táctil**: Comandos simples sobre sintaxis compleja
- **Sin interfaz gráfica rica**: Todo se comunica con texto, emojis y formato HTML

#### Bondades a Aprovechar
- **Ubicuidad**: Los jugadores tienen su teléfono siempre consigo
- **Comandos sugeridos**: El menú `/` muestra comandos disponibles dinámicamente
- **Formato enriquecido**: HTML básico (`<b>`, `<i>`, `<pre>`, `<code>`)
- **Botones inline**: Interacción mediante botones táctiles para mejor UX móvil

#### Mejores Prácticas UX
- Usa `<pre>` para textos descriptivos (ambiente, descripciones de salas)
- Mantén mensajes entre 3-8 líneas para evitar scroll excesivo
- Provee feedback inmediato para cada acción del jugador
- Usa emojis con moderación y propósito

### 3. Filosofía de Comandos

**Principio**: Comandos simples, descriptivos e intuitivos.

#### Formato Preferido
```
/<verbo_acción> [argumentos]
```

Ejemplos: `/mirar fuente`, `/coger espada`, `/activarcanal comercio`

#### Convenciones de Nomenclatura (CRÍTICO)

**REGLA FUNDAMENTAL**: Las clases de comandos **SIEMPRE** deben estar en **inglés**, independientemente del idioma del comando.

```python
# ✅ CORRECTO
class CmdLook(Command):
    names = ["mirar", "m", "l"]  # Español en los nombres

class CmdListItems(Command):
    names = ["listaritems", "litems"]

# ❌ INCORRECTO
class CmdMirar(Command):  # Clase en español
    names = ["mirar", "m"]
```

- **Comandos en español**: `/mirar`, `/coger`, `/atacar`
- **Clases en inglés**: `CmdLook`, `CmdGet`, `CmdAttack`
- **Primer alias = nombre principal**: Se usa para el menú de Telegram

#### Comandos Dedicados vs. Subcomandos
Prefiere múltiples comandos dedicados sobre subcomandos complejos.

✅ `/activarcanal comercio` + `/desactivarcanal comercio`
❌ `/canal comercio activar`

---

## 🏗️ Stack Tecnológico

### Tecnologías Principales
- **Python 3.11** + **Aiogram 2.25** (async)
- **SQLAlchemy 2.0** + **PostgreSQL 15**
- **Redis 7** (cache y FSM)
- **Alembic** (migraciones)
- **Docker + Docker Compose**
- **APScheduler** (pulse global)
- **Jinja2** (templates)
- **Pydantic** (configuración)
- **TOML** (configuración del juego)

### Arquitectura
```
handlers/ → services/ → models/ → database
```

---

## 📁 Estructura del Proyecto

```
runegram/
├── src/                          # Motor (código en inglés)
│   ├── bot/                      # Instancia de Aiogram
│   ├── handlers/                 # Coordinación de comandos
│   ├── models/                   # SQLAlchemy (Account, Character, Room, Item, Exit)
│   ├── services/                 # Lógica de negocio
│   │   ├── player_service.py
│   │   ├── command_service.py
│   │   ├── permission_service.py
│   │   ├── broadcaster_service.py
│   │   ├── narrative_service.py
│   │   ├── pulse_service.py
│   │   └── online_service.py
│   ├── templates/                # Jinja2 templates + icons
│   ├── utils/                    # Presenters, helpers
│   ├── config.py                 # Configuración (Pydantic)
│   └── db.py                     # SQLAlchemy config
├── commands/                     # Contenido (comandos en español)
│   ├── command.py                # Clase base
│   ├── player/                   # Comandos de jugador
│   └── admin/                    # Comandos de admin
├── game_data/                    # Contenido (prototipos)
│   ├── room_prototypes.py
│   ├── item_prototypes.py
│   ├── channel_prototypes.py
│   └── narrative_messages.py
├── alembic/                      # Migraciones de BD
├── docs/                         # Documentación exhaustiva
├── scripts/                      # Scripts de utilidad
└── tests/                        # Tests unitarios
```

---

## 🎨 Guía de Estilo Python

### Nomenclatura

```python
# Motor (inglés)
class Character(Base):              # PascalCase para clases
    pass

async def get_character_by_id():   # snake_case para funciones
    pass

# Contenido (español/inglés híbrido)
class CmdLook(Command):             # Clase en inglés
    names = ["mirar", "m"]          # Comandos en español

ROOM_PROTOTYPES = {                 # Prototipos en español
    "plaza_central": {...}
}
```

### Documentación (OBLIGATORIO)

```python
# Docstring de módulo (obligatorio en TODOS los archivos)
"""
Módulo de Servicio para la Gestión de Jugadores.

Responsabilidades:
1. Creación y recuperación de cuentas.
2. Creación, validación y configuración de personajes.
"""

# Docstring de clase
class Room(Base):
    """
    Representa una sala o ubicación en el mundo del juego.
    """

# Docstring de función (para funciones complejas/públicas)
async def _ensure_superadmin_exists(session):
    """
    Verifica que la cuenta del Superadmin exista con el rol correcto.
    Se ejecuta en cada arranque.
    """
```

### Manejo de Errores

```python
# SIEMPRE loggea excepciones
try:
    await execute_complex_operation()
except Exception:
    logging.exception(f"Error en operación para {character.name}")
    await message.answer("❌ Ocurrió un error inesperado.")

# SIEMPRE proporciona feedback al usuario
if not item:
    await message.answer("No encuentras ese objeto por aquí.")
    return
```

### Async/Await + Type Hints

```python
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

# Todo el código debe ser asíncrono
async def get_character(
    session: AsyncSession,
    character_id: int
) -> Optional[Character]:
    result = await session.execute(
        select(Character).where(Character.id == character_id)
    )
    return result.scalar_one_or_none()
```

### Configuración Centralizada

```python
# ❌ Malo - Número mágico hardcodeado
if player.afk_time > 300:
    mark_as_afk(player)

# ✅ Bueno - Configuración en gameconfig.toml
from src.config import settings

if player.afk_time > settings.online_threshold.total_seconds():
    mark_as_offline(player)
```

**Principio**: Si un valor podría necesitar ajustes, debe estar en `gameconfig.toml`, NO hardcodeado.

Ver: `docs/architecture/configuration.md`

---

## 🔧 Sistemas del Motor (Overview)

### 1. Sistema de Comandos
- **Dinámico y contextual**: Los comandos disponibles cambian según contexto
- **CommandSets**: Agrupaciones de comandos (`general`, `movement`, `interaction`, etc.)
- **Determinación dinámica**: Base del personaje + objetos equipados + sala + rol

Ver: `src/services/command_service.py`

### 2. Sistema de Permisos (Locks)
```python
lock = ""                    # Todos pueden acceder
lock = "rol(ADMIN)"         # Solo admins
lock = "rol(SUPERADMIN)"    # Solo superadmin
```

Ver: `src/services/permission_service.py`

### 3. Sistema de Prototipos
- **Prototipos**: Definen características estáticas (salas, items, canales)
- **Instancias**: Objetos en BD que referencian prototipos mediante `key`
- **Ventaja**: Cambiar prototipo actualiza TODAS las instancias

```python
# game_data/item_prototypes.py
ITEM_PROTOTYPES = {
    "espada_herrumbrosa": {
        "name": "Espada Herrumbrosa",
        "description": "...",
        "keywords": ["espada", "herrumbrosa"],
        "grants_command_sets": ["combat"],
        "attributes": {"damage": 5}
    }
}
```

Ver: `game_data/room_prototypes.py`, `game_data/item_prototypes.py`

### 4. Sistema de Categories y Tags
- **Category**: Un objeto pertenece a UNA categoría (`"arma"`, `"ciudad_runegard"`)
- **Tags**: Un objeto puede tener MÚLTIPLES tags (`["magica", "unica"]`)
- Comandos: `/listarsalas [cat:X] [tag:Y]`, `/listaritems [cat:X] [tag:Y]`

Ver: `docs/engine-systems/categories-and-tags.md`

### 5. Sistema de Broadcasting
```python
from src.services import broadcaster_service

# Notificar a sala (filtra offline automáticamente)
await broadcaster_service.send_message_to_room(
    session=session,
    room_id=room_id,
    message_text="¡Algo dramático sucede!",
    exclude_character_id=acting_character.id  # Opcional
)
```

Ver: `src/services/broadcaster_service.py`

### 6. Sistema de Pulse Global
- **Corazón temporal**: Tick cada 2 segundos
- **Sincronización perfecta**: Todos los sistemas en la misma timeline
- **Escalable**: O(1) jobs en lugar de O(n) jobs

```python
# En prototipos
"tick_scripts": [
    {
        "interval_ticks": 60,  # Cada 120s (60 ticks * 2s)
        "script": "script_name",
        "permanent": True
    }
]
```

Ver: `docs/engine-systems/pulse-system.md`

### 7. Sistema de Scripts
Permite ejecutar código Python almacenado como string.

```python
from src.services import script_service

await script_service.execute_script(
    script_string="character.hp += 10",
    session=session,
    character=character,
    target=item
)
```

**⚠️ Seguridad**: NO implementa sandboxing real. Solo para contenido confiable.

### 8. Sistema de Canales
- **Estáticos**: Definidos en `channel_prototypes.py` (`/ayuda`, `/comercio`)
- **Dinámicos**: Creados por jugadores (`/crearcanal`, `/invitar`)

Ver: `commands/player/dynamic_channels.py`

### 9. Sistema de Templates (Jinja2)
- **Consistencia visual**: Todos los outputs usan mismo estilo e íconos
- **Separación presentación/lógica**: Templates `.html.j2` + Python

```python
from src.templates import render_template, ICONS

output = render_template('room.html.j2', room=room, character=character)
await message.answer(output, parse_mode="HTML")
```

#### Filosofía de Outputs: Las 4 Categorías (CRÍTICO)

**1. Outputs Descriptivos**
- Descripciones del mundo, inventarios (`/mirar`, `/inventario`)
- Formato: `<pre>` + MAYÚSCULAS + listas con **4 espacios + guion**

**2. Notificaciones Sociales**
- Acciones visibles de otros (`/norte`, `/coger`)
- Formato: `<i>` + tercera persona + sin íconos

**3. Notificaciones Privadas**
- Mensajes directos (`/susurrar`, reconexión)
- Formato: `<i>` + segunda persona + sin íconos

**4. Feedback de Acciones**
- Respuestas a comandos (éxito/error)
- Formato: Texto plano + íconos de estado (✅❌❓⚠️)

**Regla de Oro de Indentación**: En `<pre>`, TODAS las listas usan **4 espacios + guion** (`    - `). NO usar tabs literales.

Ver: `docs/content-creation/output-style-guide.md` (OBLIGATORIO)

### 10. Sistema de Presentación
Funciones centralizadas para generar outputs formateados.

```python
from src.utils.presenters import format_room, format_inventory

output = format_room(room, character)
await message.answer(output, parse_mode="HTML")
```

**Presenters disponibles**: `format_room()`, `format_inventory()`, `format_character()`, `format_item_look()`, `format_who_list()`

### 11. Sistema de Botones Inline
- Botones de navegación en salas
- Flujos FSM (creación de personaje)
- Sistema de callback routing extensible

Ver: `docs/engine-systems/inline-buttons.md`

### 12. Sistema de Ordinales para Objetos Duplicados
Sintaxis estándar MUD: `N.nombre` donde N es el número ordinal.

```
📦 Tu Inventario:
1. ⚔️ espada oxidada
2. ⚔️ espada brillante

/coger 1.espada   → Primera espada
/coger 2.espada   → Segunda espada
```

**Función principal**: `find_item_in_list_with_ordinal()` en `commands/player/interaction.py`

Ver: `docs/engine-systems/item-disambiguation.md`

### 13. Sistema de Narrativa
Mensajes evocativos y aleatorios para eventos del juego.

```python
from src.services import narrative_service

# 41 variantes de mensajes en 6 categorías
message = narrative_service.get_random_narrative(
    "item_spawn",
    item_name="una espada brillante"
)
# Retorna variante aleatoria: "<i>Una espada brillante se materializa...</i>"
```

**Tipos**: `item_spawn`, `item_destroy_room`, `item_destroy_inventory`, `teleport_departure`, `teleport_arrival`, `character_suicide`

Ver: `docs/engine-systems/narrative-system.md`

---

## 🎮 Creación de Contenido (Resumen)

### Agregar Nueva Sala
1. Editar `game_data/room_prototypes.py`
2. Actualizar conexiones en salas existentes
3. Reiniciar bot (sincronización automática)

### Agregar Nuevo Item
1. Editar `game_data/item_prototypes.py`
2. Usar `/generarobjeto <key>` como admin

### Agregar Nuevo Comando
1. Crear clase `CmdNombre(Command)` en `commands/player/` o `commands/admin/`
2. Agregar a CommandSet correspondiente
3. Verificar registro en `src/handlers/player/dispatcher.py`

**Estructura de comando**:
```python
class CmdExampleAction(Command):
    names = ["accion", "acc"]
    lock = ""  # o "rol(ADMIN)"
    description = "Descripción para menú Telegram"

    async def execute(self, character, session, message, args):
        # Validación
        if not args:
            await message.answer("Uso: /accion [argumento]")
            return

        # Lógica de negocio
        result = await some_service.do_something(...)

        # Respuesta al usuario
        await message.answer(f"Resultado: {result}")

        # Commit si modificaste BD
        await session.commit()
```

Ver: `docs/content-creation/` para guías completas

---

## 🔒 Sistema de Roles y Permisos

**Roles**: `PLAYER` (default), `ADMIN`, `SUPERADMIN`

```python
# Asignar rol (como Superadmin)
/asignarrol <nombre> <rol>

# Locks en comandos
class CmdTeleport(Command):
    lock = "rol(ADMIN)"
```

---

## 🗄️ Base de Datos y Migraciones

### Crear Migración
```bash
docker exec -it runegram-bot-1 alembic revision --autogenerate -m "Descripción"
docker exec -it runegram-bot-1 alembic upgrade head
```

### Rollback
```bash
docker exec -it runegram-bot-1 alembic downgrade -1
```

Ver: `docs/admin-guide/database-migrations.md`

---

## 🐛 Debugging

### Ver Logs
```bash
docker logs -f runegram-bot-1
docker logs -f runegram-postgres-1
```

### Logging en Código
```python
import logging

logging.info(f"Jugador {character.name} entró a {room.name}")
logging.exception(f"Falló operación para {character.name}")
```

---

## 🚀 Flujo de Desarrollo

### ⚠️ POLÍTICA DE DOCUMENTACIÓN (CRÍTICO)

**OBLIGATORIO** después de CUALQUIER cambio:

#### 1. Verificar y Actualizar Documentación
- ✅ ¿`README.md` refleja el estado actual?
- ✅ ¿Hay documentación en `docs/` que necesita actualización?
- ✅ ¿Necesitas crear/actualizar/eliminar archivos en `docs/`?

**La documentación desactualizada es peor que no tener documentación.**

#### 2. Verificar Tests
- ✅ Ejecutar tests existentes: `pytest -m critical`
- ✅ Crear/actualizar tests para funcionalidad nueva
- ✅ Verificar cobertura: `pytest --cov=src`

**¿Qué requiere tests?**
- ✅ SIEMPRE: Servicios críticos (permisos, validación, player_service)
- ✅ SIEMPRE: Correcciones de bugs (test de regresión)
- ✅ FRECUENTEMENTE: Comandos complejos
- ❌ NUNCA: Prototipos de items/salas/canales

### Workflow Básico
1. **Identificar**: ¿Es motor o contenido?
2. **Diseñar**: Pensar en UX móvil de Telegram
3. **Implementar**: Crear/modificar código
4. **Documentar**: Docstrings + comentarios
5. **📚 ACTUALIZAR DOCS**: Verificar `README.md` y `docs/`
6. **Probar**: Ejecutar en local
7. **Migrar BD** (si aplica)
8. **Commit**: Mensaje descriptivo en español

### Convenciones de Git
```bash
git commit -m "Agregado sistema de combate básico"
git commit -m "Corregido bug en /coger con contenedores"
```

---

## 🤖 Guía Específica para Claude

### 🚨 REGLA #1: DOCUMENTACIÓN SIEMPRE ACTUALIZADA

**ANTES de finalizar CUALQUIER tarea**:

1. 📋 **Verificar `README.md`**
   - ¿Agregaste funcionalidad que debe mencionarse?
   - ¿Cambió el stack tecnológico?

2. 📚 **Revisar archivos en `docs/`**
   - Identificar qué necesita actualización
   - Actualizar archivos existentes desactualizados
   - Crear nuevos archivos si la funcionalidad lo amerita
   - Eliminar archivos si documentan funcionalidad removida

3. ✍️ **Actualizar `CLAUDE.md`** si:
   - Creaste un nuevo sistema del motor
   - Cambiaste la filosofía de diseño
   - Agregaste nuevas convenciones

**NUNCA digas "tarea completada" sin verificar documentación.**

### Política de Jugadores Desconectados (CRÍTICO)

**IMPORTANTE**: Los jugadores desconectados (offline) son tratados como **ausentes del mundo**.

#### Principio Fundamental
Cuando un jugador está desconectado (inactivo >5 minutos o `/desconectar`), **NO está presente en el juego**.

#### Reglas de Implementación

**✅ SIEMPRE filtrar jugadores desconectados en:**
1. Visualización de salas (`/mirar`)
2. Listados de personajes (`/personajes`)
3. Interacción con personajes (`/mirar <jugador>`, `/susurrar`)
4. Broadcasting (`broadcaster_service.send_message_to_room()` - automático)
5. Comandos sociales (`/decir`)

**❌ NUNCA:**
- Permitir interacción con jugadores desconectados
- Mostrar jugadores desconectados en listas
- Enviar mensajes a jugadores desconectados

#### Código de Verificación
```python
from src.services import online_service

is_active = await online_service.is_character_online(character.id)
if not is_active:
    await message.answer("No ves a nadie con ese nombre por aquí.")
    return
```

Ver: `docs/engine-systems/social-systems.md`

### Cuando el Usuario Pide Agregar Funcionalidad

1. **Pregunta primero**: ¿Motor o contenido?
2. **Considera Telegram**: ¿UX apropiada para pantalla pequeña?
3. **Mantén separación**: No mezcles motor con contenido
4. **Documenta código**: Docstrings + comentarios
5. **Sigue convenciones**: Inglés (motor) / Español (contenido)
6. **Código robusto**: Errores + logging + type hints
7. **Feedback usuario**: Mensajes claros
8. **🎨 USA TEMPLATES**: No hardcodees HTML
9. **⚠️ VERIFICA OFFLINE**: Filtra jugadores desconectados
10. **📚 ACTUALIZA DOCS**: Antes de terminar (REGLA #1)

### Cuando el Usuario Pide Corregir Bug

1. **Reproduce**: Lee código relevante
2. **Identifica causa raíz**: No solo síntoma
3. **Propón solución**: Explica qué y por qué
4. **Implementa**: Sin romper funcionalidad existente
5. **Agrega logging**: Para detectar futuros problemas
6. **📚 VERIFICA DOCS**: ¿El bug indica documentación incorrecta?

### Checklist Antes de Sugerir Código

#### Durante Implementación
- ✅ ¿Respeta separación motor/contenido?
- ✅ ¿UX buena para Telegram móvil?
- ✅ ¿Tiene docstrings y comentarios?
- ✅ ¿Sigue convenciones de nomenclatura?
- ✅ ¿Hay manejo de errores y logging?
- ✅ ¿Proporciona feedback claro al usuario?
- ✅ ¿Es código async (no bloqueante)?
- ✅ ¿Usa templates/presenters en lugar de HTML hardcodeado?
- ✅ ¿Íconos de `ICONS` en lugar de hardcodeados?
- ✅ **¿Filtra jugadores desconectados correctamente?**

#### Antes de Finalizar (CRÍTICO)
- ✅ ¿Verifiqué si `README.md` necesita actualización?
- ✅ ¿Revisé qué archivos en `docs/` debo actualizar?
- ✅ ¿Creé nuevos archivos de documentación si era necesario?
- ✅ ¿Actualicé `ROADMAP.md` si completé funcionalidad planificada?
- ✅ ¿La documentación refleja EXACTAMENTE el estado actual?

---

## 📖 Recursos

### Documentación Interna (Completa)
- `docs/getting-started/` - Primeros pasos
  - `installation.md` - Instalación y configuración
  - `core-philosophy.md` - Filosofía de diseño
  - `quick-reference.md` - Referencia rápida
  - `glossary.md` - Glosario de términos
- `docs/engine-systems/` - Sistemas del motor detallados
  - `command-system.md`, `permission-system.md`, `prototype-system.md`
  - `pulse-system.md`, `narrative-system.md`, `online-presence.md`
  - Y más (13 documentos en total)
- `docs/content-creation/` - Guías de creación
  - `creating-commands.md`, `building-rooms.md`, `creating-items.md`
  - `output-style-guide.md` - **OBLIGATORIO** para outputs
  - `writing-scripts.md`, `inline-buttons.md`
- `docs/admin-guide/` - Guía de administración
  - `admin-commands.md` - Comandos de administración
  - `database-migrations.md` - BD y migraciones
- `docs/architecture/` - Arquitectura del sistema
  - `core-architecture.md` - Arquitectura general
  - `configuration.md` - Sistema de configuración TOML
- `docs/roadmap/` - Hoja de ruta
  - `vision-and-goals.md` - Visión del proyecto
  - `planned-features.md`, `combat-system.md`, `skill-system.md`
- `docs/reference/` - Referencias técnicas
  - `command-reference.md` - **Referencia completa de comandos**
  - `api-reference.md` - APIs y servicios

### Documentación Externa
- [Aiogram 2.x](https://docs.aiogram.dev/en/v2.25.1/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [Telegram Bot API](https://core.telegram.org/bots/api)

---

## 🎯 Resumen Ejecutivo para Claude

**Runegram** es un MUD textual para Telegram con arquitectura Python async moderna.

### Claves del Proyecto
- **Separación motor/contenido**: Motor (inglés, genérico) vs Contenido (español, específico)
- **Optimización móvil**: UX diseñada para pantallas pequeñas de Telegram
- **Comandos simples**: Intuitivos, descriptivos, en español
- **Clases en inglés**: `CmdLook`, `CmdGet`, `CmdAttack` (NUNCA en español)

### Workflow Obligatorio
1. Identifica si es motor o contenido
2. Optimiza para UX móvil
3. Documenta código (docstrings + comentarios)
4. Maneja errores con logging
5. Proporciona feedback claro
6. Usa código async + type hints
7. **🚨 ANTES DE FINALIZAR**: Verifica y actualiza `README.md` y `docs/`

### Política de Documentación (CRÍTICO)
**La documentación DEBE estar siempre actualizada.**

Después de CUALQUIER cambio:
- ✅ Verificar `README.md`
- ✅ Revisar archivos en `docs/`
- ✅ Crear/actualizar/eliminar según sea necesario
- ✅ **NUNCA** decir "tarea completada" sin verificar

**Documentación desactualizada es peor que no tener documentación.**

### Sistemas Clave (Referencia Rápida)
- **Comandos**: Sistema dinámico con CommandSets contextuales
- **Templates**: Jinja2 para outputs consistentes (4 categorías)
- **Broadcasting**: Notificaciones automáticas (filtra offline)
- **Narrativa**: Mensajes evocativos aleatorios (41 variantes)
- **Ordinales**: Sistema `N.nombre` para objetos duplicados
- **Pulse**: Corazón temporal (tick cada 2s)
- **Offline**: Jugadores desconectados = ausentes del juego

### Objetivo Final
Crear un juego masivo, funcional e inmersivo que aproveche las fortalezas únicas de Telegram.

---

**Versión**: 1.9 (COMPACTADA)
**Última actualización**: 2025-01-09
**Changelog**:
- v1.9 (2025-01-09): Compactación del archivo sin pérdida de información crítica (~64% reducción: 2057→744 líneas)
- v1.8 (2025-01-09): Sistema de Narrativa implementado
- v1.7 (2025-10-04): Sistema de ordinales para objetos duplicados
**Mantenedor**: Proyecto Runegram

### Notas Finales
- **Reiniciar servicios**: `scripts/full_reset.bat`
- **Notificaciones Sociales**: SIEMPRE verificar si es necesario usar `broadcaster_service.send_message_to_room()` para acciones visibles
- **Regla de Oro**: Si una acción es visible, debe notificarse a jugadores presentes (online)
