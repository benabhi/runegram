# tests/test_services/test_permission_service.py
"""
Tests para el Sistema de Permisos y Locks.

Estos tests son CRÍTICOS ya que el sistema de permisos controla el acceso
a todas las funcionalidades del juego. Un error aquí podría permitir que
jugadores accedan a comandos de admin o viceversa.
"""

import pytest
from src.services import permission_service
from src.models import Account, Character, Item


@pytest.mark.critical
@pytest.mark.asyncio
class TestRoleLock:
    """Tests para la función de lock rol()."""

    async def test_superadmin_can_access_admin_commands(self, db_session):
        """
        Test: SUPERADMIN debería poder ejecutar comandos que requieren rol(ADMIN).
        """
        account = Account(telegram_id=12345, role="SUPERADMIN")
        db_session.add(account)
        await db_session.commit()

        character = Character(name="SuperUser", account_id=account.id, account=account)

        can_pass, _ = await permission_service.can_execute(character, "rol(ADMIN)")
        assert can_pass, "SUPERADMIN debería poder pasar un lock rol(ADMIN)"

    async def test_admin_can_access_admin_commands(self, db_session):
        """
        Test: ADMIN debería poder ejecutar comandos que requieren rol(ADMIN).
        """
        account = Account(telegram_id=12345, role="ADMIN")
        db_session.add(account)
        await db_session.commit()

        character = Character(name="AdminUser", account_id=account.id, account=account)

        can_pass, _ = await permission_service.can_execute(character, "rol(ADMIN)")
        assert can_pass, "ADMIN debería poder pasar un lock rol(ADMIN)"

    async def test_player_cannot_access_admin_commands(self, db_session):
        """
        Test: JUGADOR NO debería poder ejecutar comandos que requieren rol(ADMIN).
        """
        account = Account(telegram_id=12345, role="JUGADOR")
        db_session.add(account)
        await db_session.commit()

        character = Character(name="PlayerUser", account_id=account.id, account=account)

        can_pass, error_msg = await permission_service.can_execute(character, "rol(ADMIN)")
        assert not can_pass, "JUGADOR NO debería poder pasar un lock rol(ADMIN)"
        assert error_msg != "", "Debería haber un mensaje de error"

    async def test_admin_cannot_access_superadmin_commands(self, db_session):
        """
        Test: ADMIN NO debería poder ejecutar comandos que requieren rol(SUPERADMIN).
        """
        account = Account(telegram_id=12345, role="ADMIN")
        db_session.add(account)
        await db_session.commit()

        character = Character(name="AdminUser", account_id=account.id, account=account)

        can_pass, _ = await permission_service.can_execute(character, "rol(SUPERADMIN)")
        assert not can_pass, "ADMIN NO debería poder pasar un lock rol(SUPERADMIN)"


@pytest.mark.critical
@pytest.mark.asyncio
class TestTieneObjetoLock:
    """Tests para la función de lock tiene_objeto()."""

    async def test_character_with_item_passes(self, db_session, sample_room):
        """
        Test: Personaje que tiene el item requerido debería pasar el lock.
        """
        account = Account(telegram_id=12345, role="JUGADOR")
        db_session.add(account)
        await db_session.commit()

        character = Character(
            name="TestChar",
            account_id=account.id,
            account=account,
            room_id=sample_room.id
        )
        db_session.add(character)
        await db_session.commit()

        # Darle al personaje un item con key "llave_oro"
        item = Item(key="llave_oro", character_id=character.id)
        db_session.add(item)
        await db_session.commit()

        # Refrescar para cargar la relación items
        await db_session.refresh(character, ["items"])

        can_pass, _ = await permission_service.can_execute(character, "tiene_objeto(llave_oro)")
        assert can_pass, "Personaje con el item debería pasar el lock"

    async def test_character_without_item_fails(self, db_session, sample_room):
        """
        Test: Personaje que NO tiene el item requerido NO debería pasar el lock.
        """
        account = Account(telegram_id=12345, role="JUGADOR")
        db_session.add(account)
        await db_session.commit()

        character = Character(
            name="TestChar",
            account_id=account.id,
            account=account,
            room_id=sample_room.id
        )
        db_session.add(character)
        await db_session.commit()

        # NO darle ningún item

        can_pass, _ = await permission_service.can_execute(character, "tiene_objeto(llave_oro)")
        assert not can_pass, "Personaje sin el item NO debería pasar el lock"

    async def test_character_with_wrong_item_fails(self, db_session, sample_room):
        """
        Test: Personaje que tiene un item diferente NO debería pasar el lock.
        """
        account = Account(telegram_id=12345, role="JUGADOR")
        db_session.add(account)
        await db_session.commit()

        character = Character(
            name="TestChar",
            account_id=account.id,
            account=account,
            room_id=sample_room.id
        )
        db_session.add(character)
        await db_session.commit()

        # Darle un item con key diferente
        item = Item(key="espada_hierro", character_id=character.id)
        db_session.add(item)
        await db_session.commit()

        await db_session.refresh(character, ["items"])

        can_pass, _ = await permission_service.can_execute(character, "tiene_objeto(llave_oro)")
        assert not can_pass, "Personaje con item diferente NO debería pasar el lock"


@pytest.mark.critical
@pytest.mark.asyncio
class TestBooleanLogic:
    """Tests para operadores booleanos en lock strings."""

    async def test_and_operator(self, db_session, sample_room):
        """
        Test: Operador 'and' - ambas condiciones deben cumplirse.
        """
        account = Account(telegram_id=12345, role="ADMIN")
        db_session.add(account)
        await db_session.commit()

        character = Character(
            name="TestChar",
            account_id=account.id,
            account=account,
            room_id=sample_room.id
        )
        db_session.add(character)
        await db_session.commit()

        item = Item(key="llave_oro", character_id=character.id)
        db_session.add(item)
        await db_session.commit()

        await db_session.refresh(character, ["items"])

        # Test: ADMIN Y tiene llave_oro → Debería pasar
        can_pass, _ = await permission_service.can_execute(
            character,
            "rol(ADMIN) and tiene_objeto(llave_oro)"
        )
        assert can_pass, "Ambas condiciones se cumplen, debería pasar"

        # Test: ADMIN Y tiene llave_plata (que no tiene) → NO debería pasar
        can_pass, _ = await permission_service.can_execute(
            character,
            "rol(ADMIN) and tiene_objeto(llave_plata)"
        )
        assert not can_pass, "Una condición falla, NO debería pasar"

    async def test_or_operator(self, db_session, sample_room):
        """
        Test: Operador 'or' - al menos una condición debe cumplirse.
        """
        account = Account(telegram_id=12345, role="JUGADOR")
        db_session.add(account)
        await db_session.commit()

        character = Character(
            name="TestChar",
            account_id=account.id,
            account=account,
            room_id=sample_room.id
        )
        db_session.add(character)
        await db_session.commit()

        item = Item(key="llave_oro", character_id=character.id)
        db_session.add(item)
        await db_session.commit()

        await db_session.refresh(character, ["items"])

        # Test: ADMIN O tiene llave_oro → Debería pasar (tiene la llave)
        can_pass, _ = await permission_service.can_execute(
            character,
            "rol(ADMIN) or tiene_objeto(llave_oro)"
        )
        assert can_pass, "Una condición se cumple (tiene llave), debería pasar"

        # Test: ADMIN O tiene llave_plata → NO debería pasar (ninguna se cumple)
        can_pass, _ = await permission_service.can_execute(
            character,
            "rol(ADMIN) or tiene_objeto(llave_plata)"
        )
        assert not can_pass, "Ninguna condición se cumple, NO debería pasar"

    async def test_not_operator(self, db_session, sample_room):
        """
        Test: Operador 'not' - invierte el resultado.
        """
        account = Account(telegram_id=12345, role="JUGADOR")
        db_session.add(account)
        await db_session.commit()

        character = Character(
            name="TestChar",
            account_id=account.id,
            account=account,
            room_id=sample_room.id
        )
        db_session.add(character)
        await db_session.commit()

        # Test: NOT ADMIN → Debería pasar (porque NO es admin)
        can_pass, _ = await permission_service.can_execute(character, "not rol(ADMIN)")
        assert can_pass, "NO es ADMIN, debería pasar"

        # Test: NOT JUGADOR → NO debería pasar (porque SÍ es jugador)
        can_pass, _ = await permission_service.can_execute(character, "not rol(JUGADOR)")
        assert not can_pass, "SÍ es JUGADOR, NO debería pasar"

    async def test_complex_expression(self, db_session, sample_room):
        """
        Test: Expresión compleja con múltiples operadores.
        """
        account = Account(telegram_id=12345, role="ADMIN")
        db_session.add(account)
        await db_session.commit()

        character = Character(
            name="TestChar",
            account_id=account.id,
            account=account,
            room_id=sample_room.id
        )
        db_session.add(character)
        await db_session.commit()

        item = Item(key="llave_oro", character_id=character.id)
        db_session.add(item)
        await db_session.commit()

        await db_session.refresh(character, ["items"])

        # (ADMIN or tiene llave_plata) and not SUPERADMIN
        # → (True or False) and not False
        # → True and True
        # → True
        can_pass, _ = await permission_service.can_execute(
            character,
            "(rol(ADMIN) or tiene_objeto(llave_plata)) and not rol(SUPERADMIN)"
        )
        assert can_pass, "La expresión compleja debería evaluarse correctamente a True"


@pytest.mark.asyncio
class TestEdgeCases:
    """Tests para casos edge y manejo de errores."""

    async def test_empty_lock_string_always_passes(self, sample_character):
        """
        Test: Un lock string vacío debería siempre pasar (sin restricciones).
        """
        can_pass, _ = await permission_service.can_execute(sample_character, "")
        assert can_pass, "Lock string vacío debería siempre permitir el acceso"

    async def test_none_lock_string_always_passes(self, sample_character):
        """
        Test: Un lock string None debería siempre pasar.
        """
        can_pass, _ = await permission_service.can_execute(sample_character, None)
        assert can_pass, "Lock string None debería siempre permitir el acceso"

    async def test_invalid_syntax_lock_string(self, sample_character):
        """
        Test: Un lock string con sintaxis inválida debería fallar gracefully.
        """
        can_pass, error_msg = await permission_service.can_execute(
            sample_character,
            "rol(ADMIN"  # ← Falta paréntesis de cierre
        )
        assert not can_pass, "Lock string inválido debería denegar el acceso"
        assert "Error" in error_msg, "Debería haber un mensaje de error"

    async def test_unknown_lock_function(self, sample_character):
        """
        Test: Una función de lock desconocida debería fallar gracefully.
        """
        can_pass, _ = await permission_service.can_execute(
            sample_character,
            "funcion_inexistente(argumento)"
        )
        assert not can_pass, "Función de lock desconocida debería denegar el acceso"

    async def test_dangerous_code_injection_prevented(self, sample_character):
        """
        Test: El sistema NO debe permitir ejecución de código arbitrario.
        """
        # Intentos de inyección de código que deberían fallar
        dangerous_locks = [
            "__import__('os').system('ls')",
            "eval('1+1')",
            "exec('print(1)')",
            "for i in range(10): pass",
            "x = 5",
        ]

        for dangerous_lock in dangerous_locks:
            can_pass, _ = await permission_service.can_execute(sample_character, dangerous_lock)
            assert not can_pass, f"Código peligroso debería ser rechazado: {dangerous_lock}"


@pytest.mark.asyncio
class TestRoleHierarchy:
    """Tests para verificar la jerarquía de roles."""

    async def test_role_hierarchy_levels(self, db_session, sample_room):
        """
        Test: Verificar que la jerarquía de roles está correctamente definida.
        """
        # JUGADOR < ADMIN < SUPERADMIN
        assert permission_service.ROLE_HIERARCHY["JUGADOR"] < permission_service.ROLE_HIERARCHY["ADMIN"]
        assert permission_service.ROLE_HIERARCHY["ADMIN"] < permission_service.ROLE_HIERARCHY["SUPERADMIN"]

    async def test_higher_role_can_access_lower_role_commands(self, db_session, sample_room):
        """
        Test: Un rol superior debería poder acceder a comandos de roles inferiores.
        """
        account = Account(telegram_id=12345, role="SUPERADMIN")
        db_session.add(account)
        await db_session.commit()

        character = Character(
            name="SuperUser",
            account_id=account.id,
            account=account,
            room_id=sample_room.id
        )

        # SUPERADMIN debería poder ejecutar comandos de JUGADOR y ADMIN
        can_pass_player, _ = await permission_service.can_execute(character, "rol(JUGADOR)")
        can_pass_admin, _ = await permission_service.can_execute(character, "rol(ADMIN)")

        assert can_pass_player, "SUPERADMIN debería poder pasar rol(JUGADOR)"
        assert can_pass_admin, "SUPERADMIN debería poder pasar rol(ADMIN)"


@pytest.mark.critical
@pytest.mark.asyncio
class TestContextualLocks:
    """Tests para el sistema de locks contextuales (v2.0)."""

    async def test_dict_locks_with_specific_access_type(self, db_session):
        """
        Test: Locks contextuales con access_type específico funcionan correctamente.
        """
        account = Account(telegram_id=12345, role="JUGADOR")
        db_session.add(account)
        await db_session.commit()

        character = Character(name="TestChar", account_id=account.id, account=account)

        locks = {
            "get": "rol(ADMIN)",
            "open": "",  # Sin restricción
            "put": "rol(ADMIN)"
        }

        # get: requiere ADMIN (character es JUGADOR) → Debería fallar
        can_get, _ = await permission_service.can_execute(character, locks, "get")
        assert not can_get, "JUGADOR no debería poder pasar lock 'get' que requiere ADMIN"

        # open: sin restricción → Debería pasar
        can_open, _ = await permission_service.can_execute(character, locks, "open")
        assert can_open, "Lock vacío debería siempre pasar"

        # put: requiere ADMIN → Debería fallar
        can_put, _ = await permission_service.can_execute(character, locks, "put")
        assert not can_put, "JUGADOR no debería poder pasar lock 'put' que requiere ADMIN"

    async def test_dict_locks_with_default_fallback(self, db_session):
        """
        Test: Si no existe access_type específico, usa 'default'.
        """
        account = Account(telegram_id=12345, role="JUGADOR")
        db_session.add(account)
        await db_session.commit()

        character = Character(name="TestChar", account_id=account.id, account=account)

        locks = {
            "default": "rol(ADMIN)",
            "open": ""
        }

        # get: no existe, usa default (requiere ADMIN) → Debería fallar
        can_get, _ = await permission_service.can_execute(character, locks, "get")
        assert not can_get, "Debería usar 'default' si no existe access_type específico"

        # open: existe específico (vacío = sin restricción) → Debería pasar
        can_open, _ = await permission_service.can_execute(character, locks, "open")
        assert can_open, "Lock vacío específico debería pasar"

    async def test_backward_compat_string_simple(self, db_session):
        """
        Test: String simple sigue funcionando (backward compatibility).
        """
        account = Account(telegram_id=12345, role="JUGADOR")
        db_session.add(account)
        await db_session.commit()

        character = Character(name="TestChar", account_id=account.id, account=account)

        lock_string = "rol(ADMIN)"

        # Sin especificar access_type (default)
        can_pass, _ = await permission_service.can_execute(character, lock_string)
        assert not can_pass, "String simple debería funcionar como antes"

        # Especificando access_type (debería usar el string como default)
        can_pass, _ = await permission_service.can_execute(character, lock_string, "get")
        assert not can_pass, "String simple con access_type debería funcionar"

    async def test_custom_lock_messages(self, db_session):
        """
        Test: Mensajes de error personalizados funcionan correctamente.
        """
        account = Account(telegram_id=12345, role="JUGADOR")
        db_session.add(account)
        await db_session.commit()

        character = Character(name="TestChar", account_id=account.id, account=account)

        locks = {"get": "rol(SUPERADMIN)"}
        lock_messages = {"get": "El cofre es demasiado pesado para levantarlo."}

        can_pass, error_message = await permission_service.can_execute(
            character,
            locks,
            "get",
            lock_messages
        )

        assert not can_pass, "JUGADOR no debería pasar lock SUPERADMIN"
        assert error_message == "El cofre es demasiado pesado para levantarlo.", \
            "Debería retornar mensaje personalizado"

    async def test_empty_dict_lock_always_passes(self, sample_character):
        """
        Test: Diccionario vacío debería siempre pasar.
        """
        can_pass, _ = await permission_service.can_execute(sample_character, {})
        assert can_pass, "Diccionario vacío debería siempre permitir el acceso"


@pytest.mark.asyncio
class TestNewLockFunctions:
    """Tests para las nuevas lock functions (v2.0)."""

    async def test_en_sala(self, db_session, sample_room):
        """
        Test: Lock function en_sala() funciona correctamente.
        """
        account = Account(telegram_id=12345, role="JUGADOR")
        db_session.add(account)
        await db_session.commit()

        # Configurar room.key
        sample_room.key = "plaza_central"
        db_session.add(sample_room)
        await db_session.commit()

        character = Character(
            name="TestChar",
            account_id=account.id,
            account=account,
            room_id=sample_room.id,
            room=sample_room
        )
        db_session.add(character)
        await db_session.commit()

        # Character está en plaza_central → Debería pasar
        can_pass, _ = await permission_service.can_execute(character, "en_sala(plaza_central)")
        assert can_pass, "Debería pasar si está en la sala correcta"

        # Character NO está en biblioteca → NO debería pasar
        can_pass, _ = await permission_service.can_execute(character, "en_sala(biblioteca)")
        assert not can_pass, "No debería pasar si NO está en la sala"

    async def test_cuenta_items(self, db_session, sample_room):
        """
        Test: Lock function cuenta_items() funciona correctamente.
        """
        account = Account(telegram_id=12345, role="JUGADOR")
        db_session.add(account)
        await db_session.commit()

        character = Character(
            name="TestChar",
            account_id=account.id,
            account=account,
            room_id=sample_room.id
        )
        db_session.add(character)
        await db_session.commit()

        # Agregar 3 items al character
        for i in range(3):
            item = Item(key=f"item_{i}", character_id=character.id)
            db_session.add(item)
        await db_session.commit()

        await db_session.refresh(character, ["items"])

        # Character tiene >= 2 items → Debería pasar
        can_pass, _ = await permission_service.can_execute(character, "cuenta_items(2)")
        assert can_pass, "Debería pasar si tiene suficientes items"

        # Character NO tiene >= 10 items → NO debería pasar
        can_pass, _ = await permission_service.can_execute(character, "cuenta_items(10)")
        assert not can_pass, "No debería pasar si no tiene suficientes items"

    async def test_tiene_item_categoria(self, db_session, sample_room):
        """
        Test: Lock function tiene_item_categoria() funciona correctamente.
        """
        account = Account(telegram_id=12345, role="JUGADOR")
        db_session.add(account)
        await db_session.commit()

        character = Character(
            name="TestChar",
            account_id=account.id,
            account=account,
            room_id=sample_room.id
        )
        db_session.add(character)
        await db_session.commit()

        # Agregar espada (categoría "arma")
        item = Item(key="espada_hierro", category="arma", character_id=character.id)
        db_session.add(item)
        await db_session.commit()

        await db_session.refresh(character, ["items"])

        # Character tiene item de categoría "arma" → Debería pasar
        can_pass, _ = await permission_service.can_execute(character, "tiene_item_categoria(arma)")
        assert can_pass, "Debería pasar si tiene item de la categoría"

        # Character NO tiene item de categoría "armadura" → NO debería pasar
        can_pass, _ = await permission_service.can_execute(character, "tiene_item_categoria(armadura)")
        assert not can_pass, "No debería pasar si no tiene item de la categoría"
