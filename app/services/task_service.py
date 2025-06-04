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

# REFACTORIZAR ESTE MÓDULO, REESTRUCTURAR EN ARCHIVOS SEPARADOS EN CARPETA repositories

from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


'''# Desacoplar el generador de ID, del servicio
class IdGenerator:
    def __init__(self):
        self._counter = 0
    
    def next_id(self) -> int:
        self._counter += 1
        return self._counter'''

#-----------------------------------------------------Interfaz
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

#-----------------------------------------------------Implementación en memoria
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
    

#-----------------------------------------------------Servicio con inyección de dependencias
class TaskService:
    """
    Servicio que maneja la lógica de negocio de las tareas.
    No sabe qué tipo de repository usa (memoria, DB, archivo, etc.)
    """
    
    def __init__(self, repository: TaskRepository):
        self.repository = repository  # Inyección de dependencia
    
    def create_task(self, task_data: TaskCreate) -> Task:
        """Crea una nueva tarea"""
        task = Task(
            id=0, # Se inicia en cero, pero toma el valor ID del repositorio
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
        
        # Actualiza solo los campos proporcionados (HACER REFACTOR MÁS ADELANTE)
        if task_data.title is not None:
            existing_task.title = task_data.title
        if task_data.description is not None:
            existing_task.description = task_data.description
        if task_data.completed is not None:
            existing_task.completed = task_data.completed
        
        return self.repository.update(task_id, existing_task)
    
    def delete_task(self, task_id: int) -> bool:
        """Elimina una tarea"""
        return self.repository.delete(task_id)


#-----------------------------------------------------Uso
# Crear el generador de IDs
#id_generator = IdGenerator()

# Crear el repository (ACÁ DEFINO QUÉ USAR)
repository = MemoryTaskRepository()

# Inyectar el repository en el servicio
task_service = TaskService(repository)


'''# Código antiguo como referencia:

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
task_service = TaskService()'''