# Sistema de Combate

*(Este documento es un borrador y se completará a medida que el Sistema de Combate sea diseñado e implementado).*

## Visión General

El Sistema de Combate de Runegram será un sistema táctico por turnos diseñado para la interfaz de un MUD de texto. Se centrará en la claridad de la información y en decisiones significativas por parte del jugador.

## Flujo de un Turno de Combate

1.  **Iniciación:** El combate comienza cuando un jugador ataca a un PNJ agresivo o viceversa. Todos los participantes en la sala entran en "modo de combate".
2.  **Cola de Acciones:** El sistema determinará el orden de acción (basado en atributos como Agilidad o Iniciativa).
3.  **Resolución de Acciones:** Las acciones (atacar, lanzar hechizo, usar objeto) se resuelven una por una.
4.  **Fin del Turno:** Se muestra un resumen del turno a todos los participantes.
5.  **Comprobación de Fin de Combate:** Si solo queda un bando en pie, el combate termina. De lo contrario, comienza un nuevo turno.

## Comandos de Combate

El `CommandSet` de `combat` incluirá, como mínimo:
*   `/atacar <objetivo>`
*   `/lanzar <hechizo> <objetivo>`
*   `/usar <objeto> <objetivo>`
*   `/huir`

## Atributos de Personaje y PNJ

Los personajes y PNJ tendrán atributos clave para el combate:
*   Salud (HP)
*   Maná/Energía (MP/EP)
*   Atributos primarios (Fuerza, Agilidad, Inteligencia)
*   Atributos secundarios (Ataque, Defensa, Probabilidad de Crítico)