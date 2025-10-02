Primero arreglar estos errores

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

---------------------------------

IMPLEMENTACION DEL SSITEMA DE TEST (quedo a medio empezar por se habia alcanzado el limite de preguntas de claude)

continuar con el sistema de tests que habiamos empezado

Creo que estamos en un punto donde ya hace faltan "tests".

Crear un sistema robusto de tests en la carpeta tests que contemple las cosas que son realmente importante.

* Tests para evaluar comandos.
* Tests para funcionalidades criticas
* Tests para services?

Verificar cuales son los test importantes, no quiero test que no tenga mucha relevancia.
Documentar e incluir en el CLAUDE.md que siempre hay que vericicar tests y actualizar como pasa con la documentacion.