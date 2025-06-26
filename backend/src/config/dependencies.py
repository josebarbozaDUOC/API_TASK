# backend/src/config/dependencies.py

"""Dependencias globales de la aplicación."""

from enum import Enum
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

# Crear el repositorio basado en settings
def create_task_service() -> TaskService:
    try:
        repo_type = RepoType[settings.repository_type.upper()]
        repository = repo_type.value()
        logger.bind(action="using", entity='repository', type=settings.repository_type).debug("Repositorio en uso")
        return TaskService(repository)
    except KeyError:
        available = [rt.name.lower() for rt in RepoType]
        raise ValueError(f"Repository type '{settings.repository_type}' not supported. Available: {available}")

# Crear el servicio global
task_service = create_task_service()