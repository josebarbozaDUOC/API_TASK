# app/routes/tasks.py

"""
Endpoints HTTP para la gestión de tareas.

Este módulo define las rutas de la API REST para operaciones CRUD:
- GET /tasks: Listar todas las tareas
- POST /tasks: Crear nueva tarea
- GET /tasks/{id}: Obtener tarea por ID
- PUT /tasks/{id}: Actualizar tarea completa
- DELETE /tasks/{id}: Eliminar tarea

Responsabilidades:
- Validación de esquemas (FastAPI + Pydantic automático)
- Delegación de lógica de negocio al servicio
- Conversión de respuestas a formato JSON

Manejo de errores:
- Los servicios lanzan excepciones de negocio (NotFoundError, ValidationError)
- El middleware convierte automáticamente las excepciones a respuestas HTTP
- No se requiere manejo manual de errores en los endpoints
"""

from fastapi import APIRouter
from typing import List
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.config import task_service

router = APIRouter()

@router.get("/tasks", response_model=List[TaskResponse])
async def get_all_tasks():
    """Obtiene todas las tareas"""
    tasks = task_service.get_all_tasks()
    return [task.to_dict() for task in tasks]

@router.post("/tasks", response_model=TaskResponse, status_code=201)
async def create_task(task_data: TaskCreate):
    """Crea una nueva tarea"""
    task = task_service.create_task(task_data)
    return task.to_dict()

@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int):
    """Obtiene una tarea por ID"""
    task = task_service.get_task_by_id(task_id)  # Si no existe, lanza NotFoundError automáticamente
    return task.to_dict()

@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task_data: TaskUpdate):
    """Actualiza una tarea"""
    task = task_service.update_task(task_id, task_data)  # Si no existe, lanza NotFoundError automáticamente
    return task.to_dict()

@router.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: int):
    """Elimina una tarea"""
    task_service.delete_task(task_id)  # Si no existe, lanza NotFoundError automáticamente
    return {"message": "Task deleted successfully"}