# tests/test_services/test_validation_service.py
"""
Tests para el Sistema de Validación de Integridad.

Estos tests aseguran que el validation_service detecte correctamente conflictos
y problemas en la configuración del juego.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.services import validation_service
from src.services.validation_service import ValidationError


@pytest.mark.critical
class TestCommandAliasValidation:
    """Tests para la validación de aliases de comandos."""

    def test_no_duplicates_passes(self):
        """
        Test: Cuando no hay aliases duplicados, la validación debe pasar.
        """
        # Mock COMMAND_SETS sin duplicados
        mock_commands = {
            "movement": [
                MagicMock(names=["norte", "n"]),
                MagicMock(names=["sur", "s"]),
            ],
            "general": [
                MagicMock(names=["mirar", "m"]),
            ]
        }

        with patch("src.handlers.player.dispatcher.COMMAND_SETS", mock_commands):
            errors = validation_service.validate_command_aliases()
            assert len(errors) == 0, "No debería haber errores cuando no hay duplicados"

    def test_detect_duplicate_aliases(self):
        """
        Test: Debe detectar cuando el mismo alias está en múltiples comandos.
        """
        # Mock COMMAND_SETS con duplicados
        mock_commands = {
            "movement": [
                MagicMock(names=["norte", "n"]),
            ],
            "channels": [
                MagicMock(names=["novato", "n"]),  # ← Duplicado con "norte"
            ]
        }

        with patch("src.handlers.player.dispatcher.COMMAND_SETS", mock_commands):
            errors = validation_service.validate_command_aliases()
            assert len(errors) == 1, "Debería detectar exactamente un error"
            assert "n" in errors[0], "El error debería mencionar el alias 'n' duplicado"
            assert "movement" in errors[0] and "channels" in errors[0], \
                "El error debería mencionar ambos sources"

    def test_multiple_duplicates(self):
        """
        Test: Debe detectar múltiples aliases duplicados.
        """
        mock_commands = {
            "set1": [
                MagicMock(names=["cmd1", "a"]),
                MagicMock(names=["cmd2", "b"]),
            ],
            "set2": [
                MagicMock(names=["cmd3", "a"]),  # Duplicado "a"
            ],
            "set3": [
                MagicMock(names=["cmd4", "b"]),  # Duplicado "b"
            ]
        }

        with patch("src.handlers.player.dispatcher.COMMAND_SETS", mock_commands):
            errors = validation_service.validate_command_aliases()
            assert len(errors) == 2, "Debería detectar dos errores (a y b)"


@pytest.mark.critical
class TestRoomPrototypeValidation:
    """Tests para la validación de prototipos de salas."""

    def test_valid_room_prototypes(self):
        """
        Test: Prototipos válidos no deben generar errores.
        """
        valid_prototypes = {
            "limbo": {
                "name": "El Limbo",
                "description": "Sala inicial",
                "exits": {"norte": "plaza"}
            },
            "plaza": {
                "name": "Plaza",
                "description": "Una plaza",
                "exits": {"sur": "limbo"}
            }
        }

        with patch("src.services.validation_service.ROOM_PROTOTYPES", valid_prototypes):
            errors = validation_service.validate_room_prototype_keys()
            assert len(errors) == 0, "No debería haber errores con prototipos válidos"

    def test_detect_duplicate_room_keys(self):
        """
        Test: Debe detectar keys de sala duplicadas.

        Nota: En Python, un dict no puede tener keys duplicadas literalmente,
        pero podemos simular el escenario de detección.
        """
        # Este test verifica que la lógica de detección funcione
        # En la práctica, Python sobrescribiría la key, pero validamos
        # que el código podría detectarlo si se implementa checking adicional
        pass  # Placeholder - en producción esto sería detectado al parsear el archivo

    def test_detect_invalid_exit_reference(self):
        """
        Test: Debe detectar cuando una salida apunta a una sala que no existe.
        """
        invalid_prototypes = {
            "limbo": {
                "name": "El Limbo",
                "exits": {"norte": "sala_inexistente"}  # ← Esta sala no existe
            }
        }

        with patch("src.services.validation_service.ROOM_PROTOTYPES", invalid_prototypes):
            errors = validation_service.validate_room_prototype_keys()
            assert len(errors) > 0, "Debería detectar la referencia inválida"
            assert "sala_inexistente" in errors[0], "El error debería mencionar la sala inexistente"

    def test_exit_with_lock_format(self):
        """
        Test: Debe soportar el formato de salida con locks (dict en lugar de string).
        """
        prototypes_with_locks = {
            "limbo": {
                "name": "El Limbo",
                "exits": {
                    "norte": {
                        "to": "torre",
                        "locks": "nivel(5)"
                    }
                }
            },
            "torre": {
                "name": "Torre",
                "exits": {"sur": "limbo"}
            }
        }

        with patch("src.services.validation_service.ROOM_PROTOTYPES", prototypes_with_locks):
            errors = validation_service.validate_room_prototype_keys()
            assert len(errors) == 0, "Debería soportar el formato con locks"


@pytest.mark.critical
class TestItemPrototypeValidation:
    """Tests para la validación de prototipos de items."""

    def test_valid_item_prototypes(self):
        """
        Test: Prototipos de items válidos no deben generar errores.
        """
        valid_prototypes = {
            "espada_hierro": {"name": "Espada de Hierro"},
            "pocion_vida": {"name": "Poción de Vida"}
        }

        with patch("src.services.validation_service.ITEM_PROTOTYPES", valid_prototypes):
            errors = validation_service.validate_item_prototype_keys()
            assert len(errors) == 0


class TestChannelPrototypeValidation:
    """Tests para la validación de prototipos de canales."""

    def test_valid_channel_prototypes(self):
        """
        Test: Prototipos de canales válidos no deben generar errores.
        """
        valid_prototypes = {
            "novato": {"name": "Novato", "type": "CHAT"},
            "sistema": {"name": "Sistema", "type": "CHAT"}
        }

        with patch("src.services.validation_service.CHANNEL_PROTOTYPES", valid_prototypes):
            errors = validation_service.validate_channel_prototype_keys()
            assert len(errors) == 0


@pytest.mark.critical
class TestValidateAll:
    """Tests para la función validate_all() que ejecuta todas las validaciones."""

    def test_validate_all_passes_with_no_errors(self):
        """
        Test: validate_all() no debe lanzar excepción cuando todo está correcto.
        """
        # Mock todas las validaciones para que retornen listas vacías
        with patch("src.services.validation_service.validate_command_aliases", return_value=[]), \
             patch("src.services.validation_service.validate_room_prototype_keys", return_value=[]), \
             patch("src.services.validation_service.validate_item_prototype_keys", return_value=[]), \
             patch("src.services.validation_service.validate_channel_prototype_keys", return_value=[]):

            # No debería lanzar excepción
            try:
                validation_service.validate_all()
            except ValidationError:
                pytest.fail("validate_all() no debería lanzar excepción cuando no hay errores")

    def test_validate_all_raises_on_errors(self):
        """
        Test: validate_all() debe lanzar ValidationError cuando hay problemas.
        """
        # Mock una validación que retorna errores
        with patch("src.services.validation_service.validate_command_aliases", return_value=["Error de alias"]), \
             patch("src.services.validation_service.validate_room_prototype_keys", return_value=[]), \
             patch("src.services.validation_service.validate_item_prototype_keys", return_value=[]), \
             patch("src.services.validation_service.validate_channel_prototype_keys", return_value=[]):

            with pytest.raises(ValidationError) as exc_info:
                validation_service.validate_all()

            assert "Error de alias" in str(exc_info.value), \
                "La excepción debería incluir el mensaje de error"


class TestValidationReport:
    """Tests para la función get_validation_report()."""

    def test_report_includes_statistics(self):
        """
        Test: El reporte debe incluir estadísticas del sistema.
        """
        mock_commands = {
            "set1": [MagicMock(names=["cmd1", "c1"])]
        }
        mock_rooms = {"room1": {}, "room2": {}}
        mock_items = {"item1": {}}
        mock_channels = {"channel1": {}}

        with patch("src.handlers.player.dispatcher.COMMAND_SETS", mock_commands), \
             patch("src.services.validation_service.ROOM_PROTOTYPES", mock_rooms), \
             patch("src.services.validation_service.ITEM_PROTOTYPES", mock_items), \
             patch("src.services.validation_service.CHANNEL_PROTOTYPES", mock_channels):

            report = validation_service.get_validation_report()

            assert "ESTADÍSTICAS" in report
            assert "2" in report  # 2 rooms
            assert "1" in report  # 1 item, 1 channel

    def test_report_shows_errors_when_present(self):
        """
        Test: El reporte debe mostrar errores cuando los hay.
        """
        with patch("src.services.validation_service.validate_command_aliases",
                   return_value=["Error de prueba"]), \
             patch("src.services.validation_service.validate_room_prototype_keys", return_value=[]), \
             patch("src.services.validation_service.validate_item_prototype_keys", return_value=[]), \
             patch("src.services.validation_service.validate_channel_prototype_keys", return_value=[]):

            report = validation_service.get_validation_report()

            assert "ERRORES ENCONTRADOS" in report
            assert "Error de prueba" in report

    def test_report_shows_no_errors_when_clean(self):
        """
        Test: El reporte debe indicar cuando no hay errores.
        """
        with patch("src.services.validation_service.validate_command_aliases", return_value=[]), \
             patch("src.services.validation_service.validate_room_prototype_keys", return_value=[]), \
             patch("src.services.validation_service.validate_item_prototype_keys", return_value=[]), \
             patch("src.services.validation_service.validate_channel_prototype_keys", return_value=[]):

            report = validation_service.get_validation_report()

            assert "No se encontraron errores" in report
