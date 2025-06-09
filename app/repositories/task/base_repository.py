# app/repositories/task/base_repository.py

"""
Repositorio base solo para Task
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.task import Task

class TaskRepository(ABC):
    """
    Interfaz que define qué operaciones debe soportar
    cualquier almacenamiento de tareas.
    """
    
    @abstractmethod
    def create(self, task: Task) -> Task:
        """Guarda una nueva tarea"""
        pass
    
    @abstractmethod
    def get_all(self) -> List[Task]:
        """Obtiene todas las tareas"""
        pass
    
    @abstractmethod
    def get_by_id(self, task_id: int) -> Optional[Task]:
        """Busca una tarea por ID"""
        pass
    
    @abstractmethod
    def update(self, task_id: int, task: Task) -> Optional[Task]:
        """Actualiza una tarea existente"""
        pass
    
    @abstractmethod
    def delete(self, task_id: int) -> bool:
        """Elimina una tarea, retorna True si existía"""
        pass
