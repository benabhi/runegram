---
titulo: "Diseño del Sistema de Habilidades"
categoria: "Hoja de Ruta"
version: "1.0"
ultima_actualizacion: "2025-01-10"
autor: "Proyecto Runegram"
etiquetas: ["habilidades", "d100", "diseño", "no-implementado"]
documentos_relacionados:
  - "combat-system-design.md"
  - "planned-features.md"
  - "vision-and-goals.md"
referencias_codigo: []
estado: "planificado"
audiencia: "desarrolladores"
---

# ⚠️ Sistema de Habilidades - DISEÑO NO IMPLEMENTADO

**IMPORTANTE:** Este documento describe un sistema que está en **fase de diseño** y **NO ha sido implementado aún**. No intentes usar estos sistemas o mecánicas en el código actual del proyecto.

---

# Sistema de Habilidades

Este documento describe el diseño propuesto para el Sistema de Habilidades de Runegram basado en la mecánica d100.

## Visión General

El Sistema de Habilidades de Runegram se basa en el principio de **"aprender haciendo"** (*learning by doing*), inspirado en juegos como Ultima Online, Runescape y The Elder Scrolls.

### Principios Fundamentales

1. **Uso = Mejora**: Los personajes mejoran sus habilidades al usarlas exitosamente
2. **Sin puntos manuales**: No hay asignación manual de puntos de experiencia
3. **Progresión orgánica**: La mejora es natural y emerge del gameplay
4. **Sistema d100**: Resolución basada en tirada de dado de 100 caras

---

## Mecánica Central (d100)

### Resolución de Acciones

Cuando un personaje intenta una acción basada en una habilidad:

**1. Tirada de Dado**
```python
roll = random.randint(1, 100)  # d100
```

**2. Comprobación de Éxito**
```python
if roll <= character.skills[skill_name]:
    # Acción exitosa
    perform_action()
    gain_skill_experience(character, skill_name)
else:
    # Acción fallida
    show_failure_message()
```

**3. Ganancia de Experiencia**
```python
def gain_skill_experience(character, skill_name, base_gain=0.1):
    current_level = character.skills[skill_name]

    # Probabilidad de ganar punto disminuye con nivel alto
    chance = max(0.05, 1.0 - (current_level / 100))

    if random.random() < chance:
        character.skills[skill_name] += base_gain
        notify_skill_gain(character, skill_name)
```

### Ejemplo Completo

```python
# Jugador intenta forzar una cerradura
# Nivel actual en "forzar_cerraduras": 35

roll = random.randint(1, 100)  # Resultado: 28

if 28 <= 35:
    # Éxito: La cerradura se abre
    open_lock(door)
    message = "¡Logras forzar la cerradura con éxito!"

    # Probabilidad de ganar experiencia
    chance = 1.0 - (35 / 100) = 0.65 (65%)

    if random.random() < 0.65:
        character.skills["forzar_cerraduras"] += 0.1
        message += "\n✨ Tu habilidad en 'forzar_cerraduras' aumenta a 35.1"
else:
    # Fallo: La cerradura resiste
    message = "No logras forzar la cerradura. Necesitas más práctica."

await send_message(message)
```

---

## Tipos de Habilidades

### Habilidades de Combate

**Armas de Cuerpo a Cuerpo:**
- `espadas` - Armas de filo de una mano
- `espadones` - Armas grandes de dos manos
- `hachas` - Armas de corte pesadas
- `mazas` - Armas contundentes
- `dagas` - Armas ligeras y rápidas
- `lanzas` - Armas de alcance medio

**Armas a Distancia:**
- `arcos` - Armas de proyectiles
- `ballestas` - Armas de precisión
- `armas_arrojadizas` - Cuchillos, hachas arrojadizas

**Combate Defensivo:**
- `parada` - Bloquear con arma
- `esquiva` - Evasión mediante agilidad
- `escudos` - Bloqueo con escudo

**Combate sin Armas:**
- `pelea` - Combate desarmado
- `lucha` - Agarres y derribos

### Habilidades Mágicas

**Escuelas de Magia Ofensiva:**
- `evocacion` - Daño elemental directo (fuego, hielo, rayo)
- `necromancia` - Magia de muerte y drenaje de vida
- `invocacion` - Summon de criaturas

**Escuelas de Magia de Utilidad:**
- `alteracion` - Buffs, debuffs, transformaciones
- `curacion` - Restauración de HP
- `ilusion` - Engaños, invisibilidad
- `adivinacion` - Detección, revelación

**Habilidades Mágicas Complementarias:**
- `meditacion` - Regeneración de maná
- `resistencia_magica` - Defensa contra magia

### Habilidades de Artesanía

**Creación de Objetos:**
- `herreria` - Armas y armaduras de metal
- `carpinteria` - Armas y objetos de madera
- `costura` - Armaduras de cuero y tela
- `alquimia` - Pociones y elixires

**Procesamiento de Recursos:**
- `mineria` - Extracción de minerales
- `talado` - Obtención de madera
- `curtido` - Procesamiento de pieles

### Habilidades Generales

**Supervivencia:**
- `sigilo` - Moverse sin ser detectado
- `rastreo` - Seguir huellas
- `campamento` - Descanso eficiente
- `cocina` - Preparar alimentos

**Interacción:**
- `forzar_cerraduras` - Abrir cerraduras sin llave
- `desarmar_trampas` - Desactivar trampas
- `robo` - Sustraer objetos
- `comercio` - Mejores precios en NPC vendors

**Conocimiento:**
- `identificacion` - Conocer propiedades de items
- `anatomia` - Conocimiento de criaturas
- `tasacion` - Determinar valor de objetos

---

## Curvas de Progresión

### Ganancia de Experiencia

La ganancia de experiencia sigue una curva que hace que las habilidades altas sean más difíciles de mejorar:

```python
def calculate_skill_gain_chance(current_skill_level):
    """
    Calcula la probabilidad de ganar un punto de habilidad.

    Args:
        current_skill_level: Nivel actual de 0 a 100

    Returns:
        Probabilidad de 0.0 a 1.0
    """
    # Curva: Alta probabilidad al inicio, baja al final
    base_chance = 1.0 - (current_skill_level / 100)

    # Mínimo 5% de probabilidad incluso a nivel 100
    return max(0.05, base_chance)

# Ejemplos:
# Nivel 0: 100% de probabilidad
# Nivel 25: 75% de probabilidad
# Nivel 50: 50% de probabilidad
# Nivel 75: 25% de probabilidad
# Nivel 90: 10% de probabilidad
# Nivel 100: 5% de probabilidad
```

### Cantidad de Experiencia por Uso

```python
def calculate_skill_gain_amount(difficulty_multiplier=1.0):
    """
    Calcula cuánto aumenta la habilidad en un uso exitoso.

    Args:
        difficulty_multiplier: 1.0 = normal, 1.5 = difícil, 2.0 = muy difícil

    Returns:
        Cantidad de puntos a añadir
    """
    base_gain = 0.1  # Ganancia base por uso

    # Acciones más difíciles dan más experiencia
    return base_gain * difficulty_multiplier

# Ejemplos:
# Forzar cerradura simple: 0.1 puntos
# Forzar cerradura compleja: 0.15 puntos
# Forzar cerradura maestra: 0.2 puntos
```

### Tabla de Progresión Estimada

| Nivel | Usos Necesarios* | Probabilidad Ganancia | Descripción |
|-------|------------------|----------------------|-------------|
| 0-10  | ~100 usos | 95-100% | Novato |
| 10-25 | ~200 usos | 75-90% | Aprendiz |
| 25-50 | ~400 usos | 50-75% | Competente |
| 50-75 | ~800 usos | 25-50% | Experto |
| 75-90 | ~1500 usos | 10-25% | Maestro |
| 90-100 | ~3000 usos | 5-10% | Gran Maestro |

*Aproximado, varía según probabilidad de éxito

---

## Integración con el Sistema de Locks

El sistema de habilidades se integra directamente con `permission_service` para crear contenido que requiere habilidades específicas.

### Nueva Función de Lock: `habilidad()`

```python
# En permission_service.py

def lock_habilidad(character, skill_name, min_level):
    """
    Verifica si el personaje tiene el nivel mínimo en una habilidad.

    Args:
        character: El personaje a verificar
        skill_name: Nombre de la habilidad
        min_level: Nivel mínimo requerido

    Returns:
        True si cumple el requisito, False si no
    """
    if skill_name not in character.skills:
        return False

    return character.skills[skill_name] >= min_level

# Registrar la función
LOCK_FUNCTIONS["habilidad"] = lock_habilidad
```

### Sintaxis de Lock String

```python
# Ejemplos de lock strings usando habilidades:

# Cerradura simple
lock = "habilidad(forzar_cerraduras)>30"

# Cerradura compleja con alternativa mágica
lock = "habilidad(forzar_cerraduras)>70 or habilidad(alteracion)>50"

# Herrería avanzada
lock = "habilidad(herreria)>75 and tiene_objeto(martillo_especial)"

# Múltiples requisitos
lock = "habilidad(herreria)>50 and habilidad(mineria)>40"
```

### Aplicaciones del Sistema

**1. Puertas y Cerraduras**

```python
# En room_prototypes.py
ROOM_PROTOTYPES = {
    "camara_secreta": {
        "exits": {
            "norte": {
                "to_room": "tesoreria",
                "lock": "habilidad(forzar_cerraduras)>60 or tiene_objeto(llave_maestra)"
            }
        }
    }
}
```

**2. Crafteo de Objetos**

```python
# En crafteo (futuro)
RECIPE_PROTOTYPES = {
    "espada_acero": {
        "requirements": {
            "lock": "habilidad(herreria)>40",
            "materials": ["lingote_acero", "mango_madera"],
            "tool": "martillo"
        }
    }
}
```

**3. Uso de Items Avanzados**

```python
# En item_prototypes.py
ITEM_PROTOTYPES = {
    "grimorio_antiguo": {
        "name": "Grimorio Antiguo",
        "lock": "habilidad(evocacion)>50",
        "grants_command_sets": ["advanced_magic"]
    }
}
```

---

## Base de Datos

### Tabla de Habilidades

```python
class Skill(Base):
    """Define una habilidad disponible en el juego."""
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True)
    key = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    category = Column(String(50))  # "combat", "magic", "craft", "general"
    max_level = Column(Integer, default=100)

    # Relación con character_skills
    character_skills = relationship("CharacterSkill", back_populates="skill")
```

### Tabla de Habilidades de Personaje

```python
class CharacterSkill(Base):
    """Registra el nivel de habilidad de un personaje."""
    __tablename__ = "character_skills"

    id = Column(Integer, primary_key=True)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    level = Column(Float, default=0.0)  # 0.0 a 100.0
    experience = Column(Float, default=0.0)  # Experiencia acumulada
    last_used = Column(DateTime)

    # Relaciones
    character = relationship("Character", back_populates="skills")
    skill = relationship("Skill", back_populates="character_skills")

    # Índice para búsquedas rápidas
    __table_args__ = (
        Index('idx_character_skill', 'character_id', 'skill_id', unique=True),
    )
```

### Modificación al Modelo Character

```python
class Character(Base):
    # ... campos existentes ...

    # Relación con habilidades
    skills = relationship(
        "CharacterSkill",
        back_populates="character",
        cascade="all, delete-orphan"
    )

    def get_skill_level(self, skill_key: str) -> float:
        """Obtiene el nivel actual de una habilidad."""
        for char_skill in self.skills:
            if char_skill.skill.key == skill_key:
                return char_skill.level
        return 0.0

    def add_skill_experience(self, skill_key: str, amount: float):
        """Añade experiencia a una habilidad."""
        for char_skill in self.skills:
            if char_skill.skill.key == skill_key:
                char_skill.experience += amount
                char_skill.level = min(100.0, char_skill.level + amount)
                char_skill.last_used = datetime.utcnow()
                return char_skill.level

        # Si no tiene la habilidad, crearla
        # (requiere buscar el Skill en la BD)
        return None
```

---

## Servicio de Habilidades

```python
# src/services/skill_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import random

class SkillService:
    """Servicio para gestionar el sistema de habilidades d100."""

    @staticmethod
    async def check_skill(
        character,
        skill_key: str,
        difficulty_modifier: int = 0
    ) -> bool:
        """
        Realiza una tirada de habilidad d100.

        Args:
            character: El personaje que realiza la acción
            skill_key: Clave de la habilidad a verificar
            difficulty_modifier: Modificador de dificultad (-50 a +50)

        Returns:
            True si la acción fue exitosa, False si falló
        """
        skill_level = character.get_skill_level(skill_key)
        modified_level = max(0, min(100, skill_level + difficulty_modifier))

        roll = random.randint(1, 100)

        return roll <= modified_level

    @staticmethod
    async def gain_skill_experience(
        session: AsyncSession,
        character,
        skill_key: str,
        base_amount: float = 0.1,
        difficulty_multiplier: float = 1.0
    ) -> Optional[float]:
        """
        Otorga experiencia en una habilidad.

        Args:
            session: Sesión de base de datos
            character: El personaje que gana experiencia
            skill_key: Clave de la habilidad
            base_amount: Cantidad base de experiencia
            difficulty_multiplier: Multiplicador por dificultad

        Returns:
            Nuevo nivel de habilidad, o None si no se ganó experiencia
        """
        current_level = character.get_skill_level(skill_key)

        # Calcular probabilidad de ganancia
        chance = max(0.05, 1.0 - (current_level / 100))

        if random.random() < chance:
            # Calcular cantidad de ganancia
            gain = base_amount * difficulty_multiplier

            # Añadir experiencia
            new_level = character.add_skill_experience(skill_key, gain)

            await session.commit()
            return new_level

        return None

    @staticmethod
    async def get_skill_rank_name(skill_level: float) -> str:
        """Obtiene el nombre del rango de habilidad."""
        if skill_level < 10:
            return "Novato"
        elif skill_level < 25:
            return "Aprendiz"
        elif skill_level < 50:
            return "Competente"
        elif skill_level < 75:
            return "Experto"
        elif skill_level < 90:
            return "Maestro"
        else:
            return "Gran Maestro"
```

---

## Comandos de Jugador

### `/habilidades`
**Alias:** `/skills`, `/stats`

Muestra las habilidades del personaje.

**Uso:**
```
> /habilidades

⚔️ HABILIDADES DE COMBATE ⚔️
    - Espadas: 45.3 (Competente)
    - Parada: 38.7 (Competente)
    - Esquiva: 52.1 (Experto)

🔮 HABILIDADES MÁGICAS 🔮
    - Evocación: 23.4 (Aprendiz)
    - Curación: 15.8 (Aprendiz)

🛠️ HABILIDADES DE ARTESANÍA 🛠️
    - Herrería: 10.2 (Aprendiz)
    - Minería: 8.3 (Novato)

📚 HABILIDADES GENERALES 📚
    - Forzar Cerraduras: 67.9 (Experto)
    - Sigilo: 41.2 (Competente)
```

### `/entrenar <habilidad>`
**Alias:** `/train`

Practica una habilidad de forma pasiva (futuro).

---

## Ejemplo de Uso Integrado

```python
# En commands/player/interaction.py

class CmdPickLock(Command):
    """Intenta forzar una cerradura."""
    names = ["forzarcerradura", "picklock"]
    description = "Intenta forzar una cerradura"

    async def execute(self, character, session, message, args):
        # Verificar que haya una puerta cerrada
        # ... (código de validación) ...

        # Obtener dificultad de la cerradura
        difficulty = door.attributes.get("lock_difficulty", 50)

        # Calcular modificador
        modifier = difficulty - 50  # Cerraduras más difíciles = penalización

        # Tirada de habilidad
        success = await skill_service.check_skill(
            character,
            "forzar_cerraduras",
            difficulty_modifier=modifier
        )

        if success:
            # Éxito: Abrir cerradura
            door.attributes["is_locked"] = False
            await session.commit()

            await message.answer(
                "¡Logras forzar la cerradura con un clic satisfactorio!"
            )

            # Ganar experiencia
            difficulty_mult = 1.0 + (difficulty / 100)
            new_level = await skill_service.gain_skill_experience(
                session,
                character,
                "forzar_cerraduras",
                base_amount=0.1,
                difficulty_multiplier=difficulty_mult
            )

            if new_level:
                await message.answer(
                    f"✨ Tu habilidad en 'forzar_cerraduras' aumenta a {new_level:.1f}"
                )
        else:
            # Fallo
            await message.answer(
                "La cerradura resiste tus intentos. Necesitas más práctica."
            )
```

---

## Balanceo y Ajustes

### Factores a Considerar

**1. Velocidad de Progresión**
- ¿Cuántos usos para llegar a nivel 50?
- ¿Cuánto tiempo de juego representa?
- Ajustar `base_gain` y curvas de probabilidad

**2. Techo de Habilidades**
- ¿Límite total de puntos por personaje?
- ¿Especialización vs generalización?
- Considerar sistema de "skill cap" global

**3. Dificultad de Contenido**
- Asociar niveles de habilidad con contenido
- Nivel 0-25: Contenido de inicio
- Nivel 25-50: Contenido intermedio
- Nivel 50-75: Contenido avanzado
- Nivel 75-100: Contenido endgame

**4. Sinergia entre Habilidades**
- Bonificaciones por habilidades relacionadas
- Ejemplo: Herrería + Minería = bonus
- Implementar sistema de "skill chains"

---

## Próximos Pasos para Implementación

1. ✅ Revisar y aprobar diseño
2. Crear migraciones de base de datos (`skills`, `character_skills`)
3. Implementar `skill_service.py` con funciones básicas
4. Crear prototipos de habilidades (`game_data/skill_prototypes.py`)
5. Implementar comando `/habilidades`
6. Integrar con sistema de locks (`lock_habilidad()`)
7. Crear ejemplos de uso en comandos (forzar cerraduras, crafteo simple)
8. Testing de curvas de progresión
9. Balanceo basado en feedback
10. Documentación de usuario

---

## Referencias

- [Sistema de Combate](combat-system-design.md) - Integración con combate
- [Features Planificadas](planned-features.md) - Contexto general
- [Visión y Objetivos](vision-and-goals.md) - Visión estratégica
- [Sistema de Permisos](../engine-systems/permission-system.md) - Locks actuales

---

**Estado:** Diseño completo, pendiente de implementación
**Versión:** 1.0
**Última actualización:** 2025-01-10
