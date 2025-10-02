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
