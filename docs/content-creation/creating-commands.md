---
título: "Creando Comandos en Runegram"
categoría: "Creación de Contenido"
audiencia: "creador-de-contenido"
versión: "1.0"
última_actualización: "2025-01-09"
autor: "Proyecto Runegram"
etiquetas: ["comandos", "desarrollo", "python", "aiogram"]
documentos_relacionados:
  - "engine-systems/command-system.md"
  - "getting-started/core-philosophy.md"
  - "content-creation/output-style-guide.md"
referencias_código:
  - "commands/player/general.py"
  - "commands/player/interaction.py"
  - "commands/command.py"
  - "src/handlers/player/dispatcher.py"
estado: "actual"
importancia: "alta"
---

# Creando Comandos en Runegram

Esta guía te muestra el proceso paso a paso para agregar un nuevo comando a Runegram. Gracias a la arquitectura del sistema, este proceso es directo y bien estructurado.

Como ejemplo, crearemos un comando `/orar` que permite a los jugadores rezar y recibir una bendición simple.

## CRÍTICO: Convención de Nombres de Clases

**REGLA FUNDAMENTAL**: Las clases de comandos **SIEMPRE DEBEN** estar en **inglés**, independientemente del idioma del comando.

```python
# ✅ CORRECTO
class CmdLook(Command):
    names = ["mirar", "m", "l"]  # Nombres de comandos en español

class CmdPray(Command):
    names = ["orar", "rezar"]  # Nombres de comandos en español

# ❌ INCORRECTO
class CmdMirar(Command):  # Nombre de clase en español - MAL
    names = ["mirar", "m"]

class CmdOrar(Command):  # Nombre de clase en español - MAL
    names = ["orar", "rezar"]
```

**Por qué es importante:**
- El código del Motor (engine) está en inglés
- El Contenido (content) está en español
- Los nombres de clases son parte de la capa del motor
- Los nombres de comandos (atributo `names`) son parte de la capa de contenido

Ver: `docs/getting-started/core-philosophy.md` para la filosofía completa motor/contenido.

## Paso 1: Elegir o Crear el CommandSet

Primero, decide a qué grupo funcional pertenece tu nuevo comando. ¿Es una interacción general? ¿Una acción de combate? ¿Una habilidad específica de clase?

Para nuestro comando `/orar`, parece una acción general de roleplay. Lo agregaremos al CommandSet existente `GENERAL_COMMANDS`.

Si estuvieras creando un sistema completamente nuevo (ej. combate), crearías un nuevo archivo como `commands/player/combat.py` y exportarías una nueva lista como `COMBAT_COMMANDS`.

### CommandSets Disponibles

CommandSets actuales en el sistema:
- `GENERAL_COMMANDS` - Comandos básicos (`/mirar`, `/inventario`, `/ayuda`, `/quien`, `/orar`, etc.)
- `MOVEMENT_COMMANDS` - Comandos de movimiento (`/norte`, `/sur`, `/este`, `/oeste`, etc.)
- `INTERACTION_COMMANDS` - Interacción con objetos (`/coger`, `/dejar`, `/meter`, `/sacar`, etc.)
- `CHANNEL_COMMANDS` - Canales de comunicación (dinámicos, basados en prototipos)
- `DYNAMIC_CHANNEL_COMMANDS` - Canales creados por jugadores (`/crearcanal`, `/invitar`, etc.)
- `LISTING_COMMANDS` - Comandos de listado (`/items`, `/personajes`, etc.)
- `CHARACTER_COMMANDS` - Gestión de personajes (`/personaje`, `/suicidio`, etc.)
- `SETTINGS_COMMANDS` - Configuración de jugador (`/activarcanal`, `/desactivarcanal`, etc.)

Ver: directorio `commands/player/` para todos los CommandSets disponibles.

## Paso 2: Crear la Clase del Comando

Abre el archivo correspondiente. En nuestro caso, `commands/player/general.py`. Al final del archivo, antes de la línea `GENERAL_COMMANDS = [...]`, agrega tu nueva clase de comando.

Cada clase de comando debe heredar de `Command` y definir, como mínimo, los atributos `names` y `description`, y sobrescribir el método `execute`.

```python
# En commands/player/general.py

# ... (imports y otras clases de comandos) ...

class CmdPray(Command):
    """
    Comando que permite al jugador rezar a los dioses.
    """
    # Lista de aliases. El primero es el nombre principal.
    names = ["orar", "rezar"]

    # Descripción que aparece en la lista de comandos de Telegram.
    description = "Rezas a los dioses en busca de inspiración."

    # String de permisos. Un string vacío significa sin restricciones.
    lock = ""

    async def execute(
        self,
        character: Character,
        session: AsyncSession,
        message: types.Message,
        args: list[str]
    ):
        """
        Lógica que se ejecuta cuando un jugador escribe /orar.
        """
        try:
            # Aquí va la lógica de tu comando.
            # Puedes interactuar con servicios, base de datos, etc.

            # Para este ejemplo, solo enviaremos un mensaje al jugador.
            response_text = "Bajas la cabeza y murmuras una plegaria. Sientes una cálida sensación de esperanza."

            # También podrías notificar a otros en la sala (usando broadcaster).
            # await broadcaster_service.send_message_to_room(
            #     session=session,
            #     room_id=character.room_id,
            #     message_text=f"<i>{character.name} baja la cabeza y reza en silencio.</i>",
            #     exclude_character_id=character.id
            # )

            await message.answer(response_text)

        except Exception:
            # Un bloque try/except es buena práctica para capturar errores
            # inesperados y prevenir que el bot se caiga.
            await message.answer("❌ Ocurrió un error al intentar procesar tu plegaria.")
            logging.exception(f"Fallo al ejecutar /orar para {character.name}")

```

## Paso 3: Agregar el Comando al CommandSet

Ahora que la clase está creada, simplemente agrega una instancia de ella a la lista CommandSet al final del archivo.

```python
# En commands/player/general.py

# ... (definición de clase CmdPray) ...

# Exportar la lista de comandos de este módulo.
GENERAL_COMMANDS = [
    CmdLook(),
    CmdSay(),
    CmdEmotion(),
    CmdInventory(),
    CmdHelp(),
    CmdWho(),
    CmdPray(),  # <-- AGREGAR LA NUEVA INSTANCIA AQUÍ
    CmdDisconnect(),
    CmdAFK(),
    CmdWhisper(),
]
```

## Paso 4: ¡Reiniciar y Probar!

**¡Y eso es todo!** No necesitas modificar el `dispatcher` o ningún otro servicio del motor.

1. Reinicia tus contenedores para que los cambios en el código tengan efecto.
   ```bash
   docker-compose restart
   ```
2. Entra al juego y envía `/start`. El `command_service` detectará el nuevo comando en el CommandSet `general` y automáticamente lo agregará a tu lista de comandos de Telegram.
3. Prueba ejecutando `/orar`. Deberías recibir el mensaje de respuesta que definiste.

Este flujo de trabajo demuestra el poder del sistema: agregar nueva funcionalidad se reduce a crear un archivo autocontenido y agregar una sola línea a una lista, manteniendo el resto del motor intacto y estable.

## Avanzado: Usar el Broadcaster Service

Si tu comando debe notificar a otros jugadores en la sala (acciones sociales), usa el `broadcaster_service`:

```python
from src.services import broadcaster_service

class CmdDance(Command):
    names = ["bailar", "dance"]
    description = "Bailas con entusiasmo."
    lock = ""

    async def execute(self, character, session, message, args):
        try:
            # Confirmar al jugador que actúa
            await message.answer("¡Comienzas a bailar!")

            # Notificar a otros en la sala (excluir al bailarín)
            await broadcaster_service.send_message_to_room(
                session=session,
                room_id=character.room_id,
                message_text=f"<i>{character.name} comienza a bailar con entusiasmo.</i>",
                exclude_character_id=character.id
            )
        except Exception:
            await message.answer("❌ Error al bailar.")
            logging.exception(f"Error en /bailar para {character.name}")
```

**Importante**: El broadcaster automáticamente filtra jugadores offline. No necesitas verificar manualmente.

Ver: `docs/engine-systems/social-systems.md` para documentación completa sobre broadcasting.

## Avanzado: Comandos con Argumentos

Para comandos que aceptan argumentos:

```python
class CmdGive(Command):
    names = ["dar", "give"]
    description = "Le das un objeto a otro jugador. Uso: /dar <objeto> <jugador>"
    lock = ""

    async def execute(self, character, session, message, args):
        try:
            # Validar argumentos
            if len(args) < 2:
                await message.answer("Uso: /dar <objeto> <jugador>")
                return

            item_name = args[0].lower()
            target_name = " ".join(args[1:]).lower()

            # Buscar item en inventario
            item = find_item_in_list(item_name, character.items)
            if not item:
                await message.answer(f"No tienes '{item_name}'.")
                return

            # Buscar personaje objetivo en la sala
            target_char = None
            for other_char in character.room.characters:
                if other_char.id != character.id and other_char.name.lower() == target_name:
                    target_char = other_char
                    break

            if not target_char:
                await message.answer(f"No ves a '{target_name}' por aquí.")
                return

            # Verificar que el objetivo está online
            if not await online_service.is_character_online(target_char.id):
                await message.answer(f"No ves a '{target_name}' por aquí.")
                return

            # Transferir item
            item.owner_character_id = target_char.id
            item.in_room_id = None
            await session.commit()

            # Feedback al que da
            await message.answer(f"Le das {item.get_name()} a {target_char.name}.")

            # Notificar al receptor
            await broadcaster_service.send_message_to_character(
                target_char,
                f"<i>{character.name} te da: {item.get_name()}</i>"
            )

            # Notificar a la sala (opcional)
            await broadcaster_service.send_message_to_room(
                session=session,
                room_id=character.room_id,
                message_text=f"<i>{character.name} le da algo a {target_char.name}.</i>",
                exclude_character_id=character.id
            )

        except Exception:
            await message.answer("❌ Error al dar objeto.")
            logging.exception(f"Error en /dar para {character.name}")
```

## Avanzado: Comandos con Permisos (Locks)

Para restringir un comando a admins o roles específicos:

```python
class CmdTeleport(Command):
    names = ["teletransportar", "teleport", "tp"]
    description = "Teletransporta a un jugador. Uso: /tp <jugador> <sala_key>"
    lock = "rol(ADMIN)"  # Solo ADMIN y SUPERADMIN pueden usar esto

    async def execute(self, character, session, message, args):
        try:
            if len(args) < 2:
                await message.answer("Uso: /tp <jugador> <sala_key>")
                return

            # ... lógica de teletransporte ...

        except Exception:
            await message.answer("❌ Error al teletransportar.")
            logging.exception(f"Error en /tp para {character.name}")
```

**Funciones de lock disponibles:**
- `rol(ADMIN)` - Admin o superior
- `rol(SUPERADMIN)` - Solo superadmin
- `tiene_objeto(item_key)` - Tiene objeto específico
- Combinar con `and`, `or`: `"rol(ADMIN) and tiene_objeto(llave_maestra)"`

Ver: `docs/engine-systems/permission-system.md` para documentación completa sobre locks.

## Guía de Estilo de Output

**CRÍTICO**: Todos los outputs de comandos DEBEN seguir las 4 categorías de output definidas en la guía de estilo.

### Las 4 Categorías:

1. **Outputs Descriptivos** (`/mirar`, `/inventario`)
   - Usar wrapper `<pre>`
   - Títulos en MAYÚSCULAS con íconos
   - Listas con **4 espacios + guion** (`    - `)
   - Detalle rico, formato estructurado

2. **Notificaciones Sociales** (broadcasts)
   - Usar wrapper `<i>` (itálica)
   - NO `<pre>`
   - NO íconos
   - Tercera persona ("Gandalf se va...")

3. **Notificaciones Privadas** (susurros, mensajes directos)
   - Usar wrapper `<i>` (itálica)
   - NO `<pre>`
   - NO íconos
   - Segunda persona ("te susurra...")

4. **Feedback de Acciones** (mensajes de éxito/error)
   - Texto plano (no `<pre>` a menos que sea lista compleja)
   - Íconos de estado opcionales (✅❌❓⚠️)
   - Conciso y claro

**Ejemplos de outputs:**

```python
# Output descriptivo
output = f"""<pre>{ICONS['room']} <b>PLAZA CENTRAL</b>
Estás en el corazón de la ciudad.

{ICONS['item']} <b>Cosas a la vista:</b>
    - ⚔️ una espada
    - 🎒 una mochila</pre>"""

# Notificación social (broadcast)
broadcast = f"<i>{character.name} coge una espada del suelo.</i>"

# Notificación privada
private = f"<i>{sender.name} te susurra: \"Hola\"</i>"

# Feedback de acción
feedback = f"Has cogido: una espada."
error = f"❌ No encuentras ese objeto."
```

**OBLIGATORIO**: Leer `docs/content-creation/output-style-guide.md` antes de crear cualquier comando.

## Checklist de Pruebas

Antes de considerar tu comando completo:

- [ ] Nombre de clase en inglés (ej. `CmdPray`, NO `CmdOrar`)
- [ ] Nombres de comandos (atributo `names`) en español
- [ ] Primer alias en `names` es el nombre principal del comando
- [ ] Incluye docstring apropiado
- [ ] Tiene manejo de errores (try/except)
- [ ] Proporciona feedback claro al usuario
- [ ] Usa constantes `ICONS`, no emojis hardcodeados
- [ ] Sigue una de las 4 categorías de output
- [ ] Outputs descriptivos usan `<pre>` e indentación de 4 espacios
- [ ] Acciones sociales usan broadcaster (si son visibles para otros)
- [ ] Filtra jugadores offline (si interactúa con otros personajes)
- [ ] Loguea excepciones con `logging.exception()`
- [ ] Agregado a la lista de exportación del CommandSet apropiado
- [ ] Probado en cliente Telegram real

## Errores Comunes

### ❌ Hardcodear emojis en lugar de usar ICONS

```python
# MAL
await message.answer("🏛️ Plaza Central")

# BIEN
from src.templates import ICONS
await message.answer(f"{ICONS['room']} Plaza Central")
```

### ❌ No filtrar jugadores offline

```python
# MAL - muestra jugadores offline
for char in character.room.characters:
    print(char.name)

# BIEN - filtra offline automáticamente
from src.services import online_service
for char in character.room.characters:
    if await online_service.is_character_online(char.id):
        print(char.name)
```

### ❌ Usar `<pre>` para notificaciones sociales

```python
# MAL
broadcast = f"<pre><i>{character.name} se va.</i></pre>"

# BIEN
broadcast = f"<i>{character.name} se va.</i>"
```

### ❌ Nombre de clase en español

```python
# MAL
class CmdMirar(Command):
    names = ["mirar", "m"]

# BIEN
class CmdLook(Command):
    names = ["mirar", "m"]
```

## Resumen

Crear un comando en Runegram:

1. Decide a qué CommandSet pertenece
2. Crea clase heredando de `Command` (nombre en inglés)
3. Define `names` (español), `description`, `lock`, y `execute()`
4. Agrega instancia a la lista de exportación del CommandSet
5. Reinicia y prueba

La separación entre motor (inglés, genérico) y contenido (español, específico) mantiene el código mantenible y escalable.

---

**Documentación Relacionada:**
- [Arquitectura del Sistema de Comandos](../engine-systems/command-system.md)
- [Guía de Estilo de Output](output-style-guide.md) - **LECTURA OBLIGATORIA**
- [Filosofía del Proyecto](../getting-started/core-philosophy.md)
- [Sistema de Permisos](../engine-systems/permission-system.md)
- [Sistemas Sociales](../engine-systems/social-systems.md)
