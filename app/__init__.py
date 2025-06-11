# app/__init__.py

"""
Inicializaciones
"""

# Configurar logging al importar el paquete
from app.logging.logging_system import setup_logging
setup_logging()

from loguru import logger
logger.info("Aplicación iniciada")