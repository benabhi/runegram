# CLAUDE.md - Guía de Desarrollo para Runegram MUD

> **📌 NOTA IMPORTANTE PARA CLAUDE**: Este archivo debe mantenerse **SIEMPRE compacto y conciso** sin perder información relevante. Al actualizarlo, evita redundancias, sobre-explicaciones innecesarias y ejemplos excesivos. Prioriza la claridad y brevedad. La información detallada debe estar en `docs/`, no aquí.

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

**Mejoras recientes (2025-01-11)**:
- ✅ Límites de longitud de nombres de personajes (`characters.name_min_length`, `characters.name_max_length`)
- ✅ Límites del sistema de baneos (`moderation.ban_reason_max_length`, `moderation.appeal_max_length`, etc.)
- ✅ Resolución de inconsistencias históricas (50 vs 15 caracteres en nombres)

Ver: `docs/arquitectura/configuracion.md`

---

## 🔧 Sistemas del Motor (Overview)

### 1. Sistema de Comandos
- **Dinámico y contextual**: Los comandos disponibles cambian según contexto
- **CommandSets**: Agrupaciones de comandos (`general`, `movement`, `interaction`, etc.)
- **Determinación dinámica**: Base del personaje + objetos equipados + sala + rol

Ver: `src/services/command_service.py`

### 2. Sistema de Permisos (Locks) - v2.0
Sistema extensible de permisos con **9 lock functions** y soporte para **locks contextuales** (diferentes restricciones por tipo de acción).

```python
# Lock simple (backward compatible)
lock = ""                         # Todos pueden acceder
lock = "rol(ADMIN)"               # Solo admins
lock = "tiene_objeto(llave)"      # Necesita item específico

# Locks contextuales (v2.0) - diferentes por access_type
locks = {
    "get": "rol(SUPERADMIN)",      # Solo SUPERADMIN puede coger
    "put": "tiene_objeto(llave)",  # Necesita llave para meter
    "take": ""                     # Todos pueden sacar
}

# Con mensajes personalizados
lock_messages = {
    "get": "El cofre está anclado al suelo.",
    "put": "El cofre está cerrado con llave."
}
```

**9 Lock Functions**: `rol()`, `tiene_objeto()`, `cuenta_items()`, `tiene_item_categoria()`, `tiene_item_tag()`, `en_sala()`, `en_categoria_sala()`, `tiene_tag_sala()`, `online()` (asíncrona)

**Access Types**: `get`, `put`, `take`, `traverse`, `open`, `use`, `default`

Ver: `docs/sistemas-del-motor/sistema-de-permisos.md`

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

Ver: `docs/sistemas-del-motor/categorias-y-etiquetas.md`

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

Ver: `docs/sistemas-del-motor/sistema-de-pulso.md`

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

Ver: `docs/creacion-de-contenido/guia-de-estilo-de-salida.md` (OBLIGATORIO)

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

Ver: `docs/sistemas-del-motor/botones-en-linea.md`

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

Ver: `docs/sistemas-del-motor/desambiguacion-de-items.md`

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

Ver: `docs/sistemas-del-motor/sistema-de-narrativa.md`

### 14. Sistema de Baneos y Apelaciones
Sistema completo de moderación para administradores.

```python
from src.services import ban_service

# Banear cuenta (temporal)
await ban_service.ban_account(
    session=session,
    character=target_character,
    reason="Spam en canales globales",
    banned_by_account_id=admin_account.id,
    expires_at=datetime.utcnow() + timedelta(days=7)
)

# Verificar si está baneado (automático en dispatcher)
is_banned = await ban_service.is_account_banned(session, account)
```

**Características**:
- **Baneos temporales** con expiración automática
- **Baneos permanentes** sin fecha de expiración
- **Sistema de apelaciones** (una oportunidad por cuenta)
- **Auditoría completa** (quién, cuándo, por qué)
- **Bloqueo de comandos** automático (excepto `/apelar`)

**Comandos**:
- Admin: `/banear`, `/desbanear`, `/listabaneados`, `/verapelacion`
- Jugador: `/apelar`

Ver: `src/services/ban_service.py`, `docs/sistemas-del-motor/sistema-de-baneos.md`

### 15. Sistema de Filtrado de Audiencia en Canales
Doble validación (suscripción + broadcast) para controlar no solo quién puede escribir, sino quién puede recibir mensajes de canales.

```python
# game_data/channel_prototypes.py
"moderacion": {
    "lock": "rol(ADMIN)",      # Quién puede escribir
    "audience": "rol(ADMIN)"    # Quién puede recibir mensajes
}
```

**Implementación híbrida**:
- **Validación en suscripción**: Previene suscripciones incorrectas (UX)
- **Validación en broadcast**: Garantiza privacidad en tiempo real (seguridad)
- **Reutiliza `permission_service.can_execute()`**: Sintaxis consistente con locks

**Comportamiento**:
- Sin `audience` → Sin restricción (backward compatible)
- Con `audience` → Filtra destinatarios según lock expression
- Maneja cambios de rol dinámicamente (admin degradado = deja de recibir)
- `/canales` oculta canales sin permiso de acceso (no los muestra en la lista)
- **Activación automática**: Canales con `audience` se activan automáticamente si el usuario tiene permisos

Ver: `docs/sistemas-del-motor/sistema-de-canales.md`

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

Ver: `docs/creacion-de-contenido/` para guías completas

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

Ver: `docs/guia-de-administracion/migraciones-de-base-de-datos.md`

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

### 🤖 USO DE AGENTES ESPECIALIZADOS (IMPORTANTE)

Este proyecto utiliza **agentes especializados** disponibles en `.claude/agents/` para tareas específicas complejas.

#### Agentes Disponibles

1. **runegram-docs-keeper** - Mantenimiento de documentación
   - Usar después de implementar nuevas funcionalidades
   - Usar cuando cambien sistemas existentes
   - Usar para reestructurar/mejorar documentación
   - Usar para validar consistencia entre docs y código

2. **runegram-command-auditor** - Auditoría de comandos
   - Usar PROACTIVAMENTE después de crear/modificar comandos
   - Verifica convenciones del proyecto
   - Asegura consistencia con filosofía motor/contenido

#### Política de Uso de Agentes

**DEBES considerar usar agentes especializados cuando sea apropiado:**
- ✅ Usa `runegram-docs-keeper` después de cambios significativos
- ✅ Usa `runegram-command-auditor` después de crear/modificar comandos
- ✅ Los agentes pueden ejecutarse en paralelo si es necesario
- ✅ Confía en los resultados de los agentes especializados

**Ejemplo de uso proactivo:**
```
Usuario: "He implementado un nuevo sistema de inventario mejorado"
Claude: "Sistema implementado. Ahora usaré runegram-docs-keeper para actualizar la documentación."
```

#### Mantenimiento de Agentes (CRÍTICO)

**IMPORTANTE**: Los agentes deben evolucionar con el proyecto.

**Cuándo actualizar agentes:**
- 🔄 **Cambios en convenciones**: Si cambia la forma de escribir comandos, actualizar `runegram-command-auditor`
- 🔄 **Nuevos sistemas**: Si agregas un sistema del motor, actualizar instrucciones de `runegram-docs-keeper`
- 🔄 **Cambios en estructura**: Si reorganizas archivos/directorios, actualizar agentes afectados
- 🔄 **Nuevas reglas**: Si estableces nuevas políticas de código, actualizar agentes relevantes

**Ejemplos de actualización necesaria:**
- Sistema de comandos cambia estructura → Actualizar `runegram-command-auditor`
- Estructura de documentación cambia → Actualizar `runegram-docs-keeper`
- Nuevas convenciones de nomenclatura → Actualizar ambos agentes

**Regla**: Si algo cambia en el proyecto que afecta las tareas de un agente, **evalúa si el agente necesita actualizarse**.

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

Ver: `docs/sistemas-del-motor/sistemas-sociales.md`

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
- `docs/primeros-pasos/` - Primeros pasos
  - `instalacion.md` - Instalación y configuración
  - `filosofia-central.md` - Filosofía de diseño
- `docs/sistemas-del-motor/` - Sistemas del motor detallados (15 documentos)
  - `sistema-de-comandos.md`, `sistema-de-permisos.md`, `sistema-de-prototipos.md`
  - `sistema-de-pulso.md`, `sistema-de-narrativa.md`, `presencia-en-linea.md`
  - `sistema-de-baneos.md` - Sistema de baneos y apelaciones
  - `sistema-de-canales.md`, `sistema-de-scripts.md`, `sistema-de-validacion.md`
  - `servicio-de-broadcasting.md`, `categorias-y-etiquetas.md`, `sistemas-sociales.md`
  - `botones-en-linea.md`, `desambiguacion-de-items.md`
- `docs/creacion-de-contenido/` - Guías de creación
  - `creacion-de-comandos.md`, `construccion-de-salas.md`, `creacion-de-items.md`
  - `guia-de-estilo-de-salida.md` - **OBLIGATORIO** para outputs
  - `escritura-de-scripts.md`
- `docs/guia-de-administracion/` - Guía de administración
  - `comandos-de-administracion.md` - Comandos de administración
  - `migraciones-de-base-de-datos.md` - BD y migraciones
- `docs/arquitectura/` - Arquitectura del sistema
  - `configuracion.md` - Sistema de configuración TOML
- `docs/hoja-de-ruta/` - Hoja de ruta
  - `vision-y-objetivos.md` - Visión del proyecto
  - `funcionalidades-planificadas.md`, `diseno-sistema-de-combate.md`, `diseno-sistema-de-habilidades.md`
- `docs/referencia/` - Referencias técnicas
  - `referencia-de-comandos.md` - **Referencia completa de comandos**

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
- **Baneos**: Moderación con baneos temporales/permanentes y apelaciones
- **Filtrado de Audiencia**: Canales con restricción de destinatarios (campo `audience`)

### Objetivo Final
Crear un juego masivo, funcional e inmersivo que aproveche las fortalezas únicas de Telegram.

---

**Versión**: 2.2.0
**Última actualización**: 2025-01-16
**Changelog**:
- v2.2 (2025-01-16): Sistema de Permisos v2.0 (locks contextuales, 9 lock functions, mensajes personalizados, async support)
- v2.1.2 (2025-01-11): Canales con audience se activan automáticamente si hay permisos
- v2.1.1 (2025-01-11): Mejora UX: /canales oculta canales sin permiso de acceso
- v2.1 (2025-01-11): Sistema de Filtrado de Audiencia para Canales implementado
- v2.0 (2025-01-11): Sistema de Baneos y Apelaciones implementado
- v1.9 (2025-01-09): Compactación del archivo sin pérdida de información crítica (~64% reducción: 2057→744 líneas)
- v1.8 (2025-01-09): Sistema de Narrativa implementado
- v1.7 (2025-10-04): Sistema de ordinales para objetos duplicados
**Mantenedor**: Proyecto Runegram

### Notas Finales
- **Reiniciar servicios**: `scripts/full_reset.bat`
- **Notificaciones Sociales**: SIEMPRE verificar si es necesario usar `broadcaster_service.send_message_to_room()` para acciones visibles
- **Regla de Oro**: Si una acción es visible, debe notificarse a jugadores presentes (online)
