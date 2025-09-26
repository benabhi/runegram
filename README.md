# Runegram MUD

![Python](https://img.shields.io/badge/python-3.11-blue.svg)![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)![PostgreSQL](https://img.shields.io/badge/postgresql-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)

Runegram es un proyecto para crear un juego de rol textual multijugador (MUD - Multi-User Dungeon) que se juega a través de la interacción con un bot de Telegram. Este repositorio contiene una base funcional para una aplicación escalable, con registro de jugadores, un mundo explorable y herramientas de administración.

## Arquitectura y Stack Tecnológico

La arquitectura está diseñada para ser robusta y escalable, utilizando tecnologías modernas:

*   **Lenguaje**: Python 3.11 con `asyncio`.
*   **Framework de Bot**: Aiogram.
*   **Contenerización**: Docker & Docker Compose.
*   **Base de Datos**: PostgreSQL para la persistencia de datos.
*   **Almacenamiento en Memoria**: Redis para gestión de estados de conversación (FSM).
*   **ORM**: SQLAlchemy (Asíncrono) para la interacción con la base de datos.
*   **Migraciones de BD**: Alembic para gestionar la evolución del esquema de la base de datos de forma segura.

## Funcionalidades Implementadas

*   **Entorno Automatizado:** Un script (`entrypoint.sh`) asegura que las migraciones de la base de datos se apliquen automáticamente al iniciar el bot, garantizando consistencia.
*   **Flujo de Jugador Completo:** Registro de cuentas, creación de personajes y persistencia de estado.
*   **Mundo de Juego Básico:**
    *   Sistema de salas (`Rooms`) conectadas por salidas.
    *   Movimiento de jugadores entre salas mediante comandos de texto (ej: `norte`).
    *   Presentación de salas con formato de MUD clásico.
*   **Sistema de Objetos (Items):**
    *   Los objetos pueden existir en el mundo o en el inventario de un personaje.
    *   Comandos `coger` y `dejar` para interactuar con los objetos.
    *   Comando `inventario` para ver los objetos que se llevan.
*   **Herramientas de Administración:**
    *   Sistema de roles (`JUGADOR`, `ADMINISTRADOR`) para control de permisos.
    *   Comandos protegidos para crear y modificar el mundo en tiempo real (`/crearsala`, `/describirsala`, `/conectarsala`, `/teleport`, `/crearitem`).
*   **Arquitectura de Comandos Escalable:**
    *   Los comandos están separados en **Command Sets**, permitiendo agrupar funcionalidades (ej: `general`, `interaction`).
    *   El sistema está preparado para asignar `Command Sets` de forma dinámica basados en el estado, equipo o ubicación del personaje.

## Estructura del Proyecto

La estructura está organizada para separar responsabilidades, facilitando el mantenimiento y la expansión del código.

```
runegram/
├── alembic/              # Migraciones de base de datos de Alembic
├── commands/             # Clases de Comandos (sistema de Command Sets)
├── scripts/              # Scripts de utilidad (ej: full_reset.bat)
├── src/                  # Código fuente principal de la aplicación
│   ├── bot/              # Configuración del bot y dispatcher de Aiogram
│   ├── config.py         # Carga de variables de entorno y configuración
│   ├── db.py             # Configuración del motor de SQLAlchemy
│   ├── handlers/         # Manejadores de Telegram (divididos por rol)
│   ├── models/           # Modelos de datos de SQLAlchemy
│   ├── services/         # Lógica de negocio del juego
│   └── utils/            # Funciones de ayuda (ej: presenters)
├── .env                  # Archivo local para variables de entorno (ignorado por Git)
├── docker-compose.yml    # Orquestación de los contenedores de Docker
├── Dockerfile            # Definición de la imagen Docker para la app
├── entrypoint.sh         # Script de arranque que ejecuta migraciones
├── requirements.txt      # Dependencias de Python
└── run.py                # Punto de entrada para iniciar la aplicación
```

## Puesta en Marcha

Para levantar el proyecto, solo necesitas tener Docker y Docker Compose instalados.

### 1. Configuración del Entorno
Crea un archivo `.env` en la raíz del proyecto a partir del siguiente ejemplo y añade tu token de bot de Telegram:

```env
# .env
BOT_TOKEN=TU_BOT_TOKEN_AQUI
POSTGRES_USER=runegram
POSTGRES_PASSWORD=supersecret
POSTGRES_DB=runegram_db
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0```

### 2. Reinicio y Despliegue
Para asegurar un entorno limpio, se incluye un script que automatiza todo el proceso:

```bash
# En Windows (CMD o PowerShell)
scripts\full_reset.bat
```
Este script detendrá y eliminará los contenedores y volúmenes antiguos, reconstruirá la imagen del bot, levantará todos los servicios y aplicará las migraciones de la base de datos automáticamente.

### 3. Jugar
Una vez que los contenedores estén en funcionamiento, simplemente abre Telegram y envía `/start` a tu bot.

---

## Próximos Pasos y Tareas Pendientes (TODO)

Esta sección documenta las próximas mejoras y problemas conocidos a resolver para alcanzar la siguiente versión del Producto Mínimo Viable.

### ❗ **Bugs y Mejoras de Calidad de Vida**

*   **Las salas no muestran los objetos caídos:**
    *   **Problema:** La función `format_room` en el `presenter` fue actualizada para mostrar objetos, pero la estrategia de carga `selectinload` en `player_service` no se actualizó para cargar `room.items`.
    *   **Solución:** Modificar la `load_strategy` en `get_or_create_account` para que precargue `Account -> Character -> Room -> Items`.

*   **No se actualizan ambos extremos de las salidas:**
    *   **Problema:** El comando `/conectarsala norte a 2` crea una salida de la sala 1 a la 2, pero no crea automáticamente una salida "sur" de la sala 2 a la 1. Esto hace que la construcción del mundo sea tediosa y propensa a errores.
    *   **Solución:** Mejorar el servicio `world_service.link_rooms` para que acepte un argumento opcional (`--bidireccional` o similar) y que, si está presente, cree automáticamente la salida de vuelta (ej: norte <-> sur, este <-> oeste, etc.).

### 🚀 **Próximas Grandes Funcionalidades**

*   **¿Cómo se determina qué comandos le corresponde a quién?**
    *   **Problema:** Actualmente, todos los jugadores tienen los `Command Sets` "general" e "interaction" hardcodeados en el parser.
    *   **Solución:**
        1.  Refactorizar el `text_handler` para que lea la lista de `command_sets` desde el objeto `character.command_sets` de la base de datos.
        2.  Implementar la lógica para añadir sets dinámicos basados en la sala (`room.grants_command_set`) o el equipo.
        3.  Crear comandos de admin (`/addcmdset`, `/remcmdset`) para modificar los sets base de un jugador.

*   **Implementar el Sistema de Locks:**
    *   **Tarea:** Expandir el `permission_service` para que pueda parsear un string de `lock` más complejo (ej: `"tiene_objeto(llave) y habilidad(forzar_cerraduras) > 25"`).
    *   **Aplicación:** Integrar la verificación de `locks` en acciones clave como el movimiento entre salas (usando `room.locks`) o el uso de objetos (`item.locks`).

*   **Broadcasting de Mensajes:**
    *   **Tarea:** El comando `decir` actualmente solo responde al que habla. Se debe implementar un sistema (en `broadcaster.py`) que tome el mensaje y lo envíe a todos los demás jugadores que se encuentren en la misma sala.
