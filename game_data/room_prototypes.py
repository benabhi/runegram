# game_data/room_prototypes.py
"""
Definición de Prototipos de Salas (Rooms).

Este archivo es el "mapa maestro" del mundo de Runegram. Define todas las
salas estáticas, sus descripciones y, lo más importante, cómo se conectan
entre sí.

El `world_loader_service` lee este archivo al arrancar el bot para construir
o sincronizar el mundo en la base de datos.

Estructura de un Prototipo de Sala:
- <clave_unica>: (ej: "plaza_central") Un identificador único para la sala que
                 nunca debe cambiar. Se usa para las conexiones.
    - "name": (str) El nombre de la sala que ven los jugadores.
    - "description": (str) El texto principal que se muestra al entrar o mirar la sala.
    - "exits": (dict, opcional) Define las salidas desde esta sala.
        - "<direccion>": (str) La clave única de la sala de destino.
          (ej: "norte": "camino_del_bosque"). El `world_loader_service` se
          encarga de crear automáticamente la salida de vuelta (sur).
    - "grants_command_sets": (list[str], opcional) Lista de CommandSets que esta
                             sala otorga a cualquier personaje que se encuentre en ella.
"""

ROOM_PROTOTYPES = {
    # La sala de inicio, donde aparecen todos los nuevos personajes.
    "limbo": {
        "name": "El Limbo",
        "description": "Te encuentras en una habitación vacía, suspendida en la nada. Es el comienzo de tu aventura y un refugio seguro.",
        "exits": {
            # "dirección": "clave_de_la_sala_destino"
            "norte": "plaza_central"
        }
    },

    # Un nexo central desde el que parten varios caminos.
    "plaza_central": {
        "name": "Plaza Central de Runegard",
        "description": "Estás en el corazón de la ciudad. El bullicio de mercaderes y aventureros llena el aire. Varios caminos parten desde aquí.",
        "exits": {
            # El cargador creará automáticamente la salida 'sur' de vuelta al 'limbo'.
            "este": "calle_mercaderes"
        }
    },

    # Una sala temática.
    "calle_mercaderes": {
        "name": "Calle de los Mercaderes",
        "description": "Decenas de puestos se alinean en esta calle, ofreciendo todo tipo de mercancías exóticas.",
        "exits": {
            # El cargador creará automáticamente la salida 'oeste' de vuelta a 'plaza_central'.
        }
    },

    # --- Futuras salas podrían ir aquí ---
    # "forja_del_enano": {
    #     "name": "La Forja del Enano Errante",
    #     "description": "El calor del fuego y el rítmico martilleo sobre el yunque llenan esta sala.",
    #     "exits": {
    #         "sur": "plaza_central"
    #     },
    #     # Cualquier jugador en esta sala obtiene acceso a los comandos de herrería.
    #     "grants_command_sets": ["smithing"]
    # }
}