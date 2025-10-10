---
título: "Sistema de Comandos"
categoría: "Sistemas del Motor"
versión: "1.0"
última_actualización: "2025-10-09"
autor: "Proyecto Runegram"
etiquetas: ["comandos", "dispatcher", "command-sets", "telegram"]
documentos_relacionados:
  - "sistemas-del-motor/sistema-de-permisos.md"
  - "creacion-de-contenido/creacion-de-comandos.md"
  - "referencia/referencia-de-comandos.md"
referencias_código:
  - "src/handlers/player/dispatcher.py"
  - "src/services/command_service.py"
  - "commands/command.py"
estado: "actual"
---

# Command System

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
    *   Se obtiene la lista de `CommandSets` base del personaje desde la base de datos.
    *   Se inspecciona el inventario del personaje para añadir `CommandSets` otorgados por objetos.
    *   Se inspecciona la sala actual para añadir `CommandSets` otorgados por la ubicación.
    *   Se comprueba el rol del jugador para añadir sets de administración.
    *   El servicio devuelve una lista unificada de todos los `CommandSets` activos.
5.  **Búsqueda y Ejecución:**
    *   El `dispatcher` itera sobre los nombres de los `CommandSets` activos.
    *   Para cada nombre, busca la lista de comandos correspondiente en el catálogo `COMMAND_SETS`.
    *   Compara los alias (`names`) de cada comando con el comando invocado (`mirar`).
    *   Cuando encuentra una coincidencia, ejecuta el método `.execute()` de esa instancia, pasándole el contexto.

## 3. La Clase `Command` (El Contrato)

Todo comando en el juego hereda de la clase base `Command` (`commands/command.py`). Esta clase define el "contrato" que todos los comandos deben cumplir:

*   `names` (list[str]): Una lista de alias.
*   `description` (str): El texto que se muestra en la lista de comandos de Telegram.
*   `lock` (str): El string de permisos evaluado por el `permission_service`.
*   `execute()` (async method): El método que contiene la lógica del comando.

## 4. Tipos de Comandos Implementados

### Comandos Generales y de Interacción
*   Comandos básicos como `/mirar`, `/decir`, `/ayuda` y `/quien`.
*   El comando `/inventario` (`/inv`) ha sido mejorado. Ahora puede usarse sin argumentos para ver el inventario del personaje, o con un argumento para ver el contenido de un contenedor (ej: `/inv mochila`).
*   Nuevos comandos para contenedores: `/meter <objeto> en <contenedor>` y `/sacar <objeto> de <contenedor>`.

### Generación Dinámica de Comandos
Para sistemas como los canales de chat, se utiliza un patrón de "fábrica":
*   Una clase genérica como `CmdDynamicChannel` define la lógica para "hablar por un canal".
*   Una función `generate_channel_commands()` lee los prototipos de `game_data` y crea una instancia de `CmdDynamicChannel` para cada canal de tipo `CHAT` (ej: `/novato`, `/sistema`).
*   Esta lista de comandos generados se registra como un `CommandSet` más en el `dispatcher`.

## 5. Sincronización con la Interfaz de Telegram

El motor actualiza la lista de comandos visibles en el menú `/` de Telegram en tiempo real.
*   **`command_service.update_telegram_commands(character)`:** Esta función es la responsable de esta tarea.
*   **Triggers:** Se llama en puntos clave donde el contexto del jugador puede cambiar: al entrar al juego, al moverse de sala, o al coger/dejar un objeto.
*   **Funcionamiento:** La función obtiene la lista completa de comandos activos, genera los objetos `BotCommand` y los envía a la API de Telegram usando un `BotCommandScopeChat` para que la actualización solo afecte al jugador específico.

## Ver También

- [Permission System](sistema-de-permisos.md) - Sistema de locks para restricción de comandos
- [Creating Commands](../creacion-de-contenido/creacion-de-comandos.md) - Guía para crear nuevos comandos
- [Command Reference](../referencia/referencia-de-comandos.md) - Referencia completa de comandos
