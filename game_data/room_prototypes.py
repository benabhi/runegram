# game_data/room_prototypes.py

# Este diccionario es la "Fuente de la Verdad" para todas las salas del juego.
# La clave (ej: "limbo") es un identificador único que NUNCA debe cambiar.
ROOM_PROTOTYPES = {
    "limbo": {
        "name": "El Limbo",
        "description": "Te encuentras en una habitación vacía, suspendida en la nada. Es el comienzo de tu aventura y un refugio seguro.",
        "exits": {
            # "dirección": "clave_de_la_sala_destino"
            "norte": "plaza_central"
        }
    },
    "plaza_central": {
        "name": "Plaza Central de Runegard",
        "description": "Estás en el corazón de la ciudad. El bullicio de mercaderes y aventureros llena el aire. Varios caminos parten desde aquí.",
        "exits": {
            # El cargador creará automáticamente la salida 'sur' de vuelta al 'limbo'.
            "este": "calle_mercaderes"
        }
    },
    "calle_mercaderes": {
        "name": "Calle de los Mercaderes",
        "description": "Decenas de puestos se alinean en esta calle, ofreciendo todo tipo de mercancías exóticas.",
        "exits": {
            # El cargador creará 'oeste' de vuelta a 'plaza_central'.
        }
    }
}