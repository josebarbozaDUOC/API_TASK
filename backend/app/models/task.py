# backend/app/models/task.py

"""
Entidad de dominio: Task

Este módulo define la clase Task, que representa una tarea dentro del sistema.
Encapsula los atributos fundamentales y comportamientos básicos relacionados con el ciclo de vida de una tarea.

Responsabilidades:
- Representar la estructura de datos de una tarea
- Implementar comportamientos relacionados (completar/incompletar)
- Facilitar la serialización a formatos como JSON
"""

from datetime import datetime
from typing import Optional

class Task:
    """
    Clase que representa una tarea en el sistema.
    Define los atributos y métodos asociados a una tarea individual.
    """
    def __init__(self, 
                 title: str,
                 description: Optional[str] = None,
                 id: Optional[int] = None,
                 completed: bool = False,
                 created_at: Optional[datetime] = None):
        self.id             = id                            # Identificador único
        self.title          = title                         # Título de la tarea
        self.description    = description                   # Descripción opcional
        self.completed      = completed                     # Estado de finalización
        self.created_at     = created_at or datetime.now()  # Fecha y hora de creación
    
    def mark_complete(self):
        """Marca la tarea como completada"""
        self.completed = True

    def mark_incomplete(self):
        """Marca la tarea como no completada."""
        self.completed = False

    def to_dict(self):
        """Convierte la tarea a diccionario para enviar como JSON"""
        return {
            "id":           self.id,
            "title":        self.title,
            "description":  self.description,
            "completed":    self.completed,
            "created_at":   self.created_at.isoformat()
        }