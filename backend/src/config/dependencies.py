# backend/src/config/dependencies.py

"""Dependencias globales de la aplicación."""

from functools import lru_cache
from src.repositories.task.repository_factory import RepositoryFactory
from src.services.task_service import TaskService

@lru_cache()
def create_task_service() -> TaskService:
    """
    Crea el servicio de tareas con el repositorio configurado.
    Usa el factory para crear el repositorio según la configuración del entorno (.env).
    Returns:
        Instancia única (singleton) del servicio de tareas.
    """
    repository = RepositoryFactory.create()
    return TaskService(repository)


# Lazy loading del servicio
task_service = create_task_service