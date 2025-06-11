# app/services/task_service.py

"""
Servicio de lógica de negocio para la gestión de tareas.

Este módulo contiene toda la lógica de aplicación para operaciones CRUD de tareas.
Implementa el patrón Repository para desacoplar la lógica de negocio
del almacenamiento. No conoce ni le importa si usa memoria, SQLite, etc.

Classes:
    TaskService: Maneja todas las operaciones de negocio de tareas
"""

from typing import List, Optional
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate
from app.repositories.task.base_repository import TaskRepository
from app.middleware.error_handler import raise_not_found, raise_validation_error
from loguru import logger

ENTITY = "task" # Define qué tipo de entidad maneja este servicio

class TaskService:
    """Servicio que maneja la lógica de negocio de las tareas."""
    
    def __init__(self, repository: TaskRepository):
        self.repository = repository
        self.entity = ENTITY
    
    def create_task(self, task_data: TaskCreate) -> Task:
        """Crea una nueva tarea"""
        task = Task(title=task_data.title, description=task_data.description)
        created_task = self.repository.create(task)
        
        logger.bind(action="create", entity=self.entity, id=created_task.id).info("Entidad creada")
        return created_task
    
    def get_all_tasks(self) -> List[Task]:
        """Obtiene todas las tareas"""
        tasks = self.repository.get_all()
        logger.bind(action="get_all", entity=self.entity, count=len(tasks)).info("Entidades obtenidas")
        return tasks
    
    def get_task_by_id(self, task_id: int) -> Task:
        """Busca una tarea por ID"""
        task = self.repository.get_by_id(task_id)

        if not task:
            logger.bind(action="get_by_id", entity=self.entity, id=task_id).warning("Entidad no encontrada")
            raise_not_found("Task", task_id)
        
        assert task is not None # Type assertion a Pylance

        logger.bind(action="get_by_id", entity=self.entity, id=task_id).info("Entidad encontrada")
        return task
    
    def update_task(self, task_id: int, task_data: TaskUpdate) -> Task:
        """Actualiza una tarea existente"""
        existing_task = self.repository.get_by_id(task_id)
        
        # REFACTOR POSIBLE: El get_by_id ya hace log "no encontrada" y lanza excepción
        if existing_task is None:
            logger.bind(action="update", entity=self.entity, id=task_id).warning("Entidad no encontrada")
            raise_not_found("Task", task_id)
        
        # Type assertion: le decimos a Pylance que aquí existing_task YA NO es None
        assert existing_task is not None
        
        update_fields = task_data.model_dump(exclude_unset=True)
        for field, value in update_fields.items():
            setattr(existing_task, field, value)
        
        updated_task = self.repository.update(task_id, existing_task)
        
        # Type assertion para el resultado del update
        assert updated_task is not None
        
        logger.bind(action="update", entity=self.entity, id=task_id, fields=list(update_fields.keys())).info("Entidad actualizada")
        return updated_task
    
    def delete_task(self, task_id: int) -> bool:
        """Elimina una tarea"""

        existing_task = self.repository.get_by_id(task_id)

        # REFACTOR POSIBLE: El get_by_id ya hace log "no encontrada" y lanza excepción
        if not existing_task:
            logger.bind(action="delete", entity=self.entity, id=task_id).warning("Entidad no encontrada")
            raise_not_found("Task", task_id)

        success = self.repository.delete(task_id)
        logger.bind(action="delete", entity=self.entity, id=task_id, success=success).info("Entidad procesada")
        return success