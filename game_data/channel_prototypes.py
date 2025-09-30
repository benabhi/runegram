# game_data/channel_prototypes.py

CHANNEL_PROTOTYPES = {
    "novato": {
        "name": "Novato",
        "icon": "📢",
        "description": "Un canal para que los nuevos aventureros pidan ayuda.",
        # 'CHAT' permite a los jugadores enviar mensajes con /novato
        # 'BROADCAST' sería solo para anuncios del sistema.
        "type": "CHAT",
        # Los nuevos personajes tendrán este canal activado por defecto.
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