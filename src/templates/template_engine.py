# src/templates/template_engine.py
"""
Motor de Templates para Runegram.

Este módulo proporciona un sistema de plantillas basado en Jinja2 que permite
separar la lógica de presentación del código del juego. Los templates permiten
mantener formatos visuales consistentes y facilitan la personalización del output.

Principios de Diseño:
- Separación de responsabilidades: Lógica vs Presentación
- Consistencia visual: Todos los outputs siguen estándares visuales
- Extensibilidad: Los prototipos pueden definir templates personalizados
- Mantenibilidad: Cambios de formato centralizados
"""

import logging
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape, TemplateNotFound

from src.templates.icons import ICONS


# Directorio base donde están almacenados los templates
TEMPLATES_DIR = Path(__file__).parent / "base"


class TemplateEngine:
    """
    Motor de renderizado de templates para el juego.

    Utiliza Jinja2 para procesar templates HTML que se envían vía Telegram.
    Proporciona funciones helper y filtros personalizados para facilitar
    la creación de outputs consistentes.
    """

    def __init__(self):
        """Inicializa el motor de templates con configuración de Jinja2."""
        self.env = Environment(
            loader=FileSystemLoader(TEMPLATES_DIR),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=False,
            lstrip_blocks=False
        )

        # Registrar funciones helper globales
        self.env.globals['icon'] = self._get_icon
        self.env.globals['icons'] = ICONS

        # Registrar filtros personalizados
        self.env.filters['pluralize'] = self._pluralize
        self.env.filters['article'] = self._add_article

    def render(self, template_name: str, context: dict) -> str:
        """
        Renderiza un template con el contexto proporcionado.

        Args:
            template_name: Nombre del archivo template (ej: 'room.html.j2')
            context: Diccionario con variables para el template

        Returns:
            str: HTML renderizado listo para enviar a Telegram

        Raises:
            TemplateNotFound: Si el template no existe
        """
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except TemplateNotFound:
            logging.error(f"Template no encontrado: {template_name}")
            return f"<pre>❌ Error: Template '{template_name}' no encontrado.</pre>"
        except Exception as e:
            logging.exception(f"Error al renderizar template '{template_name}': {e}")
            return "<pre>❌ Error al generar el contenido.</pre>"

    def render_from_string(self, template_string: str, context: dict) -> str:
        """
        Renderiza un template desde un string en lugar de un archivo.

        Útil para templates personalizados definidos en prototipos.

        Args:
            template_string: String con sintaxis Jinja2
            context: Diccionario con variables para el template

        Returns:
            str: HTML renderizado
        """
        try:
            template = self.env.from_string(template_string)
            return template.render(**context)
        except Exception as e:
            logging.exception(f"Error al renderizar template desde string: {e}")
            return "<pre>❌ Error al generar el contenido.</pre>"

    def _get_icon(self, key: str, default: str = "") -> str:
        """
        Helper para obtener íconos por clave.

        Uso en template: {{ icon('room') }} → 📍
        """
        return ICONS.get(key, default)

    def _pluralize(self, count: int, singular: str, plural: str = None) -> str:
        """
        Filtro para pluralizar palabras basándose en cantidad.

        Uso: {{ items|length }} {{ items|length|pluralize('item', 'items') }}
        """
        if plural is None:
            plural = singular + "s"
        return singular if count == 1 else plural

    def _add_article(self, text: str) -> str:
        """
        Filtro para agregar artículo indefinido en español.

        Uso: {{ item.name|article }} → "una espada" o "un escudo"
        """
        # Regla simple: si empieza con vocal (a, e, i, o, u), usar "un"
        # Si no, usar "una" (esto es una simplificación)
        vowels = ['a', 'e', 'i', 'o', 'u']
        first_letter = text.lower()[0] if text else ''

        # En español, usamos "un" para masculino y "una" para femenino
        # Esta es una implementación básica; idealmente el género vendría del prototipo
        return f"un {text}" if first_letter in vowels else f"una {text}"


# Instancia global del motor de templates
template_engine = TemplateEngine()


def render_template(template_name: str, **context) -> str:
    """
    Función helper para renderizar templates de forma conveniente.

    Args:
        template_name: Nombre del template
        **context: Variables para pasar al template

    Returns:
        str: HTML renderizado

    Example:
        >>> render_template('room.html.j2', room=my_room, character=char)
        '<pre>📍 <b>Plaza Central</b>...</pre>'
    """
    return template_engine.render(template_name, context)


def render_from_string(template_string: str, **context) -> str:
    """
    Función helper para renderizar templates desde strings.

    Args:
        template_string: String con sintaxis Jinja2
        **context: Variables para pasar al template

    Returns:
        str: HTML renderizado
    """
    return template_engine.render_from_string(template_string, context)
