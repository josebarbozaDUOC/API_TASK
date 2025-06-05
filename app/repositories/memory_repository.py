# app/repositories/memory_repository.py

from typing import List, Optional
from app.models.task import Task
from app.repositories.base_repository import TaskRepository

class MemoryTaskRepository(TaskRepository):
    """
    Implementación que guarda las tareas en memoria (lista).
    """
    
    def __init__(self):
        self._tasks: List[Task] = []
        self._next_id = 1
    
    def create(self, task: Task) -> Task:
        task.id = self._next_id
        self._next_id += 1
        self._tasks.append(task)
        return task
    
    def get_all(self) -> List[Task]:
        return self._tasks.copy()  # Retorna copia para evitar modificaciones externas
    
    def get_by_id(self, task_id: int) -> Optional[Task]:
        return next((task for task in self._tasks if task.id == task_id), None)
    
    def update(self, task_id: int, task: Task) -> Optional[Task]:
        for i, existing_task in enumerate(self._tasks):
            if existing_task.id == task_id:
                self._tasks[i] = task
                return task
        return None
    
    def delete(self, task_id: int) -> bool:
        task = self.get_by_id(task_id)
        if task:
            self._tasks.remove(task)
            return True
        return False