# game_data/room_prototypes.py
"""
Definición de Prototipos de Salas (Rooms).

Este archivo es el "mapa maestro" del mundo de Runegram. Define todas las
salas estáticas, sus descripciones, conexiones y detalles interactivos.

El `world_loader_service` lee este archivo al arrancar el bot para construir
o sincronizar el mundo en la base de datos.

Estructura de un Prototipo de Sala:
- <clave_unica>: (ej: "plaza_central")
    - "name": (str) El nombre de la sala.
    - "description": (str) El texto principal que se muestra al entrar.
    - "exits": (dict, opcional) Conexiones a otras salas.
        - "<direccion>": (str) La clave única de la sala de destino.
        - IMPORTANTE: Todas las salidas deben ser BIDIRECCIONALES y EXPLÍCITAS.
          Si la sala A tiene salida "norte" → sala B, entonces sala B debe tener
          explícitamente la salida de vuelta (ej: "sur" → sala A).
    - "grants_command_sets": (list[str], opcional) CommandSets que la sala otorga.
    - "details": (dict, opcional) Elementos descriptivos de la sala que se
                 pueden mirar, pero no son objetos físicos.
        - "<keyword>": (dict)
            - "keywords": (list[str]) Palabras clave para mirar el detalle.
            - "description": (str) El texto que se muestra al mirar el detalle.
"""

ROOM_PROTOTYPES = {
    # La sala de inicio.
    "limbo": {
        "name": "El Limbo",
        "description": "Te encuentras en una habitación vacía, suspendida en la nada. Es el comienzo de tu aventura y un refugio seguro.",
        "exits": {
            "norte": "plaza_central"
        }
    },

    # Un nexo central con un nuevo detalle interactivo.
    "plaza_central": {
        "name": "Plaza Central de Runegard",
        "description": "Estás en el corazón de la ciudad. El bullicio de mercaderes y aventureros llena el aire. Una imponente fuente de mármol domina el centro de la plaza. Varios caminos parten desde aquí.",
        "exits": {
            "sur": "limbo",           # Salida de vuelta al Limbo
            "este": "calle_mercaderes"
        },
        "details": {
            # Este diccionario permite que el comando `/mirar fuente` funcione en esta sala.
            "fuente_plaza": {
                "keywords": ["fuente", "marmol", "fuente de marmol"],
                "description": "Es una magnífica fuente esculpida en mármol blanco. El agua cristalina fluye desde la boca de tres leones de piedra. En el fondo, puedes ver el brillo de algunas monedas arrojadas por los transeúntes."
            }
        }
    },

    # Una sala temática.
    "calle_mercaderes": {
        "name": "Calle de los Mercaderes",
        "description": "Decenas de puestos se alinean en esta calle, ofreciendo todo tipo de mercancías exóticas.",
        "exits": {
            "oeste": "plaza_central"  # Salida de vuelta a la Plaza Central
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