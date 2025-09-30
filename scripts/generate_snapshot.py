# scripts/generate_snapshot.py

import os
from pathlib import Path

# --- CONFIGURACIÓN ---

# Directorio raíz del proyecto (sube dos niveles desde este script)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Nombre del archivo de salida
OUTPUT_FILENAME = "project_snapshot.txt"

# --- LISTA NEGRA: Directorios y archivos a IGNORAR SIEMPRE ---
# Usamos sets para una búsqueda más eficiente.
EXCLUDED_DIRS = {
    ".git",
    ".idea",
    ".vscode",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    "postgres_data",
    "node_modules",
}

EXCLUDED_FILES = {
    ".env",
    OUTPUT_FILENAME,
    "poetry.lock",
    "Pipfile.lock",
}

# Extensiones de archivo a ignorar (ej: binarios, compilados)
EXCLUDED_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".pyd",
    ".so",
    ".egg-info",
    ".swp",
    ".db",
    ".sqlite3",
}

# --- FIN DE LA CONFIGURACIÓN ---


def write_file_content(output_file, file_path):
    """Escribe el contenido de un archivo en el archivo de salida, con un encabezado."""
    # Obtenemos la ruta relativa usando el estándar POSIX (barras /)
    relative_path = file_path.relative_to(PROJECT_ROOT).as_posix()
    print(f"  -> Añadiendo: {relative_path}")

    header = f"# === INICIO: {relative_path} ===\n"
    footer = f"# === FIN: {relative_path} ===\n\n\n"

    output_file.write(header)
    try:
        # Leemos el contenido del archivo
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            # Añadimos un salto de línea al final si no lo tiene, para un formato limpio
            if content and not content.endswith('\n'):
                content += '\n'
            output_file.write(content)
    except Exception as e:
        output_file.write(f"*** No se pudo leer el archivo: {e} ***\n")
    output_file.write(footer)


def main():
    """Función principal para generar el snapshot del proyecto."""
    output_path = PROJECT_ROOT / OUTPUT_FILENAME
    print(f"Generando snapshot del proyecto en: {output_path}\n")

    # Usaremos una lista para almacenar las rutas de los archivos a incluir
    files_to_process = []

    # os.walk recorre todos los directorios y archivos desde la raíz del proyecto
    for root, dirs, files in os.walk(PROJECT_ROOT, topdown=True):
        # Modificamos la lista de directorios 'in-place' para evitar que os.walk entre en ellos
        dirs[:] = [d for d in sorted(dirs) if d not in EXCLUDED_DIRS]

        # Procesamos los archivos del directorio actual
        for filename in sorted(files):
            # Comprobamos si el archivo o su extensión están en la lista negra
            if filename in EXCLUDED_FILES:
                continue

            file_path = Path(root) / filename
            if file_path.suffix in EXCLUDED_EXTENSIONS:
                continue

            # Si el archivo pasa todos los filtros, lo añadimos a la lista
            files_to_process.append(file_path)

    # Escribimos todos los archivos encontrados en el archivo de salida
    with open(output_path, 'w', encoding='utf-8') as output_file:
        for file_path in files_to_process:
            write_file_content(output_file, file_path)

    print(f"\n¡Snapshot generado con éxito! {len(files_to_process)} archivos procesados.")


if __name__ == "__main__":
    main()