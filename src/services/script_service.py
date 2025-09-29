# src/services/script_service.py

import re
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.character import Character
from src.models.item import Item

# En el futuro, este podría ser un broadcaster más complejo.
# Por ahora, es una función simple para enviar mensajes al jugador.
async def _send_message_to_character(character: Character, message_text: str):
    from src.bot.bot import bot
    await bot.send_message(chat_id=character.account.telegram_id, text=message_text)


# --- Definiciones de las Funciones de Script ---

async def script_notificar_brillo_magico(session: AsyncSession, character: Character, target: Item, **kwargs):
    """Un script que notifica al jugador que un objeto brilla al ser mirado."""
    color = kwargs.get("color", "una luz misteriosa")
    message = f"🌟 Al fijar tu vista en {target.get_name()}, notas que emite un suave brillo de color {color}."
    await _send_message_to_character(character, message)


# --- El "Motor" de Scripts ---

SCRIPT_REGISTRY = {
    "script_notificar_brillo_magico": script_notificar_brillo_magico,
}

def _parse_script_string(script_string: str) -> tuple[str, dict]:
    """
    Parsea un string de script como 'nombre_script(key1=val1, key2=val2)'
    y devuelve el nombre y un diccionario de argumentos.
    """
    match = re.match(r"(\w+)\((.*)\)", script_string)
    if not match:
        return script_string, {}

    name, args_str = match.groups()
    kwargs = {}
    if args_str:
        try:
            # Esto es un parser simple, para producción se necesitaría algo más robusto.
            kwargs = dict(arg.strip().split('=') for arg in args_str.split(','))
        except ValueError:
            print(f"ADVERTENCIA: Argumentos de script mal formados en '{script_string}'")
    return name, kwargs


async def execute_script(script_string: str, session: AsyncSession, **context):
    """
    El corazón del motor. Parsea el string del script y ejecuta la función correspondiente.
    'context' contiene las entidades relevantes al evento (character, target, etc.).
    """
    if not script_string:
        return

    script_name, kwargs = _parse_script_string(script_string)

    if script_name in SCRIPT_REGISTRY:
        script_function = SCRIPT_REGISTRY[script_name]
        await script_function(session=session, **context, **kwargs)
    else:
        print(f"ADVERTENCIA: Se intentó ejecutar un script desconocido: {script_name}")