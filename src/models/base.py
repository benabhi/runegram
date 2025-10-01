# src/models/base.py
"""
Módulo que define la Base Declarativa para todos los Modelos de SQLAlchemy.

Este archivo contiene un único pero crucial objeto: `Base`.

SQLAlchemy utiliza un sistema "declarativo" donde las clases de Python se mapean
directamente a tablas de la base de datos. Para que esto funcione, todas las
clases de modelo (como `Account`, `Character`, `Room`, etc.) deben heredar de
una clase base común.

Esta clase `Base` actúa como un registro central que recopila metadatos sobre
todas las clases de modelo que heredan de ella. Herramientas como Alembic
utilizan estos metadatos para comparar los modelos con el estado de la base
de datos y generar así las migraciones automáticamente.
"""

from sqlalchemy.orm import declarative_base

# `declarative_base()` es una función de fábrica que construye la clase base.
# Todos nuestros modelos de datos en el proyecto heredarán de este objeto `Base`.
Base = declarative_base()