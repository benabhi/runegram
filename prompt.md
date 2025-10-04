sigo teniendo errores en los botones inline de direccion que estan debajo de bloque de descripcion de sala cuando hago /mirar

2025-10-04 20:02:41 [INFO] - root: Actualizados 38 comandos de Telegram para Benabhi.
2025-10-04 20:02:42 [INFO] - root: Actualizados 38 comandos de Telegram para Benabhi.
2025-10-04 20:02:43 [INFO] - apscheduler.executors.default: Running job "_execute_global_pulse (trigger: interval[0:00:02], next run at: 2025-10-04 20:02:45 UTC)" (scheduled at 2025-10-04 20:02:43.885614+00:00)
2025-10-04 20:02:43 [INFO] - apscheduler.executors.default: Job "_execute_global_pulse (trigger: interval[0:00:02], next run at: 2025-10-04 20:02:45 UTC)" executed successfully
2025-10-04 20:02:45 [INFO] - apscheduler.executors.default: Running job "_execute_global_pulse (trigger: interval[0:00:02], next run at: 2025-10-04 20:02:47 UTC)" (scheduled at 2025-10-04 20:02:45.885614+00:00)
2025-10-04 20:02:45 [INFO] - apscheduler.executors.default: Job "_execute_global_pulse (trigger: interval[0:00:02], next run at: 2025-10-04 20:02:47 UTC)" executed successfully
2025-10-04 20:02:47 [INFO] - root: Callback recibido - Action: move, Params: {'direction': 'norte'}, User: 1664199017
2025-10-04 20:02:47 [ERROR] - root: Error manejando callback para usuario 1664199017
Traceback (most recent call last):
  File "/app/src/handlers/callbacks.py", line 238, in callback_query_router
    await handler_func(callback, params, session)
  File "/app/src/handlers/callbacks.py", line 145, in handle_movement
    await broadcaster_service.send_message_to_room(
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: send_message_to_room() got an unexpected keyword argument 'room'
2025-10-04 20:02:47 [INFO] - apscheduler.executors.default: Running job "_execute_global_pulse (trigger: interval[0:00:02], next run at: 2025-10-04 20:02:49 UTC)" (scheduled at 2025-10-04 20:02:47.885614+00:00)
2025-10-04 20:02:47 [INFO] - apscheduler.executors.default: Job "_execute_global_pulse (trigger: interval[0:00:02], next run at: 2025-10-04 20:02:49 UTC)" executed successfully
2025-10-04 20:02:49 [INFO] - apscheduler.executors.default: Running job "_execute_global_pulse (trigger: interval[0:00:02], next run at: 2025-10-04 20:02:51 UTC)" (scheduled at 2025-10-04 20:02:49.885614+00:00)
2025-10-04 20:02:49 [INFO] - apscheduler.executors.default: Job "_execute_global_pulse (trigger: interval[0:00:02], next run at: 2025-10-04 20:02:51 UTC)" executed successfully
2025-10-04 20:02:51 [INFO] - root: Callback recibido - Action: move, Params: {'direction': 'norte'}, User: 1648877346
2025-10-04 20:02:51 [ERROR] - root: Error manejando callback para usuario 1648877346
Traceback (most recent call last):
  File "/app/src/handlers/callbacks.py", line 238, in callback_query_router
    await handler_func(callback, params, session)
  File "/app/src/handlers/callbacks.py", line 145, in handle_movement
    await broadcaster_service.send_message_to_room(
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: send_message_to_room() got an unexpected keyword argument 'room'
2025-10-04 20:02:51 [INFO] - apscheduler.executors.default: Running job "_execute_global_pulse (trigger: interval[0:00:02], next run at: 2025-10-04 20:02:53 UTC)" (scheduled at 2025-10-04 20:02:51.885614+00:00)
2025-10-04 20:02:51 [INFO] - apscheduler.executors.default: Job "_execute_global_pulse (trigger: interval[0:00:02], next run at: 2025-10-04 20:02:53 UTC)" executed successfully
2025-10-04 20:02:53 [INFO] - apscheduler.executors.default: Running job "_execute_global_pulse (trigger: interval[0:00:02], next run at: 2025-10-04 20:02:55 UTC)" (scheduled at 2025-10-04 20:02:53.885614+00:00)
2025-10-04 20:02:53 [INFO] - apscheduler.executors.default: Job "_execute_global_pulse (trigger: interval[0:00:02], next run at: 2025-10-04 20:02:55 UTC)" executed successfully