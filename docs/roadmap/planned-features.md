---
titulo: "Features Planificadas"
categoria: "Hoja de Ruta"
version: "1.0"
ultima_actualizacion: "2025-01-10"
autor: "Proyecto Runegram"
etiquetas: ["roadmap", "features", "planificacion"]
documentos_relacionados:
  - "vision-and-goals.md"
  - "combat-system-design.md"
  - "skill-system-design.md"
referencias_codigo: []
estado: "planificado"
audiencia: "desarrolladores"
---

# Features Planificadas

Este documento enumera las funcionalidades específicas planificadas para Runegram, organizadas por prioridad y categoría.

## 🚀 Próximas Grandes Funcionalidades

### 1. Sistema de Combate y Habilidades
**Prioridad:** Alta
**Estado:** Diseño completo
**Tiempo estimado:** 8-12 semanas

**Visión:** Crear un sistema de combate táctico por turnos y una progresión de habilidades basada en la mecánica de "aprender haciendo" (d100).

**Tareas:**

1. **Modelos de Datos**
   - Crear tablas `skills` y `character_skills` en la base de datos
   - Añadir atributos de combate al modelo `Character`:
     - `current_hp`, `max_hp`
     - `current_mana`, `max_mana`
     - Atributos primarios (Fuerza, Agilidad, Inteligencia)
   - Migración de base de datos correspondiente

2. **Mecánica d100**
   - Implementar `skill_service` con lógica central de resolución
   - Acción exitosa si `d100 <= nivel_de_habilidad`
   - Sistema de ganancia de experiencia en habilidades
   - Curvas de progresión equilibradas

3. **PNJs (Personajes No Jugadores)**
   - Crear `game_data/npc_prototypes.py`
   - Desarrollar modelo `NPC` en base de datos
   - Implementar `npc_service` para gestión de PNJs:
     - Sistema de spawn (aparición)
     - Sistema de despawn (desaparición)
     - IA básica (agresivo, pasivo, patrulla)
   - Sistema de respawn temporal para monstruos

4. **Comandos de Combate**
   - Crear `CommandSet` de `combat`
   - Implementar comandos:
     - `/atacar [objetivo]`
     - `/huir`
     - `/lanzar [hechizo] [objetivo]`
     - `/defender`
     - `/usar [objeto] [objetivo]`

**Ver:** [Sistema de Combate](combat-system-design.md) para diseño detallado

---

### 2. Sistema de Interacción Social
**Prioridad:** Alta
**Estado:** Implementación parcial
**Tiempo estimado:** 3-4 semanas

**Visión:** Hacer que el mundo se sienta verdaderamente multijugador, donde las acciones de un jugador son visibles y tienen un impacto en los demás.

**Tareas:**

1. **Refactorizar `/decir`**
   - Modificar para usar `broadcaster_service.send_message_to_room`
   - Todos los jugadores online en la sala deben ver el mensaje
   - Implementar variaciones narrativas

2. **Notificaciones de Movimiento**
   - Implementar mensajes de "entrada/salida" en `CmdMove`
   - Sala de origen: "Benabhi se marcha hacia el norte"
   - Sala de destino: "Benabhi llega desde el sur"
   - Solo notificar a jugadores online

3. **Notificaciones de Acción**
   - Modificar `/coger` y `/dejar` para notificar a la sala
   - Ejemplos:
     - "Benabhi coge una espada viviente"
     - "Benabhi deja una antorcha en el suelo"
   - Usar `broadcaster_service` para consistencia

4. **Expandir `/mirar`**
   - Permitir mirar a otros jugadores:
     - `/mirar Gandalf`
     - Mostrar descripción del personaje
   - Permitir mirar PNJs cuando se implementen
   - Mostrar equipamiento visible (futuro)

---

### 3. Sistema de Clases y Razas
**Prioridad:** Media
**Estado:** Diseño inicial
**Tiempo estimado:** 4-6 semanas

**Visión:** Permitir a los jugadores personalizar su personaje al inicio del juego, eligiendo una clase y/o raza que defina sus habilidades y `CommandSets` iniciales.

**Tareas:**

1. **Máquina de Estados Finitos (FSM)**
   - Utilizar sistema FSM de Aiogram
   - Flujo de creación de personaje por pasos:
     1. Nombre del personaje
     2. Elegir raza
     3. Elegir clase
     4. Confirmación
   - Botones inline para selección

2. **Prototipos de Clases/Razas**
   - Crear `game_data/class_prototypes.py`
   - Crear `game_data/race_prototypes.py`
   - Definir para cada prototipo:
     - Estadísticas iniciales
     - Habilidades base
     - `CommandSets` específicos
     - Descripción y lore

3. **Integración**
   - Modificar `player_service.create_character`
   - Leer elección del jugador desde FSM
   - Aplicar plantillas al nuevo personaje
   - Crear items iniciales según clase

---

## ✨ Mejoras del Motor y Calidad de Vida

### Expandir el Sistema de Locks
**Prioridad:** Media
**Tiempo estimado:** 2-3 semanas

**Tareas:**
- Implementar nuevas funciones de lock en `permission_service`:
  - `habilidad(nombre)>valor` - Requiere nivel de habilidad
  - `clase(nombre)` - Requiere clase específica
  - `raza(nombre)` - Requiere raza específica
  - `tiene_item_key(key)` - Requiere item específico en inventario
- Integrar locks en prototipos de `Exits`
- Modificar `world_loader_service` para aplicar locks de salidas
- Permitir puertas con llave y requisitos complejos

---

### Sistema de Contenedores
**Prioridad:** Media
**Tiempo estimado:** 2 semanas

**Estado:** Parcialmente implementado (falta capacidad y restricciones)

**Tareas:**
- Modificar modelo `Item` para contenedores:
  - Atributo `capacity` (capacidad máxima)
  - Método para calcular espacio usado
  - Validación de límites
- Mejorar comandos existentes:
  - `/meter` - Validar capacidad
  - `/sacar` - Mejorar feedback
  - `/inventario [contenedor]` - Mostrar capacidad usada/total
- Implementar locks en contenedores:
  - Contenedores con llave
  - Contenedores que requieren habilidad para abrir

---

### Bandeja de Entrada para Notificaciones
**Prioridad:** Baja
**Tiempo estimado:** 2 semanas

**Visión:** Guardar mensajes importantes para jugadores inactivos.

**Tareas:**
- Crear tabla `notification_inbox` en BD
- Modificar `pulse_service` para guardar tickers importantes
- Implementar comando `/buzon` o `/notificaciones`
- Mostrar notificaciones pendientes al reconectar
- Sistema de expiración de mensajes antiguos

---

### Detalles de Sala Interactivos
**Prioridad:** Baja
**Tiempo estimado:** 1-2 semanas

**Visión:** Permitir examinar detalles de salas sin crear objetos físicos.

**Tareas:**
- Expandir `room_prototypes.py` con campo `details`:
  ```python
  "details": {
      "cuadro": "Un antiguo retrato de un rey olvidado.",
      "ventana": "Por la ventana ves el bullicioso mercado."
  }
  ```
- Modificar `CmdLook` para buscar en detalles de sala
- Ejemplos:
  - `/mirar cuadro` - Muestra detalle "cuadro"
  - `/mirar ventana` - Muestra detalle "ventana"
- No son objetos cogibles, solo texto adicional

---

## 🎨 Mejoras de UX

### Sistema de Ayuda Contextual
**Prioridad:** Media
**Tiempo estimado:** 2 semanas

**Tareas:**
- Comando `/ayuda [comando]` mejorado
- Mostrar ejemplos de uso
- Integrar con documentación
- Ayuda contextual según situación del jugador

---

### Sistema de Tutoriales Integrados
**Prioridad:** Media
**Tiempo estimado:** 3-4 semanas

**Tareas:**
- Serie de salas tutorial para nuevos jugadores
- Quests tutorial que enseñen mecánicas básicas
- Sistema de logros para guiar progresión
- Recompensas por completar tutoriales

---

## 📊 Priorización General

### Alta Prioridad
1. Sistema de Interacción Social (refactorización)
2. Sistema de Combate y Habilidades
3. Expandir Sistema de Locks

### Media Prioridad
1. Sistema de Clases y Razas
2. Mejoras al Sistema de Contenedores
3. Sistema de Ayuda Contextual
4. Sistema de Tutoriales

### Baja Prioridad
1. Bandeja de Entrada para Notificaciones
2. Detalles de Sala Interactivos

---

## 📅 Roadmap Temporal Tentativo

### Q1 2025 (Enero - Marzo)
- ✅ Sistema de Broadcasting (completado)
- ✅ Sistema de Narrativa (completado)
- 🔄 Refactorización de comandos sociales
- 🔄 Expandir sistema de locks

### Q2 2025 (Abril - Junio)
- Sistema de combate básico
- Mecánica d100 de habilidades
- PNJs y comportamiento IA básico

### Q3 2025 (Julio - Septiembre)
- Sistema de clases y razas
- Mejoras a contenedores
- Sistema de tutoriales

### Q4 2025 (Octubre - Diciembre)
- Sistema de crafteo
- Sistema de quests básico
- Economía inicial

---

## Referencias

- [Visión y Objetivos](vision-and-goals.md) - Visión estratégica a largo plazo
- [Sistema de Combate](combat-system-design.md) - Diseño técnico del combate
- [Sistema de Habilidades](skill-system-design.md) - Diseño técnico de habilidades
- [Arquitectura](../architecture/) - Documentación técnica del motor

---

**Nota:** Este roadmap es tentativo y puede cambiar según prioridades del proyecto y feedback de la comunidad.

**Última actualización:** 2025-01-10
