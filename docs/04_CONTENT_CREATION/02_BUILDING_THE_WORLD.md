# Guía Práctica: Construyendo el Mundo

Gracias a la arquitectura "Data-Driven" de Runegram, expandir el mundo del juego es una tarea de diseño de contenido, no de programación del motor. Esta guía te mostrará cómo añadir nuevas salas, objetos con `locks`, contenedores y canales, simplemente editando archivos de datos en la carpeta `game_data/`.

## 1. Construyendo Salas y Salidas con Locks

**Archivo a editar:** `game_data/room_prototypes.py`

### Sintaxis de Salidas (Exits)

Para conectar salas, se usa la clave `"exits"`. Tienes dos formas de definir una salida:

#### a) Sintaxis Simple (Bidireccional y sin Lock)

Si solo proporcionas un string con la `key` de la sala de destino, el motor creará una salida bidireccional y sin restricciones.

```python
"plaza_central": {
    "exits": { "oeste": "biblioteca_antigua" }
},
"biblioteca_antigua": {
    # No es necesario definir "este": "plaza_central" aquí.
    # El motor lo creará automáticamente.
}
```

#### b) Sintaxis Avanzada (con Locks)

Para añadir un `lock` a una salida, debes usar un diccionario. Esto te permite especificar la sala de destino y el `lock_string`.

**Importante:** Cuando usas la sintaxis avanzada, el `lock` se aplica **solo a la salida de ida**. La salida de vuelta se crea automáticamente sin `lock`.

**Ejemplo:** Vamos a crear una "Armería" a la que solo se puede entrar siendo `ADMIN` y teniendo una llave.

```python
"plaza_central": {
    "exits": {
        "norte": {
            "to": "armeria",
            "locks": "rol(ADMIN) and tiene_objeto(llave_armeria)"
        }
    }
},
"armeria": {
    "name": "La Armería de Runegard"
    # El motor creará la salida "sur" de vuelta a la "plaza_central" sin lock.
}
```
**Resultado:** Un jugador podrá salir libremente de la armería hacia el sur, pero para entrar desde la plaza hacia el norte, deberá cumplir las dos condiciones del `lock`.

### Añadiendo Detalles Interactivos
Puedes añadir elementos a una sala que se pueden `mirar` pero que no son objetos físicos usando la clave `"details"`.

```python
"plaza_central": {
    "description": "...Una imponente fuente de mármol domina el centro...",
    "details": {
        "fuente": {
            "keywords": ["fuente", "marmol"],
            "description": "Es una magnífica fuente esculpida en mármol blanco..."
        }
    }
},
```
**Resultado:** El comando `/mirar fuente` funcionará en esta sala.

## 2. Creando Objetos, Locks y Contenedores

**Archivo a editar:** `game_data/item_prototypes.py`

### Objetos con `lock` para Coger

Puedes restringir quién puede coger un objeto usando la clave `"locks"`.

```python
"espada_sagrada_antigua": {
    "name": "la Espada Sagrada Antigua",
    "keywords": ["espada", "sagrada", "antigua"],
    "description": "Una hoja legendaria que vibra con un poder inmenso.",
    "locks": "rol(SUPERADMIN)" # Solo un Superadmin puede coger este objeto.
}
```
**Resultado:** Cuando un jugador que no sea `SUPERADMIN` intente usar `/coger espada`, el comando `CmdGet` evaluará el `lock` y denegará la acción.

### Creando Contenedores

Para convertir un objeto en un contenedor, debes añadir dos claves: `"is_container": True` y `"capacity": <número>`.

#### a) Contenedor Portátil (Mochila)

```python
"mochila_cuero": {
    "name": "una mochila de cuero",
    "keywords": ["mochila", "cuero"],
    "description": "Una mochila simple pero resistente.",
    "is_container": True,
    "capacity": 10
}
```
Un jugador puede coger esta mochila y usar `/meter` y `/sacar` para gestionar su contenido.

#### b) Contenedor Fijo y Cerrado (Cofre)

Puedes combinar `locks` y propiedades de contenedor para crear objetos como cofres.

```python
"cofre_roble": {
    "name": "un cofre de roble",
    "keywords": ["cofre", "roble"],
    "description": "Un pesado cofre de madera con refuerzos de hierro.",
    "is_container": True,
    "capacity": 20,
    // El lock "rol(SUPERADMIN)" evita que nadie pueda coger el cofre del suelo.
    "locks": "tiene_objeto(llave_roble) or rol(ADMIN)"
}
```
**Resultado:**
*   Nadie podrá coger el cofre (`/coger cofre`) debido al `lock` `rol(SUPERADMIN)` (una forma de hacerlo inamovible).
*   Un jugador solo podrá interactuar con el cofre (`/meter`, `/sacar`, `/inv cofre`) si lleva la "llave_roble" o si es un `ADMIN`.

## 3. Añadiendo Canales de Chat

**Archivo a editar:** `game_data/channel_prototypes.py`

Para crear un nuevo canal donde los jugadores puedan hablar, como `/comercio`:

```python
"comercio": {
    "name": "Comercio",
    "icon": "💰",
    "description": "Para comprar, vender e intercambiar objetos.",
    "type": "CHAT",
    "default_on": True,
    "lock": "" // Sin lock, cualquiera puede hablar.
}
```
Al reiniciar el bot, el comando `/comercio` se creará automáticamente. Si quisieras que solo los administradores pudieran hablar, simplemente añadirías `"lock": "rol(ADMIN)"`.