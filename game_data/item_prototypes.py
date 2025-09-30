# game_data/item_prototypes.py

ITEM_PROTOTYPES = {
    "espada_viviente": {
        "name": "una espada viviente",
        "description": "La hoja de acero parece retorcerse y susurrarte secretos.",
        "scripts": {
            "on_look": "script_notificar_brillo_magico(color=rojo)"
        },
        "tickers": [
            {
                "schedule": "*/2 * * * *",
                "script": "script_espada_susurra_secreto",
                # Categoriza este ticker como "de ambiente".
                # El sistema lo ignorará para jugadores inactivos.
                "category": "ambient"
            }
        ]
    },

    "corazon_sangrante": {
        "name": "un corazón sangrante",
        "description": "Late débilmente y gotea un icor oscuro.",
        "tickers": [
            {
                "schedule": "interval:30",
                "script": "script_objeto_sangra_en_el_suelo",
                "category": "ambient"
            }
        ]
    }
}