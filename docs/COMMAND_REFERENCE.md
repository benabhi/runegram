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
- **Descripción:** Observa tu entorno, un objeto, personaje, detalle o sala aledaña.
- **Uso:**
  - `/mirar` - Muestra la descripción de tu sala actual
  - `/mirar espada` - Examina un objeto específico
  - `/mirar 2.espada` - Examina la segunda espada (si hay duplicados)
  - `/mirar Gandalf` - Examina a otro jugador
  - `/mirar fuente` - Examina un detalle de la sala
  - `/mirar norte` - Ve la sala al norte sin moverte
  - `/mirar sur` - Ve la sala al sur sin moverte
- **Notas:**
  - Sin argumentos, muestra la sala completa con salidas, objetos y personajes.
  - Puede ejecutar scripts `on_look` si el objeto los tiene definidos.
  - Solo muestra jugadores que estén activamente online.
  - Soporta ordinales para objetos duplicados (ver [Sistema de Ordinales](#-sistema-de-ordinales-para-objetos-duplicados)).
  - Puedes mirar salas aledañas usando el nombre de la dirección (norte, sur, este, oeste, etc.).

### `/decir <mensaje>`
- **Alias:** `'`
- **Descripción:** Habla con las personas que están en tu misma sala.
- **Uso:**
  - `/decir Hola a todos`
  - `' Hola a todos` (usando el alias)
- **Notas:**
  - El mensaje se enviará a todos los jugadores online en la sala.
  - El mensaje aparece en cursiva para otros jugadores.

### `/emocion <acción>`
- **Alias:** `/emote`, `/me`
- **Descripción:** Expresa una emoción o acción de roleplay.
- **Uso:**
  - `/emocion se rasca la nariz` → "Benabhi se rasca la nariz"
  - `/emote sonríe ampliamente` → "Benabhi sonríe ampliamente"
  - `/me guiña un ojo` → "Benabhi guiña un ojo"
- **Notas:**
  - El mensaje se muestra a todos en la sala (incluyéndote).
  - Útil para roleplay y expresar acciones del personaje.
  - El formato es: TuNombre + acción_que_escribes

### `/inventario [contenedor] [página]`
- **Alias:** `/inv`, `/i`
- **Descripción:** Muestra tu inventario o el de un contenedor con paginación automática.
- **Uso:**
  - `/inv` - Muestra tu inventario (página 1, con botones de navegación si hay más)
  - `/inv 2` - Muestra la página 2 de tu inventario
  - `/inv mochila` - Muestra el contenido de un contenedor (página 1)
  - `/inv mochila 2` - Muestra la página 2 del contenedor
  - `/inv 2.mochila` - Muestra el contenido de la segunda mochila (si hay duplicados)
  - `/inv 2.mochila 3` - Muestra la página 3 de la segunda mochila
- **Notas:**
  - **Paginación automática:** Si tienes más de 30 items, se activan botones inline y comandos de paginación.
  - Los contenedores pueden tener locks que restrinjan el acceso.
  - Los items que son contenedores muestran cuántos items contienen.
  - Soporta ordinales para contenedores duplicados (ver [Sistema de Ordinales](#-sistema-de-ordinales-para-objetos-duplicados)).

### `/ayuda`
- **Alias:** `/help`
- **Descripción:** Muestra una lista con los comandos básicos del juego.
- **Notas:** Proporciona un resumen rápido de los comandos más comunes.

### `/quien [página]`
- **Alias:** `/who`
- **Descripción:** Muestra una lista de los jugadores conectados con paginación automática.
- **Uso:**
  - `/quien` - Muestra la página 1 (con botones de navegación si hay más jugadores)
  - `/quien 2` - Muestra la página 2 de jugadores
  - `/quien 5` - Muestra la página 5
- **Notas:**
  - Solo muestra jugadores activamente online (últimos 5 minutos de actividad).
  - Incluye la sala donde se encuentra cada jugador.
  - **Paginación automática:** Si hay más de 30 jugadores, se activan botones inline y comandos de paginación.
  - Muestra el estado AFK con el mensaje personalizado si el jugador lo ha configurado.

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

### `/afk [mensaje]`
- **Descripción:** Te marca como AFK (Away From Keyboard) con un mensaje opcional.
- **Uso:**
  - `/afk` - Te marca como AFK con mensaje por defecto
  - `/afk comiendo` - Te marca como AFK con el mensaje "comiendo"
  - `/afk vuelvo en 10 minutos` - Mensaje personalizado más descriptivo
- **Notas:**
  - Tu estado AFK será visible para otros jugadores en `/quien` con el emoji 💤
  - El estado AFK se elimina automáticamente al usar cualquier comando
  - El mensaje AFK expira después de 24 horas
  - A diferencia de la desconexión automática (5 minutos de inactividad), este comando te marca AFK de manera inmediata y visible

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
  - `/coger 2.espada` - Recoge la segunda espada (si hay duplicados)
  - `/coger pocion de mochila` - Saca una poción de una mochila
- **Notas:**
  - Si se especifica un contenedor, delega a `/sacar`.
  - Los objetos pueden tener locks que restrinjan quién puede cogerlos.
  - Se notifica a la sala cuando coges un objeto.
  - Soporta ordinales para objetos duplicados (ver [Sistema de Ordinales](#-sistema-de-ordinales-para-objetos-duplicados)).

### `/dejar <objeto>`
- **Alias:** `/d`
- **Descripción:** Deja un objeto de tu inventario en el suelo.
- **Uso:**
  - `/dejar espada`
  - `/dejar 3.espada` - Deja la tercera espada (si hay duplicados)
- **Notas:**
  - Se notifica a la sala cuando dejas un objeto.
  - Soporta ordinales para objetos duplicados (ver [Sistema de Ordinales](#-sistema-de-ordinales-para-objetos-duplicados)).

### `/meter <objeto> en <contenedor>`
- **Alias:** `/guardar`
- **Descripción:** Guarda un objeto en un contenedor.
- **Uso:**
  - `/meter pocion en mochila`
  - `/meter 2.pocion en 1.mochila` - Mete la segunda poción en la primera mochila
  - `/meter espada en 3.cofre` - Mete la espada en el tercer cofre
- **Restricciones:**
  - El contenedor debe estar en tu inventario o en la sala.
  - El contenedor no puede estar lleno (límite definido en `capacity`).
  - El contenedor puede tener locks.
- **Notas:**
  - Se notifica a la sala cuando guardas un objeto.
  - Ambos argumentos (objeto y contenedor) soportan ordinales (ver [Sistema de Ordinales](#-sistema-de-ordinales-para-objetos-duplicados)).

### `/sacar <objeto> de <contenedor>`
- **Descripción:** Saca un objeto de un contenedor.
- **Uso:**
  - `/sacar pocion de mochila`
  - `/sacar 1.daga de 2.cofre` - Saca la primera daga del segundo cofre
  - `/sacar espada de 3.mochila` - Saca la espada de la tercera mochila
- **Restricciones:**
  - El contenedor debe estar en tu inventario o en la sala.
  - El contenedor puede tener locks.
- **Notas:**
  - Se notifica a la sala cuando sacas un objeto.
  - Ambos argumentos (objeto y contenedor) soportan ordinales (ver [Sistema de Ordinales](#-sistema-de-ordinales-para-objetos-duplicados)).

### `/dar <objeto> a <personaje>`
- **Alias:** `/give`
- **Descripción:** Da un objeto de tu inventario a otro personaje.
- **Uso:**
  - `/dar espada a Gandalf` - Le das la espada a Gandalf
  - `/dar 2.pocion a Legolas` - Le das la segunda poción a Legolas
- **Restricciones:**
  - El personaje debe estar en tu misma sala.
  - El personaje debe estar online.
  - Solo puedes dar objetos que tengas en tu inventario.
- **Notas:**
  - Se notifica a la sala cuando das un objeto (excepto al que da y al que recibe).
  - El que recibe recibe un mensaje directo.
  - Si el objeto otorga command sets, se actualizan los comandos de ambos jugadores.
  - Soporta ordinales para objetos duplicados (ver [Sistema de Ordinales](#-sistema-de-ordinales-para-objetos-duplicados)).

### 🔢 Sistema de Ordinales para Objetos Duplicados

Cuando tienes múltiples objetos con el mismo nombre, Runegram utiliza un **sistema de ordinales** (números) para identificarlos de forma única.

#### ¿Cómo funciona?

Todos los listados de objetos (inventario, sala, contenedores) muestran números automáticamente:

```
📦 Tu Inventario:
1. ⚔️ espada oxidada
2. 🎒 mochila de cuero
3. ⚔️ espada brillante
4. 🧪 poción de vida
```

Si intentas interactuar con un objeto duplicado sin especificar cuál, recibirás un mensaje de desambiguación:

```
❓ Hay 2 'espada'. ¿Cuál?

1. ⚔️ espada oxidada
2. ⚔️ espada brillante

Usa:
/coger 1.espada
/coger 2.espada
```

#### Sintaxis de Ordinales: `N.nombre`

Para especificar un objeto duplicado, usa el formato **`N.nombre`** donde N es el número del objeto:

- `/coger 2.espada` - Coge la segunda espada
- `/mirar 1.mochila` - Examina la primera mochila
- `/meter 3.pocion en 1.mochila` - Mete la tercera poción en la primera mochila
- `/sacar 2.daga de 2.cofre` - Saca la segunda daga del segundo cofre

#### Comandos que Soportan Ordinales

✅ **Todos los comandos de interacción con objetos:**
- `/mirar N.objeto` - Examinar objetos duplicados
- `/coger N.objeto` - Coger objetos duplicados
- `/dejar N.objeto` - Dejar objetos duplicados
- `/meter N.objeto en N.contenedor` - Ambos argumentos soportan ordinales
- `/sacar N.objeto de N.contenedor` - Ambos argumentos soportan ordinales
- `/inventario N.contenedor` - Ver contenido de contenedores duplicados

#### Notas Importantes

- **Compatibilidad hacia atrás:** Si solo hay un objeto con ese nombre, no necesitas usar ordinales.
  - `/coger espada` funciona si solo hay una espada.
- **Números basados en 1:** Los números empiezan en 1, no en 0.
- **Desambiguación automática:** Si no usas ordinales y hay duplicados, recibirás una lista con instrucciones.
- **Combinaciones flexibles:** Puedes mezclar ordinales con nombres normales:
  - `/meter pocion en 2.mochila` (poción única, segunda mochila)

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

Los siguientes comandos se generan **automáticamente** según los canales definidos en `game_data/channel_prototypes.py`:

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

**Nota:** Cada canal de tipo `CHAT` en los prototipos genera automáticamente un comando con su nombre. Para agregar nuevos canales, edita `game_data/channel_prototypes.py`.

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
  - Se envía un mensaje social a todos en la sala (solo jugadores online).

### `/destruirobjeto <ID>`
- **Alias:** `/delobj`
- **Permiso:** ADMIN
- **Descripción:** Elimina permanentemente un objeto del juego usando su ID numérico.
- **Uso:** `/destruirobjeto 42`
- **⚠️ ADVERTENCIA:** Esta acción es irreversible.
- **Notas:**
  - Usa `/examinarobjeto <ID>` o `/listaritems` para obtener el ID del objeto.
  - Si el objeto es un contenedor, los items dentro quedan huérfanos (sin parent).
  - NO envía mensaje social a la sala (usa `/decir` si quieres notificar a los jugadores).
  - El objeto se elimina permanentemente de la base de datos.

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

### `/listarsalas [cat:X] [tag:Y,Z]`
- **Alias:** `/lsalas`
- **Permiso:** ADMIN
- **Descripción:** Muestra ID, Clave y Nombre de todas las salas del mundo. Soporta filtrado por categoría y tags.
- **Uso:**
  - `/listarsalas` - Todas las salas
  - `/listarsalas cat:ciudad_runegard` - Solo salas de esa categoría
  - `/listarsalas tag:exterior` - Solo salas con ese tag
  - `/listarsalas tag:exterior,seguro` - Solo salas con ambos tags (AND)
- **Sintaxis de filtros:**
  - `cat:X` - Filtra por categoría X
  - `tag:Y,Z` - Filtra por tags Y y Z (separados por coma, lógica AND)
- **Notas:** Esencial para usar `/teleport` y navegar el mundo. Usa formato lista optimizado para móvil.

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

## Búsqueda por Categories y Tags

### `/listaritems [cat:X] [tag:Y,Z]`
- **Alias:** `/litems`
- **Permiso:** ADMIN
- **Descripción:** Lista items filtrados por categoría y tags.
- **Uso:**
  - `/listaritems` - Todos los items
  - `/listaritems cat:arma` - Solo items de esa categoría
  - `/listaritems tag:magica` - Solo items con ese tag
  - `/listaritems tag:magica,unica` - Solo items con ambos tags (AND)
- **Sintaxis de filtros:**
  - `cat:X` - Filtra por categoría X
  - `tag:Y,Z` - Filtra por tags Y y Z (separados por coma, lógica AND)
- **Notas:** Muestra ubicación (inventario/sala/contenedor), categoría y tags de cada item. Límite de 20 resultados. Formato lista optimizado para móvil.

### `/listarcategorias`
- **Alias:** `/cats`, `/lcats`
- **Permiso:** ADMIN
- **Descripción:** Muestra todas las categorías disponibles de salas e items.
- **Notas:** Útil para conocer qué categorías están definidas en los prototipos antes de filtrar. Formato lista optimizado para móvil.

### `/listartags`
- **Alias:** `/etiquetas`, `/ltags`
- **Permiso:** ADMIN
- **Descripción:** Muestra todos los tags disponibles de salas e items.
- **Notas:** Útil para conocer qué tags están definidos en los prototipos antes de filtrar. Formato lista optimizado para móvil.

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
- Varios comandos usan **paginación automática** para listas largas.
- La configuración por defecto muestra **30 items por página**.
- Usa el argumento de página para navegar: `/comando [número_página]`.
- **Navegación dual:** Puedes navegar con comandos (`/inv 2`) o con botones inline (⬅️ ➡️).
- **Comandos con paginación automática:**
  - `/inventario` - Si tienes más de 30 items
  - `/quien` - Si hay más de 30 jugadores
  - `/items` - Siempre usa paginación
  - `/personajes` - Siempre usa paginación
  - `/listarsalas`, `/listaritems` (admin) - Siempre usan paginación
- **Comandos con truncado (sin paginación):**
  - `/mirar` (sala) - Muestra máximo 10 items y usa "... y X más" (usa `/items` para ver todos)

---

**Versión:** 1.6
**Última actualización:** 2025-10-09
**Changelog:**
- v1.6 (2025-10-09): Agregado comando `/destruirobjeto` para eliminar objetos del juego
- v1.5 (2025-10-09): **Paginación unificada** - `/inventario` y `/quien` ahora usan paginación automática sin necesidad de "todo"; eliminada inconsistencia entre límites de visualización y paginación
- v1.4 (2025-10-05): Refactorizado sintaxis de filtros (category→cat, tags con comas), agregado sistema de templates, formato lista optimizado para móvil
- v1.3.1 (2025-10-05): Renombrados comandos a /listarcategorias y /listartags para consistencia
- v1.3 (2025-10-05): Agregado sistema de Categories/Tags con comandos de búsqueda (/listaritems, /listarcategorias, /listartags); extendido /listarsalas con filtros
- v1.2 (2025-10-04): Agregado sistema de ordinales para objetos duplicados (sintaxis N.nombre)
- v1.1 (2025-10-04): Agregada nota sobre generación automática de comandos de canales dinámicos
- v1.0 (2025-10-04): Primera versión completa de la referencia

**Nota:** Esta referencia se actualiza constantemente. Consulta el código fuente en `commands/` para la implementación más reciente.
