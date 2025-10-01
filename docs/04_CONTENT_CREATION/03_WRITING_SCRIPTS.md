# Guía Práctica: Escribiendo Scripts

El Motor de Scripts es lo que permite que el contenido del juego tenga comportamiento. Es el puente que conecta las definiciones de datos con la lógica del motor, dando vida a los objetos y al mundo.

Esta guía se divide en dos partes:
1.  **Para Diseñadores de Contenido:** Cómo *usar* los scripts existentes en los prototipos.
2.  **Para Desarrolladores del Motor:** Cómo *crear* nuevas funciones de script.

## 1. Para Diseñadores de Contenido: Usando Scripts

Como diseñador, no necesitas escribir código Python. Solo necesitas saber qué "habilidades" de script existen y cómo invocarlas desde los archivos de `game_data`.

Los scripts se invocan a través de `script strings`, que tienen un formato de llamada de función: `nombre_del_script(argumento=valor)`.

### Usando Scripts de Evento (`on_look`)

Los scripts de evento reaccionan a las acciones de los jugadores. Actualmente, el principal evento es `on_look`.

*   **Uso:** Se añade a la clave `"scripts"` en el prototipo de un objeto.
*   **Función Disponible:** `script_notificar_brillo_magico(color=...)`
    *   **Propósito:** Envía un mensaje privado al jugador que mira el objeto, indicando que este emite un brillo.
    *   **Argumento:** `color` (opcional, string). Define el color del brillo. Si no se especifica, usa un color por defecto.

**Ejemplo:**
```python
# En game_data/item_prototypes.py
"amuleto_antiguo": {
    "name": "un amuleto antiguo",
    "description": "Una joya opaca que parece absorber la luz.",
    "scripts": {
        "on_look": "script_notificar_brillo_magico(color=púrpura)"
    }
}
```
**Resultado:** Cuando un jugador escriba `/mirar amuleto`, primero verá la descripción y luego recibirá un mensaje privado que dice: "...notas que emite un suave brillo de color púrpura."

### Usando Scripts Proactivos (`tickers`)

Los tickers hacen que el mundo actúe por sí solo. Se definen en la clave `"tickers"` de un prototipo.

*   **Uso:** Es una lista de diccionarios, donde cada diccionario es una tarea programada.
*   **Claves:**
    *   `"schedule"`: Define cuándo se ejecuta. Puede ser un `cron` (ej: `"*/5 * * * *"`) o un intervalo en segundos (ej: `"interval:30"`).
    *   `"script"`: El `script_string` a ejecutar.
    *   `"category"`: La categoría. Si es `"ambient"`, solo se ejecutará para jugadores considerados "online", para no enviar spam.

*   **Función Disponible:** `script_espada_susurra_secreto()`
    *   **Propósito:** Envía un mensaje privado a cada jugador "online" en la misma sala que el objeto, con un "secreto" aleatorio.
    *   **Argumentos:** Ninguno.

**Ejemplo:**
```python
# En game_data/item_prototypes.py
"craneo_susurrante": {
    "name": "un cráneo susurrante",
    "description": "Un cráneo amarillento que parece murmurar cuando no lo miras directamente.",
    "tickers": [{
        "schedule": "*/5 * * * *", # Cada 5 minutos
        "script": "script_espada_susurra_secreto",
        "category": "ambient"
    }]
}
```
**Resultado:** Cada 5 minutos, todos los jugadores activos en la misma sala que el cráneo recibirán un mensaje privado con un susurro.

## 2. Para Desarrolladores del Motor: Creando Nuevas Funciones de Script

Para expandir las capacidades del juego, los desarrolladores del motor pueden crear nuevas funciones de script. El proceso es simple y seguro.

**Archivo a editar:** `src/services/script_service.py`

### Paso 1: Escribir la Función de Lógica

Crea una nueva función `async` en la "SECCIÓN 1" del archivo. La función debe aceptar `session` y `**context` como argumentos. El `context` es un diccionario que contiene los objetos relevantes al evento que disparó el script.

**Ejemplo:** Vamos a crear un script que cure ligeramente al personaje que mira un objeto.

```python
# En src/services/script_service.py

# ... (otras importaciones) ...

async def script_curacion_menor(session: AsyncSession, character: Character, target: Item, **kwargs):
    """
    Script de evento: Cura una pequeña cantidad de vida al personaje.

    - Disparador Típico: on_look
    - Contexto Esperado: character (quien es curado), target (el objeto que cura).
    - Argumentos: cantidad (int, opcional)
    """
    # (Lógica futura: cuando el personaje tenga un atributo de vida)
    # curacion = int(kwargs.get("cantidad", 5))
    # character.vida_actual += curacion
    # await session.commit()

    # Por ahora, solo notificamos al jugador.
    mensaje = f"Sientes una oleada de energía restauradora emanando de {target.get_name()}."
    await broadcaster_service.send_message_to_character(character, mensaje)
```

### Paso 2: Registrar la Nueva Función

Añade la función y su nombre en string al diccionario `SCRIPT_REGISTRY` en la "SECCIÓN 2".

```python
# En src/services/script_service.py

SCRIPT_REGISTRY = {
    "script_notificar_brillo_magico": script_notificar_brillo_magico,
    "script_espada_susurra_secreto": script_espada_susurra_secreto,

    # --- NUEVO SCRIPT REGISTRADO ---
    "script_curacion_menor": script_curacion_menor,
}
```

### Paso 3: Documentar para Diseñadores

¡Listo! La nueva "habilidad" del motor está disponible. Ahora un diseñador de contenido puede crear un objeto como este:

```python
# En game_data/item_prototypes.py
"piedra_vital": {
    "name": "una piedra de vitalidad",
    "description": "Una piedra suave y cálida al tacto.",
    "scripts": {
        "on_look": "script_curacion_menor(cantidad=10)"
    }
}
```

Este ciclo de desarrollo (crear, registrar, usar) permite al motor crecer en capacidades sin mezclar su lógica con la definición del contenido.