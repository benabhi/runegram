---
título: "Índice de Creación de Contenido"
categoría: "Creación de Contenido"
audiencia: "creador-de-contenido"
versión: "1.0"
última_actualización: "2025-01-09"
autor: "Proyecto Runegram"
etiquetas: ["índice", "navegación", "creación-contenido"]
documentos_relacionados:
  - "getting-started/core-philosophy.md"
  - "engine-systems/README.md"
referencias_código:
  - "game_data/"
  - "commands/"
estado: "actual"
importancia: "alta"
---

# Creación de Contenido

Esta sección contiene guías para creadores de contenido que desean expandir el mundo de Runegram sin necesidad de programar el motor.

## ¿Qué es la Creación de Contenido?

Runegram separa el **motor** (código genérico en inglés) del **contenido** (datos específicos del juego en español). Como creador de contenido, trabajas con:

- **Prototipos de datos** (salas, items, canales) en `game_data/`
- **Comandos de jugador** en `commands/player/`
- **Scripts reactivos** para comportamientos personalizados
- **Templates de output** para mensajes visuales

No necesitas ser programador para expandir el mundo de Runegram. Esta documentación te enseña cómo.

---

## Documentos Disponibles

### 1. [Creando Comandos](creating-commands.md)
**Audiencia**: Desarrolladores principiantes, diseñadores con conocimiento de Python
**Contenido**:
- Estructura de un comando
- Clases en inglés, nombres en español (CRÍTICO)
- CommandSets disponibles
- Broadcasting y permisos
- Ejemplos completos

**Cuándo leer**: Cuando quieras agregar nueva funcionalidad al juego (ej. `/orar`, `/bailar`, `/dar`).

---

### 2. [Construyendo Salas](building-rooms.md)
**Audiencia**: Creadores de contenido, diseñadores de mundo
**Contenido**:
- Estructura de prototipos de salas
- Salidas bidireccionales
- Salidas con locks (cerraduras)
- Detalles interactivos
- Categorías y etiquetas
- Tick scripts para eventos periódicos

**Cuándo leer**: Cuando quieras expandir el mundo con nuevas locaciones.

---

### 3. [Creando Items](creating-items.md)
**Audiencia**: Creadores de contenido, diseñadores de items
**Contenido**:
- Estructura de prototipos de items
- Items con atributos
- Contenedores (mochilas, cofres)
- Locks para restricciones
- Items que otorgan comandos
- Scripts reactivos y proactivos

**Cuándo leer**: Cuando quieras agregar objetos al mundo (armas, pociones, llaves, contenedores).

---

### 4. [Escribiendo Scripts](writing-scripts.md)
**Audiencia**: Creadores de contenido (uso), desarrolladores (creación)
**Contenido**:
- Scripts reactivos (`on_look`)
- Scripts proactivos (`tick_scripts`)
- Sistema de pulse
- Crear nuevas funciones de script

**Cuándo leer**: Cuando quieras que objetos o salas tengan comportamientos especiales.

---

### 5. [Guía de Estilo de Output](output-style-guide.md) ⚠️ **OBLIGATORIO**
**Audiencia**: Todos los creadores de contenido y desarrolladores
**Contenido**:
- Las 4 categorías de output (CRÍTICO)
- Sistema de templates Jinja2
- Reglas de formato HTML
- Íconos y constantes
- Indentación de 4 espacios (REGLA DE ORO)
- Paginación y límites

**Cuándo leer**: **ANTES** de crear cualquier comando o modificar outputs. Esta es la guía más importante para mantener la consistencia visual.

---

## Orden de Lectura Recomendado

### Para Nuevos Creadores de Contenido

Si eres nuevo en Runegram, sigue este orden:

1. **Primero**: Lee [Filosofía del Proyecto](../getting-started/core-philosophy.md) para entender la separación motor/contenido
2. **Segundo**: Lee [Guía de Estilo de Output](output-style-guide.md) - **OBLIGATORIO**
3. **Tercero**: Construye salas con [Construyendo Salas](building-rooms.md)
4. **Cuarto**: Crea objetos con [Creando Items](creating-items.md)
5. **Quinto**: Agrega comandos con [Creando Comandos](creating-commands.md)
6. **Sexto**: Agrega comportamientos con [Escribiendo Scripts](writing-scripts.md)

### Para Desarrolladores de Comandos

Si quieres crear nuevos comandos:

1. Lee [Creando Comandos](creating-commands.md)
2. **OBLIGATORIO**: Lee [Guía de Estilo de Output](output-style-guide.md)
3. Revisa [Sistema de Comandos](../engine-systems/command-system.md) (arquitectura del motor)
4. Revisa [Sistema de Permisos](../engine-systems/permission-system.md) (locks)

### Para Diseñadores de Mundo

Si quieres expandir el mundo sin programar:

1. Lee [Construyendo Salas](building-rooms.md)
2. Lee [Creando Items](creating-items.md)
3. Lee [Escribiendo Scripts](writing-scripts.md) (sección "Para Diseñadores")
4. Revisa [Sistema de Prototipos](../engine-systems/prototype-system.md) (cómo funciona internamente)

---

## Recursos Importantes

### Archivos de Datos

Estos son los archivos que editarás como creador de contenido:

```
game_data/
├── room_prototypes.py       # Todas las salas del mundo
├── item_prototypes.py       # Todos los items del juego
├── channel_prototypes.py    # Canales de comunicación
└── narrative_messages.py    # Mensajes narrativos aleatorios
```

### Comandos de Jugador

Si creas nuevos comandos, trabajarás en:

```
commands/
├── command.py               # Clase base Command
└── player/
    ├── general.py           # Comandos generales
    ├── movement.py          # Comandos de movimiento
    ├── interaction.py       # Interacción con objetos
    ├── character.py         # Gestión de personaje
    ├── channels.py          # Canales de comunicación
    └── dynamic_channels.py  # Canales creados por jugadores
```

### Templates de Output

Para crear outputs visuales consistentes:

```
src/templates/
├── icons.py                 # Constantes de íconos
├── template_engine.py       # Motor Jinja2
└── base/
    ├── room.html.j2         # Template de salas
    ├── inventory.html.j2    # Template de inventario
    ├── character.html.j2    # Template de personaje
    └── help.html.j2         # Template de ayuda
```

---

## Filosofía de Diseño

### Motor vs. Contenido

**Motor** (`src/`, código en inglés):
- Define sistemas genéricos
- No conoce la semántica del juego
- Reutilizable y abstracto

**Contenido** (`game_data/`, `commands/`, español):
- Define QUÉ existe en el juego
- Semántica específica del mundo
- Fácilmente modificable

**Ejemplo**:
- Motor: Define qué es un `Item` (modelo genérico)
- Contenido: Define que existe una "espada de fuego" con atributos específicos

Ver: [Filosofía del Proyecto](../getting-started/core-philosophy.md)

---

## Convenciones Importantes

### Nomenclatura

- **Clases de comandos**: SIEMPRE en inglés (`CmdLook`, `CmdPray`, NO `CmdMirar`)
- **Nombres de comandos**: En español (`/mirar`, `/orar`, `/coger`)
- **Prototipos**: Claves en inglés con guiones bajos (`"taverna_dragones"`)
- **Variables en código**: Inglés (`character`, `item`, `room`)
- **Descripciones de juego**: Español

### Formato de Outputs

**Las 4 Categorías (CRÍTICO)**:

1. **Outputs Descriptivos**: `<pre>` + MAYÚSCULAS + listas con 4 espacios
2. **Notificaciones Sociales**: `<i>` + tercera persona + sin íconos
3. **Notificaciones Privadas**: `<i>` + segunda persona + sin íconos
4. **Feedback de Acciones**: Texto plano + íconos de estado opcionales

Ver: [Guía de Estilo de Output](output-style-guide.md) - **LECTURA OBLIGATORIA**

---

## Herramientas de Admin

Comandos útiles para creadores de contenido:

### Gestión de Salas

```
/teletransportar <room_key>      # Ir a cualquier sala
/listarsalas [cat:X] [tag:Y]     # Listar salas con filtros
/examinarsala                     # Ver información técnica de sala actual
```

### Gestión de Items

```
/generarobjeto <item_key>         # Crear objeto del prototipo
/listaritems [cat:X] [tag:Y]      # Listar items con filtros
/destruirobjeto <objeto>          # Eliminar objeto
```

### Gestión de Personajes

```
/asignarrol <jugador> <rol>       # Cambiar rol de jugador
/personajes                       # Listar todos los personajes
```

Ver: [Guía de Admin](../admin-guide/admin-commands.md)

---

## Flujo de Trabajo Recomendado

### 1. Diseñar en Papel

Antes de editar archivos:
- Dibuja mapas de salas y sus conexiones
- Lista items y sus propiedades
- Define comandos nuevos que necesitas

### 2. Implementar Prototipos

Edita archivos en `game_data/`:
- Agrega salas a `room_prototypes.py`
- Agrega items a `item_prototypes.py`
- Verifica sintaxis Python

### 3. Reiniciar y Probar

```bash
docker-compose restart
```

Prueba en Telegram:
- Visita tus nuevas salas
- Crea y prueba objetos
- Verifica salidas y locks

### 4. Iterar

- Ajusta descripciones
- Equilibra atributos de items
- Refina locks y restricciones

---

## Preguntas Frecuentes

### ¿Necesito saber programar?

**Para crear salas e items**: NO. Solo editas archivos de datos Python simples.

**Para crear comandos**: Sí, conocimiento básico de Python async y Aiogram.

**Para crear scripts**: Conocimiento básico de Python para leer código existente.

### ¿Cómo pruebo mis cambios?

1. Edita archivos de prototipos
2. Reinicia el bot: `docker-compose restart`
3. Conéctate con Telegram
4. Usa comandos de admin para probar

### ¿Puedo romper algo?

Los prototipos de datos son **seguros de editar**. Errores de sintaxis Python impedirán que el bot inicie, pero no dañarán la base de datos.

**Recomendación**: Haz backups de tus archivos de prototipos antes de cambios grandes.

### ¿Dónde pido ayuda?

1. Revisa esta documentación
2. Examina ejemplos en `game_data/`
3. Lee código de comandos similares
4. Consulta con desarrolladores del proyecto

---

## Próximos Pasos

1. **Lee la filosofía**: [Core Philosophy](../getting-started/core-philosophy.md)
2. **Lee la guía de estilo**: [Output Style Guide](output-style-guide.md) - **OBLIGATORIO**
3. **Explora ejemplos**: Revisa `game_data/room_prototypes.py` y `game_data/item_prototypes.py`
4. **Experimenta**: Crea tu primera sala o item
5. **Contribuye**: Expande el mundo de Runegram

---

**¡Bienvenido a la creación de contenido en Runegram! El mundo está esperando tu creatividad.**
