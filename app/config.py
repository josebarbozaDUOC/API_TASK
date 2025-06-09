# app/config.py

"""
Configuración de APP.

- Inicializa el tipo de repositorio para el servicio.

Al agregar nuevos repositorios al proyecto:
- Se debe agregar a este import
- Se debe agregar a este mapeo RepoType
- Si se desea cambiar el repositorio: ACTIVE_REPOSITORY
"""

from enum import Enum
from app.services.task_service import TaskService
from app.repositories.task.memory_repository import MemoryTaskRepository
from app.repositories.task.sqlite_repository import SqliteTaskRepository
from loguru import logger

# Mapeo de repositorios
class RepoType(Enum):
    MEMORY = MemoryTaskRepository
    SQLITE = SqliteTaskRepository

# Elegir el repositorio a usar
ACTIVE_REPOSITORY = RepoType.SQLITE

# Crea e inyecta el repository al servicio
repository = ACTIVE_REPOSITORY.value()
task_service = TaskService(repository)

logger.bind(action="using", entity='repository', type=ACTIVE_REPOSITORY.name.lower()).debug("Repositorio en uso")