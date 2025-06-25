# backend/src/schemas/task.py

"""
Esquemas de validación y serialización para la entidad Task.

Este módulo define los contratos de datos para la API:
- TaskCreate: Validación de datos de entrada para crear tareas
- TaskResponse: Formato de respuesta estándar para tareas
- TaskUpdate: Validación de datos para actualizar tareas

Los esquemas usan Pydantic para validación automática y generación de documentación.
"""

from pydantic   import BaseModel, Field
from typing     import Optional
from datetime   import datetime

# Campos base
TITLE_FIELD             = Field(..., min_length=1, max_length=100, description="Título de la tarea")
TITLE_FIELD_OPTIONAL    = Field(None, min_length=1, max_length=100, description="Título opcional de la tarea")
DESCRIPTION_FIELD       = Field(None, max_length=500, description="Descripción opcional")

class TaskCreate(BaseModel):
    """
    Define qué datos debe enviar el cliente para CREAR una tarea.
    title es obligatorio, description es opcional.
    Ejemplo: POST /tasks con {"title": "comprar pan"}
    """
    title: str = TITLE_FIELD
    description: Optional[str] = DESCRIPTION_FIELD

class TaskResponse(BaseModel):
    """
    Define el formato de respuesta cuando devolvemos una tarea.
    Garantiza que siempre enviemos estos campos al cliente.
    """
    id: int
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime

class TaskUpdate(BaseModel):
    """
    Define qué campos se pueden actualizar en una tarea existente.
    Todos son opcionales porque quizás se requiere cambiar un solo campo.
    Ejemplo: PUT /tasks/1 con {"completed": true}
    """
    title: Optional[str]        = TITLE_FIELD_OPTIONAL
    description: Optional[str]  = DESCRIPTION_FIELD
    completed: Optional[bool]   = None