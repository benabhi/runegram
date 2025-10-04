# Referencia Completa de Comandos de Runegram

Esta es la referencia completa de todos los comandos disponibles en Runegram MUD, organizados por categoría y función.

## Tabla de Contenidos

1. [Comandos de Jugador](#comandos-de-jugador)
   - [Gestión de Personaje](#gestión-de-personaje)
   - [Comandos Generales](#comandos-generales)
   - [Movimiento](#movimiento)
   - [Interacción con Objetos](#interacción-con-objetos)
   - [Canales de Comunicación](#canales-de-comunicación)
   - [Listados y Paginación](#listados-y-paginación)
   - [Configuración](#configuración)
2. [Comandos de Administrador](#comandos-de-administrador)
   - [Generación de Entidades](#generación-de-entidades-spawning)
   - [Movimiento Administrativo](#movimiento-administrativo)
   - [Información y Diagnóstico](#información-y-diagnóstico)
   - [Gestión del Juego](#gestión-del-juego)

---

# Comandos de Jugador

## Gestión de Personaje

### `/crearpersonaje <nombre>`
- **Descripción:** Crea tu personaje para empezar a jugar.
- **Uso:** `/crearpersonaje Gandalf`
- **Restricciones:** Solo disponible para cuentas sin personaje.
- **Notas:**
  - El nombre debe ser único en todo el juego.
  - Máximo 50 caracteres.
  - Este es el primer comando que debe ejecutar un nuevo jugador.

### `/suicidio CONFIRMAR`
- **Alias:** `/borrarpersonaje`, `/eliminarpersonaje`
- **Descripción:** Elimina permanentemente tu personaje actual (irreversible).
- **Uso:**
  - `/suicidio` - Muestra advertencia y confirmación requerida
  - `/suicidio CONFIRMAR` - Ejecuta la eliminación
- **⚠️ ADVERTENCIA:** Esta acción es irreversible y eliminará:
  - Tu personaje y su nombre
  - Todo tu inventario
  - Todas tus configuraciones
  - Todo tu progreso en el juego
- **Notas:**
  - Requiere escribir "CONFIRMAR" en mayúsculas para evitar eliminaciones accidentales.
  - Después de eliminar el personaje, puedes crear uno nuevo con `/crearpersonaje`.

---

## Comandos Generales

### `/mirar [objetivo]`
- **Alias:** `/m`, `/l`
- **Descripción:** Observa tu entorno o un objeto/personaje/detalle específico.
- **Uso:**
  - `/mirar` - Muestra la descripción de tu sala actual
  - `/mirar espada` - Examina un objeto específico
  - `/mirar Gandalf` - Examina a otro jugador
  - `/mirar fuente` - Examina un detalle de la sala
- **Notas:**
  - Sin argumentos, muestra la sala completa con salidas, objetos y personajes.
  - Puede ejecutar scripts `on_look` si el objeto los tiene definidos.
  - Solo muestra jugadores que estén activamente online.

### `/decir <mensaje>`
- **Alias:** `'`
- **Descripción:** Habla con las personas que están en tu misma sala.
- **Uso:**
  - `/decir Hola a todos`
  - `' Hola a todos` (usando el alias)
- **Notas:**
  - El mensaje se enviará a todos los jugadores online en la sala.
  - El mensaje aparece en cursiva para otros jugadores.

### `/inventario [contenedor | todo [página]]`
- **Alias:** `/inv`, `/i`
- **Descripción:** Muestra tu inventario o el de un contenedor.
- **Uso:**
  - `/inv` - Muestra tu inventario (limitado)
  - `/inv mochila` - Muestra el contenido de un contenedor
  - `/inv todo` - Muestra tu inventario completo con paginación
  - `/inv todo 2` - Muestra la página 2 del inventario completo
- **Notas:**
  - Los contenedores pueden tener locks que restrinjan el acceso.
  - El modo "todo" es útil cuando tienes muchos objetos.

### `/ayuda`
- **Alias:** `/help`
- **Descripción:** Muestra una lista con los comandos básicos del juego.
- **Notas:** Proporciona un resumen rápido de los comandos más comunes.

### `/quien [todo [página]]`
- **Alias:** `/who`
- **Descripción:** Muestra una lista de los jugadores conectados.
- **Uso:**
  - `/quien` - Lista limitada de jugadores online
  - `/quien todo` - Lista completa con paginación
  - `/quien todo 2` - Página 2 de la lista completa
- **Notas:**
  - Solo muestra jugadores activamente online (últimos 5 minutos de actividad).
  - Incluye la sala donde se encuentra cada jugador.

### `/orar`
- **Alias:** `/rezar`
- **Descripción:** Rezas a los dioses en busca de inspiración.
- **Notas:** Comando de roleplay simple.

### `/desconectar`
- **Alias:** `/logout`, `/salir`
- **Descripción:** Te desconecta inmediatamente del juego.
- **Notas:**
  - Te marca como offline instantáneamente.
  - Al volver, recibirás un mensaje de reconexión.
  - No es necesario usar este comando; el juego te marca como offline automáticamente tras 5 minutos de inactividad.

### `/susurrar <jugador> <mensaje>`
- **Alias:** `/whisper`
- **Descripción:** Susurra un mensaje privado a un jugador en tu sala.
- **Uso:** `/susurrar Gandalf Tenemos que hablar`
- **Restricciones:**
  - El jugador objetivo debe estar en la misma sala.
  - El jugador objetivo debe estar online.
- **Notas:** El mensaje es completamente privado, otros jugadores no lo ven.

---

## Movimiento

Todos los comandos de movimiento siguen el mismo patrón: se mueven en la dirección especificada si existe una salida válida.

### Direcciones Cardinales

- `/norte` (alias: `/n`) - Moverse hacia el norte
- `/sur` (alias: `/s`) - Moverse hacia el sur
- `/este` (alias: `/e`) - Moverse hacia el este
- `/oeste` (alias: `/o`) - Moverse hacia el oeste

### Direcciones Verticales

- `/arriba` (alias: `/ar`) - Moverse hacia arriba
- `/abajo` (alias: `/ab`) - Moverse hacia abajo

### Direcciones Intermedias

- `/noreste` (alias: `/ne`) - Moverse hacia el noreste
- `/noroeste` (alias: `/no`) - Moverse hacia el noroeste
- `/sureste` (alias: `/se`) - Moverse hacia el sureste
- `/suroeste` (alias: `/so`) - Moverse hacia el suroeste

**Notas sobre movimiento:**
- Las salidas pueden tener locks (candados) que requieran permisos específicos.
- Al moverte, se notifica a la sala de origen que te fuiste y a la de destino que llegaste.
- Solo los jugadores online recibirán estas notificaciones.

---

## Interacción con Objetos

### `/coger <objeto> [de <contenedor>]`
- **Alias:** `/g`
- **Descripción:** Recoge un objeto del suelo o de un contenedor.
- **Uso:**
  - `/coger espada` - Recoge una espada del suelo
  - `/coger pocion de mochila` - Saca una poción de una mochila
- **Notas:**
  - Si se especifica un contenedor, delega a `/sacar`.
  - Los objetos pueden tener locks que restrinjan quién puede cogerlos.
  - Se notifica a la sala cuando coges un objeto.

### `/dejar <objeto>`
- **Alias:** `/d`
- **Descripción:** Deja un objeto de tu inventario en el suelo.
- **Uso:** `/dejar espada`
- **Notas:** Se notifica a la sala cuando dejas un objeto.

### `/meter <objeto> en <contenedor>`
- **Alias:** `/guardar`
- **Descripción:** Guarda un objeto en un contenedor.
- **Uso:** `/meter pocion en mochila`
- **Restricciones:**
  - El contenedor debe estar en tu inventario o en la sala.
  - El contenedor no puede estar lleno (límite definido en `capacity`).
  - El contenedor puede tener locks.
- **Notas:** Se notifica a la sala cuando guardas un objeto.

### `/sacar <objeto> de <contenedor>`
- **Descripción:** Saca un objeto de un contenedor.
- **Uso:** `/sacar pocion de mochila`
- **Restricciones:**
  - El contenedor debe estar en tu inventario o en la sala.
  - El contenedor puede tener locks.
- **Notas:** Se notifica a la sala cuando sacas un objeto.

---

## Canales de Comunicación

### `/canales`
- **Descripción:** Muestra los canales disponibles y tu estado de suscripción.
- **Notas:** Lista todos los canales estáticos del juego con su estado (activado/desactivado).

### `/activarcanal <nombre>`
- **Descripción:** Activa un canal para recibir sus mensajes.
- **Uso:** `/activarcanal novato`
- **Notas:** Debes activar un canal antes de poder enviar mensajes en él.

### `/desactivarcanal <nombre>`
- **Descripción:** Desactiva un canal para no recibir sus mensajes.
- **Uso:** `/desactivarcanal sistema`
- **Notas:** Si desactivas un canal, no podrás enviar ni recibir mensajes de él.

### Canales Dinámicos (Enviar Mensajes)

Los siguientes comandos se generan automáticamente según los canales definidos:

#### `/novato <mensaje>`
- **Descripción:** Envía un mensaje por el canal Novato (📢).
- **Uso:** `/novato ¿Cómo me muevo por el mapa?`
- **Restricciones:** Debes tener el canal activado.
- **Notas:** Canal para que nuevos jugadores pidan ayuda.

#### `/sistema <mensaje>`
- **Descripción:** Envía un mensaje por el canal Sistema (⚙️).
- **Uso:** `/sistema Mantenimiento en 5 minutos`
- **Restricciones:**
  - Solo usuarios con rol ADMIN o superior.
  - Debes tener el canal activado.
- **Notas:** Canal para anuncios del juego y notificaciones automáticas.

---

## Listados y Paginación

### `/items [página]`
- **Descripción:** Muestra todos los items de la sala actual con paginación.
- **Uso:**
  - `/items` - Muestra la primera página
  - `/items 2` - Muestra la página 2
- **Notas:** Útil cuando hay muchos objetos en el suelo.

### `/personajes [página]`
- **Descripción:** Muestra todos los personajes en la sala actual con paginación.
- **Uso:**
  - `/personajes` - Muestra la primera página
  - `/personajes 2` - Muestra la página 2
- **Restricciones:** Solo muestra jugadores online.
- **Notas:** Útil en salas concurridas.

---

## Configuración

### `/config`
- **Alias:** `/opciones`
- **Descripción:** Muestra las opciones de configuración disponibles.
- **Notas:**
  - Actualmente enfocado en gestión de canales.
  - En el futuro incluirá más opciones de personalización.

---

# Comandos de Administrador

Todos los comandos de administrador requieren el rol **ADMIN** o superior, a menos que se especifique lo contrario.

## Generación de Entidades (Spawning)

### `/generarobjeto <clave_prototipo>`
- **Alias:** `/genobj`
- **Permiso:** ADMIN
- **Descripción:** Genera un objeto en la sala actual a partir de su clave de prototipo.
- **Uso:** `/generarobjeto espada_viviente`
- **Notas:**
  - La clave debe existir en `game_data/item_prototypes.py`.
  - El objeto aparece en el suelo de la sala actual.
  - Se envía un mensaje social a todos en la sala.

---

## Movimiento Administrativo

### `/teleport <id_sala>`
- **Alias:** `/tp`
- **Permiso:** ADMIN
- **Descripción:** Teletranspórtate a cualquier sala usando su ID numérico.
- **Uso:** `/tp 3`
- **Notas:**
  - Usa `/listarsalas` para ver los IDs de todas las salas.
  - No está sujeto a las restricciones de salidas normales.
  - Actualiza automáticamente tus comandos disponibles según la nueva sala.

---

## Información y Diagnóstico

### `/listarsalas`
- **Alias:** `/lsalas`
- **Permiso:** ADMIN
- **Descripción:** Muestra ID, Clave y Nombre de todas las salas del mundo.
- **Notas:** Esencial para usar `/teleport` y navegar el mundo.

### `/examinarsala <id o key>`
- **Alias:** `/exsala`
- **Permiso:** ADMIN
- **Descripción:** Examina información detallada de una sala por ID o key.
- **Uso:**
  - `/examinarsala 1`
  - `/examinarsala plaza_central`
- **Información mostrada:**
  - ID, key, nombre, descripción
  - Locks aplicados
  - Salidas disponibles
  - Objetos en la sala
  - Personajes en la sala

### `/examinarpersonaje <nombre o ID>`
- **Alias:** `/exchar`
- **Permiso:** ADMIN
- **Descripción:** Muestra información detallada de un personaje.
- **Uso:**
  - `/exchar Gandalf`
  - `/exchar 1`
- **Información mostrada:**
  - ID del personaje y de la cuenta
  - Rol de la cuenta
  - Sala actual
  - CommandSets base
  - Inventario completo

### `/examinarobjeto <ID>`
- **Alias:** `/exobj`
- **Permiso:** ADMIN
- **Descripción:** Muestra información detallada de una instancia de objeto.
- **Uso:** `/exobj 12`
- **Información mostrada:**
  - ID de la instancia
  - Clave de prototipo
  - Ubicación (sala, inventario o contenedor)
  - Overrides de nombre y descripción

### `/validar`
- **Alias:** `/reportevalidacion`
- **Permiso:** ADMIN
- **Descripción:** Muestra un reporte de validación de integridad del sistema.
- **Notas:**
  - Detecta conflictos de aliases entre comandos.
  - Identifica keys duplicadas.
  - Muestra advertencias de configuración.
  - Útil para diagnosticar problemas después de modificar prototipos o comandos.

---

## Gestión del Juego

### `/asignarrol <nombre_personaje> <rol>`
- **Permiso:** SUPERADMIN
- **Descripción:** Cambia el rol de la cuenta asociada al personaje especificado.
- **Uso:** `/asignarrol Gandalf ADMIN`
- **Roles disponibles:** JUGADOR, ADMIN, SUPERADMIN
- **Restricciones:**
  - No puedes asignar un rol igual o superior al tuyo a otra persona.
  - Solo el SUPERADMIN puede usar este comando.
- **Notas:** El cambio de rol afecta inmediatamente los comandos disponibles para el jugador.

---

## Notas Generales

### Sobre los Aliases
- Muchos comandos tienen aliases (formas abreviadas de escribirlos).
- Los aliases se muestran entre paréntesis en la descripción.
- Ejemplo: `/mirar` puede escribirse como `/m` o `/l`.

### Sobre los Permisos
- Los comandos de jugador están disponibles para todos por defecto.
- Los comandos de admin requieren el rol ADMIN o SUPERADMIN.
- Los comandos pueden tener locks adicionales definidos en sus prototipos.

### Sobre las Notificaciones Sociales
- Muchas acciones notifican a otros jugadores en la sala.
- Solo los jugadores online recibirán estas notificaciones.
- Las notificaciones aparecen en cursiva para diferenciarlas del texto normal.

### Sobre la Paginación
- Varios comandos soportan paginación para listas largas.
- La configuración por defecto muestra 20 items por página.
- Usa el argumento de página para navegar: `/comando [número_página]`.

---

**Versión:** 1.0
**Última actualización:** 2025-10-04
**Nota:** Esta referencia se actualiza constantemente. Consulta el código fuente en `commands/` para la implementación más reciente.
