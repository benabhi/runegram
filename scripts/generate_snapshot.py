# scripts/generate_snapshot.py

import os
from pathlib import Path

# --- CONFIGURACIÓN ---

# Directorio raíz del proyecto (sube dos niveles desde scripts/generate_snapshot.py)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Nombre del archivo de salida que se creará en la raíz del proyecto
OUTPUT_FILENAME = "project_snapshot.txt"

# Lista de directorios a incluir de forma recursiva
DIRECTORIES_TO_INCLUDE = [
    "src",
    "alembic",
    "scripts"
]

# Lista de archivos específicos en la raíz del proyecto a incluir
FILES_TO_INCLUDE = [
    ".gitignore",
    "alembic.ini",
    "docker-compose.yml",
    "Dockerfile",
    "requirements.txt",
    "run.py",
    "README.md"
]

# Lista de directorios y archivos a excluir siempre
EXCLUSIONS = {
    "__pycache__",
    ".venv",
    "venv",
    ".git",
    "postgres_data",
    # El propio archivo de salida no debe ser incluido
    OUTPUT_FILENAME,
    # El archivo .env contiene secretos, es mejor no incluirlo
    ".env"
}

# --- FIN DE LA CONFIGURACIÓN ---

def write_file_content(output_file, file_path):
    """Escribe el contenido de un archivo en el archivo de salida, con un encabezado."""
    relative_path = file_path.relative_to(PROJECT_ROOT).as_posix()

    # No incluir el propio script de snapshot en la salida
    if "generate_snapshot.py" in str(relative_path):
        return

    print(f"  -> Añadiendo: {relative_path}")

    header = f"# === INICIO: {relative_path} ===\n"
    footer = f"# === FIN: {relative_path} ===\n\n\n"

    output_file.write(header)
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            output_file.write(content)
    except Exception as e:
        output_file.write(f"*** No se pudo leer el archivo: {e} ***\n")
    output_file.write(f"\n{footer}")


def main():
    """Función principal para generar el snapshot del proyecto."""
    output_path = PROJECT_ROOT / OUTPUT_FILENAME
    print(f"Generando snapshot del proyecto en: {output_path}")

    with open(output_path, 'w', encoding='utf-8') as output_file:
        # 1. Añadir los archivos individuales de la raíz
        output_file.write("# === Archivos Raíz ===\n\n")
        for filename in FILES_TO_INCLUDE:
            file_path = PROJECT_ROOT / filename
            if file_path.is_file():
                write_file_content(output_file, file_path)

        # 2. Añadir los directorios de forma recursiva
        for dir_name in DIRECTORIES_TO_INCLUDE:
            directory_path = PROJECT_ROOT / dir_name
            if not directory_path.is_dir():
                continue

            output_file.write(f"\n# === Contenido del Directorio: {dir_name} ===\n\n")

            for root, dirs, files in os.walk(directory_path, topdown=True):
                # Excluir directorios no deseados
                dirs[:] = [d for d in dirs if d not in EXCLUSIONS]

                # Ordenar archivos y directorios para una salida consistente
                dirs.sort()
                files.sort()

                for file in files:
                    if file not in EXCLUSIONS:
                        file_path = Path(root) / file
                        write_file_content(output_file, file_path)

    print("\n¡Snapshot generado con éxito!")


if __name__ == "__main__":
    main()