# backend/src/repositories/task/repository_factory.py

"""Factory para crear repositorios de tareas."""

from typing import Optional
from typing import Dict, Type
from src.repositories.task.base_repository import TaskRepository
from src.repositories.task.memory_repository import MemoryTaskRepository
from src.repositories.task.sqlite_repository import SqliteTaskRepository
from src.repositories.task.postgresql_repository import PostgresqlTaskRepository
from src.repositories.task.mysql_repository import MysqlTaskRepository
from src.config.settings import settings
from loguru import logger

class RepositoryFactory:
    """
    Factory para crear instancias de repositorios.
    Centraliza la lógica de creación de repositorios según el tipo configurado en las variables de entorno.
    """
    
    # Mapeo de tipos a clases
    _repositories: Dict[str, Type[TaskRepository]] = {
        "memory": MemoryTaskRepository,
        "sqlite": SqliteTaskRepository,
        "postgres": PostgresqlTaskRepository,
        "postgresql": PostgresqlTaskRepository,  # alias para compatibilidad
        "mysql": MysqlTaskRepository,
    }
    
    @classmethod
    def create(cls, repository_type: Optional[str] = None) -> TaskRepository:
        """
        Crea una instancia del repositorio especificado.
        Args:
            repository_type: Tipo de repositorio. Si es None, usa la configuración.
        Returns:
            Instancia del repositorio solicitado.
        Raises:
            ValueError: Si el tipo de repositorio no está soportado.
        """
        # Determinar tipo de repositorio
        if repository_type is None:
            repository_type = settings.repository_type
            # En modo testing, usar el tipo de test
            if settings.environment.upper() == 'TESTING':
                repository_type = settings.test_repository_type
        
        # Normalizar a minúsculas
        repo_type_lower = repository_type.lower()
        
        # Validar que existe
        if repo_type_lower not in cls._repositories:
            available = list(cls._repositories.keys())
            raise ValueError(
                f"Repository type '{repository_type}' not supported. "
                f"Available types: {', '.join(available)}"
            )
        
        # Crear instancia
        repository_class = cls._repositories[repo_type_lower]
        repository = repository_class()
        
        # Log de creación
        logger.bind(
            action="created",
            entity="repository",
            type=repo_type_lower,
            class_name=repository_class.__name__,
            environment=settings.environment
        ).debug("Repository instance created")
        
        return repository
    
    @classmethod
    def get_available_types(cls) -> list:
        """Retorna lista de tipos de repositorio disponibles."""
        return list(cls._repositories.keys())