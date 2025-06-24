# backend/app/__init__.py
"""
Inicializaciones
"""

# Configurar logging al importar el paquete
from app.logging.logging_system import setup_logging
setup_logging()
from loguru import logger

# Exportar settings para acceso fácil
from app.config.settings import settings
__all__ = ["settings"]

logger.bind(action="startup", entity="app", environment=settings.environment).info("Aplicación iniciada")