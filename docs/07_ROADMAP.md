# Visión a Futuro y Roadmap de Runegram

Este documento describe la visión a largo plazo para el desarrollo de Runegram y enumera las próximas grandes funcionalidades y mejoras planificadas. Actúa como una hoja de ruta para evolucionar desde el motor de juego actual hacia una experiencia MUD completa y rica.

## Visión General

El objetivo es transformar Runegram en un MUD social y dinámico con sistemas de juego profundos, incluyendo combate, progresión de habilidades, crafteo y quests. La arquitectura actual, basada en la separación de Motor y Contenido, está diseñada para facilitar la implementación de estas características de manera modular y escalable.

---

## 🚀 Próximas Grandes Funcionalidades

Estas son las características de alto impacto que definirán la siguiente etapa del juego.

### 1. Sistema de Combate y Habilidades
*   **Visión:** Crear un sistema de combate táctico por turnos y una progresión de habilidades basada en la mecánica de "aprender haciendo" (d100).
*   **Tareas:**
    1.  **Modelos de Datos:** Crear las tablas `skills` y `character_skills` en la base de datos. Añadir atributos de combate (ej: `current_hp`, `max_hp`, `current_mana`, `max_mana`) al modelo `Character`.
    2.  **Mecánica d100:** Implementar en un `skill_service` la lógica central de resolución de acciones: una acción tiene éxito si `d100 <= nivel_de_habilidad`. El éxito otorga experiencia en esa habilidad.
    3.  **PNJs (Personajes No Jugadores):**
        *   Crear un archivo `game_data/npc_prototypes.py` y un modelo `NPC` en la base de datos.
        *   Desarrollar un `npc_service` para gestionar el "spawn" (aparición), el "despawn" (desaparición) y la IA básica (ej: agresivo, pasivo, patrulla).
        *   Implementar un sistema de "respawn" para que los monstruos vuelvan a aparecer después de un tiempo.
    4.  **Comandos de Combate:** Crear el `CommandSet` de `combat` con comandos como `/atacar [objetivo]`, `/huir`, `/lanzar [hechizo] [objetivo]`, etc.

### 2. Sistema de Interacción Social
*   **Visión:** Hacer que el mundo se sienta verdaderamente multijugador, donde las acciones de un jugador son visibles y tienen un impacto en los demás.
*   **Tareas:**
    1.  **Refactorizar `/decir`:** Modificar el comando para que use `broadcaster_service.send_message_to_room`, de modo que todos los jugadores *online* en la misma sala vean el mensaje.
    2.  **Notificaciones de Movimiento:** Implementar mensajes de "entrada/salida" en el `CmdMove`. Cuando un jugador se mueve, los jugadores en la sala de origen y de destino deben ser notificados.
    3.  **Notificaciones de Acción:** Modificar comandos como `/coger` y `/dejar` para que notifiquen a la sala sobre la acción (ej: "Benabhi coge una espada viviente.").
    4.  **Expandir `/mirar`:** Mejorar el comando para que pueda `mirar` a otros jugadores y PNJ en la sala, mostrando sus descripciones.

### 3. Sistema de Clases y Razas
*   **Visión:** Permitir a los jugadores personalizar su personaje al inicio del juego, eligiendo una clase y/o raza que defina sus habilidades y `CommandSets` iniciales.
*   **Tareas:**
    1.  **Máquina de Estados Finitos (FSM):** Utilizar el sistema de `FSM` de Aiogram para guiar al jugador a través de un proceso de creación de personaje por pasos (nombre -> elegir raza -> elegir clase).
    2.  **Prototipos de Clases/Razas:** Crear archivos en `game_data` que definan las estadísticas, habilidades y `CommandSets` base para cada clase y raza.
    3.  **Integración:** Hacer que el `player_service.create_character` lea la elección del jugador y aplique las plantillas correspondientes al nuevo personaje.

---

## ✨ Mejoras del Motor y Calidad de Vida

Estas son mejoras a los sistemas existentes que pulirán la experiencia de juego y desarrollo.

*   **Expandir el Sistema de Locks:**
    *   Implementar y registrar nuevas funciones de `lock` en el `permission_service`, como `habilidad(nombre)>valor`, `clase(nombre)`, etc.
    *   Integrar los `locks` en los prototipos de `Exits` para que el `world_loader_service` los aplique, permitiendo la creación de puertas con llave.

*   **Sistema de Contenedores:**
    *   Modificar el modelo `Item` para que pueda actuar como un contenedor (con capacidad, inventario propio).
    *   Crear comandos como `/meter [objeto] en [contenedor]` y `/sacar [objeto] de [contenedor]`.

*   **Bandeja de Entrada para Notificaciones:**
    *   Para los tickers de categoría `important` o `quest`, implementar la lógica para guardar los mensajes para los jugadores inactivos y presentárselos cuando vuelvan a conectarse.

*   **Detalles de Sala Interactivos:**
    *   Expandir `room_prototypes.py` y `CmdLook` para permitir "keywords" en la descripción de una sala. Al `mirar` una `keyword` (ej: `/mirar cuadro`), se revelaría un texto adicional sin necesidad de que sea un objeto físico.
