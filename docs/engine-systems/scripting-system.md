---
título: "Sistema de Scripts"
categoría: "Sistemas del Motor"
versión: "1.0"
última_actualización: "2025-10-09"
autor: "Proyecto Runegram"
etiquetas: ["scripts", "eventos", "tick-scripts", "automatización"]
documentos_relacionados:
  - "engine-systems/pulse-system.md"
  - "engine-systems/prototype-system.md"
  - "content-creation/writing-scripts.md"
referencias_código:
  - "src/services/script_service.py"
  - "src/services/pulse_service.py"
estado: "actual"
---

# Scripting System

El Motor de Scripts es el sistema que permite que el **Contenido** del juego (definido en `game_data`) pueda ejecutar **Lógica** del juego (definida en el `src/services`). Es el mecanismo que da comportamiento a los objetos y al mundo.

El motor tiene una arquitectura dual, separando las acciones que son una **reacción** a algo que hace el jugador (Eventos) de las acciones que ocurren de forma **proactiva** con el tiempo (Tick Scripts). Toda la lógica está centralizada en `src/services/script_service.py`.

## 1. El `script_service`

Este servicio actúa como un "traductor" e "invocador" seguro. Su funcionamiento es análogo al del `permission_service`:

1.  **Registro de Funciones (`SCRIPT_REGISTRY`):** Es un diccionario que mapea nombres de script (en formato string, ej: `"script_espada_susurra_secreto"`) a las funciones de Python reales que contienen la lógica.
2.  **Parser de Scripts (`_parse_script_string`):** Una función simple que toma un string como `"nombre_script(arg1=valor1)"` y lo descompone en el nombre de la función y un diccionario de argumentos.
3.  **Ejecutor (`execute_script`):** Es el corazón del servicio. Recibe un `script_string` y un `contexto` (que contiene los objetos relevantes como `character`, `target`, `room`), busca la función en el registro y la ejecuta de forma segura, pasándole el contexto y los argumentos.

## 2. Scripts Reactivos (Eventos)

Estos scripts se ejecutan como respuesta directa a una acción del jugador.

*   **Definición:** Se definen en la clave `"scripts"` de un prototipo. La clave del diccionario es el nombre del evento (el "trigger") y el valor es el `script_string`.

    ```python
    # En game_data/item_prototypes.py
    "espada_viviente": {
        "scripts": {
            "on_look": "script_notificar_brillo_magico(color=rojo)"
        }
    }
    ```

*   **Flujo de Ejecución (Ejemplo: `/mirar espada`):**
    1.  El jugador ejecuta el comando `/mirar`.
    2.  La lógica de `CmdLook.execute()` encuentra el objeto `Item` de la espada.
    3.  Después de mostrar la descripción, el comando comprueba si el prototipo del objeto tiene una clave `"on_look"` dentro de `"scripts"`.
    4.  Si la encuentra, llama a `script_service.execute_script()` pasándole el `script_string` `"script_notificar_brillo_magico(color=rojo)"` y el contexto (`character` y `target`).
    5.  El `script_service` parsea el string, encuentra `script_notificar_brillo_magico` en su registro y la ejecuta.

Actualmente, el único evento implementado es `on_look`, pero la arquitectura permite añadir fácilmente nuevos "triggers" en otros comandos (`on_get`, `on_drop`, `on_enter_room`, etc.).

## 3. Scripts Proactivos (Tick Scripts)

Estos scripts se ejecutan de forma programada basándose en el sistema de pulse global, haciendo que el mundo se sienta vivo incluso cuando los jugadores no hacen nada. Están gestionados por el `pulse_service`.

*   **Definición:** Se definen como una lista en la clave `"tick_scripts"` de un prototipo. Cada elemento es un diccionario que define cuándo y cómo se ejecuta el script.

    ```python
    # En game_data/item_prototypes.py
    "espada_viviente": {
        "tick_scripts": [{
            "interval_ticks": 60,  # Cada 60 ticks (120 segundos con tick=2s)
            "script": "script_espada_susurra_secreto",
            "category": "ambient",
            "permanent": True  # Se repite indefinidamente
        }]
    }
    ```

*   **Flujo de Ejecución:**
    1.  **Arranque del Bot:** El `pulse_service` inicia un job global que se ejecuta cada 2 segundos (el "pulse").
    2.  **Cada Pulse:** El sistema procesa TODAS las entidades con `tick_scripts` y determina cuáles deben ejecutarse en el tick actual.
    3.  **Creación de Entidad:** Cuando se crea un nuevo objeto (`/generarobjeto`), **NO** requiere registro especial - el pulse lo detecta automáticamente en el siguiente tick.
    4.  **Verificación de Intervalo:** Para cada tick_script, se verifica si han pasado suficientes ticks desde la última ejecución (`current_tick - last_executed_tick >= interval_ticks`).
    5.  **Contextualización y Filtrado (en `pulse_service`):**
        *   Se recupera la entidad (la espada) y su ubicación (la sala, o la sala del personaje que la lleva).
        *   Se obtienen todos los personajes en esa sala.
        *   Se itera sobre cada personaje y se comprueba si está "online" (`online_service`). Si el tick_script es de categoría `"ambient"` y el jugador está inactivo, se le ignora.
    6.  **Ejecución Final:** Por cada personaje que pasa el filtro, se llama a `script_service.execute_script()` con el `script_string` y el contexto (`target`, `room`, y el `character` específico que va a recibir el efecto).
    7.  **Tracking:** El sistema actualiza `item.tick_data` con el tick actual y marca el script como ejecutado.

**Ventajas sobre el sistema antiguo de tickers:**
- ✅ Escalable: Un solo job procesa todas las entidades
- ✅ Sincronizado: Todos los scripts operan en la misma timeline
- ✅ Simple: "60 ticks" es más claro que `*/2 * * * *`
- ✅ Flexible: Soporta scripts one-shot (`permanent: False`)

Ver: [Pulse System](pulse-system.md) para más detalles.

## 4. Cómo Crear una Nueva "Habilidad" de Script

Para dar a los diseñadores de contenido una nueva herramienta (ej: un script que haga que un objeto se mueva a una sala aleatoria), un desarrollador del motor debe seguir estos pasos:

1.  **Escribir la Lógica:** Añadir una nueva función `async` en `src/services/script_service.py`. Debe aceptar `session` y `**context` como argumentos.
    ```python
    async def script_teleport_aleatorio(session: AsyncSession, target: Item, **kwargs):
        # Lógica para encontrar una sala aleatoria y mover el 'target' (el objeto).
        # ...
        await broadcaster_service.send_message_to_room(...)
    ```
2.  **Registrar la Función:** Añadir la nueva función y su nombre en string al diccionario `SCRIPT_REGISTRY`.
    ```python
    SCRIPT_REGISTRY = {
        # ...
        "script_teleport_aleatorio": script_teleport_aleatorio,
    }
    ```
3.  **Documentar para Diseñadores:** ¡Listo! Ahora un diseñador puede usar `"script": "script_teleport_aleatorio"` en un `tick_script` o en un `evento` para hacer que los objetos se teletransporten.

## Ver También

- [Pulse System](pulse-system.md) - Sistema de ticks global
- [Writing Scripts](../content-creation/writing-scripts.md) - Guía para crear scripts
- [Prototype System](prototype-system.md) - Usar scripts en prototipos
