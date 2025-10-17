---
título: "Índice de Sistemas del Motor"
categoría: "Sistemas del Motor"
audiencia: "desarrollador"
versión: "1.1"
última_actualización: "2025-01-11"
autor: "Proyecto Runegram"
etiquetas: ["índice", "navegación", "motor", "arquitectura"]
documentos_relacionados:
  - "arquitectura/README.md"
  - "creacion-de-contenido/README.md"
referencias_código:
  - "src/services/"
  - "src/models/"
estado: "actual"
importancia: "alta"
---

# Sistemas del Motor

Esta sección documenta los sistemas internos del motor de Runegram. Son los componentes genéricos y reutilizables que conforman la arquitectura del juego.

## ¿Qué es el Motor?

El **motor** es la capa de código en inglés, genérico y abstracto que define los sistemas fundamentales del juego. No conoce la semántica específica (qué es una "espada" o "taberna"), solo maneja estructuras genéricas (`Item`, `Room`, `Character`).

**Principio fundamental**: El motor debe ser reutilizable para cualquier MUD, no solo Runegram.

Ver: [Filosofía del Proyecto](../primeros-pasos/filosofia-central.md)

---

## Documentos Disponibles

### Sistemas Fundamentales

#### 1. [Sistema de Comandos](sistema-de-comandos.md)
**Audiencia**: Desarrolladores de comandos, arquitectos de sistemas
**Contenido**:
- Arquitectura del sistema de comandos
- CommandSets y agrupación de comandos
- Determinación dinámica de comandos disponibles
- Registro y dispatching de comandos
- Integración con menú de Telegram

**Cuándo leer**: Antes de crear nuevos comandos o modificar el sistema de comandos.

---

#### 2. [Sistema de Permisos (Locks)](sistema-de-permisos.md)
**Audiencia**: Desarrolladores de comandos, diseñadores de contenido
**Contenido**:
- Sintaxis de locks (`rol(ADMIN)`, `tiene(llave_oro)`)
- Evaluación de permisos
- Locks en comandos, salidas y objetos
- Roles del sistema (PLAYER, ADMIN, SUPERADMIN)

**Cuándo leer**: Cuando necesites restringir acceso a comandos, salas o items.

---

#### 3. [Sistema de Prototipos](sistema-de-prototipos.md)
**Audiencia**: Desarrolladores, creadores de contenido avanzados
**Contenido**:
- Filosofía de prototipos vs instancias
- Sincronización automática en arranque
- Claves de prototipo (`key`)
- Propagación de cambios a instancias existentes
- Atributos estáticos vs dinámicos

**Cuándo leer**: Para entender cómo funcionan los prototipos internamente.

---

#### 4. [Sistema de Validación](sistema-de-validacion.md)
**Audiencia**: Desarrolladores de servicios, creadores de comandos
**Contenido**:
- Validación de nombres de personajes
- Validación de parámetros de comandos
- Sanitización de inputs
- Mensajes de error consistentes
- Validación de datos de prototipos

**Cuándo leer**: Cuando necesites validar inputs de usuario o datos de configuración.

---

#### 5. [Sistema de Baneos y Apelaciones](sistema-de-baneos.md)
**Audiencia**: Desarrolladores de sistemas, administradores
**Contenido**:
- Baneos temporales y permanentes
- Sistema de apelaciones (una por cuenta)
- Verificación automática de expiración
- Auditoría completa (quién, cuándo, por qué)
- Integración con dispatcher
- Comandos de moderación

**Cuándo leer**: Para entender el sistema de moderación y baneos del juego.

---

### Sistemas de Interacción

#### 6. [Sistema de Canales](sistema-de-canales.md)
**Audiencia**: Desarrolladores, creadores de contenido
**Contenido**:
- Canales estáticos (definidos en prototipos)
- Canales dinámicos (creados por jugadores)
- Suscripción y gestión
- Broadcasting a canales
- Permisos de canales

**Cuándo leer**: Para entender o extender el sistema de comunicación.

---

#### 7. [Sistema de Presencia Online](presencia-en-linea.md)
**Audiencia**: Desarrolladores de comandos, diseñadores de sistemas
**Contenido**:
- Detección de actividad (heartbeat)
- Timeout de inactividad (5 minutos)
- Filtrado de jugadores offline
- Broadcasting solo a jugadores online
- Comando `/desconectar`

**Cuándo leer**: **CRÍTICO** antes de crear comandos que interactúen con otros jugadores.

---

#### 8. [Sistemas Sociales](sistemas-sociales.md)
**Audiencia**: Desarrolladores de comandos de interacción
**Contenido**:
- Comandos sociales (`/decir`, `/susurrar`)
- Broadcasting a salas
- Notificaciones privadas vs públicas
- Integración con sistema de presencia online
- Formato de mensajes sociales

**Cuándo leer**: Cuando crees comandos de comunicación o interacción social.

---

#### 9. [Sistema de Desambiguación de Items](desambiguacion-de-items.md)
**Audiencia**: Desarrolladores de comandos de interacción
**Contenido**:
- Sintaxis ordinal (`1.espada`, `2.espada`)
- Función `find_item_in_list_with_ordinal()`
- Matching de keywords
- Mensajes de error claros
- Ejemplos de uso

**Cuándo leer**: Cuando crees comandos que manipulen objetos (`/coger`, `/soltar`, `/examinar`).

---

### Sistemas Avanzados

#### 10. [Sistema de Scripts](sistema-de-scripts.md)
**Audiencia**: Desarrolladores, creadores de contenido avanzados
**Contenido**:
- Scripts reactivos (`on_look`, `on_get`)
- Scripts proactivos (`tick_scripts`)
- Ejecución de código Python seguro
- Variables disponibles en scripts
- Creación de nuevas funciones de script

**Cuándo leer**: Para agregar comportamientos dinámicos a objetos y salas.

---

#### 10. [Sistema de Scheduling](sistema-de-scheduling.md)
**Audiencia**: Desarrolladores de sistemas, diseñadores de eventos periódicos
**Contenido**:
- Sistema híbrido tick-based + cron-based
- Tick scripts (v1.0 retrocompatible)
- Cron scripts (v2.0 nuevo)
- Escalabilidad optimizada
- Integración con APScheduler

**Cuándo leer**: Para entender el sistema temporal o crear eventos periódicos.

---

#### 11. [Sistema de Eventos](sistema-de-eventos.md)
**Audiencia**: Desarrolladores de sistemas, creadores de contenido avanzados
**Contenido**:
- Event Hub centralizado
- Scripts BEFORE/AFTER con prioridades
- Cancelación de acciones (scripts BEFORE)
- Hooks globales del motor
- Normalización de formatos v1.0 y v2.0

**Cuándo leer**: Para crear scripts reactivos con eventos BEFORE/AFTER.

---

#### 12. [Sistema de Estado](sistema-de-estado.md)
**Audiencia**: Desarrolladores de scripts, creadores de contenido avanzados
**Contenido**:
- Estado persistente (PostgreSQL + JSONB)
- Estado transiente (Redis con TTL)
- Cooldowns y timers
- Contadores y progreso de quests
- Integración con scripts v2.0

**Cuándo leer**: Para scripts que necesitan mantener estado entre ejecuciones.

---

#### 13. [Sistema de Narrativa](sistema-de-narrativa.md)
**Audiencia**: Desarrolladores, creadores de contenido
**Contenido**:
- 41 mensajes evocativos en 6 categorías
- Randomización para variedad
- Tipos de eventos (`item_spawn`, `teleport_arrival`, etc.)
- Integración con broadcasting
- Personalización de mensajes

**Cuándo leer**: Para agregar mensajes narrativos aleatorios a eventos del juego.

---

### Sistemas de Presentación

#### 14. [Sistema de Categorías y Etiquetas](categorias-y-etiquetas.md)
**Audiencia**: Desarrolladores, creadores de contenido
**Contenido**:
- Category (una por objeto)
- Tags (múltiples por objeto)
- Filtrado y búsqueda
- Comandos de listado (`/listarsalas`, `/listaritems`)
- Organización de contenido

**Cuándo leer**: Para organizar y categorizar contenido del juego.

---

#### 15. [Sistema de Botones Inline](botones-en-linea.md)
**Audiencia**: Desarrolladores de UX, creadores de FSM
**Contenido**:
- Botones de navegación en salas
- Flujos FSM (creación de personaje)
- Callback routing
- Integración con Aiogram 2
- Mejores prácticas de UX móvil

**Cuándo leer**: Para crear interfaces de botones en Telegram.

---

## Orden de Lectura Recomendado

### Para Nuevos Desarrolladores

Si eres nuevo en el motor de Runegram, sigue este orden:

1. **Primero**: Lee [Filosofía del Proyecto](../primeros-pasos/filosofia-central.md)
2. **Segundo**: Lee [Configuración del Sistema](../arquitectura/configuracion.md)
3. **Tercero**: Lee [Sistema de Comandos](sistema-de-comandos.md)
4. **Cuarto**: Lee [Sistema de Permisos](sistema-de-permisos.md)
5. **Quinto**: Lee [Sistema de Prototipos](sistema-de-prototipos.md)
6. **Sexto**: Lee [Sistema de Presencia Online](presencia-en-linea.md) - **CRÍTICO**

### Para Desarrolladores de Comandos

Si quieres crear nuevos comandos:

1. Lee [Sistema de Comandos](sistema-de-comandos.md)
2. Lee [Sistema de Permisos](sistema-de-permisos.md)
3. **OBLIGATORIO**: Lee [Sistema de Presencia Online](presencia-en-linea.md)
4. Lee [Sistema de Desambiguación de Items](desambiguacion-de-items.md)
5. Revisa [Creando Comandos](../creacion-de-contenido/creacion-de-comandos.md) (guía práctica)

### Para Administradores de Sistema

Si administras el juego:

1. Lee [Sistema de Permisos](sistema-de-permisos.md)
2. Lee [Sistema de Presencia Online](presencia-en-linea.md)
3. Lee [Sistema de Canales](sistema-de-canales.md)
4. Lee [Sistema de Categorías y Etiquetas](categorias-y-etiquetas.md)
5. Lee [Sistema de Baneos](sistema-de-baneos.md)

### Para Arquitectos de Sistemas

Si quieres extender el motor:

1. Lee [Configuración del Sistema](../arquitectura/configuracion.md)
2. Lee [Sistema de Scripts](sistema-de-scripts.md)
3. Lee [Sistema de Eventos](sistema-de-eventos.md)
4. Lee [Sistema de Scheduling](sistema-de-scheduling.md)
5. Lee [Sistema de Estado](sistema-de-estado.md)
6. Lee [Sistema de Validación](sistema-de-validacion.md)
7. Revisa código fuente en `src/services/`

---

## Convenciones del Motor

### Nomenclatura

Todo el código del motor está en **inglés**:

```python
# ✅ CORRECTO - Motor
class Character(Base):
    pass

class CommandService:
    pass

async def get_character_by_id():
    pass

# ❌ INCORRECTO - Español en motor
class Personaje(Base):
    pass
```

### Separación de Responsabilidades

```
handlers/ → Coordinación (delgado)
    ↓
services/ → Lógica de negocio (grueso)
    ↓
models/ → Persistencia (ORM)
    ↓
database → PostgreSQL
```

### Async/Await Obligatorio

Todo el código del motor es asíncrono:

```python
# ✅ Correcto
async def get_room(session: AsyncSession, room_id: int) -> Optional[Room]:
    result = await session.execute(select(Room).where(Room.id == room_id))
    return result.scalar_one_or_none()

# ❌ Incorrecto - Bloqueante
def get_room(session, room_id):
    return session.query(Room).filter_by(id=room_id).first()
```

### Type Hints Obligatorios

```python
# ✅ Correcto
async def teleport_character(
    session: AsyncSession,
    character: Character,
    destination_key: str
) -> Optional[Room]:
    ...

# ❌ Incorrecto - Sin types
async def teleport_character(session, character, destination_key):
    ...
```

---

## Recursos Importantes

### Código Fuente

Los sistemas documentados aquí están implementados en:

```
src/
├── services/               # Servicios del motor
│   ├── player_service.py
│   ├── command_service.py
│   ├── permission_service.py
│   ├── broadcaster_service.py
│   ├── narrative_service.py
│   ├── scheduler_service.py    # v2.0 (reemplaza pulse_service)
│   ├── event_service.py        # v2.0 (nuevo)
│   ├── state_service.py        # v2.0 (nuevo)
│   ├── online_service.py
│   ├── ban_service.py
│   └── script_service.py       # v2.0 (actualizado)
├── models/                 # Modelos SQLAlchemy
│   ├── account.py
│   ├── character.py
│   ├── room.py
│   ├── item.py
│   ├── exit.py
│   └── channel.py
├── handlers/               # Handlers Aiogram
│   └── player/
│       └── dispatcher.py
└── utils/                  # Utilidades
    ├── presenters.py
    └── helpers.py
```

### Archivos de Configuración

```
gameconfig.toml            # Configuración del juego
alembic/                   # Migraciones de BD
```

---

## Filosofía de Diseño del Motor

### Genérico y Reutilizable

El motor NO debe conocer detalles específicos del juego:

```python
# ✅ Motor - Genérico
class Item(Base):
    """Representa cualquier objeto en el juego."""
    name = Column(String)
    description = Column(Text)
    attributes = Column(JSON)  # Atributos genéricos

# ❌ Motor - Específico del juego
class Item(Base):
    name = Column(String)
    damage = Column(Integer)  # Específico de armas
    armor_value = Column(Integer)  # Específico de armaduras
```

### Extensible por Contenido

Los sistemas del motor deben ser extensibles mediante datos, no código:

```python
# ✅ Extensible - Nuevo comando agregado vía datos
ITEM_PROTOTYPES = {
    "espada_fuego": {
        "grants_command_sets": ["combat"],  # Extiende funcionalidad
        ...
    }
}

# ❌ No extensible - Requiere modificar motor
if item.key == "espada_fuego":
    character.add_command("atacar")
```

---

## Preguntas Frecuentes

### ¿Cuándo modifico el motor vs contenido?

**Modifica motor** si:
- Necesitas un nuevo sistema genérico (ej. sistema de comercio)
- Quieres cambiar cómo funciona algo internamente
- Necesitas agregar funcionalidad reutilizable

**Modifica contenido** si:
- Quieres agregar salas, items o comandos específicos
- Necesitas cambiar descripciones o atributos
- Quieres crear nuevos prototipos

### ¿Cómo agrego un nuevo sistema?

1. Diseña la arquitectura (diagrama, pseudocódigo)
2. Crea servicio en `src/services/`
3. Agrega modelos si necesitas persistencia
4. Integra con handlers existentes
5. **Documenta en `docs/sistemas-del-motor/`**
6. Actualiza `README.md` y `CLAUDE.md`

### ¿Cómo depuro sistemas del motor?

```python
# Logging exhaustivo
import logging

logging.info(f"Character {character.name} executing command {cmd.names[0]}")
logging.exception(f"Error in command execution for {character.name}")
```

```bash
# Ver logs en tiempo real
docker logs -f runegram-bot-1
```

---

## Próximos Pasos

1. **Lee la arquitectura**: [Configuración del Sistema](../arquitectura/configuracion.md)
2. **Explora servicios**: Revisa código en `src/services/`
3. **Estudia modelos**: Revisa `src/models/`
4. **Experimenta**: Crea un nuevo sistema o extiende uno existente
5. **Contribuye**: Mejora la arquitectura del motor

---

**El motor es el corazón de Runegram. Manténlo genérico, robusto y bien documentado.**
