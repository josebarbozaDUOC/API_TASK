# backend/app/database/base.py

"""
Base de datos con SQLAlchemy.

Configuración central para SQLAlchemy ORM. Define la clase base
para modelos y funciones helper para crear engines y sesiones.

Referencias:
- https://docs.sqlalchemy.org/en/20/orm/quickstart.html
- https://docs.sqlalchemy.org/en/20/tutorial/engine.html
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Base declarativa: todos los modelos ORM heredan de aquí
Base = declarative_base()

def get_engine(database_url: str):
    """Crea engine de conexión a BD."""
    return create_engine(database_url)

def get_session_factory(engine):
    """Crea factory para generar sesiones de BD."""
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)