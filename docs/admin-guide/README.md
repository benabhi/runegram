---
título: "Índice de Guía de Administración"
categoría: "Guía de Administración"
audiencia: "administrador"
versión: "1.0"
última_actualización: "2025-01-09"
autor: "Proyecto Runegram"
etiquetas: ["índice", "navegación", "administración", "comandos-admin"]
documentos_relacionados:
  - "engine-systems/permission-system.md"
  - "content-creation/README.md"
referencias_código:
  - "commands/admin/"
  - "src/services/player_service.py"
  - "alembic/"
estado: "actual"
importancia: "alta"
---

# Guía de Administración

Esta sección contiene documentación para administradores del sistema y del juego. Aquí encontrarás comandos de administración, gestión de la base de datos y procedimientos operativos.

## ¿Quién es un Administrador?

Runegram distingue entre tres roles:

- **PLAYER**: Jugador normal (rol por defecto)
- **ADMIN**: Administrador del juego (puede crear objetos, teletransportarse, gestionar jugadores)
- **SUPERADMIN**: Superadministrador (puede asignar roles, acceso total al sistema)

Ver: [Sistema de Permisos](../engine-systems/permission-system.md)

---

## Documentos Disponibles

### 1. [Comandos de Administración](admin-commands.md)
**Audiencia**: Administradores y Superadministradores
**Contenido**:
- Comandos de gestión de salas
- Comandos de gestión de items
- Comandos de gestión de personajes
- Comandos de comunicación admin
- Comandos de roles y permisos
- Ejemplos completos de uso

**Cuándo leer**: Para aprender a usar los comandos administrativos del juego.

---

### 2. [Migraciones de Base de Datos](database-migrations.md)
**Audiencia**: Administradores de sistema, desarrolladores
**Contenido**:
- Crear migraciones con Alembic
- Aplicar migraciones
- Hacer rollback de migraciones
- Estrategias de migración seguras
- Backups y restauración
- Troubleshooting de migraciones

**Cuándo leer**: Cuando necesites modificar el esquema de base de datos.

---

## Orden de Lectura Recomendado

### Para Nuevos Administradores

Si acabas de recibir rol ADMIN:

1. **Primero**: Lee [Comandos de Administración](admin-commands.md)
2. **Segundo**: Prueba comandos básicos en entorno de desarrollo
3. **Tercero**: Familiarízate con [Sistema de Permisos](../engine-systems/permission-system.md)
4. **Cuarto**: Explora [Creación de Contenido](../content-creation/README.md) para expandir el mundo

### Para Administradores de Sistema

Si gestionas la infraestructura:

1. Lee [Migraciones de Base de Datos](database-migrations.md)
2. Revisa [Configuración del Sistema](../architecture/configuration.md)
3. Familiarízate con [Configuración del Sistema](../architecture/configuration.md)
4. Aprende procedimientos de backup y restauración

---

## Comandos Administrativos por Categoría

### Gestión de Salas

```
/teletransportar <room_key>      # Ir a cualquier sala
/listarsalas [cat:X] [tag:Y]     # Listar salas con filtros
/examinarsala                     # Ver información técnica de sala actual
```

**Casos de uso**:
- Inspeccionar nuevas salas creadas
- Navegar rápidamente por el mundo
- Verificar implementación de prototipos

---

### Gestión de Items

```
/generarobjeto <item_key>         # Crear objeto del prototipo
/listaritems [cat:X] [tag:Y]      # Listar items con filtros
/destruirobjeto <objeto>          # Eliminar objeto
```

**Casos de uso**:
- Crear items para probar funcionalidad
- Limpiar objetos duplicados
- Dar items a jugadores para eventos

---

### Gestión de Personajes

```
/asignarrol <jugador> <rol>       # Cambiar rol de jugador (SUPERADMIN only)
/personajes                       # Listar todos los personajes
/suicidio                         # Eliminar personaje propio (ADMIN puede usar sin confirmación)
```

**Casos de uso**:
- Promover moderadores a ADMIN
- Ver quién ha creado personaje
- Limpiar personajes de prueba

---

### Comunicación Administrativa

```
/ayuda <mensaje>                  # Enviar mensaje a canal de ayuda
```

**Casos de uso**:
- Responder preguntas de jugadores
- Hacer anuncios en canal de ayuda
- Coordinar con otros administradores

---

## Flujo de Trabajo Administrativo

### Agregar Nuevo Contenido

1. **Diseñar contenido** (salas, items, comandos)
2. **Editar prototipos** en `game_data/`
3. **Reiniciar bot** para sincronizar prototipos
4. **Probar con comandos admin** (`/teletransportar`, `/generarobjeto`)
5. **Ajustar y refinar** según sea necesario

Ver: [Creación de Contenido](../content-creation/README.md)

---

### Modificar Base de Datos

1. **Hacer backup** de base de datos
2. **Crear migración** con Alembic
3. **Revisar migración** generada
4. **Probar en entorno de desarrollo** primero
5. **Aplicar en producción** con cuidado

Ver: [Migraciones de Base de Datos](database-migrations.md)

---

### Gestionar Roles de Jugadores

1. **Identificar jugador** (`/personajes`)
2. **Verificar comportamiento** (jugador confiable)
3. **Asignar rol** (`/asignarrol <jugador> ADMIN`) - **SUPERADMIN only**
4. **Comunicar responsabilidades** al nuevo admin

**⚠️ IMPORTANTE**: Solo SUPERADMIN puede asignar roles. Este es un control de seguridad crítico.

---

## Procedimientos Operativos

### Backup de Base de Datos

```bash
# Backup completo
docker exec runegram-postgres-1 pg_dump -U runegram_user runegram_db > backup_$(date +%Y%m%d).sql

# Restaurar backup
docker exec -i runegram-postgres-1 psql -U runegram_user runegram_db < backup_20250109.sql
```

**Frecuencia recomendada**: Diario antes de cambios grandes

---

### Reiniciar Servicios

```bash
# Reinicio completo
docker-compose down
docker-compose up -d

# Reinicio solo bot (mantiene BD y Redis)
docker-compose restart bot

# Ver logs en tiempo real
docker logs -f runegram-bot-1
```

---

### Limpieza de Datos

```bash
# Acceder a shell de PostgreSQL
docker exec -it runegram-postgres-1 psql -U runegram_user runegram_db

# Ver items duplicados
SELECT key, COUNT(*) FROM items GROUP BY key HAVING COUNT(*) > 1;

# Ver personajes inactivos
SELECT name, account_id FROM characters WHERE id NOT IN (
    SELECT character_id FROM online_characters WHERE is_active = true
);
```

---

## Permisos y Seguridad

### Roles del Sistema

| Rol | Permisos | Quién lo asigna |
|-----|----------|-----------------|
| PLAYER | Comandos básicos de juego | Automático al crear personaje |
| ADMIN | Gestión de contenido, teletransporte, creación de objetos | SUPERADMIN |
| SUPERADMIN | Gestión de roles, acceso total | Cuenta creada en `gameconfig.toml` |

---

### Locks en Comandos

Los comandos administrativos tienen locks:

```python
class CmdTeleport(Command):
    lock = "rol(ADMIN)"  # Solo ADMIN y SUPERADMIN

class CmdAssignRole(Command):
    lock = "rol(SUPERADMIN)"  # Solo SUPERADMIN
```

Ver: [Sistema de Permisos](../engine-systems/permission-system.md)

---

### Configuración de Superadmin

Edita `gameconfig.toml`:

```toml
[superadmin]
telegram_id = 123456789
username = "admin_username"
character_name = "Administrador"
```

El Superadmin se crea automáticamente en el primer arranque.

Ver: [Configuración del Sistema](../architecture/configuration.md)

---

## Monitoreo y Debugging

### Ver Logs del Bot

```bash
# Logs en tiempo real
docker logs -f runegram-bot-1

# Últimas 100 líneas
docker logs --tail 100 runegram-bot-1

# Buscar errores
docker logs runegram-bot-1 | grep ERROR
```

---

### Ver Estado de Servicios

```bash
# Estado de contenedores
docker-compose ps

# Uso de recursos
docker stats runegram-bot-1 runegram-postgres-1 runegram-redis-1

# Verificar conexión a BD
docker exec runegram-bot-1 python -c "from src.db import engine; print('BD OK')"
```

---

### Debugging de Comandos

Para verificar qué comandos están disponibles para un personaje:

```bash
# Ver comandos en logs cuando jugador usa /
# Los logs muestran: "Available commands for character X: [...]"
docker logs -f runegram-bot-1 | grep "Available commands"
```

---

## Troubleshooting Común

### Bot no arranca

1. Verificar logs: `docker logs runegram-bot-1`
2. Verificar variables de entorno en `.env`
3. Verificar conexión a PostgreSQL y Redis
4. Verificar sintaxis en archivos de prototipos

---

### Comandos no aparecen en menú

1. Verificar que el comando esté registrado en `dispatcher.py`
2. Verificar que el personaje tenga permisos (lock)
3. Verificar que el comando esté en CommandSet activo
4. Reiniciar bot para recargar comandos

---

### Objetos no aparecen después de `/generarobjeto`

1. Verificar logs para errores
2. Verificar que la key del prototipo exista
3. Verificar sintaxis del prototipo en `item_prototypes.py`
4. Verificar que el objeto se creó: `/inventario`

---

### Migración falla

1. **NUNCA aplicar en producción sin probar primero**
2. Hacer rollback: `docker exec runegram-bot-1 alembic downgrade -1`
3. Revisar migración generada en `alembic/versions/`
4. Corregir código y regenerar migración
5. Probar en entorno de desarrollo

Ver: [Migraciones de Base de Datos](database-migrations.md)

---

## Mejores Prácticas

### Para Administradores de Juego

- ✅ Usa `/examinarsala` para verificar implementación de salas nuevas
- ✅ Prueba objetos con `/generarobjeto` antes de agregarlos a salas permanentemente
- ✅ Documenta cambios grandes en prototipos (comentarios en código)
- ✅ Comunica a jugadores cuando hagas cambios que los afecten
- ❌ No elimines objetos en uso por jugadores sin advertencia
- ❌ No cambies prototipos dramáticamente sin considerar instancias existentes

---

### Para Administradores de Sistema

- ✅ Haz backups antes de migraciones
- ✅ Prueba cambios en entorno de desarrollo primero
- ✅ Monitorea logs regularmente
- ✅ Mantén Docker y dependencias actualizadas
- ❌ No apliques migraciones en producción sin probar
- ❌ No modifiques BD manualmente sin migración
- ❌ No compartas credenciales de Superadmin

---

## Recursos Importantes

### Archivos de Configuración

```
gameconfig.toml               # Configuración del juego
.env                          # Variables de entorno (credenciales)
docker-compose.yml            # Configuración de servicios
alembic.ini                   # Configuración de Alembic
```

---

### Comandos de Admin Implementados

```
commands/admin/
├── admin_commands.py         # Comandos generales de admin
├── room_management.py        # Gestión de salas
├── item_management.py        # Gestión de items
└── character_management.py   # Gestión de personajes
```

---

### Scripts Útiles

```
scripts/
├── full_reset.bat            # Reset completo (Windows)
├── full_reset.sh             # Reset completo (Linux/Mac)
└── create_migration.sh       # Crear migración
```

---

## Preguntas Frecuentes

### ¿Cómo me convierto en ADMIN?

Solo el SUPERADMIN puede asignar roles usando `/asignarrol`. El Superadmin se define en `gameconfig.toml`.

---

### ¿Puedo deshacer un comando admin?

Depende del comando:
- `/generarobjeto`: Sí, usa `/destruirobjeto`
- `/asignarrol`: Sí, reasigna rol anterior
- `/suicidio`: NO, elimina permanentemente (pero sin confirmación para admins)

---

### ¿Los comandos admin son visibles para jugadores?

NO. Los comandos con `lock = "rol(ADMIN)"` solo aparecen en el menú `/` para usuarios con rol ADMIN o SUPERADMIN.

---

### ¿Cómo veo todos los comandos disponibles?

Como admin, escribe `/` en Telegram. Telegram te mostrará todos los comandos disponibles según tu rol y contexto.

Ver: [Sistema de Comandos](../engine-systems/command-system.md)

---

## Próximos Pasos

1. **Aprende comandos básicos**: Lee [Comandos de Administración](admin-commands.md)
2. **Familiarízate con la arquitectura**: Revisa [Configuración del Sistema](../architecture/configuration.md)
3. **Practica en desarrollo**: Usa Docker Compose localmente
4. **Expande el mundo**: Aprende [Creación de Contenido](../content-creation/README.md)
5. **Gestiona la BD**: Domina [Migraciones de Base de Datos](database-migrations.md)

---

**Con gran poder viene gran responsabilidad. Administra Runegram con cuidado y sabiduría.**
