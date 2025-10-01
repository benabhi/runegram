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
    - "type": (str) Define si se debe generar un comando para hablar en el canal.
        - "CHAT": Se generará un comando dinámico (ej: /novato) para que los jugadores hablen.
    - "default_on": (bool) Si es `True`, los nuevos personajes se suscriben
                    automáticamente a este canal al ser creados.
    - "lock": (str, opcional) Un lock string que se aplica al comando de chat generado.
             Permite restringir quién puede hablar en el canal.
"""

CHANNEL_PROTOTYPES = {
    # Canal para que los nuevos jugadores puedan hacer preguntas.
    "novato": {
        "name": "Novato",
        "icon": "📢",
        "description": "Un canal para que los nuevos aventureros pidan ayuda.",
        "type": "CHAT",
        "default_on": True,
        "lock": "", # Sin lock, cualquiera puede hablar.
    },

    # Canal para notificaciones automáticas del juego y comunicación de administradores.
    "sistema": {
        "name": "Sistema",
        "icon": "⚙️",
        "description": "Anuncios del juego y notificaciones automáticas.",
        "type": "CHAT", # Es de tipo CHAT para que se genere el comando /sistema.
        "default_on": True,
        # Se añade un lock para que solo los ADMINS o superior puedan hablar en él.
        "lock": "rol(ADMIN)"
    },

    # --- Futuros canales podrían ir aquí ---
    # "comercio": {
    #     "name": "Comercio",
    #     "icon": "💰",
    #     "description": "Para comprar y vender objetos con otros jugadores.",
    #     "type": "CHAT",
    #     "default_on": True,
    #     "lock": "",
    # },
}