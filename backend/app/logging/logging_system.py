# backend/app/logging/logging_system.py

"""
Sistema de logging personalizado con almacenamiento en SQLite.

Proporciona una implementación de logging usando Loguru con persistencia
en base de datos SQLite para análisis y auditoría de logs.

Setup:
    from app.logging.logging_system import setup_logging
    from loguru import logger
    setup_logging()

Uso básico:
    from loguru import logger
    logger.info("Mensaje informativo")
    logger.error("Error crítico")

Uso con contexto:
    logger.bind(action="create", entity="user", id=123).info("Usuario creado")
"""

import sqlite3
import json
from loguru import logger
from app.config.settings import settings

# Guard global para evitar configuración múltiple
_logging_configured = False

class SQLiteHandler:
    """Handler personalizado para almacenar logs en SQLite."""
    def __init__(self, db_path: str = settings.log_db_absolute_path):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Crea la tabla de logs si no existe."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    level TEXT,
                    message TEXT,
                    module TEXT,
                    function TEXT,
                    line INTEGER,
                    extra_json TEXT,
                    exception TEXT
                )
            """)
    
    def write(self, message):
        """Procesa y almacena un registro de log en SQLite."""
        record = message.record
        
        # Serializar extra si existe
        extra_json = json.dumps(record["extra"]) if record["extra"] else None
        
        # Serializar excepción si existe
        exception_text = None
        if record["exception"]:
            exc = record["exception"]
            exception_text = f"{exc.type.__name__}: {exc.value}\n{''.join(exc.traceback)}"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO logs (timestamp, level, message, module, function, line, extra_json, exception)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record["time"].isoformat(),
                record["level"].name,
                record["message"],
                record["module"],
                record["function"],
                record["line"],
                extra_json,
                exception_text
            ))

# Configuración inicial (inicializada en app/__init__.py)
def setup_logging():
    """
    Configura el sistema de logging con SQLite.
    Remueve el handler por defecto de Loguru y configura almacenamiento
    en SQLite. Opcionalmente mantiene salida a consola para desarrollo.
    """

    global _logging_configured
    
    # Evitar reconfiguración en reloads
    if _logging_configured:
        return logger
    
    _logging_configured = True

    # Remover handler por defecto para usar solo SQLite
    logger.remove()
    
    # Configurar handler de SQLite
    db_handler = SQLiteHandler()
    logger.add(db_handler.write, format="{message}")
    
    # Opcional: mantener salida a consola para desarrollo
    # logger.add(sys.stderr, level="INFO")

    logger.bind(action="config", entity='logger', success='true').debug("Logger configurado")
    
    return logger