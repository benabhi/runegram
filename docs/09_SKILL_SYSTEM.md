# Sistema de Habilidades

*(Este documento es un borrador y se completará a medida que el Sistema de Habilidades sea diseñado e implementado).*

## Visión General

El Sistema de Habilidades de Runegram se basará en el principio de "aprender haciendo" (*learning by doing*). Los personajes mejorarán sus habilidades al usarlas exitosamente, en lugar de gastar puntos de experiencia de forma manual. La resolución de acciones se basará en una tirada de d100.

## Mecánica Central (d100)

1.  **Resolución de Acción:** Cuando un personaje intenta una acción basada en una habilidad (ej: forzar una cerradura), el sistema realiza una tirada de `d100` (un número aleatorio entre 1 y 100).
2.  **Comprobación:** La acción tiene éxito si `d100 <= Nivel de Habilidad del Personaje`.
3.  **Progresión:** Si la acción tiene éxito, el personaje tiene una probabilidad de ganar un punto (o una fracción de punto) en esa habilidad. La probabilidad de ganar un punto disminuirá a medida que el nivel de la habilidad aumente, haciendo que la progresión sea natural.

## Tipos de Habilidades

Las habilidades se dividirán en categorías, como:

*   **Habilidades de Combate:**
    *   `espadas`
    *   `hachas`
    *   `arcos`
    *   `parada`
    *   `esquiva`
*   **Habilidades Mágicas:**
    *   `evocacion`
    *   `alteracion`
    *   `necromancia`
*   **Habilidades de Artesanía y Generales:**
    *   `herreria`
    *   `alquimia`
    *   `forzar_cerraduras`
    *   `sigilo`

## Integración con el Sistema de Locks

Este sistema se integrará directamente con el `permission_service`. Se creará una nueva función de `lock`, `habilidad()`, que permitirá crear `lock strings` como:

*   `"habilidad(forzar_cerraduras)>50"`
*   `"habilidad(herreria)>75 and tiene_objeto(martillo_especial)"`