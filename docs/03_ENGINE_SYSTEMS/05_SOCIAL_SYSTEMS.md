# Sistemas Sociales: Presencia y Canales

Un MUD (Multi-User Dungeon) es, por definición, una experiencia social. Runegram implementa dos sistemas clave que trabajan juntos para crear la sensación de un mundo compartido y vivo: el **Sistema de Presencia** (que gestiona quién está "online") y el **Sistema de Canales** (que gestiona la comunicación global).

## 1. Sistema de Presencia (Online / AFK)

Debido a la naturaleza asíncrona de un bot de Telegram, no existe una "conexión" persistente con el jugador. Por lo tanto, el concepto de "online" se redefine como: **"¿Ha interactuado el jugador con el juego recientemente?"**

Toda esta lógica está encapsulada en `src/services/online_service.py`.

### Arquitectura

*   **Almacenamiento en Redis:** Para una velocidad máxima, el estado de actividad no se guarda en PostgreSQL. Se utiliza Redis para almacenar dos piezas de información por cada personaje:
    1.  `last_seen:<character_id>`: Un timestamp de Unix que registra la última vez que el personaje envió un comando.
    2.  `afk_notified:<character_id>`: Un "flag" o marcador que indica si ya se le ha notificado al jugador que ha entrado en estado AFK.

*   **Umbral de Actividad (`ONLINE_THRESHOLD`):** Una constante (actualmente 5 minutos) que define el tiempo máximo de inactividad antes de que un jugador se considere "offline" o AFK.

### Flujo de Funcionamiento

1.  **Actualización de Actividad (`update_last_seen`):**
    *   En cada mensaje recibido, el `dispatcher` principal llama a esta función.
    *   Actualiza el `timestamp` `last_seen` del personaje en Redis a la hora actual.
    *   Comprueba si existía un `flag` `afk_notified`. Si es así, significa que el jugador estaba AFK y acaba de volver. En este caso, le envía un mensaje privado ("Has vuelto de tu inactividad.") y borra el `flag`.

2.  **Chequeo Periódico de AFK (`check_for_newly_afk_players`):**
    *   El `ticker_service` ejecuta esta tarea global cada 60 segundos.
    *   La tarea mantiene una lista en memoria (`PREVIOUSLY_ONLINE_IDS`) de quién estaba online en el chequeo anterior.
    *   Compara esa lista con quién está online *ahora*.
    *   Cualquier jugador que estuviera en la lista anterior pero no en la actual acaba de pasar a estado AFK.
    *   A estos jugadores recién inactivos, les envía un mensaje privado ("Has entrado en modo de inactividad (AFK).") y establece su `flag` `afk_notified` en Redis para no volver a notificarles.
    *   Finalmente, actualiza `PREVIOUSLY_ONLINE_IDS` para el siguiente ciclo.

Este sistema dual asegura notificaciones de estado AFK precisas y sin spam.

## 2. Sistema de Canales

El Sistema de Canales proporciona un medio para la comunicación global entre jugadores, así como para anuncios del sistema. Está gestionado por `src/services/channel_service.py`.

### Arquitectura "Data-Driven"

*   **Prototipos de Canal (`game_data/channel_prototypes.py`):** Es la "fuente de la verdad". Define todos los canales, su nombre, icono, descripción y, lo más importante, su **tipo** y sus **permisos**.
    *   `"type": "CHAT"`: Indica al sistema que debe generar dinámicamente un comando (ej: `/novato`) para que los jugadores puedan hablar en este canal.
    *   `"lock": "rol(ADMIN)"`: Un `lock string` opcional que se asigna al comando generado, restringiendo quién puede hablar.

*   **Configuración de Usuario (`CharacterSetting`):** La suscripción de un jugador a un canal se almacena en la base de datos, en la columna `active_channels` de su tabla de `character_settings`. Esto hace que sus preferencias sean persistentes.

### Flujo de Funcionamiento

*   **Hablar en un Canal (ej: `/novato ¡hola!`):**
    1.  El `dispatcher` identifica el comando `/novato`, que fue generado dinámicamente por el módulo `dynamic_channels`.
    2.  Se comprueban los `locks` del comando (leídos desde el prototipo del canal).
    3.  `CmdDynamicChannel.execute()` se ejecuta. Llama a `channel_service` para comprobar si el jugador está suscrito al canal "novato".
    4.  Si está suscrito, se llama a `channel_service.broadcast_to_channel()`.
    5.  Esta función recupera de la base de datos a **todos los personajes del juego**.
    6.  Itera sobre ellos, y para cada uno, comprueba si tiene el canal "novato" activo en su configuración.
    7.  Si es así, utiliza el `broadcaster_service` para enviarle el mensaje formateado.

*   **Gestión de Canales:**
    *   `/canales`: Lista todos los prototipos de canal y muestra si el jugador está suscrito a cada uno.
    *   `/activarcanal <nombre>` y `/desactivarcanal <nombre>`: Modifican la lista de `active_channels` en la configuración del personaje en la base de datos.