---
título: "Escribiendo Scripts en Runegram"
categoría: "Creación de Contenido"
audiencia: "creador-de-contenido, desarrollador"
versión: "1.0"
última_actualización: "2025-01-09"
autor: "Proyecto Runegram"
etiquetas: ["scripts", "prototipos", "eventos", "tick_scripts", "pulse"]
documentos_relacionados:
  - "engine-systems/pulse-system.md"
  - "engine-systems/script-system.md"
  - "content-creation/creating-items.md"
referencias_código:
  - "src/services/script_service.py"
  - "game_data/item_prototypes.py"
estado: "actual"
importancia: "alta"
---

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

### Usando Scripts Proactivos (`tick_scripts`)

Los tick_scripts hacen que el mundo actúe por sí solo, ejecutándose basándose en el sistema de pulse global. Se definen en la clave `"tick_scripts"` de un prototipo.

*   **Uso:** Es una lista de diccionarios, donde cada diccionario define cuándo y cómo se ejecuta el script.
*   **Claves:**
    *   `"interval_ticks"`: Cada cuántos ticks se ejecuta. Con la configuración por defecto (tick=2s), usa la fórmula: `segundos_deseados / 2`.
    *   `"script"`: El `script_string` a ejecutar.
    *   `"category"`: La categoría. Si es `"ambient"`, solo se ejecutará para jugadores considerados "online".
    *   `"permanent"`: `True` (se repite indefinidamente) o `False` (se ejecuta una sola vez).

*   **Función Disponible:** `script_espada_susurra_secreto()`
    *   **Propósito:** Envía un mensaje privado a cada jugador "online" en la misma sala que el objeto, con un "secreto" aleatorio.
    *   **Argumentos:** Ninguno.

**Ejemplo:**
```python
# En game_data/item_prototypes.py
"craneo_susurrante": {
    "name": "un cráneo susurrante",
    "description": "Un cráneo amarillento que parece murmurar cuando no lo miras directamente.",
    "tick_scripts": [{
        "interval_ticks": 150,  # Cada 150 ticks (300 segundos = 5 minutos)
        "script": "script_espada_susurra_secreto",
        "category": "ambient",
        "permanent": True  # Se repite indefinidamente
    }]
}
```
**Resultado:** Cada 5 minutos, todos los jugadores activos en la misma sala que el cráneo recibirán un mensaje privado con un susurro.

**Cálculo de `interval_ticks`:**
- 10 segundos → `10 / 2 = 5 ticks`
- 1 minuto → `60 / 2 = 30 ticks`
- 5 minutos → `300 / 2 = 150 ticks`
- 1 hora → `3600 / 2 = 1800 ticks`

Ver: `docs/engine-systems/pulse-system.md` para más detalles sobre el sistema de pulse.

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

---

**Documentación Relacionada:**
- [Sistema de Pulse](../engine-systems/pulse-system.md)
- [Sistema de Scripts](../engine-systems/scripting-system.md)
- [Creando Items](creating-items.md)
