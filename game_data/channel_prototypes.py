# game_data/channel_prototypes.py
"""
Definición de Prototipos de Canales de Chat.

Este archivo actúa como la "Fuente de la Verdad" para todos los canales de
comunicación globales disponibles en el juego. El `channel_service` utiliza
esta información para gestionar las suscripciones y formatear los mensajes.

Añadir un nuevo canal al juego es tan simple como añadir una nueva entrada
a este diccionario.

Estructura de un Prototipo de Canal:
- <clave_unica>: (ej: "novato")
    - "name": (str) El nombre del canal que ven los jugadores.
    - "icon": (str) Un icono emoji que precede a los mensajes del canal.
    - "description": (str) Una breve explicación que se muestra en el comando /canales.
    - "type": (str) Define el comportamiento del canal:
        - "CHAT": Los jugadores pueden enviar mensajes a través de un comando (ej: /novato).
        - "BROADCAST": Solo el sistema puede enviar mensajes (ej: anuncios).
    - "default_on": (bool) Si es `True`, los nuevos personajes se suscriben
                    automáticamente a este canal al ser creados.
"""

CHANNEL_PROTOTYPES = {
    # Canal para que los nuevos jugadores puedan hacer preguntas.
    "novato": {
        "name": "Novato",
        "icon": "📢",
        "description": "Un canal para que los nuevos aventureros pidan ayuda.",
        "type": "CHAT",
        "default_on": True,
    },

    # Canal para notificaciones automáticas del juego.
    "sistema": {
        "name": "Sistema",
        "icon": "⚙️",
        "description": "Anuncios automáticos del juego, como estados de actividad.",
        "type": "BROADCAST",
        "default_on": True,
    },

    # --- Futuros canales podrían ir aquí ---
    # "comercio": {
    #     "name": "Comercio",
    #     "icon": "💰",
    #     "description": "Para comprar y vender objetos con otros jugadores.",
    #     "type": "CHAT",
    #     "default_on": True,
    # },
    # "anuncios": {
    #     "name": "Anuncios",
    #     "icon": "📜",
    #     "description": "Noticias y eventos importantes del mundo.",
    #     "type": "BROADCAST",
    #     "default_on": True,
    # }
}