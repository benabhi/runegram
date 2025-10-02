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


## Errores

* Al usar el comando "decir" me dice "Dices <mensaje>" pero a los personajes de la misma sala no les aparece "Benbhi dice XXX" o algo similar, no les aparece anda.

* La priemra vez que quise crear una cuenta que no sea la de admin salio esto, intente una vez mas una segunda vez y se creo el personaje, pero no entiendo por que fallo la primera.

```
2025-10-02 13:33:47 [INFO] - root: Creando nueva cuenta para el telegram_id: 1534804932
2025-10-02 13:33:47 [ERROR] - root: Error crítico no manejado en el dispatcher principal para el usuario 1534804932
Traceback (most recent call last):
  File "/app/src/handlers/player/dispatcher.py", line 79, in main_command_dispatcher
    character = account.character
                ^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/attributes.py", line 566, in __get__
    return self.impl.get(state, dict_)  # type: ignore[no-any-return]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/attributes.py", line 1086, in get
    value = self._fire_loader_callables(state, key, passive)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/attributes.py", line 1121, in _fire_loader_callables
    return self.callable_(state, passive)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/strategies.py", line 966, in _load_for_state
    return self._emit_lazyload(
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/strategies.py", line 1129, in _emit_lazyload
    result = session.execute(
             ^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 2262, in execute
    return self._execute_internal(
           ^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 2144, in _execute_internal
    result: Result[Any] = compile_state_cls.orm_execute_statement(
                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/context.py", line 293, in orm_execute_statement
    result = conn.execute(
             ^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1412, in execute
    return meth(
           ^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/sql/elements.py", line 516, in _execute_on_connection
    return connection._execute_clauseelement(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1635, in _execute_clauseelement
    ret = self._execute_context(
          ^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1844, in _execute_context
    return self._exec_single_context(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1984, in _exec_single_context
    self._handle_dbapi_exception(
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 2342, in _handle_dbapi_exception
    raise exc_info[1].with_traceback(exc_info[2])
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1965, in _exec_single_context
    self.dialect.do_execute(
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/default.py", line 921, in do_execute
    cursor.execute(statement, parameters)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/dialects/postgresql/asyncpg.py", line 585, in execute
    self._adapt_connection.await_(
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 116, in await_only
    raise exc.MissingGreenlet(
sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called; can't call await_only() here. Was IO attempted in an unexpected place? (Background on this error at: https://sqlalche.me/e/20/xd2s)
2025-10-02 13:34:00 [INFO] - apscheduler.executors.default: Running job "execute_ticker_script (trigger: cron[month='*', day='*', day_of_week='*', hour='*', minute='*/2'], next run at: 2025-10-02 13:36:00 UTC)" (scheduled at 2025-10-02 13:34:00+00:00)
2025-10-02 13:34:00 [INFO] - apscheduler.executors.default: Job "execute_ticker_script (trigger: cron[month='*', day='*', day_of_week='*', hour='*', minute='*/2'], next run at: 2025-10-02 13:36:00 UTC)" executed successfully
```

* Al usar /susurrar cristian <mensaje> me da ele error, cristian era el otro personaje

```
2025-10-02 13:37:35 [ERROR] - root: Fallo al ejecutar /susurrar para benabhi
Traceback (most recent call last):
  File "/app/commands/player/general.py", line 290, in execute
    await broadcaster_service.send_message_to_character(
  File "/app/src/services/broadcaster_service.py", line 47, in send_message_to_character
    if not character.account:
           ^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/attributes.py", line 566, in __get__
    return self.impl.get(state, dict_)  # type: ignore[no-any-return]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/attributes.py", line 1086, in get
    value = self._fire_loader_callables(state, key, passive)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/attributes.py", line 1121, in _fire_loader_callables
    return self.callable_(state, passive)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/strategies.py", line 966, in _load_for_state
    return self._emit_lazyload(
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/strategies.py", line 1067, in _emit_lazyload
    return loading.load_on_pk_identity(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/loading.py", line 666, in load_on_pk_identity
    session.execute(
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 2262, in execute
    return self._execute_internal(
           ^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 2144, in _execute_internal
    result: Result[Any] = compile_state_cls.orm_execute_statement(
                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/context.py", line 293, in orm_execute_statement
    result = conn.execute(
             ^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1412, in execute
    return meth(
           ^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/sql/elements.py", line 516, in _execute_on_connection
    return connection._execute_clauseelement(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1635, in _execute_clauseelement
    ret = self._execute_context(
          ^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1844, in _execute_context
    return self._exec_single_context(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1984, in _exec_single_context
    self._handle_dbapi_exception(
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 2342, in _handle_dbapi_exception
    raise exc_info[1].with_traceback(exc_info[2])
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1965, in _exec_single_context
    self.dialect.do_execute(
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/default.py", line 921, in do_execute
    cursor.execute(statement, parameters)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/dialects/postgresql/asyncpg.py", line 585, in execute
    self._adapt_connection.await_(
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 116, in await_only
    raise exc.MissingGreenlet(
sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called; can't call await_only() here. Was IO attempted in an unexpected place? (Background on this error at: https://sqlalche.me/e/20/xd2s)
2025-10-02 13:37:42 [INFO] - apscheduler.executors.default: Running job "check_for_newly_afk_players (trigger: interval[0:01:00], next run at: 2025-10-02 13:38:42 UTC)" (scheduled at 2025-10-02 13:37:42.235806+00:00)
2025-10-02 13:37:42 [INFO] - root: [AFK CHECK] Ejecutando chequeo de jugadores inactivos...
2025-10-02 13:37:42 [INFO] - root: [AFK CHECK] Chequeo finalizado. 2 jugadores online.
2025-10-02 13:37:42 [INFO] - apscheduler.executors.default: Job "check_for_newly_afk_players (trigger: interval[0:01:00], next run at: 2025-10-02 13:38:42 UTC)" executed successfully
```
* Error al examinar otro personaje

```
2025-10-02 13:54:13 [ERROR] - root: Fallo al ejecutar /examinarpersonaje para 'cristian'
Traceback (most recent call last):
  File "/app/commands/admin/diagnostics.py", line 56, in execute
    f"<b>Cuenta ID:</b> {full_char.account_id} (Rol: {full_char.account.role})",
                                                      ^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/attributes.py", line 566, in __get__
    return self.impl.get(state, dict_)  # type: ignore[no-any-return]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/attributes.py", line 1086, in get
    value = self._fire_loader_callables(state, key, passive)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/attributes.py", line 1121, in _fire_loader_callables
    return self.callable_(state, passive)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/strategies.py", line 966, in _load_for_state
    return self._emit_lazyload(
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/strategies.py", line 1067, in _emit_lazyload
    return loading.load_on_pk_identity(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/loading.py", line 666, in load_on_pk_identity
    session.execute(
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 2262, in execute
    return self._execute_internal(
           ^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 2144, in _execute_internal
    result: Result[Any] = compile_state_cls.orm_execute_statement(
                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/context.py", line 293, in orm_execute_statement
    result = conn.execute(
             ^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1412, in execute
    return meth(
           ^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/sql/elements.py", line 516, in _execute_on_connection
    return connection._execute_clauseelement(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1635, in _execute_clauseelement
    ret = self._execute_context(
          ^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1844, in _execute_context
    return self._exec_single_context(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1984, in _exec_single_context
    self._handle_dbapi_exception(
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 2342, in _handle_dbapi_exception
    raise exc_info[1].with_traceback(exc_info[2])
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1965, in _exec_single_context
    self.dialect.do_execute(
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/default.py", line 921, in do_execute
    cursor.execute(statement, parameters)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/dialects/postgresql/asyncpg.py", line 585, in execute
    self._adapt_connection.await_(
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 116, in await_only
    raise exc.MissingGreenlet(
sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called; can't call await_only() here. Was IO attempted in an unexpected place? (Background on this error at: https://sqlalche.me/e/20/xd2s)
2025-10-02 13:54:30 [ERROR] - root: Fallo al ejecutar /examinarpersonaje para '2'
Traceback (most recent call last):
  File "/app/commands/admin/diagnostics.py", line 56, in execute
    f"<b>Cuenta ID:</b> {full_char.account_id} (Rol: {full_char.account.role})",
                                                      ^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/attributes.py", line 566, in __get__
    return self.impl.get(state, dict_)  # type: ignore[no-any-return]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/attributes.py", line 1086, in get
    value = self._fire_loader_callables(state, key, passive)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/attributes.py", line 1121, in _fire_loader_callables
    return self.callable_(state, passive)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/strategies.py", line 966, in _load_for_state
    return self._emit_lazyload(
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/strategies.py", line 1067, in _emit_lazyload
    return loading.load_on_pk_identity(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/loading.py", line 666, in load_on_pk_identity
    session.execute(
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 2262, in execute
    return self._execute_internal(
           ^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 2144, in _execute_internal
    result: Result[Any] = compile_state_cls.orm_execute_statement(
                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/context.py", line 293, in orm_execute_statement
    result = conn.execute(
             ^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1412, in execute
    return meth(
           ^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/sql/elements.py", line 516, in _execute_on_connection
    return connection._execute_clauseelement(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1635, in _execute_clauseelement
    ret = self._execute_context(
          ^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1844, in _execute_context
    return self._exec_single_context(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1984, in _exec_single_context
    self._handle_dbapi_exception(
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 2342, in _handle_dbapi_exception
    raise exc_info[1].with_traceback(exc_info[2])
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1965, in _exec_single_context
    self.dialect.do_execute(
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/default.py", line 921, in do_execute
    cursor.execute(statement, parameters)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/dialects/postgresql/asyncpg.py", line 585, in execute
    self._adapt_connection.await_(
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 116, in await_only
    raise exc.MissingGreenlet(
sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called; can't call await_only() here. Was IO attempted in an unexpected place? (Background on this error at: https://sqlalche.me/e/20/xd2s)
2025-10-02 13:54:42 [INFO] - apscheduler.executors.default: Running job "check_for_newly_afk_players (trigger: interval[0:01:00], next run at: 2025-10-02 13:55:42 UTC)" (scheduled at 2025-10-02 13:54:42.235806+00:00)
2025-10-02 13:54:42 [INFO] - root: [AFK CHECK] Ejecutando chequeo de jugadores inactivos...
2025-10-02 13:54:42 [INFO] - root: [AFK CHECK] Chequeo finalizado. 1 jugadores online.
2025-10-02 13:54:42 [INFO] - apscheduler.executors.default: Job "check_for_newly_afk_players (trigger: interval[0:01:00], next run at: 2025-10-02 13:55:42 UTC)" executed successfully
2025-10-02 13:55:42 [INFO] - apscheduler.executors.default: Running job "check_for_newly_afk_players (trigger: interval[0:01:00], next run at: 2025-10-02 13:56:42 UTC)" (scheduled at 2025-10-02 13:55:42.235806+00:00)
2025-10-02 13:55:42 [INFO] - root: [AFK CHECK] Ejecutando chequeo de jugadores inactivos...
2025-10-02 13:55:42 [INFO] - root: [AFK CHECK] Chequeo finalizado. 1 jugadores online.
2025-10-02 13:55:42 [INFO] - apscheduler.executors.default: Job "check_for_newly_afk_players (trigger: interval[0:01:00], next run at: 2025-10-02 13:56:42 UTC)" executed successfully
```
