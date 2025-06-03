# app/services/task_service.py

"""
Servicio de lógica de negocio para la gestión de tareas.

Este módulo contiene toda la lógica de aplicación para operaciones CRUD de tareas.
Actualmente usa almacenamiento en memoria, diseñado para migrar fácilmente a base de datos.

Classes:
    TaskService: Maneja todas las operaciones de negocio de tareas
    
Module variables:
    task_service: Instancia singleton del servicio
"""

# REFACTORIZAR ESTE MÓDULO 
# (adaptar para tomar info en listas, independiente de donde venga (memoria, db, etc))

from typing import List, Optional
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate

class TaskService:
    """
    Maneja toda la lógica de negocio de las tareas.
    Por ahora usa memoria, después cambiaremos a DB.
    """
    def __init__(self):
        self.tasks: List[Task] = []  # Lista en memoria (temporal)
        self.next_id = 1             # Contador para IDs únicos
    
    def create_task(self, task_data: TaskCreate) -> Task:
        """Crea una nueva tarea"""
        task = Task(
            id=self.next_id,
            title=task_data.title,
            description=task_data.description
        )
        self.tasks.append(task)
        self.next_id += 1
        return task
    
    def get_all_tasks(self) -> List[Task]:
        """Obtiene todas las tareas"""
        return self.tasks
    
    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """Busca una tarea por ID"""
        #return next((task for task in self.tasks if task.id == task_id), None)
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def update_task(self, task_id: int, task_data: TaskUpdate) -> Optional[Task]:
        """Actualiza una tarea existente"""
        task = self.get_task_by_id(task_id)
        if not task:
            return None
        
        # Actualiza solo los campos enviados
        if task_data.title is not None:
            task.title = task_data.title
        if task_data.description is not None:
            task.description = task_data.description
        if task_data.completed is not None:
            task.completed = task_data.completed
            
        return task
    
    def delete_task(self, task_id: int) -> bool:
        """Elimina una tarea"""
        task = self.get_task_by_id(task_id)
        if task:
            self.tasks.remove(task)
            return True
        return False

# Instancia global (singleton simple)
task_service = TaskService()