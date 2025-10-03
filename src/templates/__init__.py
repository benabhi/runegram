# src/templates/__init__.py
"""
Sistema de Templates para Runegram.

Este módulo proporciona un motor de plantillas basado en Jinja2 que permite
separar la lógica de presentación del código del juego.

Exports principales:
    - render_template: Función para renderizar templates desde archivos
    - render_from_string: Función para renderizar templates desde strings
    - ICONS: Diccionario con todos los íconos del juego
    - template_engine: Instancia del motor de templates
"""

from src.templates.template_engine import (
    template_engine,
    render_template,
    render_from_string
)
from src.templates.icons import ICONS, get_direction_icon, get_item_icon

__all__ = [
    'template_engine',
    'render_template',
    'render_from_string',
    'ICONS',
    'get_direction_icon',
    'get_item_icon',
]
