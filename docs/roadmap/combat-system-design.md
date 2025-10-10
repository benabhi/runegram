---
titulo: "Diseño del Sistema de Combate"
categoria: "Hoja de Ruta"
version: "1.0"
ultima_actualizacion: "2025-01-10"
autor: "Proyecto Runegram"
etiquetas: ["combate", "diseño", "mecanicas", "no-implementado"]
documentos_relacionados:
  - "skill-system-design.md"
  - "planned-features.md"
  - "vision-and-goals.md"
referencias_codigo: []
estado: "planificado"
audiencia: "desarrolladores"
---

# ⚠️ Sistema de Combate - DISEÑO NO IMPLEMENTADO

**IMPORTANTE:** Este documento describe un sistema que está en **fase de diseño** y **NO ha sido implementado aún**. No intentes usar estos comandos o mecánicas en el código actual del proyecto.

---

# Sistema de Combate

Este documento describe el diseño propuesto para el Sistema de Combate de Runegram.

## Visión General

El Sistema de Combate de Runegram será un sistema **táctico por turnos** diseñado para la interfaz de un MUD de texto. Se centrará en:

- **Claridad de la información** - Estado del combate siempre visible
- **Decisiones significativas** - Cada acción del jugador importa
- **Optimización móvil** - Interfaz clara en pantallas pequeñas
- **Feedback inmediato** - Resultados claros de cada acción

## Flujo de un Turno de Combate

### 1. Iniciación del Combate

El combate comienza cuando:
- Un jugador ataca a un PNJ agresivo
- Un PNJ agresivo ataca a un jugador
- Un jugador ataca a otro jugador (PvP, si está habilitado)

**Acciones del sistema:**
- Todos los participantes en la sala entran en "modo de combate"
- Se determina el orden de acción inicial
- Se muestra el estado de combate a todos los participantes

### 2. Cola de Acciones

**Orden de acción determinado por:**
- Atributo de Agilidad/Iniciativa
- Bonificaciones de equipamiento
- Efectos de habilidades activas

**Formato de visualización:**
```
⚔️ COMBATE EN CURSO ⚔️

Orden de turno:
1. Elfo Arquero (PNJ)
2. Benabhi (Jugador)
3. Orco Guerrero (PNJ)

Tu turno: Usa /atacar, /lanzar, /huir, /defender
```

### 3. Resolución de Acciones

Cada acción se resuelve secuencialmente:

**a) Declaración**
- El jugador ejecuta su comando (`/atacar orco`)
- Se validan requisitos (rango, maná, equipamiento)

**b) Resolución**
- Se calcula probabilidad de éxito (sistema d100)
- Se determina daño/efecto
- Se aplican modificadores (críticos, resistencias)

**c) Feedback**
- Mensaje de resultado al actor
- Mensaje de observación a espectadores
- Actualización de estado de combate

### 4. Fin del Turno

Se muestra un resumen del turno:

```
📊 Resumen del Turno #3:

• Elfo Arquero dispara a Orco Guerrero por 12 HP
• Benabhi ataca a Orco Guerrero por 8 HP
• Orco Guerrero ataca a Benabhi por 15 HP

Estado actual:
🧝 Elfo Arquero: 45/45 HP
⚔️ Benabhi: 35/50 HP
👹 Orco Guerrero: 25/60 HP
```

### 5. Comprobación de Fin de Combate

El combate termina cuando:
- Solo queda un bando en pie
- Todos los participantes huyen
- Se cumple una condición especial (tiempo, evento)

**Acciones al terminar:**
- Distribución de experiencia
- Loot de objetos derrotados
- Restauración de estado (fuera de combate)

---

## Comandos de Combate

### CommandSet: `combat`

Este conjunto de comandos se activa automáticamente al entrar en combate.

#### `/atacar <objetivo>`
**Alias:** `/atk`, `/attack`

Realiza un ataque físico básico contra un objetivo.

**Mecánica:**
- Usa habilidad de arma equipada (espadas, hachas, etc.)
- Tirada: `d100 <= nivel_habilidad_arma`
- Daño base: `arma.damage + (Fuerza / 10)`
- Crítico: 5% de probabilidad, daño x2

**Ejemplo:**
```
> /atacar orco

Blandiendo tu espada oxidada, golpeas al Orco Guerrero.
🎯 Impacto: 12 HP de daño

Orco Guerrero: 48/60 HP
```

#### `/lanzar <hechizo> <objetivo>`
**Alias:** `/cast`

Lanza un hechizo contra un objetivo.

**Mecánica:**
- Usa habilidad de escuela mágica correspondiente
- Consume maná según el hechizo
- Tirada: `d100 <= nivel_habilidad_magica`
- Daño/efecto según prototipo del hechizo

**Ejemplo:**
```
> /lanzar bola_fuego orco

Conjuras una esfera de fuego ardiente.
🔥 Bola de Fuego golpea al Orco Guerrero por 18 HP
💙 Maná: 35/50 (-15)

Orco Guerrero: 30/60 HP
```

#### `/usar <objeto> <objetivo>`
**Alias:** `/use`

Usa un objeto consumible durante el combate.

**Mecánica:**
- Consume el objeto del inventario
- Ejecuta script del objeto
- No requiere tirada de habilidad (siempre funciona)
- Puede targetear a uno mismo o aliados

**Ejemplo:**
```
> /usar pocion_vida

Bebes la Poción de Vida Menor.
❤️ Recuperas 25 HP
💚 Salud: 50/50 HP

Has consumido: Poción de Vida Menor
```

#### `/huir`
**Alias:** `/flee`, `/escape`

Intenta escapar del combate.

**Mecánica:**
- Tirada: `d100 <= (Agilidad * 2)`
- Éxito: Sales de combate y te mueves a una sala aleatoria adyacente
- Fallo: Pierdes tu turno, recibes ataque de oportunidad

**Ejemplo (éxito):**
```
> /huir

¡Escapas del combate!
Huyes hacia el sur en pánico.

--- Calle Principal ---
[descripción de la sala...]
```

**Ejemplo (fallo):**
```
> /huir

¡No logras escapar!
El Orco Guerrero aprovecha tu distracción.
💥 Ataque de oportunidad: 20 HP de daño
```

#### `/defender`
**Alias:** `/def`, `/block`

Adoptas una postura defensiva hasta tu próximo turno.

**Mecánica:**
- Incrementa defensa en 50% hasta el próximo turno
- No puedes atacar mientras defiendes
- Ideal para regenerar o esperar refuerzos

**Ejemplo:**
```
> /defender

Adoptas una postura defensiva.
🛡️ Defensa: +50% hasta tu próximo turno
```

---

## Atributos de Personaje y PNJ

### Atributos Primarios

Estos atributos definen las capacidades básicas del personaje:

**Fuerza (STR)**
- Aumenta daño físico
- Requisito para armas pesadas
- Afecta capacidad de carga

**Agilidad (AGI)**
- Determina orden de turno (Iniciativa)
- Afecta probabilidad de esquivar
- Requisito para armas ligeras/arcos

**Inteligencia (INT)**
- Aumenta daño mágico
- Incrementa maná máximo
- Velocidad de aprendizaje de habilidades mágicas

**Constitución (CON)**
- Determina HP máximo
- Resistencia a venenos/enfermedades
- Regeneración natural

### Atributos Derivados

Calculados automáticamente a partir de los primarios:

**HP (Salud)**
- Fórmula: `50 + (Constitución * 5)`
- Ejemplo: CON 10 → 100 HP máximo

**Maná (MP)**
- Fórmula: `30 + (Inteligencia * 4)`
- Ejemplo: INT 15 → 90 MP máximo

**Iniciativa**
- Fórmula: `Agilidad + d20`
- Determina orden de turno cada combate

**Ataque Físico**
- Fórmula: `arma.damage + (Fuerza / 10)`
- Ejemplo: Espada (10 daño) + STR 15 → 11.5 daño base

**Defensa Física**
- Fórmula: `armadura.defense + (Agilidad / 20)`
- Reduce daño recibido

**Poder Mágico**
- Fórmula: `hechizo.power * (1 + Inteligencia / 100)`
- Ejemplo: Bola de Fuego (20 poder) + INT 50 → 30 poder total

---

## Integración con Sistema de Habilidades

El combate está profundamente integrado con el sistema d100 de habilidades (ver [skill-system-design.md](skill-system-design.md)).

### Habilidades de Combate Físico

- `espadas` - Armas de una mano con filo
- `hachas` - Armas pesadas de corte
- `mazas` - Armas contundentes
- `arcos` - Armas de proyectiles
- `lanzas` - Armas de alcance medio

### Habilidades de Combate Defensivo

- `parada` - Bloquear ataques físicos con arma
- `esquiva` - Evadir ataques mediante agilidad
- `escudos` - Bloquear con escudo equipado

### Habilidades de Combate Mágico

- `evocacion` - Hechizos de daño elemental
- `alteracion` - Buffs y debuffs
- `necromancia` - Magia de muerte y drenaje
- `curacion` - Hechizos de restauración

### Progresión Durante el Combate

Cada acción exitosa en combate otorga experiencia en la habilidad correspondiente:

```python
# Ejemplo de ganancia de experiencia
if d100 <= character.skills["espadas"]:
    # Ataque exitoso
    damage = calculate_damage(...)
    apply_damage(target, damage)

    # Ganar experiencia en habilidad
    gain_skill_experience(character, "espadas", base_gain=0.1)
```

---

## Consideraciones de Implementación

### Base de Datos

**Nuevas tablas necesarias:**

```python
# Modificaciones al modelo Character
class Character(Base):
    # ... campos existentes ...

    # Atributos primarios
    strength = Column(Integer, default=10)
    agility = Column(Integer, default=10)
    intelligence = Column(Integer, default=10)
    constitution = Column(Integer, default=10)

    # Atributos dinámicos
    current_hp = Column(Integer)
    max_hp = Column(Integer)
    current_mana = Column(Integer)
    max_mana = Column(Integer)

    # Estado de combate
    in_combat = Column(Boolean, default=False)
    combat_id = Column(Integer, ForeignKey("combats.id"), nullable=True)

# Nueva tabla para gestionar combates activos
class Combat(Base):
    __tablename__ = "combats"

    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    turn_number = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Participantes (relación many-to-many)
    participants = relationship("CombatParticipant", back_populates="combat")

class CombatParticipant(Base):
    __tablename__ = "combat_participants"

    id = Column(Integer, primary_key=True)
    combat_id = Column(Integer, ForeignKey("combats.id"))
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=True)
    npc_id = Column(Integer, ForeignKey("npcs.id"), nullable=True)
    initiative = Column(Integer)
    is_active = Column(Boolean, default=True)
```

### Servicios Necesarios

**`combat_service.py`**
- `start_combat()` - Iniciar nuevo combate
- `end_combat()` - Finalizar combate
- `process_turn()` - Procesar turno actual
- `calculate_damage()` - Calcular daño de ataque
- `apply_effects()` - Aplicar efectos de estado

**`npc_service.py`**
- `spawn_npc()` - Crear PNJ en sala
- `despawn_npc()` - Eliminar PNJ
- `npc_ai_action()` - Decidir acción de PNJ
- `respawn_npc()` - Reaparecer PNJ después de tiempo

### Comandos a Implementar

**Player commands:**
- `CmdAttack` - Atacar en combate
- `CmdCast` - Lanzar hechizo
- `CmdFlee` - Huir del combate
- `CmdDefend` - Postura defensiva
- `CmdUseItem` - Usar objeto en combate

**Admin commands:**
- `CmdSpawnNPC` - Generar PNJ
- `CmdDespawnNPC` - Eliminar PNJ
- `CmdForceEndCombat` - Forzar fin de combate

---

## Ejemplo de Flujo Completo

```
[Sala: Bosque Oscuro]
Ves a un Lobo Salvaje (PNJ) aquí.

> /atacar lobo

⚔️ ¡COMBATE INICIADO! ⚔️

Orden de turno:
1. Lobo Salvaje
2. Benabhi

--- TURNO 1 ---
🐺 Lobo Salvaje ataca a Benabhi
💥 Recibes 8 HP de daño
💚 Salud: 42/50 HP

Tu turno: /atacar, /lanzar, /huir, /defender

> /atacar lobo

Blandiendo tu espada oxidada, golpeas al Lobo Salvaje.
🎯 Impacto: 12 HP de daño
🐺 Lobo Salvaje: 18/30 HP

--- TURNO 2 ---
🐺 Lobo Salvaje ataca a Benabhi
💥 Recibes 7 HP de daño
💚 Salud: 35/50 HP

Tu turno: /atacar, /lanzar, /huir, /defender

> /usar pocion_vida

Bebes la Poción de Vida Menor.
❤️ Recuperas 25 HP
💚 Salud: 50/50 HP (completa)

--- TURNO 3 ---
🐺 Lobo Salvaje ataca a Benabhi
🛡️ ¡Esquivas el ataque!

Tu turno: /atacar, /lanzar, /huir, /defender

> /atacar lobo

¡Golpe crítico! Tu espada corta profundamente.
💥 Daño crítico: 24 HP
🐺 Lobo Salvaje: ¡DERROTADO!

✅ VICTORIA ✅

Experiencia ganada:
• +0.3 en habilidad 'espadas' (ahora: 23.7)
• +15 XP

Botín:
• Piel de Lobo
• Colmillo Afilado

El cadáver del Lobo Salvaje yace en el suelo.
```

---

## Balanceo y Ajustes

### Factores a Considerar

1. **Curvas de Progresión**
   - HP/Maná debe escalar adecuadamente con nivel
   - Daño de armas balanceado con HP de PNJs
   - Costos de maná apropiados para hechizos

2. **Dificultad de Combates**
   - PNJs iniciales fáciles para tutorial
   - Escalar dificultad gradualmente
   - Bosses significativamente más difíciles

3. **Recompensas**
   - XP proporcional a dificultad de PNJ
   - Loot valioso para combates difíciles
   - Progresión de habilidades satisfactoria

4. **Tiempo de Combate**
   - Combates no deben ser excesivamente largos
   - Turnos deben resolverse rápidamente
   - Opciones para combates rápidos (auto-ataque)

---

## Próximos Pasos para Implementación

1. ✅ Revisar y aprobar diseño
2. Crear migraciones de base de datos
3. Implementar modelos `Combat`, `CombatParticipant`, `NPC`
4. Desarrollar `combat_service.py` básico
5. Crear comandos de combate básicos (`/atacar`, `/huir`)
6. Implementar PNJs con IA simple
7. Testing exhaustivo de balanceo
8. Integración con sistema de habilidades d100
9. Documentación de usuario
10. Beta testing con jugadores reales

---

## Referencias

- [Sistema de Habilidades](skill-system-design.md) - Mecánica d100
- [Features Planificadas](planned-features.md) - Contexto general
- [Visión y Objetivos](vision-and-goals.md) - Visión estratégica

---

**Estado:** Diseño completo, pendiente de implementación
**Versión:** 1.0
**Última actualización:** 2025-01-10
