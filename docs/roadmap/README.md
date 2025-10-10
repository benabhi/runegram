---
titulo: "Hoja de Ruta - Índice"
categoria: "Hoja de Ruta"
version: "1.0"
ultima_actualizacion: "2025-01-10"
autor: "Proyecto Runegram"
etiquetas: ["roadmap", "planificacion", "indice"]
documentos_relacionados:
  - "vision-and-goals.md"
  - "planned-features.md"
  - "combat-system-design.md"
  - "skill-system-design.md"
referencias_codigo: []
estado: "actual"
audiencia: "desarrolladores"
---

# Hoja de Ruta

Esta sección contiene la visión a futuro del proyecto Runegram y diseños de sistemas que aún no han sido implementados.

## ⚠️ IMPORTANTE

Los documentos en esta sección describen funcionalidades **PLANIFICADAS** pero **NO IMPLEMENTADAS**. No intentes usar estos sistemas en el código actual del proyecto.

Antes de implementar cualquier funcionalidad de esta sección:
1. Revisa el diseño completo
2. Actualiza el diseño si es necesario
3. Consulta con el equipo de desarrollo
4. Verifica dependencias con sistemas existentes
5. Actualiza la documentación después de implementar

---

## 📋 Documentos Disponibles

### Visión y Planificación

#### [Visión y Objetivos](vision-and-goals.md)
Visión general y objetivos estratégicos a largo plazo del proyecto.

**Contenido:**
- Visión general del proyecto
- Objetivos estratégicos
- Filosofía de diseño futura
- Hitos de desarrollo
- Métricas de éxito

**Audiencia:** Desarrolladores, stakeholders
**Estado:** Documento vivo, revisión trimestral

---

#### [Features Planificadas](planned-features.md)
Lista detallada de funcionalidades pendientes de implementar.

**Contenido:**
- Sistema de Combate y Habilidades
- Sistema de Interacción Social (mejoras)
- Sistema de Clases y Razas
- Mejoras del Motor
- Mejoras de UX
- Roadmap temporal tentativo

**Audiencia:** Desarrolladores
**Estado:** Actualizado regularmente según prioridades

---

### Diseños de Sistemas Futuros

#### [Sistema de Combate](combat-system-design.md) 🚧 **[DISEÑO - NO IMPLEMENTADO]**
Mecánicas de combate táctico por turnos propuestas.

**Contenido:**
- Flujo de combate por turnos
- Comandos de combate (`/atacar`, `/lanzar`, `/huir`, etc.)
- Atributos de personaje (HP, Maná, Fuerza, etc.)
- Integración con sistema de habilidades
- Diseño de base de datos
- Ejemplos de flujo completo

**Audiencia:** Desarrolladores
**Prioridad:** Alta
**Tiempo estimado:** 8-12 semanas
**Estado:** Diseño completo, pendiente de implementación

---

#### [Sistema de Habilidades](skill-system-design.md) 🚧 **[DISEÑO - NO IMPLEMENTADO]**
Sistema d100 de habilidades "aprender haciendo".

**Contenido:**
- Mecánica d100 (tirada de dado)
- Tipos de habilidades (combate, magia, artesanía, generales)
- Curvas de progresión
- Integración con sistema de locks
- Diseño de base de datos
- Servicio de habilidades
- Ejemplos de implementación

**Audiencia:** Desarrolladores
**Prioridad:** Alta
**Tiempo estimado:** 6-8 semanas
**Estado:** Diseño completo, pendiente de implementación

---

## 🗺️ Estado de Implementación

| Sistema | Estado | Prioridad | Tiempo Estimado | Dependencias |
|---------|--------|-----------|-----------------|--------------|
| **Combate** | 📝 Diseño | Alta | 8-12 semanas | Sistema de Habilidades, PNJs |
| **Habilidades d100** | 📝 Diseño | Alta | 6-8 semanas | Locks expandidos |
| **Interacción Social** | 🔄 Parcial | Alta | 3-4 semanas | Broadcasting (✅) |
| **Clases y Razas** | 📝 Diseño | Media | 4-6 semanas | Sistema de Habilidades |
| **Locks Expandidos** | 📝 Diseño | Media | 2-3 semanas | Sistema de Habilidades |
| **Contenedores Mejorados** | 🔄 Parcial | Media | 2 semanas | - |
| **Tutoriales** | 📝 Diseño | Media | 3-4 semanas | - |
| **Bandeja de Entrada** | 📝 Diseño | Baja | 2 semanas | - |
| **Detalles de Sala** | 📝 Diseño | Baja | 1-2 semanas | - |

**Leyenda:**
- ✅ Completado
- 🔄 Implementación parcial
- 📝 Solo diseño
- ❌ Bloqueado

---

## 🎯 Roadmap Temporal (Tentativo)

### Q1 2025 (Enero - Marzo)
- ✅ Sistema de Broadcasting (completado)
- ✅ Sistema de Narrativa (completado)
- 🔄 Refactorización de comandos sociales (en progreso)
- 🔄 Expandir sistema de locks (planificado)

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

## 🚀 Cómo Contribuir

### Para Desarrolladores

Si deseas contribuir a la implementación de estos sistemas:

1. **Lee el diseño completo** del sistema que te interesa
2. **Consulta dependencias** en la tabla de estado
3. **Revisa la arquitectura actual** en `docs/architecture/`
4. **Consulta los sistemas del motor** en `docs/engine-systems/`
5. **Propón cambios al diseño** si es necesario (PR al documento de diseño)
6. **Implementa en ramas feature** (`feature/combat-system`, etc.)
7. **Actualiza documentación** después de implementar

### Para Diseñadores de Contenido

- Los sistemas de **Combate** y **Habilidades** abrirán muchas posibilidades de contenido
- Mientras tanto, puedes preparar:
  - Descripciones de PNJs futuros
  - Balanceo de dificultad de contenido existente
  - Ideas para quests y narrativas

---

## 📚 Referencias Relacionadas

### Documentación Actual (Implementado)
- [Filosofía del Proyecto](../getting-started/core-philosophy.md) - Principios fundamentales actuales
- [Arquitectura](../architecture/) - Estructura técnica del motor
- [Sistemas del Motor](../engine-systems/) - Sistemas ya implementados
- [Creación de Contenido](../content-creation/) - Guías para crear contenido actual

### Documentación Externa
- [Aiogram 2.x](https://docs.aiogram.dev/en/v2.25.1/) - Framework de bot
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/) - ORM
- [Telegram Bot API](https://core.telegram.org/bots/api) - API de Telegram

---

## 💬 Feedback y Sugerencias

Si tienes ideas para mejorar estos diseños o sugerir nuevas funcionalidades:

1. Revisa los documentos existentes
2. Verifica que no esté ya contemplado
3. Considera la filosofía del proyecto (Motor vs Contenido)
4. Abre un issue o discusión en el repositorio
5. Propón cambios concretos con justificación

---

**Última actualización:** 2025-01-10
**Mantenedor:** Proyecto Runegram
**Revisión recomendada:** Mensual

---

## Notas Finales

Esta sección de documentación es **aspiracional** y describe hacia dónde queremos llevar Runegram. Los diseños aquí presentados son detallados pero no definitivos, y pueden evolucionar según feedback y necesidades del proyecto.

El objetivo es tener diseños bien pensados **antes** de implementar, para evitar refactorizaciones costosas y mantener la coherencia arquitectónica del proyecto.
