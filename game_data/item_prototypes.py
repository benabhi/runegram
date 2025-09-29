# game_data/item_prototypes.py

# Este diccionario contiene las "plantillas" para todos los objetos del juego.
# La base de datos solo almacenará la 'key' (ej: "espada_corta"), y el resto de
# los datos se leerán desde aquí.

ITEM_PROTOTYPES = {
    "espada_corta": {
        "name": "una espada corta",
        "keywords": ["espada", "corta"],
        "description": "Es una hoja simple pero afilada, perfecta para un principiante.",
        "scripts": {
            # Cuando alguien mire esta espada, se ejecutará este script.
            "on_look": "script_notificar_brillo_magico(color=azul)",
        }
    },
    "antorcha_apagada": {
        "name": "una antorcha apagada",
        "keywords": ["antorcha", "palo"],
        "description": "Un palo con un trapo empapado en brea. Está frío al tacto.",
        # Este no tiene script on_look, demostrando que es opcional.
    },
    "llave_oxidada": {
        "name": "una llave oxidada",
        "keywords": ["llave", "oxidada"],
        "description": "Una vieja llave de hierro, cubierta de óxido. Te preguntas qué abrirá.",
    },
    "roca_afilada": {
        "name": "una roca afilada",
        "keywords": ["roca", "piedra", "afilada"],
        "description": "Una simple roca con un borde que podría servir para cortar.",
    }
}