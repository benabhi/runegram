# game_data/narrative_messages.py
"""
Base de Datos de Mensajes Narrativos Evocativos.

Este archivo contiene todos los mensajes narrativos aleatorios que se usan
en diversos comandos del juego para mejorar la inmersión y evitar la repetición.

Cada clave en NARRATIVE_MESSAGES corresponde a un tipo de evento del juego,
y contiene una lista de mensajes equivalentes pero con redacción variada.

Variables soportadas (usar {variable_name} para formateo):
- {item_name}: Nombre del objeto
- {character_name}: Nombre del personaje
- Otras según el contexto específico del mensaje
"""

NARRATIVE_MESSAGES = {
    # Mensajes para la aparición de objetos (/generarobjeto)
    "item_spawn": [
        "<i>{item_name} aparece de la nada.</i>",
        "<i>{item_name} se materializa con un destello de luz.</i>",
        "<i>Un portal dimensional deposita {item_name} en el suelo.</i>",
        "<i>{item_name} cae del cielo con un sonido sordo.</i>",
        "<i>Las sombras se arremolinan y revelan {item_name}.</i>",
        "<i>Un brillo mágico envuelve el aire, dejando tras de sí {item_name}.</i>",
        "<i>El tejido de la realidad se desgarra brevemente, expulsando {item_name}.</i>",
    ],

    # Mensajes para la destrucción de objetos en una sala (/destruirobjeto)
    "item_destroy_room": [
        "<i>{item_name} se desvanece en el aire.</i>",
        "<i>{item_name} se convierte en polvo y desaparece.</i>",
        "<i>{item_name} explota en mil partículas de luz que se extinguen rápidamente.</i>",
        "<i>{item_name} se disuelve lentamente hasta no dejar rastro.</i>",
        "<i>Un destello cegador consume {item_name}, que desaparece para siempre.</i>",
        "<i>{item_name} se desintegra en cenizas que se dispersan con el viento.</i>",
        "<i>Las sombras devoran {item_name}, borrándolo de la existencia.</i>",
    ],

    # Mensajes para la destrucción de objetos en un inventario (/destruirobjeto)
    "item_destroy_inventory": [
        "Sientes cómo {item_name} desaparece de tu inventario.",
        "{item_name} se evapora entre tus posesiones.",
        "Un escalofrío recorre tu cuerpo mientras {item_name} se desvanece de tu poder.",
        "{item_name} se disuelve en tu inventario, dejando solo un eco de su existencia.",
        "Percibes cómo {item_name} es arrancado de tu inventario por una fuerza desconocida.",
        "{item_name} titila en tu inventario y luego desaparece sin dejar rastro.",
    ],

    # Mensajes para cuando un admin se teletransporta - sala de origen (/teleport)
    "teleport_departure": [
        "<i>{character_name} desaparece en un destello brillante.</i>",
        "<i>{character_name} se desvanece en la niebla.</i>",
        "<i>Un portal se abre y {character_name} atraviesa hacia lo desconocido.</i>",
        "<i>Las sombras envuelven a {character_name}, que desaparece entre ellas.</i>",
        "<i>Un vórtice de energía absorbe a {character_name}, que se desvanece instantáneamente.</i>",
        "<i>{character_name} parpadea una vez y deja de existir en este lugar.</i>",
        "<i>El aire se distorsiona alrededor de {character_name}, que desaparece con un susurro.</i>",
    ],

    # Mensajes para cuando un admin llega por teletransporte - sala de destino (/teleport)
    "teleport_arrival": [
        "<i>{character_name} aparece de la nada.</i>",
        "<i>{character_name} se materializa con un destello.</i>",
        "<i>Un portal dimensional expulsa a {character_name}.</i>",
        "<i>Las sombras se disipan, revelando a {character_name}.</i>",
        "<i>{character_name} emerge de un vórtice de energía que se cierra tras él.</i>",
        "<i>El aire chisporrotea y {character_name} aparece súbitamente.</i>",
        "<i>Una luz brillante se condensa, formando la figura de {character_name}.</i>",
    ],

    # Mensajes para cuando un jugador se suicida (/suicidio)
    "character_suicide": [
        "<i>{character_name} desaparece en una luz cegadora.</i>",
        "<i>{character_name} se desvanece lentamente, como si nunca hubiera existido.</i>",
        "<i>El cuerpo de {character_name} se desintegra en partículas de luz.</i>",
        "<i>{character_name} cierra los ojos y su forma se disuelve en el aire.</i>",
        "<i>Un viento sobrenatural arrastra la esencia de {character_name} hacia el vacío.</i>",
        "<i>{character_name} se fragmenta en ecos de realidad que se desvanecen uno a uno.</i>",
        "<i>La silueta de {character_name} se difumina hasta desaparecer completamente.</i>",
    ],
}
