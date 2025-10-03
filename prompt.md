Tengo este error:

(venv) PS C:\Users\benabhi\Documents\Code\python\runegram> docker logs 6c
--- [Entrypoint] Esperando a que PostgreSQL esté disponible... ---
Connection to postgres (172.18.0.3) 5432 port [tcp/postgresql] succeeded!
--- [Entrypoint] ✅ PostgreSQL está listo. ---
--- [Entrypoint] Ejecutando migraciones de la base de datos con Alembic... ---
%(levelname)-5.5s [%(name)s] %(message)s
%(levelname)-5.5s [%(name)s] %(message)s
%(levelname)-5.5s [%(name)s] %(message)s
%(levelname)-5.5s [%(name)s] %(message)s
%(levelname)-5.5s [%(name)s] %(message)s
%(levelname)-5.5s [%(name)s] %(message)s
%(levelname)-5.5s [%(name)s] %(message)s
%(levelname)-5.5s [%(name)s] %(message)s
%(levelname)-5.5s [%(name)s] %(message)s
%(levelname)-5.5s [%(name)s] %(message)s
%(levelname)-5.5s [%(name)s] %(message)s
%(levelname)-5.5s [%(name)s] %(message)s
%(levelname)-5.5s [%(name)s] %(message)s
%(levelname)-5.5s [%(name)s] %(message)s
%(levelname)-5.5s [%(name)s] %(message)s
%(levelname)-5.5s [%(name)s] %(message)s
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/dialects/postgresql/asyncpg.py", line 552, in _prepare_and_execute
    self._rows = await prepared_stmt.fetch(*parameters)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/asyncpg/prepared_stmt.py", line 176, in fetch
    data = await self.__bind_execute(args, 0, timeout)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/asyncpg/prepared_stmt.py", line 241, in __bind_execute
    data, status, _ = await self.__do_execute(
                      ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/asyncpg/prepared_stmt.py", line 230, in __do_execute
    return await executor(protocol)
           ^^^^^^^^^^^^^^^^^^^^^^^^
  File "asyncpg/protocol/protocol.pyx", line 201, in bind_execute
asyncpg.exceptions.UndefinedObjectError: index "ix_apscheduler_jobs_next_run_time" does not exist

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1965, in _exec_single_context
    self.dialect.do_execute(
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/default.py", line 921, in do_execute
    cursor.execute(statement, parameters)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/dialects/postgresql/asyncpg.py", line 585, in execute
    self._adapt_connection.await_(
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 125, in await_only
    return current.driver.switch(awaitable)  # type: ignore[no-any-return]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 185, in greenlet_spawn
    value = await result
            ^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/dialects/postgresql/asyncpg.py", line 564, in _prepare_and_execute
    self._handle_exception(error)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/dialects/postgresql/asyncpg.py", line 515, in _handle_exception
    self._adapt_connection._handle_exception(error)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/dialects/postgresql/asyncpg.py", line 802, in _handle_exception
    raise translated_error from error
sqlalchemy.dialects.postgresql.asyncpg.AsyncAdapt_asyncpg_dbapi.ProgrammingError: <class 'asyncpg.exceptions.UndefinedObjectError'>: index "ix_apscheduler_jobs_next_run_time" does not exist

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/usr/local/bin/alembic", line 8, in <module>
    sys.exit(main())
             ^^^^^^
  File "/usr/local/lib/python3.11/site-packages/alembic/config.py", line 630, in main
    CommandLine(prog=prog).main(argv=argv)
  File "/usr/local/lib/python3.11/site-packages/alembic/config.py", line 624, in main
    self.run_cmd(cfg, options)
  File "/usr/local/lib/python3.11/site-packages/alembic/config.py", line 601, in run_cmd
    fn(
  File "/usr/local/lib/python3.11/site-packages/alembic/command.py", line 399, in upgrade
    script.run_env()
  File "/usr/local/lib/python3.11/site-packages/alembic/script/base.py", line 578, in run_env
    util.load_python_file(self.dir, "env.py")
  File "/usr/local/lib/python3.11/site-packages/alembic/util/pyfiles.py", line 93, in load_python_file
    module = load_module_py(module_id, path)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/alembic/util/pyfiles.py", line 109, in load_module_py
    spec.loader.exec_module(module)  # type: ignore
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap_external>", line 940, in exec_module
  File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
  File "/app/alembic/env.py", line 120, in <module>
    asyncio.run(run_migrations_online())
  File "/usr/local/lib/python3.11/asyncio/runners.py", line 190, in run
    return runner.run(main)
           ^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/asyncio/base_events.py", line 654, in run_until_complete
    return future.result()
           ^^^^^^^^^^^^^^^
  File "/app/alembic/env.py", line 111, in run_migrations_online
    await connection.run_sync(do_run_migrations)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/engine.py", line 884, in run_sync
    return await greenlet_spawn(fn, self._proxied, *arg, **kw)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 192, in greenlet_spawn
    result = context.switch(value)
             ^^^^^^^^^^^^^^^^^^^^^
  File "/app/alembic/env.py", line 91, in do_run_migrations
    context.run_migrations()
  File "<string>", line 8, in run_migrations
  File "/usr/local/lib/python3.11/site-packages/alembic/runtime/environment.py", line 937, in run_migrations
    self.get_context().run_migrations(**kw)
  File "/usr/local/lib/python3.11/site-packages/alembic/runtime/migration.py", line 624, in run_migrations
    step.migration_fn(**kw)
  File "/app/alembic/versions/c89c472e9f7b_agregar_campo_tick_data_a_items_para_.py", line 23, in upgrade
    op.drop_index('ix_apscheduler_jobs_next_run_time', table_name='apscheduler_jobs')
  File "<string>", line 8, in drop_index
  File "<string>", line 3, in drop_index
  File "/usr/local/lib/python3.11/site-packages/alembic/operations/ops.py", line 1122, in drop_index
    return operations.invoke(op)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/alembic/operations/base.py", line 393, in invoke
    return fn(self, operation)
           ^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/alembic/operations/toimpl.py", line 117, in drop_index
    operations.impl.drop_index(
  File "/usr/local/lib/python3.11/site-packages/alembic/ddl/impl.py", line 395, in drop_index
    self._exec(schema.DropIndex(index, **kw))
  File "/usr/local/lib/python3.11/site-packages/alembic/ddl/impl.py", line 193, in _exec
    return conn.execute(  # type: ignore[call-overload]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1412, in execute
    return meth(
           ^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/sql/ddl.py", line 181, in _execute_on_connection
    return connection._execute_ddl(
           ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1524, in _execute_ddl
    ret = self._execute_context(
          ^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1844, in _execute_context
    return self._exec_single_context(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1984, in _exec_single_context
    self._handle_dbapi_exception(
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 2339, in _handle_dbapi_exception
    raise sqlalchemy_exception.with_traceback(exc_info[2]) from e
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1965, in _exec_single_context
    self.dialect.do_execute(
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/default.py", line 921, in do_execute
    cursor.execute(statement, parameters)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/dialects/postgresql/asyncpg.py", line 585, in execute
    self._adapt_connection.await_(
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 125, in await_only
    return current.driver.switch(awaitable)  # type: ignore[no-any-return]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 185, in greenlet_spawn
    value = await result
            ^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/dialects/postgresql/asyncpg.py", line 564, in _prepare_and_execute
    self._handle_exception(error)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/dialects/postgresql/asyncpg.py", line 515, in _handle_exception
    self._adapt_connection._handle_exception(error)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/dialects/postgresql/asyncpg.py", line 802, in _handle_exception
    raise translated_error from error
sqlalchemy.exc.ProgrammingError: (sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedObjectError'>: index "ix_apscheduler_jobs_next_run_time" does not exist
[SQL:
DROP INDEX ix_apscheduler_jobs_next_run_time]
(Background on this error at: https://sqlalche.me/e/20/f405)

