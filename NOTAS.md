## TODO

* Se pueden meter contenedores en contenedores?
* Sistema de habilidades
* Sistema de magia (low magic) runas (lo que le da nombre al juego)
* Comando mapa con los puntos cardinales y las salidas y si existe o no sala
* Sistema de tags y categorias como evennia?
* Sistema de ayuda que parsee docuemtos fiisicos.
* Cuanto duran los items tirados en una sala?
* En el titulo de la sala me gustaria que se pueda poner al principio y de forma opcional un icono (emoji), deberia estar por defecto vacio en el prototipo.
* Es necesario que los keys sean unicos? me parece que pudo reformular esto:
    - por ejemplo si el key esta repetido por ejemplo "/meter espada en mochila", deberia preguntarme que espada? en que mochila? (tambien estaria bueno que en el inventario los items tengan numeracion por si hay "dos" mochilas)
* Cuando el admin usa teleport estaria bueno que en la sala diga un mensaje interesante sobre eso.
* Cuando un persoanje se va de un area debe notificar al resto <personaje> se ha movido hacia <direccion> o algo asi. Lo mismo a la inversa <personaje> ha llegado desde <direccion>
* TODOS los comandos del juego deben devolver sus mensajes en un estilo <pre> o (```) formato de codigo como lo hace el comando /mirar actualmente, debe ser una filosofia de diseño, usar emojis dentro esta bien para dar mas estilo pero siempre debe estar la respuesta completa en <pre>. Guardare esta informacion en la documentacion y en CLAUDE.md.
* Si el usuario está afk no debería mostrarse en /mirar, al no tener la posibilidad de logout vamos a usar este sistema para algo similar, puesto que si 500 usuarios están afk la lista sería interminable en /mirar, documentar esto de como vamos a usar el afk por qué puede ser de utilidad para otros comandos. También debería contemplar el "cuando" ponerse afk posteriormente puesto que no tiene sentido quedarse afk durante un combate si no hago nada, obviamente cuando el combate esté implementado, pero al igual que este ejemplo seguramente pose con otras cosas, simplemente afk es cuando el personaje esta tranquilo (talvez se podria evitar afk si hay enemigo ocosas parecidas)
* Crear librerias de facil accedo como api, como tiene evennia:

```
La siguiente estructura es para ejemplificar (es solo un ejemplo!) como expone las funciones el frameworks de muds clasicos escrito en python "evennia" en una api clara y de facil acceso:
    evennia.accounts - the out-of-character entities representing players
    evennia.commands - handle all inputs. Also includes default commands
    evennia.comms - in-game channels and messaging
    evennia.contrib - game-specific tools and code contributed by the community
    evennia.help - in-game help system
    evennia.locks - limiting access to various systems and resources
    evennia.objects - all in-game entities, like Rooms, Characters, Exits etc
    evennia.prototypes - customize entities using dicts
    evennia.scripts - all out-of-character game objects
    evennia.server - core Server and Portal programs, also network protocols
    evennia.typeclasses - core database-python bridge
    evennia.utils - lots of useful coding tools and utilities
    evennia.web - webclient, website and other web resources
```

Tambien tiene atajos o shortcuts para funciones de busqueda como evennia.search_object, etc

(Repito que el listado anterior es solo un ejemplo la idea seria adaptar algo similar a lo que tengo yo y los requisitos de mi proyecto)

ver https://www.evennia.com/docs/latest/Evennia-API.html para tener una idea mas amplia.

Es posible que yo pueda hacer algo similar en mi mud para ir previendo temas de escalabilidada a futuro?

De ser posible esta implementacion tambien deberiamos refactorizar para que los archuivos del mud usen esta api para dejar todo mas limpio si es que en reliadad hace una diferencia.



* Comandos a futuro.
    * Jugador
        - /personaje: Informacion general del personaje
        - /estado: ve el estado del personaje (ardiendo, envenenado, etc)
        - /vestir <armadura>: para colocarse una armadura
        - /empuñar <arma>: para equiparse un arma
        - /dar <objeto> a <personaje>: para dar un item a otro personaje
        - /seguir <personaje>: para seguir automaticamente a un pesonaje
        - /correr <s,e,e,n,o>: para hacer un camino de multiples salas
        - /inspeccionar <objeto|personaje>: para dar detalles finos de algo
        - /party: para chequear el grupo
        - /clan: podria ser el canal de comunicacion del clan
        - /atacar <monstruo>: para comenzar una lucha con un monstruo.
        - /suicidio: para eliminar el personaje
        - /hablar <npc>: para comenzar dialogo con npc
        - /listaamigos: lista de amigos
        - /agregaramigo <personaje>: agrega un personaje a la lista de amigos
        - /quitaramigo <personaje>: remueve un personaje de la lista de migos
        - /quienes <personaje>: informacion publica de un personaje
        - /mapa: muestra un mapa detalaldo del area del pesonaje y las cicundantes.
        - /emocion <emocion>: por ejemplo /emocion se rie a cargajadas -> benabhi se rie a carcajadas
    * Admin
        - /banearcuenta <personaje|cuenta>: bloquea acceso a una cuenta
        - /desbanearcuenta <personaje|cuenta>: desbloquea el acceso a una cuenta

    Seguir pensando mas comandos para administradores y jugadores...





## Test que faltan

  Test Coverage Analysis:

  Services WITH tests:
  - ✅ permission_service.py (90% coverage)
  - ✅ validation_service.py (97% coverage)

  Services WITHOUT tests (CRITICAL):
  - ❌ player_service.py (20% coverage) - Account/character management
  - ❌ broadcaster_service.py (27% coverage) - Messaging system
  - ❌ channel_service.py (21% coverage) - Channel management
  - ❌ online_service.py (26% coverage) - Session management
  - ❌ item_service.py (32% coverage) - Item operations
  - ❌ command_service.py (20% coverage) - Command discovery
  - ❌ world_loader_service.py (0% coverage) - World initialization
  - ❌ world_service.py (0% coverage) - World state

  Commands WITHOUT tests (ALL):
  - ❌ No command tests exist for any commands (general, movement, interaction, channels, admin, etc.)

  The test infrastructure is working correctly, but command tests and most service tests are missing. The existing tests cover validation and
  permissions well, which are foundational systems.