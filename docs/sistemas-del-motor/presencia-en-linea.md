---
título: "Sistema de Presencia en Línea"
categoría: "Sistemas del Motor"
versión: "1.1"
última_actualización: "2025-10-09"
autor: "Proyecto Runegram"
etiquetas: ["online", "presencia", "redis", "social", "afk"]
documentos_relacionados:
  - "broadcaster-service.md"
  - "sistema-de-canales.md"
  - "../arquitectura/configuracion.md"
referencias_código:
  - "src/services/online_service.py"
  - "gameconfig.toml"
estado: "actual"
---

# Sistema de Presencia (Online / Offline)

Debido a la naturaleza asíncrona de un bot de Telegram, no existe una "conexión" persistente con el jugador. Por lo tanto, el concepto de "online" se redefine como: **"¿Ha interactuado el jugador con el juego recientemente?"**

Toda esta lógica está encapsulada en `src/services/online_service.py`.

## Arquitectura

*   **Almacenamiento en Redis:** Para una velocidad máxima, el estado de actividad no se guarda en PostgreSQL. Se utiliza Redis para almacenar dos piezas de información por cada personaje:
    1.  `last_seen:<character_id>`: Un timestamp de Unix que registra la última vez que el personaje envió un comando.
    2.  `offline_notified:<character_id>`: Un "flag" o marcador que indica si ya se le ha notificado al jugador que se ha desconectado por inactividad.

*   **Umbral de Actividad:** El tiempo máximo de inactividad antes de que un jugador se considere desconectado (offline). Este valor se configura en `gameconfig.toml` bajo `[online] threshold_minutes` (por defecto: 5 minutos).

## Flujo de Funcionamiento

### 1. Actualización de Actividad (`update_last_seen`)

*   En cada mensaje recibido, el `dispatcher` principal llama a esta función.
*   Actualiza el `timestamp` `last_seen` del personaje en Redis a la hora actual.
*   Comprueba si existía un `flag` `offline_notified`. Si es así, significa que el jugador estaba desconectado y acaba de volver. En este caso, le envía un mensaje privado ("Te has reconectado al juego.") y borra el `flag`.

### 2. Chequeo Periódico de Desconexiones (`check_for_newly_offline_players`)

*   El sistema de pulse ejecuta esta tarea global cada 60 segundos.
*   La tarea mantiene una lista en memoria (`PREVIOUSLY_ONLINE_IDS`) de quién estaba online en el chequeo anterior.
*   Compara esa lista con quién está online *ahora*.
*   Cualquier jugador que estuviera en la lista anterior pero no en la actual se ha desconectado por inactividad.
*   A estos jugadores recién desconectados, les envía un mensaje privado ("Te has desconectado del juego por inactividad. Vuelve cuando quieras con cualquier comando.") y establece su `flag` `offline_notified` en Redis para no volver a notificarles.
*   Finalmente, actualiza `PREVIOUSLY_ONLINE_IDS` para el siguiente ciclo.

Este sistema dual asegura notificaciones de estado online/offline precisas y sin spam.

## Desconexión Manual

Los jugadores pueden desconectarse manualmente del juego en cualquier momento usando el comando `/desconectar` (también disponible como `/salir` o `/logout`).

**Comportamiento:**
1. Elimina la clave `last_seen` del jugador en Redis
2. Establece la clave `offline_notified` para marcar la desconexión
3. El sistema considera al jugador como desconectado inmediatamente
4. Cuando el jugador vuelva con cualquier comando, recibirá el mensaje: "Te has reconectado al juego."

## Sistema AFK (Away From Keyboard)

**Comando:** `/afk [mensaje]`

Los jugadores pueden marcarse explícitamente como AFK con un mensaje opcional:

```
/afk comiendo
/afk vuelvo en 10 minutos
```

**Comportamiento:**
- El estado AFK se almacena en Redis con TTL de 24 horas
- El jugador se marca como offline inmediatamente (sin esperar 5 minutos)
- El mensaje AFK es visible en `/quien` con emoji 💤
- El estado AFK se elimina automáticamente al usar cualquier comando

**Diferencia con desconexión por inactividad:**
- **AFK manual:** Inmediato y visible para otros jugadores
- **Inactividad:** Después de 5 minutos sin comandos, sin mensaje personalizado

## Política de Jugadores Desconectados en el Juego

**IMPORTANTE:** Los jugadores desconectados (offline) son tratados como **ausentes del mundo del juego**. Esto es fundamental para mantener la coherencia de la experiencia de juego en un MUD.

### Principio Fundamental

Cuando un jugador está desconectado (inactivo por más de 5 minutos o desconectado manualmente), **desde el punto de vista del juego, ese jugador no está presente**, aunque técnicamente su personaje permanezca en la base de datos en una sala específica.

### Comportamiento del Sistema

Todos los comandos y sistemas del motor **deben ignorar** a los jugadores desconectados:

**✅ Sistemas que filtran jugadores desconectados:**

1. **Visualización de Salas (`/mirar`)**: No muestra personajes desconectados en la lista de "Personajes"
2. **Listado de Personajes (`/personajes`)**: Solo muestra jugadores activos (online)
3. **Mirar Personajes (`/mirar <jugador>`)**: No permite ver la descripción de un jugador desconectado
4. **Susurrar (`/susurrar`)**: No permite enviar mensajes a jugadores desconectados
5. **Decir (`/decir`)**: No envía mensajes a jugadores desconectados en la sala
6. **Broadcasting de Sala**: `broadcaster_service.send_message_to_room()` excluye automáticamente jugadores desconectados
7. **Comandos de Admin**: Deberían respetar esta regla en comandos de interacción

**⚠️ Excepciones (sistemas que SÍ incluyen desconectados):**

- **Lista de Jugadores Globales (`/quien`)**: Muestra solo jugadores online (usa `online_service.get_online_characters()`)
- **Scripts del sistema**: Pueden necesitar acceder a personajes desconectados para limpieza o mantenimiento
- **Comandos de diagnóstico de admin**: Pueden mostrar todos los personajes sin filtrar para debugging

### Implementación Técnica

Para verificar si un personaje está activo (online), usar:

```python
from src.services import online_service

# En un comando o servicio
is_active = await online_service.is_character_online(character.id)
if not is_active:
    # El jugador está desconectado, no interactuar con él
    await message.answer("No ves a nadie con ese nombre por aquí.")
    return
```

### Consideraciones Futuras

En sistemas futuros (como combate), será importante definir reglas adicionales:

- ¿Puede un jugador desconectarse durante un combate?
- ¿Debe el sistema cancelar combates si un jugador se desconecta?
- ¿Cómo afecta la desconexión a efectos temporales (buffs, debuffs)?

Estas reglas deberán definirse en la documentación de cada sistema específico.

## Configuración

En `gameconfig.toml`:

```toml
[online]
threshold_minutes = 5              # Minutos de inactividad antes de marcar offline
last_seen_ttl_days = 7             # TTL en Redis para timestamps
offline_notified_ttl_days = 1      # TTL en Redis para flags
```

Ver [Configuration System](../arquitectura/configuracion.md) para más detalles.

## API del Online Service

### Funciones Principales

```python
from src.services import online_service

# Verificar si un personaje está online
is_online = await online_service.is_character_online(character_id)

# Obtener lista de IDs de personajes online
online_ids = await online_service.get_online_character_ids()

# Obtener objetos Character online (con sesión DB)
online_characters = await online_service.get_online_characters(session)

# Actualizar último visto (se llama automáticamente en dispatcher)
await online_service.update_last_seen(character_id, bot)

# Desconectar manualmente
await online_service.disconnect_character(character_id, bot)
```

---

## Próximos Pasos

- Consulta [Broadcaster Service](broadcaster-service.md) para entender cómo se envían mensajes a jugadores online
- Lee [Channels System](sistema-de-canales.md) para comunicación global
- Explora [Configuration System](../arquitectura/configuracion.md) para ajustar umbrales

---

**Changelog:**
- v1.1 (2025-10-09): Migrado a nueva estructura, agregado sistema AFK, actualizado con YAML frontmatter
- v1.0 (2025-01-09): Versión original como parte de SOCIAL_SYSTEMS.md
