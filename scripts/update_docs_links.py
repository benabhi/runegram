"""
Script para actualizar masivamente enlaces en documentación después del renombrado a español.
"""

import os
import re
from pathlib import Path

# Directorio base de documentación
DOCS_DIR = Path(__file__).parent.parent / "docs"

# Mapeo de reemplazos (patrón antiguo -> patrón nuevo)
REPLACEMENTS = {
    # Directorios
    r'getting-started/': 'primeros-pasos/',
    r'architecture/': 'arquitectura/',
    r'engine-systems/': 'sistemas-del-motor/',
    r'content-creation/': 'creacion-de-contenido/',
    r'admin-guide/': 'guia-de-administracion/',
    r'roadmap/': 'hoja-de-ruta/',
    r'reference/': 'referencia/',

    # Archivos en primeros-pasos/
    r'installation\.md': 'instalacion.md',
    r'core-philosophy\.md': 'filosofia-central.md',

    # Archivos en arquitectura/
    r'configuration\.md': 'configuracion.md',

    # Archivos en sistemas-del-motor/
    r'online-presence\.md': 'presencia-en-linea.md',
    r'command-system\.md': 'sistema-de-comandos.md',
    r'permission-system\.md': 'sistema-de-permisos.md',
    r'prototype-system\.md': 'sistema-de-prototipos.md',
    r'scripting-system\.md': 'sistema-de-scripts.md',
    r'social-systems\.md': 'sistemas-sociales.md',
    r'channels-system\.md': 'sistema-de-canales.md',
    r'validation-system\.md': 'sistema-de-validacion.md',
    r'pulse-system\.md': 'sistema-de-pulso.md',
    r'categories-and-tags\.md': 'categorias-y-etiquetas.md',
    r'item-disambiguation\.md': 'desambiguacion-de-items.md',
    r'narrative-system\.md': 'sistema-de-narrativa.md',
    r'inline-buttons\.md': 'botones-en-linea.md',

    # Archivos en creacion-de-contenido/
    r'building-rooms\.md': 'construccion-de-salas.md',
    r'creating-commands\.md': 'creacion-de-comandos.md',
    r'output-style-guide\.md': 'guia-de-estilo-de-salida.md',
    r'creating-items\.md': 'creacion-de-items.md',
    r'writing-scripts\.md': 'escritura-de-scripts.md',

    # Archivos en guia-de-administracion/
    r'admin-commands\.md': 'comandos-de-administracion.md',
    r'database-migrations\.md': 'migraciones-de-base-de-datos.md',

    # Archivos en hoja-de-ruta/
    r'vision-and-goals\.md': 'vision-y-objetivos.md',
    r'planned-features\.md': 'funcionalidades-planificadas.md',
    r'combat-system-design\.md': 'diseno-sistema-de-combate.md',
    r'skill-system-design\.md': 'diseno-sistema-de-habilidades.md',

    # Archivos en referencia/
    r'command-reference\.md': 'referencia-de-comandos.md',
}

def update_file(filepath):
    """Actualiza enlaces en un archivo."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Aplicar todos los reemplazos
    for pattern, replacement in REPLACEMENTS.items():
        content = re.sub(pattern, replacement, content)

    # Solo escribir si hubo cambios
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    """Procesa todos los archivos .md en docs/"""
    updated_count = 0

    for md_file in DOCS_DIR.rglob("*.md"):
        if update_file(md_file):
            updated_count += 1
            print(f"[OK] Actualizado: {md_file.relative_to(DOCS_DIR)}")

    print(f"\nProceso completado. {updated_count} archivos actualizados.")

if __name__ == "__main__":
    main()
