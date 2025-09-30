# game_data/channel_prototypes.py

CHANNEL_PROTOTYPES = {
    "novato": {
        "name": "Novato",
        "icon": "📢",
        "description": "Un canal para que los nuevos aventureros pidan ayuda.",
        "type": "CHAT",
        "default_on": True,
    },
    # --- NUEVO CANAL AÑADIDO ---
    "sistema": {
        "name": "Sistema",
        "icon": "⚙️",
        "description": "Anuncios automáticos del juego, como estados de actividad.",
        # 'BROADCAST' significa que los jugadores no pueden escribir en él.
        "type": "BROADCAST",
        "default_on": True,
    }
}