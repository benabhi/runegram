# Análisis del Problema Real

## 🔍 Problema Identificado

En los logs:
```
Callback recibido - Action: move, User: 1664199017   ← Usuario real
Creando nueva cuenta para telegram_id: 7647451243   ← ID del BOT
```

**Causa**: En un CallbackQuery, `callback.message.from_user.id` es el ID del BOT (porque el mensaje fue enviado por el bot), NO del usuario.

## ✅ Solución

Modificar `show_current_room()` para aceptar un parámetro opcional `character`.

Si se pasa character, usarlo directamente. Si no, buscarlo (para backwards compatibility con comandos normales).

### Cambios:

1. `show_current_room(message, ..., character: Character = None)`
2. En `handle_movement`, pasar el character que ya tenemos:
   ```python
   await show_current_room(callback.message, edit=True, session=session, character=character)
   ```

Esto evita buscar el character de nuevo usando el telegram_id incorrecto.
