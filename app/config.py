# app/config.py

"""
Configuración de APP.

- Inicializa el tipo de repositorio para el servicio.
"""

from app.services.task_service import TaskService
from app.repositories.memory_repository import MemoryTaskRepository

# REFACTOR POSIBLE PARA SELECCIONAR REPOSITORIO

# Crear el repository deseado
repository = MemoryTaskRepository()

# Inyectar el repository en el servicio
task_service = TaskService(repository)