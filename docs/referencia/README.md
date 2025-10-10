---
título: "Referencia - Índice"
categoría: "Referencia"
versión: "1.0"
última_actualización: "2025-01-10"
autor: "Proyecto Runegram"
etiquetas: ["referencia", "comandos", "indice"]
documentos_relacionados:
  - "referencia-de-comandos.md"
  - "../creacion-de-contenido/creacion-de-comandos.md"
  - "../sistemas-del-motor/sistema-de-comandos.md"
referencias_código:
  - "commands/"
estado: "actual"
audiencia: "all"
---

# Referencia

Esta sección contiene documentación de referencia rápida para consulta inmediata.

## 📚 Documentos Disponibles

### [Referencia de Comandos](referencia-de-comandos.md)
Lista completa y detallada de todos los comandos del juego.

**Contenido:**
- **Comandos de Jugador:**
  - Gestión de personaje
  - Comandos generales
  - Movimiento
  - Interacción con objetos
  - Canales de comunicación
  - Listados y paginación
  - Configuración

- **Comandos de Administrador:**
  - Generación de entidades
  - Movimiento administrativo
  - Información y diagnóstico
  - Búsqueda por categorías/tags
  - Gestión del juego

**Incluye:**
- Descripción completa de cada comando
- Sintaxis y ejemplos de uso
- Restricciones y permisos
- Notas técnicas importantes
- Sistema de ordinales para objetos duplicados
- Guía de paginación

**Audiencia:** Todos (jugadores, creadores de contenido, administradores, desarrolladores)
**Última actualización:** v1.7 (2025-01-10)

---

## 🎯 Audiencia

Esta documentación es útil para:

### Jugadores
- Consultar sintaxis de comandos
- Aprender comandos nuevos
- Resolver dudas sobre funcionalidades
- Entender el sistema de ordinales para objetos duplicados

### Creadores de Contenido
- Verificar comandos disponibles antes de diseñar contenido
- Conocer restricciones y permisos
- Entender sistemas de interacción (canales, paginación, etc.)

### Administradores
- Consultar comandos administrativos
- Conocer sintaxis de filtrado por categorías/tags
- Aprender comandos de diagnóstico y validación
- Gestión de roles y permisos

### Desarrolladores
- Referencia rápida de comandos implementados
- Verificar funcionalidad existente antes de agregar nuevos comandos
- Entender patrones de uso y sintaxis
- Consultar aliases y permisos

---

## 🔍 Búsqueda Rápida

### Comandos por Categoría

**Movimiento:**
- `/norte`, `/sur`, `/este`, `/oeste`
- `/arriba`, `/abajo`
- `/noreste`, `/noroeste`, `/sureste`, `/suroeste`

**Interacción Básica:**
- `/mirar` - Examinar entorno
- `/coger` - Recoger objetos
- `/dejar` - Soltar objetos
- `/inventario` - Ver inventario

**Comunicación:**
- `/decir` - Hablar en la sala
- `/emocion` - Expresar acciones
- `/susurrar` - Mensaje privado
- `/canales` - Ver canales disponibles

**Admin Esenciales:**
- `/generarobjeto` - Crear objetos
- `/teleport` - Teletransportarse
- `/listarsalas` - Ver todas las salas
- `/examinarsala` - Examinar sala específica

### Comandos por Alias

**Abreviaciones Comunes:**
- `/m`, `/l` → `/mirar`
- `/i`, `/inv` → `/inventario`
- `/g` → `/coger`
- `/d` → `/dejar`
- `/n`, `/s`, `/e`, `/o` → direcciones cardinales

**Comandos Admin:**
- `/tp` → `/teleport`
- `/genobj` → `/generarobjeto`
- `/delobj` → `/destruirobjeto`
- `/lsalas` → `/listarsalas`
- `/litems` → `/listaritems`

---

## 📖 Relacionado

### Para Jugadores
- [Guía de Jugador](../primeros-pasos/player-guide.md) - Tutorial paso a paso
- [Filosofía del Proyecto](../primeros-pasos/filosofia-central.md) - Cómo funciona el juego

### Para Creadores de Contenido
- [Creando Salas](../creacion-de-contenido/construccion-de-salas.md) - Guía de creación de salas
- [Creando Items](../creacion-de-contenido/creacion-de-items.md) - Guía de creación de items
- [Sistema de Categories y Tags](../sistemas-del-motor/categorias-y-etiquetas.md) - Organización de contenido

### Para Desarrolladores
- [Creando Comandos](../creacion-de-contenido/creacion-de-comandos.md) - Guía para desarrolladores
- [Sistema de Comandos](../sistemas-del-motor/sistema-de-comandos.md) - Arquitectura técnica
- [Sistema de Permisos](../sistemas-del-motor/sistema-de-permisos.md) - Locks y permisos

### Para Administradores
- [Guía de Administración](../admin/admin-guide.md) - Guía completa de administración
- [Gestión del Mundo](../admin/world-management.md) - Administración de salas y contenido

---

## 💡 Consejos de Uso

### Para Búsquedas Rápidas

**Si sabes el nombre del comando:**
- Usa Ctrl+F (Buscar) en `referencia-de-comandos.md`
- Busca el nombre del comando con `/`

**Si no sabes el nombre:**
- Revisa el índice por categorías
- Busca por funcionalidad (ej: "movimiento", "comunicación")
- Consulta la lista de aliases comunes

### Para Aprender Comandos Nuevos

1. Lee la sección de tu audiencia (jugador/admin)
2. Revisa ejemplos de uso
3. Presta atención a las restricciones
4. Experimenta en el juego

### Para Verificar Sintaxis

- Consulta la sección "Uso" de cada comando
- Revisa los ejemplos prácticos
- Verifica restricciones y permisos
- Prueba con casos simples primero

---

## 🔄 Actualizaciones

Esta sección de referencia se actualiza con cada nueva funcionalidad.

**Última actualización:** 2025-01-10 (v1.7)

**Últimos cambios:**
- Sistema de Narrativa implementado (mensajes evocativos)
- Comando `/destruirobjeto` agregado
- Paginación unificada en `/inventario` y `/quien`
- Sistema de ordinales documentado
- Sistema de categories/tags expandido

**Política de actualización:**
- Se actualiza inmediatamente después de agregar/modificar comandos
- Changelog mantenido en `referencia-de-comandos.md`
- Versión incrementada según cambios (major.minor)

---

## 📝 Contribuir

Si encuentras información desactualizada o faltante:

1. Verifica que el comando esté implementado en `commands/`
2. Consulta la implementación actual
3. Propón actualización al documento
4. Actualiza versión y changelog

**Regla:** La referencia DEBE estar siempre sincronizada con el código actual.

---

**Última actualización:** 2025-01-10
**Mantenedor:** Proyecto Runegram
