# Sistema de Comandos

El Sistema de Comandos es el corazón de la interacción del jugador con el mundo de Runegram. Está diseñado para ser robusto, extensible y, sobre todo, dinámico. Esta documentación desglosa su arquitectura, desde la estructura de un comando individual hasta cómo el sistema decide qué comandos están disponibles para un jugador en un momento dado.

## 1. Arquitectura General

El sistema se basa en tres componentes principales que trabajan en conjunto:

1.  **El Dispatcher Principal (`dispatcher.py`):** Un único manejador de Aiogram que actúa como el "cerebro" central. Intercepta todos los mensajes de texto y orquesta el proceso de identificación y ejecución del comando.
2.  **El Catálogo de Comandos (`COMMAND_SETS`):** Un diccionario global en el `dispatcher` que contiene una instancia de cada comando disponible en todo el juego, agrupados por funcionalidad en `CommandSets`.
3.  **El Servicio de Comandos (`command_service.py`):** La lógica de negocio que determina, en tiempo real, qué `CommandSets` están activos para un personaje según su contexto (rol, inventario, ubicación).

## 2. El Flujo de Ejecución de un Comando

Cuando un jugador envía un mensaje como `/mirar espada`, ocurre el siguiente flujo:

1.  **Intercepción:** El `main_command_dispatcher` recibe el objeto de mensaje de Aiogram.
2.  **Contextualización:** Se obtiene la `Account` y el `Character` del jugador desde la base de datos.
3.  **Determinación de Comandos Activos:** El `dispatcher` llama a `command_service.get_active_command_sets_for_character(character)`.
4.  **Construcción Dinámica (en `command_service`):**
    *   Se obtiene la lista de `CommandSets` base del personaje desde la base de datos (ej: `["general", "movement", ...]`).
    *   Se inspecciona el inventario del personaje. Si un objeto tiene la propiedad `"grants_command_sets": ["thievery"]`, el set `"thievery"` se añade a la lista.
    *   Se inspecciona la sala actual. Si su prototipo otorga un `CommandSet`, también se añade.
    *   Se comprueba el rol del jugador. Si es `ADMIN` o `SUPERADMIN`, se añaden los sets de administración correspondientes.
    *   El servicio devuelve una lista unificada de todos los `CommandSets` activos para ese jugador en ese preciso instante.
5.  **Búsqueda y Ejecución:**
    *   El `dispatcher` itera sobre los nombres de los `CommandSets` activos.
    *   Para cada nombre, busca la lista de comandos correspondiente en el catálogo `COMMAND_SETS`.
    *   Compara los alias (`names`) de cada comando con el comando invocado (`mirar`).
    *   Cuando encuentra una coincidencia, ejecuta el método `.execute()` de esa instancia de comando, pasándole el contexto (personaje, sesión, mensaje).

## 3. La Clase `Command` (El Contrato)

Todo comando en el juego hereda de la clase base `Command` (`commands/command.py`). Esta clase define el "contrato" que todos los comandos deben cumplir:

*   `names` (list[str]): Una lista de alias. El primero es el nombre principal.
*   `description` (str): El texto que se muestra en la lista de comandos de Telegram.
*   `lock` (str): El string de permisos evaluado por el `permission_service`.
*   `execute()` (async method): El método que contiene la lógica del comando.

## 4. Generación Dinámica de Comandos

Para sistemas como los canales de chat, no es práctico crear una clase por cada comando (`CmdNovato`, `CmdComercio`, etc.). En su lugar, se utiliza un patrón de "fábrica":

*   **Clase Genérica:** Una clase como `CmdDynamicChannel` define la lógica para "hablar por un canal".
*   **Función Fábrica:** Una función como `generate_channel_commands()` en `commands/player/dynamic_channels.py` lee los prototipos de `game_data` (ej: `channel_prototypes.py`).
*   **Instanciación:** Por cada canal de tipo `CHAT` que encuentra, crea una instancia de `CmdDynamicChannel`, le asigna el nombre y la descripción correspondientes, y la añade a una lista.
*   **Exportación:** Esta lista (`DYNAMIC_CHANNEL_COMMANDS`) se exporta y se registra en el `dispatcher` como un `CommandSet` más.

Este enfoque asegura que el contenido del juego (los canales) y la interfaz (los comandos para usarlos) estén siempre sincronizados, cumpliendo con la filosofía "Data-Driven".

## 5. Sincronización con la Interfaz de Telegram

Para proporcionar una experiencia de usuario fluida, el motor actualiza la lista de comandos visibles en el menú `/` de Telegram.

*   **`command_service.update_telegram_commands(character)`:** Esta función es la responsable de esta tarea.
*   **Triggers:** Se llama en puntos clave donde el contexto del jugador puede cambiar:
    *   Al entrar al juego (`/start`).
    *   Después de moverse a una nueva sala.
    *   Después de coger o dejar un objeto que podría otorgar un `CommandSet`.
*   **Funcionamiento:** La función obtiene la lista completa de comandos activos, genera los objetos `BotCommand` que la API de Telegram requiere y los envía usando un `BotCommandScopeChat` para que la actualización solo afecte a ese jugador específico.