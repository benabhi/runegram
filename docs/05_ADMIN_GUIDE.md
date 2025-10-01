# Guía de Comandos de Administración

Este documento es una referencia completa para todos los comandos especiales disponibles para los roles de `ADMIN` y `SUPERADMIN`. Estos comandos son herramientas para la creación, depuración y gestión del mundo de Runegram.

## Jerarquía de Roles

El sistema de permisos se basa en una jerarquía simple:
*   **SUPERADMIN:** Tiene acceso a todos los comandos. Es el rol más alto.
*   **ADMIN:** Tiene acceso a la mayoría de los comandos de construcción y moderación, pero no a los que son potencialmente destructivos o alteran la configuración fundamental del juego.
*   **JUGADOR:** El rol base sin acceso a comandos administrativos.

---

## Comandos de Generación (Spawning)

Estos comandos permiten crear nuevas instancias de entidades en el mundo.

### `/generarobjeto <clave_prototipo>`
*   **Alias:** `/genobj`
*   **Permiso:** `ADMIN`
*   **Descripción:** Crea una instancia del objeto especificado por su `clave_prototipo` y la coloca en el suelo de la sala actual del administrador. La clave debe corresponder a una entrada en `game_data/item_prototypes.py`.
*   **Uso:**
    ```
    /generarobjeto espada_viviente
    ```

---

## Comandos de Movimiento

Estos comandos permiten a los administradores moverse libremente por el mundo.

### `/teleport <id_sala>`
*   **Alias:** `/tp`
*   **Permiso:** `ADMIN`
*   **Descripción:** Te teletransporta instantáneamente a la sala especificada por su `ID` numérico. Para encontrar el ID de una sala, utiliza el comando `/listarsalas`.
*   **Uso:**
    ```
    /tp 3
    ```

---

## Comandos de Información y Diagnóstico

Estos comandos son herramientas de solo lectura para inspeccionar el estado del juego.

### `/listarsalas`
*   **Alias:** `/lsalas`
*   **Permiso:** `ADMIN`
*   **Descripción:** Muestra una lista de todas las salas que existen en el mundo, incluyendo su `ID`, su `key` de prototipo y su `nombre`. Esencial para usar `/teleport`.

### `/examinarpersonaje <nombre_o_id>`
*   **Alias:** `/exchar`
*   **Permiso:** `ADMIN`
*   **Descripción:** Muestra un informe detallado sobre un personaje. Incluye su ID, sala actual, rol de cuenta, CommandSets base y contenido del inventario.
*   **Uso:**
    ```
    /exchar Ben
    /exchar 1
    ```

### `/examinarobjeto <id>`
*   **Alias:** `/exobj`
*   **Permiso:** `ADMIN`
*   **Descripción:** Muestra un informe detallado sobre una **instancia** específica de un objeto, identificado por su ID único en la base de datos. Incluye su clave de prototipo, ubicación (sala o inventario de un jugador) y cualquier `override` de nombre o descripción.
*   **Uso:**
    ```
    /exobj 12
    ```

---

## Comandos de Gestión (Management)

Estos comandos modifican el estado fundamental de las entidades del juego y generalmente requieren el permiso más alto.

### `/asignarrol <nombre_personaje> <rol>`
*   **Permiso:** `SUPERADMIN`
*   **Descripción:** Cambia el rol de la cuenta asociada al personaje especificado. El Superadmin no puede asignar un rol igual o superior al suyo a otra persona.
*   **Roles Disponibles:** `JUGADOR`, `ADMIN`, `SUPERADMIN`.
*   **Uso:**
    ```
    /asignarrol Pippin ADMIN
    ```