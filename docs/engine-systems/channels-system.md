---
título: "Sistema de Canales"
categoría: "Sistemas del Motor"
versión: "1.0"
última_actualización: "2025-10-09"
autor: "Proyecto Runegram"
etiquetas: ["canales", "comunicación", "global", "canales-dinámicos"]
documentos_relacionados:
  - "engine-systems/social-systems.md"
  - "engine-systems/command-system.md"
referencias_código:
  - "src/services/channel_service.py"
  - "game_data/channel_prototypes.py"
  - "commands/player/dynamic_channels.py"
  - "src/models/character_setting.py"
estado: "actual"
---

# Channels System

El Sistema de Canales proporciona un medio para la comunicación global entre jugadores, así como para anuncios del sistema. Está gestionado por `src/services/channel_service.py`.

## Arquitectura "Data-Driven"

*   **Prototipos de Canal (`game_data/channel_prototypes.py`):** Es la "fuente de la verdad". Define todos los canales, su nombre, icono, descripción y, lo más importante, su **tipo** y sus **permisos**.
    *   `"type": "CHAT"`: Indica al sistema que debe generar dinámicamente un comando (ej: `/novato`) para que los jugadores puedan hablar en este canal.
    *   `"lock": "rol(ADMIN)"`: Un `lock string` opcional que se asigna al comando generado, restringiendo quién puede hablar.

*   **Configuración de Usuario (`CharacterSetting`):** La suscripción de un jugador a un canal se almacena en la base de datos, en la columna `active_channels` de su tabla de `character_settings`. Esto hace que sus preferencias sean persistentes.

## Flujo de Funcionamiento

*   **Hablar en un Canal (ej: `/novato ¡hola!`):**
    1.  El `dispatcher` identifica el comando `/novato`, que fue generado dinámicamente por el módulo `dynamic_channels`.
    2.  Se comprueban los `locks` del comando (leídos desde el prototipo del canal).
    3.  `CmdDynamicChannel.execute()` se ejecuta. Llama a `channel_service` para comprobar si el jugador está suscrito al canal "novato".
    4.  Si está suscrito, se llama a `channel_service.broadcast_to_channel()`.
    5.  Esta función recupera de la base de datos a **todos los personajes del juego**.
    6.  Itera sobre ellos, y para cada uno, comprueba si tiene el canal "novato" activo en su configuración.
    7.  Si es así, utiliza el `broadcaster_service` para enviarle el mensaje formateado.

*   **Gestión de Canales:**
    *   `/canales`: Lista todos los prototipos de canal y muestra si el jugador está suscrito a cada uno.
    *   `/activarcanal <nombre>` y `/desactivarcanal <nombre>`: Modifican la lista de `active_channels` en la configuración del personaje en la base de datos.

## Tipos de Canales

### Canales Estáticos

Los canales estáticos están definidos en `channel_prototypes.py` y se crean automáticamente al arrancar el bot.

**Ejemplo:**
```python
"novato": {
    "name": "Canal Novato",
    "icon": "🌱",
    "description": "Canal de ayuda para jugadores nuevos",
    "type": "CHAT",
    "lock": "",  # Todos pueden usar este canal
}

"admin": {
    "name": "Canal de Administración",
    "icon": "⚙️",
    "description": "Canal privado para administradores",
    "type": "CHAT",
    "lock": "rol(ADMIN)",  # Solo admins
}
```

### Canales Dinámicos (Futuro)

El sistema está preparado para soportar canales creados por jugadores:
- `/crearcanal <nombre>`: Crea un canal privado
- `/invitar <jugador> <canal>`: Invita a otro jugador al canal
- `/salircanal <nombre>`: Abandona un canal creado por jugador

## Comandos de Gestión

### `/canales`
Lista todos los canales disponibles y muestra el estado de suscripción.

**Ejemplo de salida:**
```
📻 CANALES DISPONIBLES

🌱 Canal Novato [ACTIVO]
   Canal de ayuda para jugadores nuevos

⚙️ Canal de Administración
   Canal privado para administradores

Para activar: /activarcanal <nombre>
Para desactivar: /desactivarcanal <nombre>
```

### `/activarcanal <nombre>`
Suscribe al jugador a un canal específico.

**Ejemplo:**
```
> /activarcanal novato
✅ Te has suscrito al canal 'novato'.
```

### `/desactivarcanal <nombre>`
Desuscribe al jugador de un canal.

**Ejemplo:**
```
> /desactivarcanal novato
✅ Te has desuscrito del canal 'novato'.
```

### Hablar en un Canal

Una vez suscrito, el jugador puede hablar usando el comando del canal:

```
> /novato Hola a todos, soy nuevo!

[🌱 Novato] Juan: Hola a todos, soy nuevo!
```

Todos los jugadores suscritos al canal recibirán el mensaje.

## Formato de Mensajes

Los mensajes de canal usan un formato específico:

```
[ICONO NOMBRE_CANAL] Jugador: Mensaje
```

**Ejemplos:**
```
[🌱 Novato] Juan: ¿Dónde encuentro la espada?
[⚙️ Admin] María: Servidor reiniciándose en 5 minutos
```

## Permisos y Locks

Los canales pueden tener restricciones mediante `lock strings`:

```python
"comercio": {
    "lock": ""  # Todos pueden usar
}

"vip": {
    "lock": "tiene_objeto(pase_vip)"  # Solo con item específico
}

"admin": {
    "lock": "rol(ADMIN)"  # Solo administradores
}
```

## Persistencia

Las preferencias de canal se guardan en la base de datos:

```python
# En CharacterSetting model
active_channels = Column(ARRAY(String), default=[], nullable=False)
```

Esto permite que:
- Las suscripciones persistan entre sesiones
- El jugador mantenga sus preferencias al reconectarse
- Se puedan consultar/modificar las suscripciones programáticamente

## Implementación Técnica

### Generar Comandos Dinámicos

```python
# En commands/player/dynamic_channels.py

def generate_channel_commands():
    """Genera comandos dinámicos para canales de tipo CHAT."""
    commands = []

    for key, proto in CHANNEL_PROTOTYPES.items():
        if proto.get("type") == "CHAT":
            cmd = CmdDynamicChannel(
                channel_key=key,
                names=[key],  # /novato, /admin, etc.
                description=proto.get("description"),
                lock=proto.get("lock", "")
            )
            commands.append(cmd)

    return commands
```

### Broadcast a Canal

```python
# En src/services/channel_service.py

async def broadcast_to_channel(
    session: AsyncSession,
    channel_key: str,
    sender_name: str,
    message: str
):
    """Envía un mensaje a todos los suscritos a un canal."""

    # Obtener prototipo del canal
    channel_proto = CHANNEL_PROTOTYPES.get(channel_key)

    # Formatear mensaje
    icon = channel_proto.get("icon", "📻")
    name = channel_proto.get("name", channel_key)
    formatted = f"[{icon} {name}] {sender_name}: {message}"

    # Obtener todos los personajes
    result = await session.execute(select(Character))
    all_characters = result.scalars().all()

    # Filtrar suscritos y enviar
    for char in all_characters:
        if channel_key in char.settings.active_channels:
            await broadcaster_service.send_message_to_character(
                char, formatted
            )
```

## Extensiones Futuras

### Canales Privados/Personales

```python
# Futuro: crear canales privados
/crearcanal mi_grupo
/invitar Juan mi_grupo
/invitar María mi_grupo
```

### Moderación de Canales

```python
# Futuro: moderación
/mutear <jugador> <canal>
/expulsar <jugador> <canal>
```

### Historial de Canales

```python
# Futuro: ver mensajes anteriores
/historial novato
```

## Ver También

- [Social Systems](social-systems.md) - Interacción entre jugadores
- [Command System](command-system.md) - Generación dinámica de comandos
- [Broadcaster Service](broadcaster-service.md) - Envío de mensajes
