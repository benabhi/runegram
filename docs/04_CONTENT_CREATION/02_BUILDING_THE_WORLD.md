# Guía Práctica: Construyendo el Mundo

Gracias a la arquitectura "Data-Driven" de Runegram, expandir el mundo del juego es una tarea de diseño de contenido, no de programación del motor. Esta guía te mostrará cómo añadir nuevas salas, objetos y canales simplemente editando archivos de datos en la carpeta `game_data/`.

## 1. Añadiendo una Nueva Sala y Conectándola

Vamos a crear una nueva sala, la "Biblioteca Antigua", y la conectaremos a la `plaza_central`.

**Archivo a editar:** `game_data/room_prototypes.py`

### Paso 1: Definir la Nueva Sala

Añade una nueva entrada al diccionario `ROOM_PROTOTYPES`. La clave (`"biblioteca_antigua"`) debe ser única y descriptiva.

```python
# En game_data/room_prototypes.py

ROOM_PROTOTYPES = {
    # ... (salas existentes) ...

    "calle_mercaderes": {
        # ...
    },

    # --- NUEVA SALA AÑADIDA ---
    "biblioteca_antigua": {
        "name": "La Biblioteca Antigua",
        "description": "El aire aquí es denso con el olor a papel viejo y polvo. Estanterías altísimas, repletas de tomos encuadernados en cuero, se pierden en la penumbra de las alturas."
        # Aún no definimos salidas DESDE aquí.
    }
}```

### Paso 2: Conectar la Sala Existente a la Nueva

Ahora, modifica el prototipo de la `plaza_central` para que tenga una salida que lleve a nuestra nueva biblioteca.

```python
# En game_data/room_prototypes.py

    # ...
    "plaza_central": {
        "name": "Plaza Central de Runegard",
        "description": "Estás en el corazón de la ciudad...",
        "exits": {
            # El cargador creará automáticamente 'sur' de vuelta al 'limbo'.
            "este": "calle_mercaderes",
            # --- NUEVA SALIDA AÑADIDA ---
            "oeste": "biblioteca_antigua"
        }
    },
    # ...
```

### ¡Y eso es todo!

Al reiniciar el bot, el `world_loader_service` detectará los cambios:
1.  Creará la nueva sala "La Biblioteca Antigua" en la base de datos.
2.  Creará una salida "oeste" desde la "Plaza Central" hacia la biblioteca.
3.  Creará automáticamente la salida de vuelta "este" desde la "Biblioteca Antigua" hacia la plaza.

## 2. Añadiendo un Nuevo Objeto

Vamos a crear un "libro polvoriento" y lo haremos aparecer en la nueva biblioteca. Los objetos se crean en dos pasos: definir el prototipo y luego generar una instancia en el mundo.

**Archivo a editar:** `game_data/item_prototypes.py`

### Paso 1: Definir el Prototipo del Objeto

Añade una nueva entrada al diccionario `ITEM_PROTOTYPES`.

```python
# En game_data/item_prototypes.py

ITEM_PROTOTYPES = {
    # ... (objetos existentes) ...

    # --- NUEVO OBJETO AÑADIDO ---
    "libro_polvoriento": {
        "name": "un libro polvoriento",
        "keywords": ["libro", "polvoriento", "tomo"],
        "description": "Un pesado tomo encuadernado en cuero agrietado. En su portada, apenas legible, se lee: 'Historias de la Primera Era'."
    }
}
```

### Paso 2: Generar el Objeto en el Mundo

A diferencia de las salas, que son estáticas, los objetos son dinámicos. Para hacer que un objeto aparezca, un administrador debe generarlo (`spawn`) en la sala deseada.

1.  Reinicia el bot para que cargue la nueva sala.
2.  Entra al juego como Superadmin.
3.  Ve a la nueva sala: `/oeste` desde la Plaza Central.
4.  Usa el comando `/generarobjeto` con la clave del prototipo que acabas de crear:
    ```
    /generarobjeto libro_polvoriento
    ```
El objeto "un libro polvoriento" aparecerá ahora en el suelo de la biblioteca para que cualquier jugador lo vea y lo coja.

## 3. Añadiendo un Nuevo Canal de Chat

Vamos a añadir un canal de "Comercio" para que los jugadores puedan comprar y vender.

**Archivo a editar:** `game_data/channel_prototypes.py`

### Paso 1: Definir el Prototipo del Canal

Añade una nueva entrada al diccionario `CHANNEL_PROTOTYPES`.

```python
# En game_data/channel_prototypes.py

CHANNEL_PROTOTYPES = {
    # ... (canales existentes) ...

    # --- NUEVO CANAL AÑADIDO ---
    "comercio": {
        "name": "Comercio",
        "icon": "💰",
        "description": "Para comprar, vender e intercambiar objetos con otros jugadores.",
        "type": "CHAT",
        "default_on": True,
        "lock": "" # Sin lock, cualquiera puede hablar.
    }
}
```

### ¡Y eso es todo!

Al reiniciar el bot, el sistema de comandos dinámicos detectará este nuevo canal:
1.  La función `generate_channel_commands` creará automáticamente una instancia de `CmdDynamicChannel` para el comando `/comercio`.
2.  El `dispatcher` lo registrará.
3.  El `command_service` lo añadirá a la lista de comandos de Telegram de los jugadores.
4.  El comando `/canales` mostrará el nuevo canal de "Comercio" en la lista.

Este flujo de trabajo demuestra cómo el diseño "Data-Driven" te permite expandir masivamente el contenido de Runegram de una manera rápida, segura y sin necesidad de tocar el motor del juego.