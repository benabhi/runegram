# CLAUDE.md - Guía de Desarrollo para Runegram MUD

## 🎯 Visión del Proyecto

**Runegram** es un motor de juego de rol textual multijugador (MUD - Multi-User Dungeon) diseñado específicamente para ser jugado a través de Telegram. El objetivo final es crear un **juego masivo completamente funcional** con sistemas de combate, habilidades, economía, y una experiencia rica e inmersiva optimizada para dispositivos móviles.

---

## 📋 Principios Fundamentales

### 1. Separación Motor vs. Contenido

Esta es la filosofía arquitectónica más importante del proyecto:

- **Motor (`src/`)**: Código genérico en **inglés** que no conoce la semántica del juego
  - No sabe qué es una "espada", solo maneja objetos `Item`
  - Define sistemas, servicios, modelos y lógica de negocio
  - Es reutilizable y abstracto

- **Contenido (`game_data/`, `commands/`)**: Datos y definiciones en **español**
  - Define qué objetos existen, qué hacen los comandos específicos
  - Describe el mundo, las salas, los prototipos
  - Es específico del juego y fácilmente modificable

**Regla de Oro**: Al agregar funcionalidad, pregúntate: "¿Esto es parte del motor o del contenido?" Mantén esta separación estricta.

### 2. Optimización para Telegram Mobile

Telegram tiene características y limitaciones únicas que deben guiar todas las decisiones de diseño:

#### Limitaciones a Considerar
- **Pantallas pequeñas**: Los textos deben ser concisos pero descriptivos
- **Interacción táctil**: Prefiere comandos simples sobre sintaxis compleja
- **Sin interfaz gráfica rica**: Todo se comunica con texto, emojis y formato Markdown/HTML
- **Mensajes asíncronos**: Los jugadores pueden responder con demora
- **Notificaciones push**: Se pueden enviar mensajes proactivos

#### Bondades a Aprovechar
- **Ubicuidad**: Los jugadores tienen su teléfono siempre consigo
- **Comandos sugeridos**: El menú `/` de Telegram muestra comandos disponibles dinámicamente
- **Formato enriquecido**: HTML básico (`<b>`, `<i>`, `<pre>`, `<code>`)
- **Multimedia**: Envío de imágenes, documentos, stickers
- **Botones inline**: Interacción mediante botones táctiles para mejor UX móvil
- **Bot API robusta**: Aiogram proporciona una excelente abstracción

#### Mejores Prácticas UX
- Usa `<pre>` para textos descriptivos (ambiente, descripciones de salas)
- Usa `<b>` para destacar nombres importantes
- Mantén los mensajes entre 3-8 líneas para evitar scroll excesivo
- Divide información larga en múltiples mensajes
- Provee feedback inmediato para cada acción del jugador
- Usa emojis con moderación y propósito (estados, alertas importantes)

### 3. Filosofía de Comandos

**Principio**: Comandos simples, descriptivos e intuitivos.

#### Formato Preferido
```
/<verbo_acción> [argumentos]
```

Ejemplos buenos:
- `/mirar fuente`
- `/coger espada`
- `/activarcanal comercio`
- `/norte`

Ejemplos a evitar:
- `/canal comercio activar` (demasiado complejo)
- `/move n` (demasiado críptico)

#### Convenciones de Nomenclatura
- **Comandos en español**: `/mirar`, `/coger`, `/atacar`
- **Clases de comandos en inglés**: `CmdLook`, `CmdGet`, `CmdAttack`
- **Múltiples aliases permitidos**: `["mirar", "m", "l"]`
- **Primer alias = nombre principal**: Se usa para el menú de Telegram

#### Comandos Dedicados vs. Subcomandos
Prefiere múltiples comandos dedicados a un solo comando con subcomandos:

✅ **Bueno**:
```python
/activarcanal comercio
/desactivarcanal comercio
```

❌ **Evitar**:
```python
/canal comercio activar
/canal comercio desactivar
```

**Excepción**: Comandos de administración complejos pueden usar subcomandos si la alternativa sería docenas de comandos.

---

## 🏗️ Stack Tecnológico

### Tecnologías Principales
- **Python 3.11**: Lenguaje base
- **Aiogram 2.25**: Framework para bots de Telegram (async)
- **SQLAlchemy 2.0**: ORM para base de datos (async)
- **PostgreSQL 15**: Base de datos principal
- **Redis 7**: Cache y almacenamiento de estados de FSM
- **Alembic**: Migraciones de base de datos
- **Docker + Docker Compose**: Contenedorización y orquestación
- **APScheduler**: Sistema de pulse global y tareas programadas
- **Pydantic**: Validación de configuración
- **Jinja2**: Motor de templates para outputs consistentes
- **TOML**: Formato de configuración del juego (legible y versionable)

### Arquitectura de Servicios
El proyecto sigue una arquitectura de servicios para mantener la lógica de negocio separada de los handlers:

```
handlers/ → services/ → models/ → database
```

- **Handlers**: Reciben mensajes de Telegram y coordinan
- **Services**: Contienen toda la lógica de negocio
- **Models**: Definen la estructura de datos (SQLAlchemy)
- **Utils**: Funciones auxiliares (presenters, helpers)

---

## 📁 Estructura del Proyecto

```
runegram/
├── src/                          # Motor del juego (código en inglés)
│   ├── bot/
│   │   ├── bot.py               # Instancia del Bot de Aiogram
│   │   └── dispatcher.py        # Configuración del Dispatcher
│   ├── handlers/
│   │   └── player/
│   │       └── dispatcher.py    # Dispatcher principal de comandos
│   ├── models/                  # Modelos SQLAlchemy
│   │   ├── base.py
│   │   ├── account.py
│   │   ├── character.py
│   │   ├── room.py
│   │   ├── item.py
│   │   ├── exit.py
│   │   └── character_setting.py
│   ├── services/                # Lógica de negocio
│   │   ├── player_service.py
│   │   ├── command_service.py
│   │   ├── permission_service.py
│   │   ├── world_service.py
│   │   ├── world_loader_service.py
│   │   ├── item_service.py
│   │   ├── broadcaster_service.py
│   │   ├── channel_service.py
│   │   ├── script_service.py
│   │   ├── online_service.py
│   │   └── pulse_service.py
│   ├── templates/               # Sistema de templates
│   │   ├── __init__.py
│   │   ├── template_engine.py
│   │   ├── icons.py
│   │   └── base/                # Templates base Jinja2
│   │       ├── room.html.j2
│   │       ├── inventory.html.j2
│   │       ├── character.html.j2
│   │       ├── help.html.j2
│   │       ├── item_look.html.j2
│   │       └── who.html.j2
│   ├── utils/
│   │   └── presenters.py        # Funciones de presentación
│   ├── config.py                # Configuración centralizada (Pydantic)
│   └── db.py                    # Configuración de SQLAlchemy
├── commands/                     # Contenido: Definición de comandos (español)
│   ├── command.py               # Clase base Command
│   ├── player/
│   │   ├── general.py
│   │   ├── character.py
│   │   ├── interaction.py
│   │   ├── movement.py
│   │   ├── channels.py
│   │   ├── dynamic_channels.py
│   │   └── settings.py
│   └── admin/
│       ├── building.py
│       ├── movement.py
│       ├── info.py
│       ├── diagnostics.py
│       └── management.py
├── game_data/                   # Contenido: Prototipos del mundo (español)
│   ├── room_prototypes.py
│   ├── item_prototypes.py
│   └── channel_prototypes.py
├── alembic/                     # Migraciones de base de datos
│   └── versions/
├── assets/                      # Recursos multimedia
│   └── images/
├── docs/                        # Documentación exhaustiva
├── scripts/                     # Scripts de utilidad
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── run.py                       # Punto de entrada
└── .env                         # Variables de entorno
```

---

## 🎨 Guía de Estilo y Buenas Prácticas Python

### Nomenclatura

#### Código del Motor (inglés)
```python
# Nombres de clases: PascalCase
class Character(Base):
    pass

class PlayerService:
    pass

# Nombres de funciones/métodos: snake_case
async def get_character_by_id(session, character_id):
    pass

async def update_last_seen(session, character):
    pass

# Nombres de variables: snake_case
active_characters = []
room_prototype = {}
```

#### Contenido del Juego (español/inglés híbrido)
```python
# Comandos: CmdVerboIngles (aunque el comando sea en español)
class CmdLook(Command):
    names = ["mirar", "m", "l"]  # Español en los nombres de comando

class CmdAttack(Command):
    names = ["atacar", "atk"]

# Prototipos: snake_case en español
ROOM_PROTOTYPES = {
    "plaza_central": {...},
    "calle_mercaderes": {...}
}

ITEM_PROTOTYPES = {
    "espada_herrumbrosa": {...},
    "pocion_vida_menor": {...}
}
```

### Documentación

#### Docstrings de Módulo
**Obligatorio** en todos los archivos. Debe explicar el propósito del módulo:

```python
# src/services/player_service.py
"""
Módulo de Servicio para la Gestión de Jugadores.

Este servicio actúa como la capa de lógica de negocio para todas las
operaciones relacionadas con cuentas y personajes de jugadores.

Responsabilidades:
1. Creación y recuperación de cuentas desde la base de datos.
2. Creación, validación y configuración de personajes.
3. Orquestación de sistemas relacionados (comandos de Telegram, configuraciones).
"""
```

#### Docstrings de Clase
```python
class Room(Base):
    """
    Representa una sala o ubicación en el mundo del juego.

    Cada sala es una instancia que corresponde a un prototipo definido
    en `game_data/room_prototypes.py`, vinculado mediante la columna `key`.
    """
```

#### Docstrings de Función
Para funciones complejas o públicas:

```python
async def _ensure_superadmin_exists(session):
    """
    Verifica que la cuenta del Superadmin (definida en .env) exista y tenga
    el rol correcto. La crea o actualiza si es necesario.

    Esta función de "autocorrección" se ejecuta en cada arranque para garantizar
    que el Superadmin siempre esté configurado correctamente, eliminando la
    necesidad de sembrar datos frágiles en las migraciones.
    """
```

#### Comentarios Inline
Para lógica compleja o no obvia:

```python
# 1. Empezamos con los sets base del personaje desde la BD.
active_sets = set(character.command_sets)

# 2. Añadimos sets otorgados por los objetos en el inventario.
for item in character.items:
    granted_sets = item.prototype.get("grants_command_sets", [])
    active_sets.update(granted_sets)
```

### Manejo de Errores

#### Nunca Fallar Silenciosamente
Siempre loggea excepciones:

```python
try:
    await execute_complex_operation()
except Exception:
    logging.exception(f"Error en operación compleja para {character.name}")
    await message.answer("❌ Ocurrió un error inesperado.")
```

#### Niveles de Logging
- `logging.debug()`: Información detallada para debugging
- `logging.info()`: Eventos importantes normales
- `logging.warning()`: Situaciones inesperadas pero manejables
- `logging.error()`: Errores que necesitan atención
- `logging.exception()`: Errores con traceback completo

#### Feedback al Usuario
Siempre proporciona feedback claro:

```python
# ❌ Malo
if not item:
    return

# ✅ Bueno
if not item:
    await message.answer("No encuentras ese objeto por aquí.")
    return
```

### Async/Await

Todo el código debe ser asíncrono:

```python
# ✅ Correcto
async def get_character(session: AsyncSession, character_id: int) -> Character:
    result = await session.execute(
        select(Character).where(Character.id == character_id)
    )
    return result.scalar_one_or_none()

# ❌ Incorrecto - operaciones bloqueantes
def load_data_blocking():
    with open('file.txt') as f:
        return f.read()  # Bloquea el event loop
```

### Type Hints

Usa type hints siempre que sea posible:

```python
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict

async def find_room_by_key(
    session: AsyncSession,
    room_key: str
) -> Optional[Room]:
    # ...

def get_active_command_sets(character: Character) -> List[str]:
    # ...

def get_prototype_data(item_key: str) -> Dict[str, Any]:
    # ...
```

### Imports

Orden de imports:

```python
# 1. Biblioteca estándar
import logging
import asyncio
from typing import Optional, List

# 2. Librerías de terceros
from aiogram import types
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# 3. Imports del proyecto (src/)
from src.bot.bot import bot
from src.models import Character, Room
from src.services import player_service

# 4. Imports relativos (mismo paquete)
from .base import Base
from .utils import helper_function
```

### Código Limpio

#### Funciones Pequeñas y Focalizadas
```python
# ✅ Bueno - funciones pequeñas con una responsabilidad
async def get_or_create_account(session, telegram_id):
    account = await find_account_by_telegram_id(session, telegram_id)
    if not account:
        account = await create_new_account(session, telegram_id)
    return account

# ❌ Malo - función gigante que hace demasiado
async def handle_player_action(session, message, args):
    # 200 líneas de código mezclando validación, lógica de negocio y presentación
```

#### Evita Números Mágicos - Usa Configuración Centralizada
```python
# ❌ Malo - Número mágico hardcodeado
if player.afk_time > 300:
    mark_as_afk(player)

# ⚠️ Aceptable - Constante con nombre
AFK_THRESHOLD_SECONDS = 300  # 5 minutos
if player.afk_time > AFK_THRESHOLD_SECONDS:
    mark_as_afk(player)

# ✅ MEJOR - Configuración centralizada en gameconfig.toml
from src.config import settings

if player.afk_time > settings.online_threshold.total_seconds():
    mark_as_offline(player)
```

**Principio:** Si un valor podría necesitar ajustes de balanceo, debugging o personalización, debe estar en `gameconfig.toml`, NO hardcodeado.

**Ver:** `docs/10_CONFIGURATION.md` para guía completa de configuración.

#### DRY (Don't Repeat Yourself)
```python
# ✅ Bueno - Lógica centralizada en un servicio
from src.services import permission_service

can_execute, error_msg = await permission_service.can_execute(
    character,
    lock_string
)

# ❌ Malo - Duplicar lógica de permisos en cada comando
```

---

## 🔧 Sistemas del Motor

### 1. Sistema de Comandos

El sistema de comandos es **completamente dinámico** y contextual.

#### Estructura de un Comando
```python
from commands.command import Command
from src.models import Character
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import types

class CmdExampleAction(Command):
    """
    Descripción del comando.
    """
    # Lista de aliases (el primero es el principal)
    names = ["accion", "acc", "a"]

    # String de permisos (vacío = todos pueden usar)
    lock = ""

    # Descripción para el menú de Telegram
    description = "Realiza una acción de ejemplo."

    async def execute(
        self,
        character: Character,
        session: AsyncSession,
        message: types.Message,
        args: list[str]
    ):
        """
        Lógica del comando.

        Args:
            character: El personaje que ejecuta el comando (precargado con relaciones)
            session: Sesión de BD activa
            message: Mensaje de Telegram
            args: Lista de argumentos (ya parseados)
        """
        try:
            # Validación
            if not args:
                await message.answer("Uso: /accion [argumento]")
                return

            # Lógica de negocio
            result = await some_service.do_something(session, character, args)

            # Respuesta al usuario
            await message.answer(f"Resultado: {result}")

            # Commit si modificaste la BD
            await session.commit()

        except Exception:
            await message.answer("❌ Error al ejecutar la acción.")
            logging.exception(f"Error en /accion para {character.name}")
```

#### CommandSets

Los comandos se agrupan en **CommandSets** que representan conjuntos de funcionalidad:

```python
# commands/player/general.py

GENERAL_COMMANDS = [
    CmdLook(),
    CmdSay(),
    CmdInventory(),
    CmdHelp(),
    CmdWho(),
]
```

Los CommandSets activos se determinan dinámicamente basándose en:
- **Base del personaje**: Conjuntos definidos en `character.command_sets`
- **Objetos equipados**: Items que otorgan `grants_command_sets`
- **Sala actual**: Salas que otorgan `grants_command_sets`
- **Rol de cuenta**: Admins obtienen sets adicionales

Ver: `src/services/command_service.py:get_active_command_sets_for_character()`

#### Registro de CommandSets
En `src/handlers/player/dispatcher.py`:

```python
COMMAND_SETS = {
    # Comandos de jugador
    "general": GENERAL_COMMANDS,
    "movement": MOVEMENT_COMMANDS,
    "interaction": INTERACTION_COMMANDS,
    # ...

    # Comandos de admin
    "spawning": SPAWN_COMMANDS,
    "admin_movement": ADMIN_MOVEMENT_COMMANDS,
    # ...
}
```

### 2. Sistema de Permisos (Locks)

Los locks controlan el acceso a comandos y objetos.

#### Sintaxis de Locks
```python
# Vacío = todos pueden acceder
lock = ""

# Requiere rol específico
lock = "role:ADMIN"
lock = "role:SUPERADMIN"

# Lógica compleja (futuro)
lock = "has_item:llave_maestra AND in_room:torre_mago"
```

#### Implementación
Ver: `src/services/permission_service.py`

```python
can_execute, error_message = await permission_service.can_execute(
    character,
    lock_string
)

if not can_execute:
    await message.answer(error_message or "No tienes permiso.")
    return
```

### 3. Sistema de Prototipos

Los prototipos definen las características estáticas de objetos, salas, canales, etc.

#### Ejemplo: Prototipo de Sala
```python
# game_data/room_prototypes.py

ROOM_PROTOTYPES = {
    "plaza_central": {
        "name": "Plaza Central de Runegard",
        "description": "Estás en el corazón de la ciudad...",
        "exits": {
            "norte": "calle_mercaderes",
            "sur": "templo_antiguo"
        },
        "grants_command_sets": [],  # Opcional
        "details": {  # Elementos mirables no-objetos
            "fuente_plaza": {
                "keywords": ["fuente", "marmol"],
                "description": "Una magnífica fuente de mármol..."
            }
        }
    }
}
```

#### Ejemplo: Prototipo de Item
```python
# game_data/item_prototypes.py

ITEM_PROTOTYPES = {
    "espada_herrumbrosa": {
        "name": "Espada Herrumbrosa",
        "description": "Una espada vieja y oxidada, pero aún funcional.",
        "keywords": ["espada", "herrumbrosa", "hoja"],
        "stackable": False,
        "is_container": False,
        "grants_command_sets": ["combat"],  # Otorga comandos de combate
        "attributes": {
            "damage": 5,
            "weight": 3
        },
        "scripts": {  # Opcional
            "on_look": "print('La espada vibra levemente.')",
            "on_get": "..."
        }
    },

    "pocion_vida_menor": {
        "name": "Poción de Vida Menor",
        "description": "Un pequeño vial con líquido rojo brillante.",
        "keywords": ["pocion", "vida", "vial"],
        "stackable": True,  # Múltiples instancias se apilan
        "is_container": False,
        "grants_command_sets": ["consumable"],
        "attributes": {
            "heal_amount": 20
        }
    }
}
```

#### Relación Instancia-Prototipo

```python
# Modelo en BD (instancia)
item = Item(
    key="espada_herrumbrosa",  # Vincula al prototipo
    instance_name=None,         # Null = usa nombre del prototipo
    room_id=123,
    character_id=None
)

# Acceso al prototipo
item.prototype  # Returns: ITEM_PROTOTYPES["espada_herrumbrosa"]
item.get_name()  # Returns: "Espada Herrumbrosa"
item.get_description()  # Returns: descripción del prototipo
```

**Ventaja**: Cambiar un prototipo actualiza **todas** las instancias instantáneamente.

### 4. Sistema de Broadcasting

Permite enviar mensajes a múltiples jugadores simultáneamente.

```python
from src.services import broadcaster_service

# Notificar a todos en una sala
await broadcaster_service.msg_room(
    session=session,
    room=current_room,
    message_text="¡Algo dramático sucede!",
    exclude_character=acting_character  # Opcional
)

# Notificar a un canal
await broadcaster_service.msg_channel(
    session=session,
    channel_key="comercio",
    sender_name=character.name,
    message_text="¡Vendo espadas!"
)
```

Ver: `src/services/broadcaster_service.py`

### 5. Sistema de Pulse Global

El corazón temporal de Runegram. Ejecuta un "tick" cada 2 segundos, permitiendo que todos los sistemas basados en tiempo se sincronicen.

#### Concepto
```
Un solo job global → Procesa todas las entidades → Sincronización perfecta
```

**Ventajas sobre el enfoque anterior (APScheduler individual)**:
- ✅ Escalable: O(1) jobs en lugar de O(n) jobs
- ✅ Sincronizado: Todos los sistemas en la misma timeline
- ✅ Simple: "60 ticks" es más claro que `*/2 * * * *`
- ✅ Flexible: Soporta scripts one-shot y permanentes

#### Uso en Prototipos
```python
# En game_data/item_prototypes.py
"espada_viviente": {
    "tick_scripts": [
        {
            "interval_ticks": 60,  # Cada 60 ticks (120s con tick=2s)
            "script": "script_espada_susurra",
            "category": "ambient",
            "permanent": True  # Se repite indefinidamente
        },
        {
            "interval_ticks": 1,  # Al primer tick
            "script": "script_despierta",
            "category": "ambient",
            "permanent": False  # Una sola vez
        }
    ]
}
```

#### Uso Programático
```python
from src.services import pulse_service

# Consultar tick actual
current_tick = pulse_service.get_current_tick()

# Añadir jobs adicionales al scheduler
pulse_service.scheduler.add_job(
    func=my_async_function,
    trigger='interval',
    seconds=60,
    id='unique_id',
    replace_existing=True
)
```

Ver: `docs/03_ENGINE_SYSTEMS/07_PULSE_SYSTEM.md` para detalles completos.

**Casos de Uso**:
- ✅ Sistema de combate por turnos (futuro)
- ✅ Clima dinámico sincronizado (futuro)
- ✅ Monstruos errantes coordinados (futuro)
- ✅ Efectos ambientales de items (actual)
- ✅ Chequeo de jugadores AFK (actual)

### 6. Sistema de Scripts

Permite ejecutar código Python almacenado como string (con sandboxing).

```python
from src.services import script_service

# Ejecutar un script
await script_service.execute_script(
    script_string="character.hp += 10; print('¡Curado!')",
    session=session,
    character=character,
    target=item  # Opcional
)
```

**Contexto Disponible en Scripts**:
- `character`: El personaje que ejecuta
- `target`: El objeto target (item, personaje, sala)
- `session`: Sesión de BD
- `bot`: Instancia del bot de Telegram

Ver: `src/services/script_service.py`

**⚠️ Seguridad**: Actualmente NO implementa sandboxing real. Solo usar para contenido confiable.

### 7. Sistema de Canales

Canales de comunicación global entre jugadores.

#### Canales Estáticos
Definidos en `game_data/channel_prototypes.py`:

```python
CHANNEL_PROTOTYPES = {
    "ayuda": {
        "name": "Canal de Ayuda",
        "description": "Un canal para pedir ayuda a otros jugadores.",
        "default_active": True  # Activado por defecto
    },
    "comercio": {
        "name": "Canal de Comercio",
        "description": "Compra y vende aquí.",
        "default_active": False
    }
}
```

Comandos generados automáticamente: `/ayuda [mensaje]`, `/comercio [mensaje]`

#### Canales Dinámicos
Los jugadores pueden crear sus propios canales privados:

```python
/crearcanal mi_grupo
/invitar mi_grupo Juan
/mi_grupo Hola equipo!
```

Ver: `commands/player/dynamic_channels.py`

### 8. Sistema de Templates

Sistema centralizado de templates con **Jinja2** que separa la presentación del código, permitiendo outputs consistentes y fácilmente personalizables.

#### Beneficios
- **Consistencia Visual**: Todos los outputs usan el mismo estilo e íconos
- **Facilidad de Modificación**: Cambiar el formato de un comando sin tocar código Python
- **Personalización**: Los prototipos pueden definir templates y íconos personalizados
- **Mantenibilidad**: Separación clara entre lógica de negocio y presentación

#### Estructura
```
src/templates/
├── __init__.py            # Exports principales
├── template_engine.py     # Motor de renderizado Jinja2
├── icons.py              # Diccionario de íconos/emojis
└── base/                 # Templates base
    ├── room.html.j2
    ├── inventory.html.j2
    ├── character.html.j2
    ├── help.html.j2
    ├── item_look.html.j2
    └── who.html.j2
```

#### Uso Básico
```python
from src.templates import render_template, ICONS

# Renderizar un template
output = render_template('room.html.j2', room=room, character=character)
await message.answer(output, parse_mode="HTML")

# Usar íconos en código
message_text = f"{ICONS['room']} {room.name}"
```

#### Personalización en Prototipos
Los prototipos pueden definir íconos y templates personalizados mediante el campo `display`:

```python
# En game_data/room_prototypes.py
ROOM_PROTOTYPES = {
    "plaza_central": {
        "name": "Plaza Central",
        "description": "...",
        "display": {
            "icon": "🏛️",                      # Ícono personalizado
            "template": "custom_plaza.html.j2"  # Template personalizado (opcional)
        }
    }
}

# En game_data/item_prototypes.py
ITEM_PROTOTYPES = {
    "espada_viviente": {
        "name": "una espada viviente",
        "description": "...",
        "display": {
            "icon": "⚔️",  # Se muestra en inventarios y listados
        }
    }
}
```

#### Estándares de Formato

**Estructura Visual Consistente**:
```
[ÍCONO] [TÍTULO EN NEGRITA EN MAYÚSCULAS]
[Descripción de 1-3 líneas]

[ÍCONO] [SECCIÓN]:
    - Item 1
    - Item 2
```

**Regla de Indentación (CRÍTICA - Filosofía de Diseño)**:
- **TODOS** los ítems en listas **DEBEN** estar indentados con **4 espacios** + guion
- Esta es una regla universal que aplica a todos los templates
- Los 4 espacios simulan un tab y mejoran la legibilidad en Telegram
- NO usar tabs literales (se renderizan como 1 espacio)
- Ejemplo correcto: `    - ⬆️ Norte` (4 espacios + guion + espacio)

**Reglas de Íconos**:
- Siempre usar íconos al inicio de cada sección
- Un ícono por concepto (no reutilizar para cosas diferentes)
- Usar íconos de dirección (⬆️ ⬇️ ➡️ ⬅️) para salidas
- Preferir constantes de `ICONS` sobre emojis hardcodeados

**Formato de Texto**:
- Títulos en `<b>negrita</b>`
- Narración/ambiente en texto normal
- Diálogos/emotes en `<i>cursiva</i>`
- Todo envuelto en `<pre>` para formato monoespaciado

Ver: `docs/04_CONTENT_CREATION/04_OUTPUT_TEMPLATES.md` para guía completa.

### 9. Sistema de Presentación

Funciones centralizadas para generar texto formateado para el usuario usando el sistema de templates.

```python
from src.utils.presenters import show_current_room, format_item_look

# Muestra la sala actual al jugador
await show_current_room(message)

# Muestra la descripción de un objeto
output = format_item_look(item, can_interact=True)
await message.answer(output, parse_mode="HTML")
```

**Beneficio**: Mantiene la lógica de presentación separada de la lógica de negocio.

**Presenters Disponibles**:
- `format_room()`: Descripción completa de sala
- `format_inventory()`: Inventario de personaje o contenedor
- `format_character()`: Hoja de personaje
- `format_item_look()`: Descripción detallada de item
- `format_who_list()`: Lista de jugadores online

Ver: `src/utils/presenters.py`

### 10. Sistema de Botones Inline

Sistema de interacción mediante botones de Telegram para mejorar la UX móvil.

#### Características Implementadas
- ✅ **Botón de creación de personaje** con flujo FSM
- ✅ **Botones de navegación** en salas (direcciones)
- ✅ **Sistema de callback routing** extensible
- ✅ **Soporte para FSM** (conversaciones multi-paso)

#### Componentes Principales

```python
from src.utils.inline_keyboards import (
    create_callback_data,           # Genera callback_data estructurado
    parse_callback_data,            # Parsea callback_data
    create_room_navigation_keyboard,  # Botones de salidas
    create_character_creation_keyboard,  # Botón de crear personaje
    create_confirmation_keyboard,   # Botones Sí/No
)

# Ejemplo: Crear botones de navegación
keyboard = create_room_navigation_keyboard(room)
await message.answer(formatted_room, reply_markup=keyboard)

# Ejemplo: Crear callback data personalizado
callback_data = create_callback_data("use_item", item_id=5, action="consume")
# Resultado: "use_item:item_id=5:action=consume"
```

#### Callback Handlers

Los callbacks se procesan en `src/handlers/callbacks.py`:

```python
# Router principal
@dp.callback_query_handler(lambda c: True)
async def callback_query_router(callback: types.CallbackQuery):
    callback_info = parse_callback_data(callback.data)
    action = callback_info["action"]
    params = callback_info["params"]

    handler_func = CALLBACK_HANDLERS.get(action)
    if handler_func:
        await handler_func(callback, params, session)

# Handlers específicos
CALLBACK_HANDLERS = {
    "create_char": handle_character_creation,  # Inicia FSM
    "move": handle_movement,                   # Navegación
    "refresh": handle_refresh,                 # Actualizar
    # ... agregar nuevos handlers aquí
}
```

#### FSM para Flujos Multi-paso

```python
from aiogram.dispatcher.filters.state import State, StatesGroup

class CharacterCreationStates(StatesGroup):
    waiting_for_name = State()

# Iniciar FSM desde callback
state = dp.current_state(user=callback.from_user.id)
await state.set_state(CharacterCreationStates.waiting_for_name)

# Handler de estado FSM
@dp.message_handler(state=CharacterCreationStates.waiting_for_name)
async def process_character_name(message, state: FSMContext):
    # Validar y procesar input
    # await state.finish() cuando termine
```

#### Roadmap Futuro
- 🚧 **Teclado dinámico completo** para jugar sin comandos
- 🚧 **Teclado contextual de sala** con acciones rápidas
- 🚧 **Teclado de inventario** con interacción por botones
- 🚧 **Teclado de combate** (cuando se implemente sistema de combate)
- 🚧 **Configuración de settings** mediante menús

Ver: `docs/11_INLINE_BUTTONS.md` para guía completa y ejemplos.

---

## 🎮 Creación de Contenido

### Agregar una Nueva Sala

1. **Editar `game_data/room_prototypes.py`**:

```python
ROOM_PROTOTYPES = {
    # ... salas existentes ...

    "forja_enano": {
        "name": "La Forja del Enano Errante",
        "description": "El calor del fuego y el martilleo llenan esta sala.",
        "exits": {
            "sur": "plaza_central"
        },
        "grants_command_sets": ["smithing"],  # Opcional
        "details": {
            "yunque": {
                "keywords": ["yunque", "yunque de hierro"],
                "description": "Un yunque desgastado pero resistente."
            }
        }
    }
}
```

2. **Actualizar conexiones** en salas existentes:

```python
"plaza_central": {
    # ...
    "exits": {
        "este": "calle_mercaderes",
        "norte": "forja_enano"  # Nueva conexión
    }
}
```

3. **Reiniciar el bot**: El `world_loader_service` sincroniza automáticamente.

### Agregar un Nuevo Item

1. **Editar `game_data/item_prototypes.py`**:

```python
ITEM_PROTOTYPES = {
    # ... items existentes ...

    "hacha_leñador": {
        "name": "Hacha de Leñador",
        "description": "Un hacha pesada con el mango de madera.",
        "keywords": ["hacha", "leñador", "hacha de leñador"],
        "stackable": False,
        "is_container": False,
        "grants_command_sets": ["woodcutting"],
        "attributes": {
            "damage": 7,
            "weight": 5,
            "durability": 100
        },
        "scripts": {
            "on_get": "print('Tomas el hacha. Pesa bastante.')"
        }
    }
}
```

2. **Spawning del item** (como admin):

```
/crear hacha_leñador
```

### Agregar un Nuevo Comando de Jugador

1. **Crear o editar archivo en `commands/player/`**:

```python
# commands/player/interaction.py

class CmdUse(Command):
    """Comando para usar un objeto."""
    names = ["usar", "use"]
    lock = ""
    description = "Usa un objeto de tu inventario."

    async def execute(self, character, session, message, args):
        if not args:
            await message.answer("¿Qué quieres usar?")
            return

        item_name = " ".join(args).lower()
        item = find_item_in_list(item_name, character.items)

        if not item:
            await message.answer("No tienes ese objeto.")
            return

        # Ejecutar script "on_use" si existe
        if "on_use" in item.prototype.get("scripts", {}):
            await script_service.execute_script(
                script_string=item.prototype["scripts"]["on_use"],
                session=session,
                character=character,
                target=item
            )
        else:
            await message.answer(f"No sabes cómo usar {item.get_name()}.")
```

2. **Agregar al CommandSet**:

```python
# Al final del archivo commands/player/interaction.py

INTERACTION_COMMANDS = [
    CmdGet(),
    CmdDrop(),
    CmdUse(),  # Nuevo comando
]
```

3. **Verificar registro** en `src/handlers/player/dispatcher.py`:

```python
COMMAND_SETS = {
    "interaction": INTERACTION_COMMANDS,  # Ya debería estar
    # ...
}
```

4. **Asegurar que el set esté activo** en personajes:

```python
# En src/models/character.py, el default ya incluye "interaction"
command_sets = Column(
    JSONB,
    default=["general", "interaction", "movement", ...]
)
```

### Agregar un Nuevo Canal de Comunicación

1. **Editar `game_data/channel_prototypes.py`**:

```python
CHANNEL_PROTOTYPES = {
    # ... canales existentes ...

    "roleplay": {
        "name": "Canal de Roleplay",
        "description": "Canal para historias y roleplay.",
        "default_active": False
    }
}
```

2. **Reiniciar el bot**: El comando `/roleplay [mensaje]` se genera automáticamente.

3. **Activar en personaje**:

```
/activarcanal roleplay
```

---

## 🔒 Sistema de Roles y Permisos

### Roles de Cuenta
```python
# src/models/account.py

class Account(Base):
    role = Column(
        String(20),
        nullable=False,
        default="PLAYER"
    )
```

Roles disponibles:
- `PLAYER` (default): Jugador normal
- `ADMIN`: Administrador con comandos de construcción
- `SUPERADMIN`: Acceso total (definido en `.env`)

### Asignar Rol (como Superadmin)

```python
# Comando de admin (futuro)
/setrole @username ADMIN
```

Actualmente, modificar directamente en BD o usar script de admin.

### Locks en Comandos

```python
class CmdTeleport(Command):
    names = ["teletransportar", "tp"]
    lock = "role:ADMIN"  # Solo admins
    description = "Teletransportarse a cualquier sala."
```

---

## 🗄️ Base de Datos y Migraciones

### Modelos Principales

```
Account (Cuenta de Telegram)
  ↓ 1:1
Character (Personaje del jugador)
  ↓ N:1
Room (Sala/Ubicación)
  ↓ 1:N
Exit (Conexiones entre salas)

Character
  ↓ 1:N
Item (Objetos en inventario)

Room
  ↓ 1:N
Item (Objetos en el suelo)

Item
  ↓ 1:N
Item (Objetos dentro de contenedores)
```

### Crear una Nueva Migración

Después de modificar modelos en `src/models/`:

```bash
# Dentro del contenedor Docker
docker exec -it runegram-bot-1 alembic revision --autogenerate -m "Descripción del cambio"

# Aplicar migración
docker exec -it runegram-bot-1 alembic upgrade head
```

### Rollback de Migración

```bash
docker exec -it runegram-bot-1 alembic downgrade -1
```

Ver: `docs/06_DATABASE_AND_MIGRATIONS.md`

---

## 🐛 Debugging y Logging

### Niveles de Logging

Configurados en `run.py`:

```python
logging.basicConfig(
    level=logging.INFO,  # Cambiar a DEBUG para más detalle
    stream=sys.stdout,
    format="%(asctime)s [%(levelname)s] - %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
```

### Ver Logs en Docker

```bash
# Logs del contenedor del bot
docker logs -f runegram-bot-1

# Logs de PostgreSQL
docker logs -f runegram-postgres-1
```

### Logging en Código

```python
import logging

# En funciones/métodos
logging.info(f"Jugador {character.name} entró a {room.name}")
logging.warning(f"Intento de acción inválida por {character.name}")
logging.error(f"Error crítico: {error_details}")

# Con traceback completo
try:
    risky_operation()
except Exception:
    logging.exception(f"Falló operación para {character.name}")
```

---

## 🚀 Flujo de Desarrollo

### ⚠️ POLÍTICA DE DOCUMENTACIÓN Y TESTS (CRÍTICO)

**OBLIGATORIO**: Después de **CUALQUIER** cambio en el código (agregar funcionalidad, corregir bug, refactorizar), se debe:

#### 1. Verificar y Actualizar Documentación

1. ✅ **Verificar `README.md`**: ¿Refleja correctamente el estado actual del proyecto?
2. ✅ **Revisar `docs/`**: ¿Hay documentación que necesita actualización?
3. ✅ **Crear/Actualizar/Eliminar** archivos en `docs/` según sea necesario:
   - **Crear**: Si la funcionalidad nueva merece documentación propia
   - **Actualizar**: Si modificaste un sistema existente documentado
   - **Eliminar**: Si la funcionalidad fue removida o deprecated
   - **Reorganizar**: Si la estructura de docs ya no refleja la arquitectura

**La documentación desactualizada es peor que no tener documentación.**

#### 2. Verificar y Actualizar Tests

**Tests críticos DEBEN pasar siempre antes de commit.**

1. ✅ **Ejecutar tests existentes**: `pytest -m critical`
2. ✅ **Crear/actualizar tests** para funcionalidad nueva o modificada:
   - Tests críticos para sistemas de seguridad/permisos
   - Tests para servicios core modificados
   - Tests de regresión para bugs corregidos
3. ✅ **Verificar cobertura**: `pytest --cov=src`
   - Mantener cobertura >70% en código crítico
   - No bajar la cobertura existente

**¿Qué requiere tests?**
- ✅ **SIEMPRE**: Servicios críticos (permisos, validación, player_service)
- ✅ **SIEMPRE**: Correcciones de bugs (test de regresión)
- ✅ **FRECUENTEMENTE**: Comandos complejos con lógica de negocio
- ⚠️ **A VECES**: Comandos simples de contenido
- ❌ **NUNCA**: Scripts de contenido específico
- ❌ **NUNCA**: Prototipos de items/salas/canales

Ver: `tests/README.md` para guía completa de testing.

#### Archivos que Típicamente Necesitan Actualización

| Cambio en Código | Documentos a Revisar |
|------------------|---------------------|
| Nuevo sistema del motor | `docs/03_ENGINE_SYSTEMS/` (crear nuevo archivo) |
| Nuevo tipo de contenido | `docs/04_CONTENT_CREATION/` |
| Cambio en comandos | `docs/04_CONTENT_CREATION/01_CREATING_COMMANDS.md` |
| Cambio en modelos BD | `docs/06_DATABASE_AND_MIGRATIONS.md` |
| Nueva funcionalidad mayor | `README.md` + `docs/07_ROADMAP.md` |
| Stack tecnológico | `README.md` + `CLAUDE.md` (sección Stack) |

### Agregar Nueva Funcionalidad

1. **Identificar**: ¿Es motor o contenido?
2. **Diseñar**: Pensar en la experiencia móvil de Telegram
3. **Implementar**:
   - Si es motor: Crear/modificar servicios, modelos, handlers
   - Si es contenido: Agregar comandos, prototipos
4. **Documentar código**: Docstrings, comentarios explicativos
5. **📚 ACTUALIZAR DOCUMENTACIÓN** (Ver política arriba):
   - Verificar `README.md`
   - Actualizar/crear archivos en `docs/`
   - Actualizar `CLAUDE.md` si afecta decisiones de desarrollo
6. **Probar**: Ejecutar en entorno local, verificar edge cases
7. **Migrar BD** (si aplica): Crear migración de Alembic
8. **Commit**: Mensaje descriptivo en español (incluir "docs:" si actualizaste documentación)

### Convenciones de Git

```bash
# Mensajes de commit en español, descriptivos
git commit -m "Agregado sistema de combate básico"
git commit -m "Corregido bug en comando /coger con contenedores"
git commit -m "Actualizado prototipo de espada con nuevos atributos"
```

---

## 📚 Futuro y Roadmap

Ver: `docs/07_ROADMAP.md`

Sistemas planificados:
- ✅ Sistema de comandos dinámicos
- ✅ Sistema de canales y broadcasting
- ✅ Sistema de pulse global
- ✅ Sistema de online/AFK
- 🚧 Sistema de combate (en diseño)
- 🚧 Sistema de habilidades
- ⏳ Sistema de crafting
- ⏳ Sistema económico (moneda, shops NPCs)
- ⏳ Sistema de quests
- ⏳ Sistema de facciones
- ⏳ Sistema de clima y día/noche
- ⏳ NPCs con IA básica

---

## 🤖 Guía Específica para Claude

### 🚨 REGLA #1: DOCUMENTACIÓN SIEMPRE ACTUALIZADA

**ANTES de finalizar CUALQUIER tarea**, debes:

1. 📋 **Verificar si `README.md` necesita actualización**
   - ¿Agregaste una funcionalidad que debe mencionarse?
   - ¿Cambió el stack tecnológico?
   - ¿El quick start sigue siendo válido?

2. 📚 **Revisar TODOS los archivos en `docs/`**
   - Leer títulos y contenido para identificar qué necesita actualización
   - Actualizar archivos existentes que ahora están desactualizados
   - **Crear nuevos archivos** si la funcionalidad lo amerita
   - **Eliminar archivos** si documentan funcionalidad removida
   - Actualizar índices/TOC si los hay

3. ✍️ **Actualizar este archivo (`CLAUDE.md`)** si:
   - Creaste un nuevo sistema del motor
   - Cambiaste la filosofía de diseño
   - Agregaste nuevas convenciones o buenas prácticas

**NUNCA digas "tarea completada" sin verificar documentación.**

**Ejemplos de qué actualizar**:
- Agregaste sistema de combate → Actualizar `docs/08_COMBAT_SYSTEM.md` + `README.md`
- Agregaste nuevo comando → Actualizar `docs/04_CONTENT_CREATION/01_CREATING_COMMANDS.md`
- Cambiaste modelo de BD → Actualizar `docs/06_DATABASE_AND_MIGRATIONS.md`
- Nuevo servicio → Crear `docs/03_ENGINE_SYSTEMS/XX_NUEVO_SERVICIO.md`

### Política de Jugadores Desconectados (CRÍTICO)

**IMPORTANTE:** Los jugadores desconectados (offline) son tratados como **ausentes del mundo del juego**. Esta es una regla fundamental de diseño del MUD.

#### Principio Fundamental

Cuando un jugador está desconectado (inactivo por más de 5 minutos o desconectado manualmente), **ese jugador NO está presente en el juego**, aunque su personaje permanezca técnicamente en la base de datos.

#### Reglas de Implementación

**✅ SIEMPRE filtrar jugadores desconectados en:**

1. **Visualización de salas** (`/mirar`): No mostrar personajes desconectados
2. **Listados de personajes** (`/personajes`): Solo jugadores online
3. **Interacción con personajes** (`/mirar <jugador>`, `/susurrar`): Rechazar si el objetivo está desconectado
4. **Broadcasting de sala** (`broadcaster_service.send_message_to_room()`): Automáticamente excluye desconectados
5. **Comandos sociales** (`/decir`): Solo enviar a jugadores online

**❌ NUNCA:**
- Permitir interacción con jugadores desconectados
- Mostrar jugadores desconectados en listas de "presencia"
- Enviar mensajes de eventos de sala a jugadores desconectados

#### Código de Verificación

```python
from src.services import online_service

# Verificar si un personaje está activo (online)
is_active = await online_service.is_character_online(character.id)
if not is_active:
    # El jugador está desconectado, tratarlo como ausente
    await message.answer("No ves a nadie con ese nombre por aquí.")
    return
```

#### Desconexión Manual y Automática

Los jugadores pueden desconectarse de dos formas:

1. **Desconexión Manual**: Usando `/desconectar` (también `/salir` o `/logout`)
2. **Desconexión Automática**: Por inactividad (5 minutos sin enviar comandos)

**Comportamiento en ambos casos:**
- Se elimina `last_seen` → el jugador se marca como offline inmediatamente
- Se establece `offline_notified` → cuando vuelva, recibirá notificación de reconexión
- **Mensaje de confirmación**: "Te has desconectado del juego. Vuelve cuando quieras con cualquier comando. ¡Hasta pronto!"
- **Al volver**: El jugador recibe "Te has reconectado al juego."

**Nota**: Ambos tipos de desconexión ahora informan explícitamente que con cualquier comando se vuelve a estar online.

#### Consideraciones Futuras

Al implementar nuevos sistemas (combate, comercio, etc.), **SIEMPRE** define cómo afecta la desconexión:
- ¿Puede un jugador desconectarse durante un combate?
- ¿Debe cancelarse la interacción si alguien se desconecta?
- ¿Los efectos temporales continúan mientras el jugador está desconectado?

Ver `docs/03_ENGINE_SYSTEMS/05_SOCIAL_SYSTEMS.md` para más detalles.

### Cuando el Usuario Pide Agregar Funcionalidad

1. **Pregunta primero**: "¿Esto es parte del motor (genérico) o del contenido (específico del juego)?"
2. **Considera Telegram**: ¿La UX es apropiada para una pantalla pequeña?
3. **Mantén la separación**: No mezcles lógica de motor con contenido
4. **Documenta código**: Docstrings, comentarios explicativos
5. **Sigue las convenciones**: Nombres en inglés (motor) / español (contenido)
6. **Código robusto**: Manejo de errores, logging, type hints
7. **Feedback al usuario**: Siempre responde al jugador con mensajes claros
8. **🎨 USA TEMPLATES**: Para outputs visuales, usa el sistema de templates y presenters, NO hardcodees HTML
9. **⚠️ VERIFICA JUGADORES DESCONECTADOS**: Si el comando interactúa con otros jugadores, filtra los desconectados (offline)
10. **📚 ACTUALIZA DOCUMENTACIÓN**: Antes de dar por terminada la tarea (ver REGLA #1)

### Cuando el Usuario Pide Corregir un Bug

1. **Reproduce el problema**: Lee el código relevante
2. **Identifica la causa raíz**: No solo el síntoma
3. **Propón la solución**: Explica qué cambiarás y por qué
4. **Implementa con cuidado**: No rompas funcionalidad existente
5. **Agrega logging**: Para detectar futuros problemas similares
6. **📚 VERIFICA DOCUMENTACIÓN**: ¿El bug indica que la documentación era incorrecta?

### Cuando el Usuario Pide Explicar Código

1. **Contexto primero**: Explica para qué sirve el archivo/módulo
2. **Flujo de ejecución**: Describe cómo se conecta con otros sistemas
3. **Detalles técnicos**: Explica las partes complejas
4. **Relación con el juego**: Cómo impacta la experiencia del jugador

### Preguntas para Hacerte Antes de Sugerir Código

#### Durante la Implementación
- ✅ ¿Esto respeta la separación motor/contenido?
- ✅ ¿La UX es buena para Telegram móvil?
- ✅ ¿El código tiene docstrings y comentarios?
- ✅ ¿Sigo las convenciones de nomenclatura?
- ✅ ¿Hay manejo de errores apropiado?
- ✅ ¿Hay logging para debugging?
- ✅ ¿Proporciono feedback claro al usuario?
- ✅ ¿Es código async (no bloqueante)?
- ✅ ¿Necesita migración de BD?
- ✅ ¿Estoy usando templates/presenters para outputs visuales en lugar de hardcodear HTML?
- ✅ ¿Los íconos vienen de `ICONS` en lugar de estar hardcodeados?
- ✅ **¿Si interactúa con otros jugadores, estoy filtrando jugadores desconectados (offline) correctamente?**

#### Antes de Finalizar (CRÍTICO)
- ✅ ¿Verifiqué si `README.md` necesita actualización?
- ✅ ¿Revisé qué archivos en `docs/` debo actualizar?
- ✅ ¿Creé nuevos archivos de documentación si era necesario?
- ✅ ¿Actualicé el `ROADMAP.md` si completé una funcionalidad planificada?
- ✅ ¿La documentación refleja EXACTAMENTE el estado actual del código?

---

## 📖 Recursos y Referencias

### Documentación Interna
- `docs/01_GETTING_STARTED.md`: Guía de inicio
- `docs/02_CORE_PHILOSOPHY.md`: Filosofía de diseño
- `docs/03_ENGINE_SYSTEMS/`: Sistemas del motor en detalle
- `docs/04_CONTENT_CREATION/`: Guías de creación de contenido
  - `04_OUTPUT_TEMPLATES.md`: Sistema de templates y outputs consistentes
- `docs/05_ADMIN_GUIDE.md`: Comandos de administración
- `docs/06_DATABASE_AND_MIGRATIONS.md`: BD y migraciones
- `docs/07_ROADMAP.md`: Planes futuros
- `docs/08_COMBAT_SYSTEM.md`: Diseño del sistema de combate
- `docs/09_SKILL_SYSTEM.md`: Diseño del sistema de habilidades
- `docs/10_CONFIGURATION.md`: Sistema de configuración centralizada con TOML
- `docs/11_INLINE_BUTTONS.md`: Sistema de botones inline de Telegram
- `docs/COMMAND_REFERENCE.md`: **Referencia completa de todos los comandos** (jugador y admin)

### Documentación Externa
- [Aiogram 2.x Docs](https://docs.aiogram.dev/en/v2.25.1/)
- [SQLAlchemy 2.0 Docs](https://docs.sqlalchemy.org/en/20/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [APScheduler](https://apscheduler.readthedocs.io/)
- [Pydantic](https://docs.pydantic.dev/)

---

## 🎯 Resumen Ejecutivo para Claude

**Runegram** es un MUD textual para Telegram construido con arquitectura moderna Python async. La clave es mantener la **separación entre motor (inglés, genérico) y contenido (español, específico)**. Todo el código debe estar **documentado**, seguir **convenciones de nomenclatura estrictas**, tener **manejo robusto de errores**, y estar **optimizado para la experiencia móvil de Telegram**.

### Workflow de Desarrollo (OBLIGATORIO)

Al sugerir o implementar funcionalidad:
1. Identifica si es motor o contenido
2. Optimiza para UX móvil de Telegram
3. Documenta código (docstrings, comentarios)
4. Maneja errores con logging
5. Proporciona feedback claro al usuario
6. Usa código async, type hints, y principios SOLID
7. **🚨 ANTES DE FINALIZAR**: Verifica y actualiza `README.md` y `docs/`

### Política de Documentación (CRÍTICO)

**La documentación DEBE estar siempre actualizada.**

Después de CUALQUIER cambio:
- ✅ Verificar si `README.md` refleja el estado actual
- ✅ Revisar qué archivos en `docs/` necesitan actualización
- ✅ Crear/actualizar/eliminar archivos según sea necesario
- ✅ **NUNCA** decir "tarea completada" sin verificar documentación

**Documentación desactualizada es peor que no tener documentación.**

### Filosofía de Diseño

**Comandos**: Simples, descriptivos, intuitivos. Prefiere múltiples comandos dedicados sobre subcomandos complejos.

**Objetivo final**: Crear un juego masivo, funcional, inmersivo y divertido que aproveche las fortalezas únicas de Telegram como plataforma de juego.

---

**Versión**: 1.6
**Última actualización**: 2025-10-04
**Changelog**:
- v1.6 (2025-10-04): Filosofía de diseño de indentación: 4 espacios + guion para listas, títulos en mayúsculas
- v1.5 (2025-10-04): Mejorado mensaje de desconexión automática para incluir instrucción de reconexión
- v1.4 (2025-10-04): Agregado comando /suicidio y documentación completa de comandos (COMMAND_REFERENCE.md)
- v1.3 (2025-10-03): Implementado sistema de pulse global, reemplazando ticker_service
- v1.2 (2025-10-03): Agregado sistema de templates (Jinja2) y guías de outputs consistentes
- v1.1 (2025-10-02): Agregada política obligatoria de documentación actualizada
**Mantenedor**: Proyecto Runegram
- Si hay que reiniciar servicios utilizar "scripts/full_reset.bat" que hace un reinicio general de todos los contenedores.
- **Notificaciones Sociales en Comandos**: Al crear comandos nuevos para Runegram, **SIEMPRE** verificar si es necesario notificar a otros jugadores en la sala usando `broadcaster_service.send_message_to_room()`. Ejemplos:
  - **Movimiento** (`/norte`, `/sur`, etc.): Notifica a la sala de origen que el jugador se fue y a la sala de destino que llegó
  - **Objetos** (`/coger`, `/dejar`): Notifica a la sala que el jugador cogió/dejó un item
  - **Contenedores** (`/meter`, `/sacar`): Notifica la interacción con contenedores
  - **Regla**: Si una acción es visible, debe notificarse a los jugadores presentes (online)