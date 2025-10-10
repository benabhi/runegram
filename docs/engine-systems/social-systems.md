---
título: "Sistemas de Interacción Social"
categoría: "Sistemas del Motor"
versión: "1.0"
última_actualización: "2025-10-09"
autor: "Proyecto Runegram"
etiquetas: ["social", "interacción", "broadcast", "presencia", "online"]
documentos_relacionados:
  - "engine-systems/online-presence.md"
  - "engine-systems/channels-system.md"
  - "engine-systems/broadcaster-service.md"
referencias_código:
  - "src/services/online_service.py"
  - "src/services/broadcaster_service.py"
  - "src/utils/presenters.py"
  - "commands/player/general.py"
estado: "actual"
---

# Social Interaction Systems

Un MUD (Multi-User Dungeon) es, por definición, una experiencia social. Runegram implementa sistemas que trabajan juntos para crear la sensación de un mundo compartido y vivo donde los jugadores pueden ver e interactuar con otros.

## 1. Sistema de Presencia (Online/Offline)

Debido a la naturaleza asíncrona de un bot de Telegram, no existe una "conexión" persistente con el jugador. Por lo tanto, el concepto de "online" se redefine como: **"¿Ha interactuado el jugador con el juego recientemente?"**

Toda esta lógica está encapsulada en `src/services/online_service.py`.

### Arquitectura

*   **Almacenamiento en Redis:** Para una velocidad máxima, el estado de actividad no se guarda en PostgreSQL. Se utiliza Redis para almacenar dos piezas de información por cada personaje:
    1.  `last_seen:<character_id>`: Un timestamp de Unix que registra la última vez que el personaje envió un comando.
    2.  `offline_notified:<character_id>`: Un "flag" o marcador que indica si ya se le ha notificado al jugador que se ha desconectado por inactividad.

*   **Umbral de Actividad:** El tiempo máximo de inactividad antes de que un jugador se considere desconectado (offline). Este valor se configura en `gameconfig.toml` bajo `[online] threshold_minutes` (por defecto: 5 minutos).

### Flujo de Funcionamiento

1.  **Actualización de Actividad (`update_last_seen`):**
    *   En cada mensaje recibido, el `dispatcher` principal llama a esta función.
    *   Actualiza el `timestamp` `last_seen` del personaje en Redis a la hora actual.
    *   Comprueba si existía un `flag` `offline_notified`. Si es así, significa que el jugador estaba desconectado y acaba de volver. En este caso, le envía un mensaje privado ("Te has reconectado al juego.") y borra el `flag`.

2.  **Chequeo Periódico de Desconexiones (`check_for_newly_offline_players`):**
    *   El sistema de pulse ejecuta esta tarea global cada 60 segundos.
    *   La tarea mantiene una lista en memoria (`PREVIOUSLY_ONLINE_IDS`) de quién estaba online en el chequeo anterior.
    *   Compara esa lista con quién está online *ahora*.
    *   Cualquier jugador que estuviera en la lista anterior pero no en la actual se ha desconectado por inactividad.
    *   A estos jugadores recién desconectados, les envía un mensaje privado ("Te has desconectado del juego por inactividad. Vuelve cuando quieras con cualquier comando.") y establece su `flag` `offline_notified` en Redis para no volver a notificarles.
    *   Finalmente, actualiza `PREVIOUSLY_ONLINE_IDS` para el siguiente ciclo.

Este sistema dual asegura notificaciones de estado online/offline precisas y sin spam.

### Desconexión Manual

Los jugadores pueden desconectarse manualmente del juego en cualquier momento usando el comando `/desconectar` (también disponible como `/salir` o `/logout`).

**Comportamiento:**
1. Elimina la clave `last_seen` del jugador en Redis
2. Establece la clave `offline_notified` para marcar la desconexión
3. El sistema considera al jugador como desconectado inmediatamente
4. Cuando el jugador vuelva con cualquier comando, recibirá el mensaje: "Te has reconectado al juego."

### Política de Jugadores Desconectados

**IMPORTANTE:** Los jugadores desconectados (offline) son tratados como **ausentes del mundo del juego**. Esto es fundamental para mantener la coherencia de la experiencia de juego en un MUD.

#### Principio Fundamental

Cuando un jugador está desconectado (inactivo por más de 5 minutos o desconectado manualmente), **desde el punto de vista del juego, ese jugador no está presente**, aunque técnicamente su personaje permanezca en la base de datos en una sala específica.

#### Comportamiento del Sistema

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

#### Implementación Técnica

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

## 2. Visualización de Personajes

**Implementado en:** `src/utils/presenters.py:format_room()`

Cuando un jugador mira una sala (usando `/mirar` sin argumentos), el sistema:

1. Obtiene todos los personajes presentes en la sala desde la relación `room.characters`
2. **Filtra jugadores desconectados** usando `online_service.is_character_online()` (solo muestra jugadores online)
3. Filtra al personaje que está mirando para no mostrarse a sí mismo
4. Muestra una línea adicional: **"Personajes:"** con los nombres de otros jugadores activos

**Ejemplo de salida:**
```
El Limbo
Te encuentras en una habitación vacía...

También están aquí: Juan, María.

Salidas: [ Norte ]
```

**Beneficios:**
- Los jugadores saben inmediatamente quién comparte su ubicación
- Facilita la interacción social espontánea
- Fomenta el roleplay y la comunicación

## 3. Mensajes Sociales (Broadcast de Acciones)

**Implementado en:** `src/services/broadcaster_service.py`

El motor utiliza el `broadcaster_service.send_message_to_room()` para notificar a todos los jugadores **activos** en una sala cuando alguien realiza una acción visible.

**IMPORTANTE:** El sistema automáticamente **excluye jugadores offline** del broadcasting. Solo los jugadores activamente jugando reciben estos mensajes.

**Comandos con mensajes sociales:**

| Comando | Mensaje a la Sala |
|---------|-------------------|
| `/norte`, `/sur`, etc. (movimiento) | **Sala de origen:** *"[Jugador] se ha ido hacia el [dirección]."*<br>**Sala de destino:** *"[Jugador] ha llegado desde el [dirección_opuesta]."* |
| `/coger <objeto>` | *"[Jugador] ha cogido [objeto] del suelo."* |
| `/dejar <objeto>` | *"[Jugador] ha dejado [objeto] en el suelo."* |
| `/meter <objeto> en <contenedor>` | *"[Jugador] guarda [objeto] en [contenedor]."* |
| `/sacar <objeto> de <contenedor>` | *"[Jugador] saca [objeto] de [contenedor]."* |
| `/generarobjeto <key>` (admin) | *"[Objeto] aparece de la nada."* |

**Formato:** Los mensajes se envían en itálicas (`<i>`) para distinguirlos visualmente de mensajes de sistema o diálogos.

**Parámetro `exclude_character_id`:** Permite excluir al jugador que realiza la acción del broadcast, para evitar mensajes redundantes.

## 4. Comunicación Local: Comando `/susurrar`

**Implementado en:** `commands/player/general.py:CmdWhisper`

El comando `/susurrar` permite enviar mensajes privados a un jugador específico que se encuentre en la **misma sala** y esté **activamente jugando**.

**Uso:** `/susurrar <jugador> <mensaje>`

**Ejemplo:**
```
> /susurrar María Hola, ¿quieres explorar juntos?

Le susurras a María: "Hola, ¿quieres explorar juntos?"
```

María recibe:
```
Juan te susurra: "Hola, ¿quieres explorar juntos?"
```

**Validaciones:**
- El jugador objetivo debe estar presente en la sala
- **El jugador objetivo NO debe estar offline** (inactivo)
- Si no se encuentra o está offline, se muestra: "No ves a ningún '[nombre]' por aquí."

**Diferencia con `/decir`:**
- `/decir`: Todos en la sala escuchan
- `/susurrar`: Solo el jugador objetivo recibe el mensaje

## 5. Visualización de Contenedores

**Implementado en:** `src/utils/presenters.py:format_room()` y comandos `/mirar`, `/inventario`

El sistema muestra **cuántos items contiene un contenedor** para mejorar la información al jugador.

**En la sala:**
```
Ves aquí: una mochila de cuero (5 items), una espada viviente.
```

**En el inventario:**
```
Llevas lo siguiente:
 - una mochila de cuero (5 items)
 - una poción de vida menor
```

**Al mirar un contenedor:**
```
> /mirar mochila

Una mochila simple pero resistente...

Contiene:
 - una poción de vida menor (3)
 - una llave oxidada
```

**Lógica:**
- El sistema verifica si `item.prototype.get("is_container")` es `True`
- Carga la relación `item.contained_items` mediante `session.refresh()`
- Muestra `(X items)` o `(X item)` según la cantidad
- Si está vacío, muestra: **"Está vacío."**

## Ver También

- [Online Presence System](online-presence.md) - Detalles del sistema de presencia
- [Channels System](channels-system.md) - Comunicación global
- [Broadcaster Service](broadcaster-service.md) - Sistema de mensajería a salas
