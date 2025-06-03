# app/models/task.py

"""
Entidad de dominio Task.

Este módulo define la clase Task que representa una tarea en el sistema.
Contiene la lógica de negocio y las propiedades fundamentales de una tarea.

Responsabilidades:
- Definir la estructura de datos de una tarea
- Implementar comportamientos básicos (marcar como completada)
- Proporcionar serialización a diccionario
"""

from datetime import datetime
from typing import Optional

class Task:
    """
    Clase que representa una tarea en nuestro sistema.
    Es como el "molde" para crear tareas individuales.
    """
    def __init__(self, id: int, title: str, description: Optional[str] = None):
        # Propiedades básicas de cada tarea
        self.id             = id                # Identificador único
        self.title          = title             # Título de la tarea
        self.description    = description       # Descripción opcional
        self.completed      = False             # Por defecto, no está completada
        self.created_at     = datetime.now()    # Timestamp de cuándo se creó
    
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