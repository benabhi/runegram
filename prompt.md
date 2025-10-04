
Los botones debajo de las salas que ayudan a ir en una dirección me dan este mensaje de error:

2], next run at: 2025-10-04 16:17:22 UTC)" (scheduled at 2025-10-04 16:17:20.998263+00:00)
2025-10-04 16:17:21 [INFO] - apscheduler.executors.default: Job "_execute_global_pulse (trigger: interval[0:00:02], next run at: 2025-10-04 16:17:22 UTC)" executed successfully
2025-10-04 16:17:21 [INFO] - root: Callback recibido - Action: move, Params: {'direction': 'norte'}, User: 1648877346
2025-10-04 16:17:21 [ERROR] - root: Error manejando callback para usuario 1648877346
Traceback (most recent call last):
  File "/app/src/handlers/callbacks.py", line 238, in callback_query_router
    await handler_func(callback, params, session)
  File "/app/src/handlers/callbacks.py", line 126, in handle_movement
    if exit_found.lock_string:
       ^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'Exit' object has no attribute 'lock_string'
2025-10-04 16:17:23 [INFO] - apscheduler.executors.default: Running job "_execute_global_pulse (trigger: interval[0:00:02], next run at: 2025-10-04 16:17:24 UTC)" (scheduled at 2025-10-04 16:17:22.998263+00:00)