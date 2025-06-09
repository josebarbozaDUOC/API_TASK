# app/repositories/task/memory_repository.py

"""
Repositorio memoria ram solo para Task (almacena en lista)

Características:
- Asigna IDs automáticamente de forma incremental
- Almacena copias de los objetos para mantener independencia
- Retorna copias para evitar modificaciones externas accidentales
"""

from typing import List, Optional
from datetime import datetime
from app.models.task import Task
from app.repositories.task.base_repository import TaskRepository

class MemoryTaskRepository(TaskRepository):
    def __init__(self):
        self._tasks: List[Task] = []
        self._next_id = 1
    
    def create(self, task: Task) -> Task:
        """Crea una nueva tarea asignando un ID único."""
        # Crear una copia del objeto para mantener independencia
        new_task = Task(
            title=task.title,
            description=task.description,
            completed=task.completed,
            created_at=task.created_at or datetime.now(),
            id=self._next_id
        )
        self._next_id += 1
        self._tasks.append(new_task)
        return new_task
    
    def get_all(self) -> List[Task]:
        """Retorna una copia de todas las tareas para evitar modificaciones externas."""
        return self._tasks.copy()
    
    def get_by_id(self, task_id: int) -> Optional[Task]:
        """Busca una tarea por su ID."""
        return next((task for task in self._tasks if task.id == task_id), None)
    
    def update(self, task_id: int, task: Task) -> Optional[Task]:
        """
        Actualiza una tarea existente preservando su ID original.
        Retorna la tarea actualizada o None si no se encuentra.
        """
        for i, existing_task in enumerate(self._tasks):
            if existing_task.id == task_id:
                # Crear nueva instancia con el ID preservado
                updated_task = Task(
                    title=task.title,
                    description=task.description,
                    completed=task.completed,
                    created_at=existing_task.created_at,  # Preservar fecha original
                    id=task_id  # Preservar ID original
                )
                self._tasks[i] = updated_task
                return updated_task
        return None
    
    def delete(self, task_id: int) -> bool:
        """
        Elimina una tarea por su ID.
        Retorna True si se eliminó, False si no se encontró.
        """
        task = self.get_by_id(task_id)
        if task:
            self._tasks.remove(task)
            return True
        return False