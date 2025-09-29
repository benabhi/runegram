# game_data/item_prototypes.py

# Este diccionario contiene las "plantillas" para todos los objetos del juego.
# La base de datos solo almacenará la 'key' (ej: "espada_corta"), y el resto de
# los datos se leerán desde aquí.

ITEM_PROTOTYPES = {
    "espada_corta": {
        "name": "una espada corta",
        "description": "Es una hoja simple pero afilada, perfecta para un principiante.",
        # --- Atributos para el futuro ---
        # "wearable": {"slot": "mano_derecha", "attack_bonus": 2},
        # "value": 10,
    },
    "antorcha_apagada": {
        "name": "una antorcha apagada",
        "description": "Un palo con un trapo empapado en brea. Está frío al tacto.",
        # "can_light": True,
    },
    "llave_oxidada": {
        "name": "una llave oxidada",
        "description": "Una vieja llave de hierro, cubierta de óxido. Te preguntas qué abrirá.",
    },
    "roca_afilada": {
        "name": "una roca afilada",
        "description": "Una simple roca con un borde que podría servir para cortar.",
    }
}