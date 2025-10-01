# Guía Práctica: Creando Comandos

Esta guía te mostrará el proceso paso a paso para añadir un nuevo comando a Runegram. Gracias a la arquitectura del sistema, este proceso es sencillo y está bien estructurado.

Como ejemplo, crearemos un comando `/orar`, que permitirá a los jugadores rezar y recibir una bendición simple.

## Paso 1: Elegir o Crear el `CommandSet`

Primero, decide a qué grupo funcional pertenece tu nuevo comando. ¿Es una interacción general? ¿Una acción de combate? ¿Una habilidad de una clase específica?

Para nuestro comando `/orar`, parece una acción general de "rol-playing". Lo añadiremos al `CommandSet` `GENERAL_COMMANDS` que ya existe.

Si estuvieras creando un sistema completamente nuevo (ej: combate), crearías un nuevo archivo como `commands/player/combat.py` y una nueva lista exportada como `COMBAT_COMMANDS`.

## Paso 2: Crear la Clase del Comando

Abre el archivo correspondiente. En nuestro caso, `commands/player/general.py`. Al final del archivo, antes de la línea `GENERAL_COMMANDS = [...]`, añade la nueva clase para tu comando.

Toda clase de comando debe heredar de `Command` y definir, como mínimo, los atributos `names` y `description`, y sobrescribir el método `execute`.

```python
# En commands/player/general.py

# ... (importaciones y otras clases de comando) ...

class CmdOrar(Command):
    """
    Comando que permite al jugador rezar a los dioses.
    """
    # Lista de alias. El primero es el nombre principal.
    names = ["orar", "rezar"]

    # Descripción que aparecerá en la lista de comandos de Telegram.
    description = "Rezas a los dioses en busca de inspiración."

    # String de permisos. Una cadena vacía significa que no hay restricciones.
    lock = ""

    async def execute(
        self,
        character: Character,
        session: AsyncSession,
        message: types.Message,
        args: list[str]
    ):
        """
        La lógica que se ejecuta cuando un jugador escribe /orar.
        """
        try:
            # Aquí va la lógica de tu comando.
            # Puedes interactuar con los servicios, la base de datos, etc.

            # Para este ejemplo, solo enviaremos un mensaje al jugador.
            response_text = "Bajas la cabeza y murmuras una plegaria. Sientes una cálida sensación de esperanza."

            # También podrías notificar a otros en la sala (futura mejora del broadcaster).
            # await broadcaster_service.send_to_room_from_character(
            #     character, f"{character.name} baja la cabeza y reza en silencio."
            # )

            await message.answer(response_text)

        except Exception:
            # Un bloque try/except es una buena práctica para capturar errores
            # inesperados y evitar que el bot se caiga.
            await message.answer("❌ Ocurrió un error al intentar procesar tu plegaria.")
            logging.exception(f"Fallo al ejecutar /orar para {character.name}")

```

## Paso 3: Añadir el Comando al `CommandSet`

Ahora que la clase está creada, simplemente añade una instancia de ella a la lista del `CommandSet` al final del archivo.

```python
# En commands/player/general.py

# ... (definición de la clase CmdOrar) ...

# Exportamos la lista de comandos de este módulo.
GENERAL_COMMANDS = [
    CmdLook(),
    CmdSay(),
    CmdInventory(),
    CmdHelp(),
    CmdWho(),
    CmdOrar(),  # <-- AÑADE LA NUEVA INSTANCIA AQUÍ
]
```

## Paso 4: ¡Reiniciar y Probar!

**¡Y eso es todo!** No necesitas modificar el `dispatcher` ni ningún otro servicio del motor.

1.  Reinicia tus contenedores para que los cambios en el código se apliquen.
    ```bash
    docker-compose up -d
    ```
2.  Entra al juego y envía `/start`. El `command_service` detectará el nuevo comando en el `CommandSet` `general` y lo añadirá automáticamente a tu lista de comandos en Telegram.
3.  Prueba a ejecutar `/orar`. Deberías recibir el mensaje de respuesta que definiste.

Este flujo de trabajo demuestra el poder del sistema: añadir nuevas funcionalidades se reduce a crear un archivo autocontenido y añadir una sola línea a una lista, manteniendo el resto del motor intacto y estable.