# game_data/item_prototypes.py
"""
Definición de Prototipos de Objetos (Items).

Este archivo es el catálogo central de todos los objetos que pueden existir
en el mundo de Runegram. Sigue un sistema de prototipos, lo que significa que
este archivo define las "plantillas" o "planos" de los objetos, mientras que
la base de datos solo almacena las "instancias" individuales de esos objetos
(su ubicación, si tienen un nombre personalizado, etc.).

Esta separación es clave para la filosofía de diseño del motor, permitiendo
añadir cientos de objetos nuevos sin modificar el código fuente ni la
estructura de la base de datos.

Estructura de un Prototipo de Objeto:
- <clave_unica>: (ej: "espada_viviente")
    - "name": (str) El nombre que ven los jugadores (ej: "una espada viviente").
    - "keywords": (list[str]) Palabras clave para que los jugadores puedan interactuar
                    con el objeto (ej: /mirar espada).
    - "description": (str) El texto que se muestra al mirar el objeto.
    - "scripts": (dict, opcional) Define scripts reactivos a eventos.
        - "on_look": (str) El script a ejecutar cuando un jugador mira el objeto.
    - "tickers": (list[dict], opcional) Define scripts proactivos que se ejecutan
                 periódicamente.
        - "schedule": (str) El horario (cron o intervalo).
        - "script": (str) El script a ejecutar.
        - "category": (str) La categoría del ticker (ej: "ambient").
    - "grants_command_sets": (list[str], opcional) Lista de CommandSets que este
                             objeto otorga al personaje que lo posea.
"""

ITEM_PROTOTYPES = {
    # Un objeto mágico que susurra secretos periódicamente.
    "espada_viviente": {
        "name": "una espada viviente",
        "description": "La hoja de acero parece retorcerse y susurrarte secretos.",
        "keywords": ["espada", "viviente"],
        "scripts": {
            # Cuando se mira, emite un brillo rojo.
            "on_look": "script_notificar_brillo_magico(color=rojo)"
        },
        "tickers": [
            {
                # Cada 2 minutos, ejecuta el script de susurrar.
                "schedule": "*/2 * * * *",
                "script": "script_espada_susurra_secreto",
                # Se categoriza como "ambient" para no molestar a jugadores inactivos.
                "category": "ambient"
            }
        ]
    },

    # Un objeto decorativo con un ticker de intervalo.
    "corazon_sangrante": {
        "name": "un corazón sangrante",
        "description": "Late débilmente y gotea un icor oscuro.",
        "keywords": ["corazon", "sangrante"],
        "tickers": [
            {
                # Cada 30 segundos, ejecuta un script (aún por definir).
                "schedule": "interval:30",
                "script": "script_objeto_sangra_en_el_suelo",
                "category": "ambient"
            }
        ]
    },

    # --- Futuros objetos podrían ir aquí ---
    # "ganzuas_maestras": {
    #     "name": "unas ganzúas maestras",
    #     "keywords": ["ganzuas", "herramientas"],
    #     "description": "Unas herramientas de precisión para el ladrón experto.",
    #     # Este objeto otorga acceso al CommandSet "thievery" mientras se posea.
    #     "grants_command_sets": ["thievery"]
    # },
}