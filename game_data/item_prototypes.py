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
    - "category": (str, opcional) Categoría principal del item (ej: "arma", "contenedor", "consumible").
    - "tags": (list[str], opcional) Etiquetas múltiples (ej: ["espada", "magico", "unica"]).
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
        "category": "arma",
        "tags": ["espada", "magica", "unica", "una_mano"],
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
        "category": "contenedor",
        "tags": ["mochila", "portatil", "cuero"],
        "is_container": True,
        "capacity": 10, # Puede contener hasta 10 objetos.
        "display": {
            "icon": "🎒",  # Icono de mochila
        }
    },

    # Un contenedor fijo con locks contextuales y mensajes personalizados.
    "cofre_roble": {
        "name": "un cofre de roble",
        "keywords": ["cofre", "roble"],
        "description": "Un pesado cofre de madera de roble con refuerzos de hierro. Está cerrado.",
        "category": "contenedor",
        "tags": ["cofre", "fijo", "madera", "cerrado"],
        "is_container": True,
        "capacity": 20,
        # Sistema de locks contextuales
        "locks": {
            "get": "rol(SUPERADMIN)",  # Solo SUPERADMIN puede cogerlo (muy pesado)
            "put": "",                  # Todos pueden meter cosas (sin lock)
            "take": ""                  # Todos pueden sacar cosas (sin lock)
        },
        # Mensajes de error personalizados por access type
        "lock_messages": {
            "get": "El cofre es demasiado pesado para levantarlo. Está firmemente anclado al suelo."
        },
        "display": {
            "icon": "📦",  # Icono de cofre/caja
        }
    },

    # Ejemplo de contenedor con llave (locks contextuales avanzados)
    "cofre_magico": {
        "name": "un cofre mágico",
        "keywords": ["cofre", "magico"],
        "description": "Un cofre ornamentado con runas brillantes. Parece necesitar una llave especial para abrirlo.",
        "category": "contenedor",
        "tags": ["cofre", "magico", "cerrado", "fijo"],
        "is_container": True,
        "capacity": 10,
        "locks": {
            "get": "rol(SUPERADMIN)",  # Demasiado pesado para cogerlo
            "put": "tiene_objeto(llave_magica)",  # Necesita llave para meter
            "take": "tiene_objeto(llave_magica)"  # Necesita llave para sacar
        },
        "lock_messages": {
            "get": "El cofre está encantado y firmemente fijado al suelo.",
            "put": "El cofre está sellado con magia. Necesitas la llave mágica.",
            "take": "El cofre está sellado con magia. Necesitas la llave mágica."
        },
        "display": {
            "icon": "📦✨",
        }
    },

    # Llave mágica para el cofre
    "llave_magica": {
        "name": "una llave de cristal",
        "keywords": ["llave", "cristal", "magica"],
        "description": "Una llave hecha de cristal translúcido que emite un suave brillo azul.",
        "category": "llave",
        "tags": ["llave", "magica", "unica"],
        "display": {
            "icon": "🔑",
        }
    },

    # Objeto que solo puede cogerse en ciertas salas
    "reliquia_sagrada": {
        "name": "una reliquia sagrada",
        "keywords": ["reliquia", "sagrada"],
        "description": "Un objeto de poder divino que solo puede ser tocado en lugares sagrados.",
        "category": "quest",
        "tags": ["quest", "unica", "sagrada"],
        "locks": {
            "get": "en_categoria_sala(templo) or rol(ADMIN)",
            "drop": "en_categoria_sala(templo) or rol(ADMIN)"
        },
        "lock_messages": {
            "get": "La reliquia rechaza tu toque. Solo puede ser recogida en un lugar sagrado.",
            "drop": "La reliquia rechaza ser abandonada aquí. Debe permanecer en un lugar sagrado."
        },
        "display": {
            "icon": "✨",
        }
    },

    # Objeto con límite de inventario
    "saco_pesado": {
        "name": "un saco pesado",
        "keywords": ["saco", "pesado"],
        "description": "Un saco lleno de piedras. Muy pesado.",
        "category": "objeto",
        "tags": ["pesado"],
        "locks": {
            "get": "not cuenta_items(10)"  # Solo si tiene menos de 10 items
        },
        "lock_messages": {
            "get": "Ya llevas demasiadas cosas. No puedes cargar más peso."
        },
        "display": {
            "icon": "💼",
        }
    },

    # --- EJEMPLOS DE SCRIPTS GLOBALES ---

    # Poción de curación que usa script global
    "pocion_curacion": {
        "name": "una poción de curación",
        "keywords": ["pocion", "curacion", "pocima"],
        "description": "Un frasco de cristal con un líquido rojo brillante. Huele a hierbas medicinales.",
        "category": "consumible",
        "tags": ["pocion", "curacion", "consumible"],
        "scripts": {
            "after_on_use": "global:curar_personaje(cantidad=50, mensaje='La poción te restaura la salud')"
        },
        "display": {
            "icon": "🧪",
        }
    },

    # Trampa que daña al personaje
    "trampa_espinas": {
        "name": "una trampa de espinas",
        "keywords": ["trampa", "espinas"],
        "description": "Una trampa oculta con espinas afiladas. Parece peligrosa.",
        "category": "trampa",
        "tags": ["trampa", "peligroso"],
        "scripts": {
            "after_on_look": "global:danar_personaje(cantidad=10, mensaje='¡Te pinchas con las espinas!')"
        },
        "display": {
            "icon": "🦔",
        }
    },

    # Portal mágico que teleporta
    "portal_magico": {
        "name": "un portal mágico",
        "keywords": ["portal", "magico"],
        "description": "Un portal resplandeciente que distorsiona el espacio. ¿A dónde llevará?",
        "category": "portal",
        "tags": ["portal", "magico", "transporte"],
        "scripts": {
            "after_on_use": "global:teleport_aleatorio(mensaje='El portal te absorbe y te transporta a otro lugar')"
        },
        "display": {
            "icon": "🌀",
        }
    },

    # Altar que spawna items periódicamente
    "altar_generador": {
        "name": "un altar antiguo",
        "keywords": ["altar", "antiguo", "generador"],
        "description": "Un altar de piedra cubierto de runas. Irradia poder mágico.",
        "category": "altar",
        "tags": ["altar", "magico", "generador"],
        "scheduled_scripts": [
            {
                "schedule": "*/5 * * * *",  # Cada 5 minutos
                "script": "global:spawn_item(item_key='pocion_curacion', mensaje='El altar brilla y materializa una poción')",
                "permanent": True,
                "global": True,
                "category": "ambient"
            }
        ],
        "display": {
            "icon": "⛩️",
        }
    },

    # --- EJEMPLOS DE SCRIPTS BEFORE/AFTER CON CANCELACIÓN ---

    # Item que demuestra cancelación en BEFORE phase
    "orbe_maldito": {
        "name": "un orbe maldito",
        "keywords": ["orbe", "maldito", "esfera"],
        "description": "Una esfera oscura que emite una energía siniestra. Algo te advierte que no deberías cogerla.",
        "category": "maldito",
        "tags": ["maldito", "peligroso", "magico"],
        "scripts": {
            # BEFORE: Cancela la acción si el personaje tiene poca salud
            "before_on_get": """
# Cancelar si el personaje tiene menos de 50 HP
if character.hp < 50:
    result.cancel_action = True
    result.message = '❌ El orbe rechaza tu toque. Tu fuerza vital es demasiado débil.'
else:
    # Permitir, pero advertir
    await context.send_message(character, '⚠️ Sientes una energía oscura fluir hacia ti al tocar el orbe.')
""",
            # AFTER: Daña al personaje después de cogerlo
            "after_on_get": "global:danar_personaje(cantidad=20, mensaje='El orbe maldito drena tu energía vital')",

            # AFTER: Cura al personaje cuando lo deja
            "after_on_drop": "global:curar_personaje(cantidad=30, mensaje='Te sientes aliviado al soltar el orbe maldito')"
        },
        "display": {
            "icon": "🔮",
        }
    },

    # Item con múltiples scripts BEFORE/AFTER
    "gema_resonante": {
        "name": "una gema resonante",
        "keywords": ["gema", "resonante", "cristal"],
        "description": "Un cristal que vibra suavemente. Al mirarlo, sientes que resuena con tu presencia.",
        "category": "gema",
        "tags": ["gema", "magica", "curiosa"],
        "scripts": {
            # BEFORE on_look: Verifica estado del personaje
            "before_on_look": """
# Solo permite mirar si el personaje está en buena salud
if character.hp < 30:
    result.cancel_action = True
    result.message = '⚠️ Tu visión se nubla. Estás demasiado débil para concentrarte en la gema.'
""",
            # AFTER on_look: Muestra mensaje especial basado en HP
            "after_on_look": """
if character.hp > 80:
    await context.send_message(character, '✨ La gema brilla intensamente, respondiendo a tu fuerza vital.')
elif character.hp > 50:
    await context.send_message(character, '💎 La gema emite un brillo moderado.')
else:
    await context.send_message(character, '🔹 La gema apenas titila, reflejando tu debilidad.')
""",
            # AFTER on_drop: Mensaje de despedida
            "after_on_drop": """
await context.send_message(character, '<i>La gema deja de vibrar al separarte de ella.</i>')
"""
        },
        "display": {
            "icon": "💎",
        }
    },

    # Item que usa estado persistente para limitar usos
    "anillo_deseos": {
        "name": "un anillo de los deseos",
        "keywords": ["anillo", "deseos"],
        "description": "Un anillo dorado con una inscripción: 'Solo tres deseos concederé'.",
        "category": "magico",
        "tags": ["anillo", "magico", "unico"],
        "scripts": {
            # BEFORE on_use: Verifica usos restantes
            "before_on_use": """
from src.services import state_service

# Obtener usos restantes del estado persistente del item
usos_restantes = await state_service.get_persistent(session, target, 'usos_restantes', default=3)

if usos_restantes <= 0:
    result.cancel_action = True
    result.message = '❌ El anillo ha perdido su magia. No quedan deseos.'
else:
    # Decrementar usos
    await state_service.set_persistent(session, target, 'usos_restantes', usos_restantes - 1)
    await context.send_message(character, f'✨ El anillo brilla. Te quedan {usos_restantes - 1} deseos.')
""",
            # AFTER on_use: Curar al personaje (el "deseo")
            "after_on_use": "global:curar_personaje(cantidad=100, mensaje='Tu deseo es concedido: ¡salud restaurada!')"
        },
        "display": {
            "icon": "💍",
        }
    },
}