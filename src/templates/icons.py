# src/templates/icons.py
"""
Convenciones de Íconos para Runegram.

Este archivo centraliza todos los emojis/íconos utilizados en el juego
para mantener consistencia visual en todos los outputs.

Los íconos están organizados por categorías y se acceden mediante claves
descriptivas en lugar de copiar/pegar emojis directamente en el código.

Principio de Diseño:
- Un ícono por concepto (no usar el mismo ícono para diferentes cosas)
- Íconos reconocibles y universales
- Consistencia en toda la aplicación

Uso:
    from src.templates.icons import ICONS

    # En código Python:
    message = f"{ICONS['room']} {room.name}"

    # En templates Jinja2:
    {{ icon('room') }} {{ room.name }}
"""

# ============================================================================
# CATEGORÍAS PRINCIPALES
# ============================================================================

# Navegación y Lugares
NAVIGATION = {
    'room': '📍',           # Ubicación/Sala
    'exit': '🚪',           # Salidas generales
    'north': '⬆️',          # Norte
    'south': '⬇️',          # Sur
    'east': '➡️',           # Este
    'west': '⬅️',           # Oeste
    'up': '⤴️',             # Arriba
    'down': '⤵️',           # Abajo
    'map': '🗺️',            # Mapa del mundo
}

# Personajes y Jugadores
CHARACTERS = {
    'character': '👤',      # Personaje genérico
    'player': '🧑',         # Jugador
    'npc': '🤖',            # NPC
    'enemy': '👹',          # Enemigo
    'ally': '🤝',           # Aliado
    'status': '❤️',         # Estado de vida/salud
}

# Items y Objetos
ITEMS = {
    'item': '📦',           # Objeto genérico
    'inventory': '🎒',      # Inventario
    'loot': '💎',           # Botín/Tesoro
    'container': '🧳',      # Contenedor
    'key': '🔑',            # Llave
    'coin': '💰',           # Monedas/Dinero
    'food': '🍖',           # Comida
    'potion': '🧪',         # Poción
}

# Equipamiento
EQUIPMENT = {
    'weapon': '⚔️',         # Arma
    'sword': '🗡️',          # Espada
    'axe': '🪓',            # Hacha
    'bow': '🏹',            # Arco
    'shield': '🛡️',         # Escudo
    'armor': '🛡️',          # Armadura (mismo que escudo por ahora)
    'helmet': '⛑️',         # Casco
    'boots': '👢',          # Botas
    'ring': '💍',           # Anillo
    'amulet': '📿',         # Amuleto
}

# Acciones y Comandos
ACTIONS = {
    'look': '👁️',           # Mirar/Observar
    'take': '🤲',           # Coger/Tomar
    'drop': '📤',           # Soltar/Dejar
    'use': '🔧',            # Usar
    'open': '🔓',           # Abrir
    'close': '🔒',          # Cerrar
    'lock': '🔐',           # Cerrar con llave
    'unlock': '🗝️',         # Abrir con llave
}

# Combate
COMBAT = {
    'attack': '⚔️',         # Atacar
    'defend': '🛡️',         # Defender
    'magic': '✨',          # Magia
    'heal': '💚',           # Curar
    'damage': '💥',         # Daño
    'critical': '🎯',       # Golpe crítico
    'miss': '💨',           # Fallar
    'death': '💀',          # Muerte
}

# Habilidades y Stats
SKILLS = {
    'strength': '💪',       # Fuerza (STR)
    'dexterity': '🏃',      # Destreza (DEX)
    'vitality': '❤️',       # Vitalidad (VIT)
    'mind': '🧠',           # Mente (MND)
    'level': '⭐',          # Nivel
    'xp': '📈',             # Experiencia
    'skill': '🔧',          # Habilidad genérica
}

# Comunicación
COMMUNICATION = {
    'say': '💬',            # Decir/Hablar
    'whisper': '🤫',        # Susurrar
    'shout': '📢',          # Gritar
    'emote': '🎭',          # Emotear/Actuar
    'channel': '📻',        # Canal de chat
    'mail': '📧',           # Correo/Mensaje
}

# Sistema y Ayuda
SYSTEM = {
    'help': '❓',           # Ayuda
    'info': 'ℹ️',           # Información
    'warning': '⚠️',        # Advertencia
    'error': '❌',          # Error
    'success': '✅',        # Éxito
    'loading': '⏳',        # Cargando
    'settings': '⚙️',       # Configuración
    'admin': '👑',          # Admin/Superadmin
    'list': '📋',           # Listados/búsquedas
    'category': '📂',       # Categorías
    'tag': '🏷️',           # Tags/Etiquetas
    'filter': '🔍',         # Filtros aplicados
}

# Mundo y Ambiente
WORLD = {
    'day': '☀️',            # Día
    'night': '🌙',          # Noche
    'weather': '⛅',        # Clima
    'fire': '🔥',           # Fuego
    'water': '💧',          # Agua
    'earth': '🌍',          # Tierra
    'air': '💨',            # Aire
    'magic_aura': '✨',     # Aura mágica
}

# Crafting y Profesiones
CRAFTING = {
    'craft': '🔨',          # Craftear
    'mining': '⛏️',         # Minería
    'fishing': '🎣',        # Pesca
    'cooking': '🍳',        # Cocina
    'alchemy': '⚗️',        # Alquimia
    'smithing': '⚒️',       # Herrería
}

# Social y Roleplay
SOCIAL = {
    'friend': '👥',         # Amigos
    'group': '👨‍👩‍👧‍👦',         # Grupo/Party
    'guild': '🏰',          # Clan/Guild
    'quest': '📜',          # Quest/Misión
    'achievement': '🏆',    # Logro
}

# ============================================================================
# DICCIONARIO MAESTRO
# ============================================================================

# Combina todas las categorías en un solo diccionario
ICONS = {
    **NAVIGATION,
    **CHARACTERS,
    **ITEMS,
    **EQUIPMENT,
    **ACTIONS,
    **COMBAT,
    **SKILLS,
    **COMMUNICATION,
    **SYSTEM,
    **WORLD,
    **CRAFTING,
    **SOCIAL,
}


# ============================================================================
# FUNCIONES HELPER
# ============================================================================

def get_direction_icon(direction: str) -> str:
    """
    Obtiene el ícono para una dirección específica.

    Args:
        direction: Nombre de la dirección ('norte', 'sur', 'este', 'oeste', etc.)

    Returns:
        str: Emoji correspondiente o ícono genérico de salida

    Examples:
        >>> get_direction_icon('norte')
        '⬆️'
        >>> get_direction_icon('custom_exit')
        '🚪'
    """
    direction_map = {
        'norte': 'north',
        'sur': 'south',
        'este': 'east',
        'oeste': 'west',
        'arriba': 'up',
        'abajo': 'down',
        'north': 'north',
        'south': 'south',
        'east': 'east',
        'west': 'west',
        'up': 'up',
        'down': 'down',
    }

    icon_key = direction_map.get(direction.lower(), 'exit')
    return ICONS.get(icon_key, ICONS['exit'])


def get_item_icon(item_type: str) -> str:
    """
    Obtiene el ícono apropiado para un tipo de item.

    Args:
        item_type: Tipo de item ('weapon', 'armor', 'potion', etc.)

    Returns:
        str: Emoji correspondiente o ícono genérico de item

    Examples:
        >>> get_item_icon('weapon')
        '⚔️'
        >>> get_item_icon('unknown')
        '📦'
    """
    return ICONS.get(item_type, ICONS['item'])
