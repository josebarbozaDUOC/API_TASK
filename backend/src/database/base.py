# backend/src/database/base.py

"""
Base de datos con SQLAlchemy.

Configuración central para SQLAlchemy ORM. 
Define la clase Base para todos los modelos ORM y funciones
helper para crear engines y sesiones.

Referencias:
- https://docs.sqlalchemy.org/en/20/orm/quickstart.html
- https://docs.sqlalchemy.org/en/20/tutorial/engine.html
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import StaticPool

# Clase base para todos los modelos
class Base(DeclarativeBase):
    pass

def get_engine(database_url: str):
    """
    Crea un engine de SQLAlchemy con configuración apropiada.
    Para SQLite usa StaticPool para evitar problemas de threading.
    """
    if database_url.startswith("sqlite"):
        # Configuración especial para SQLite
        return create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        # PostgreSQL u otras BD
        return create_engine(database_url)

def get_session_factory(engine):
    """Crea una factory de sesiones para el engine dado."""
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)