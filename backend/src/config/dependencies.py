# backend/src/config/dependencies.py

"""Dependencias globales de la aplicación."""

from enum import Enum
from functools import lru_cache
from src.config.settings import settings
from src.services.task_service import TaskService
from src.repositories.task.memory_repository import MemoryTaskRepository
from src.repositories.task.sqlite_repository import SqliteTaskRepository
from src.repositories.task.postgresql_repository import PostgresqlTaskRepository
from src.repositories.task.mysql_repository import MysqlTaskRepository
from loguru import logger

# Mapeo de repositorios
class RepoType(Enum):
    MEMORY      = MemoryTaskRepository
    SQLITE      = SqliteTaskRepository
    POSTGRES    = PostgresqlTaskRepository
    MYSQL       = MysqlTaskRepository


# Crear el repositorio basado en settings, cache para singleton
@lru_cache()
def create_task_service() -> TaskService:
    """Crea el servicio de tareas con el repositorio configurado según el environment."""
    
    repository_type = settings.repository_type
    if settings.environment.upper() == 'TESTING':
        repository_type = settings.test_repository_type
    
    try:
        repo_type = RepoType[repository_type.upper()]
        repository = repo_type.value()
        logger.bind(
            action="using", 
            entity='repository', 
            type=repository_type,
            environment=settings.environment
        ).debug("Repositorio en uso")
        return TaskService(repository)
    except KeyError:
        available = [rt.name.lower() for rt in RepoType]
        raise ValueError(f"Repository type '{repository_type}' not supported. Available: {available}")

# Crear el servicio global con lazy loading
task_service = create_task_service