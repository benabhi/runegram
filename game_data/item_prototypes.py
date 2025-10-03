# game_data/item_prototypes.py
"""
Definición de Prototipos de Objetos (Items).

Este archivo es el catálogo central de todos los objetos que pueden existir
en el mundo de Runegram. Sigue un sistema de prototipos, lo que significa que
este archivo define las "plantillas" de los objetos.

Estructura de un Prototipo de Objeto:
- <clave_unica>:
    - "name": (str) El nombre que ven los jugadores.
    - "keywords": (list[str]) Palabras clave para interactuar con el objeto.
    - "description": (str) El texto que se muestra al mirar el objeto.
    - "scripts": (dict, opcional) Scripts reactivos a eventos.
    - "tick_scripts": (list[dict], opcional) Scripts proactivos basados en el sistema de pulse.
        Cada tick_script tiene:
        - "interval_ticks": (int) Cada cuántos ticks se ejecuta.
        - "script": (str) Nombre del script a ejecutar.
        - "category": (str) Categoría ("ambient", "combat", "system").
        - "permanent": (bool) True = se repite, False = se ejecuta una sola vez.
    - "grants_command_sets": (list[str], opcional) CommandSets que este objeto otorga.
    - "locks": (str, opcional) Restricciones para interactuar. En un objeto normal,
               se usa para el comando 'coger'. En un contenedor, se usa para 'abrir',
               'meter' o 'sacar'.

    - "is_container": (bool, opcional) Si es `True`, este objeto puede contener otros.
    - "capacity": (int, opcional) El número máximo de objetos que puede contener.
"""

ITEM_PROTOTYPES = {
    # Un objeto mágico que susurra secretos periódicamente.
    "espada_viviente": {
        "name": "una espada viviente",
        "description": "La hoja de acero parece retorcerse y susurrarte secretos.",
        "keywords": ["espada", "viviente"],
        "scripts": {
            "on_look": "script_notificar_brillo_magico(color=rojo)"
        },
        "tick_scripts": [
            {
                "interval_ticks": 60,  # Cada 60 ticks (120 segundos con tick=2s)
                "script": "script_espada_susurra_secreto",
                "category": "ambient",
                "permanent": True  # Se repite indefinidamente
            }
        ],
        "display": {
            "icon": "⚔️",  # Icono de espada
        }
    },

    # --- NUEVOS EJEMPLOS DE CONTENEDORES ---

    # Un contenedor simple que se puede llevar en el inventario.
    "mochila_cuero": {
        "name": "una mochila de cuero",
        "keywords": ["mochila", "cuero"],
        "description": "Una mochila simple pero resistente, hecha de cuero curtido. Parece que tiene espacio para algunas cosas.",
        "is_container": True,
        "capacity": 10, # Puede contener hasta 10 objetos.
        "display": {
            "icon": "🎒",  # Icono de mochila
        }
    },

    # Un contenedor fijo que no se puede coger y necesita una llave (futuro).
    "cofre_roble": {
        "name": "un cofre de roble",
        "keywords": ["cofre", "roble"],
        "description": "Un pesado cofre de madera de roble con refuerzos de hierro. Está cerrado.",
        "is_container": True,
        "capacity": 20,
        # Este lock evita que el objeto sea cogido con `/coger`.
        "locks": "rol(SUPERADMIN)",
        # Futuro: Podríamos tener un lock específico para abrir/cerrar.
        # "open_lock": "tiene_objeto(llave_cofre_roble)"
        "display": {
            "icon": "📦",  # Icono de cofre/caja
        }
    },
}