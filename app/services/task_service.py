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
from app.repositories.base_repository import TaskRepository

class TaskService:
    """
    Servicio que maneja la lógica de negocio de las tareas.
    """
    
    def __init__(self, repository: TaskRepository):
        self.repository = repository  # Inyección de dependencia
    
    def create_task(self, task_data: TaskCreate) -> Task:
        """Crea una nueva tarea"""
        task = Task(
            title=task_data.title,
            description=task_data.description
        )
        return self.repository.create(task)
    
    def get_all_tasks(self) -> List[Task]:
        """Obtiene todas las tareas"""
        return self.repository.get_all()
    
    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """Busca una tarea por ID"""
        return self.repository.get_by_id(task_id)
    
    def update_task(self, task_id: int, task_data: TaskUpdate) -> Optional[Task]:
        """Actualiza una tarea existente"""
        existing_task = self.repository.get_by_id(task_id)
        if not existing_task:
            return None
        
        # Convierte el objeto Pydantic a diccionario, excluyendo campos no enviados
        # Luego itera sobre los campos y los asigna dinámicamente
        update_fields = task_data.model_dump(exclude_unset=True)
        for field, value in update_fields.items():
            setattr(existing_task, field, value)
        
        return self.repository.update(task_id, existing_task)
    
    def delete_task(self, task_id: int) -> bool:
        """Elimina una tarea"""
        return self.repository.delete(task_id)
