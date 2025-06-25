# backend/tests/conftest.py

"""
Configuración compartida para todos los tests.

Define fixtures y configuraciones que pueden ser usadas
por cualquier test en el proyecto.

Ejecución (todos los test):
    python -m pytest tests/ -v
    python -m pytest tests/ --cov=app --cov-report=term-missing -v

Generar medalla de cobertura:
    python -m pytest tests/ --cov=app --cov-report=term-missing --cov-report=xml -v
    python -m coverage_badge -o coverage.svg
    
HTML (entrar desde ruta file:///D:/PROYECTOS/API_TASK/htmlcov/function_index.html)
    python -m pytest tests/ --cov=app --cov-report=html -v

"""

import pytest
from src.repositories.task.memory_repository import MemoryTaskRepository
from src.repositories.task.sqlite_repository import SqliteTaskRepository
from src.services.task_service import TaskService
from src.config.settings import settings

@pytest.fixture
def clean_repository():
    """Proporciona un repositorio limpio para tests."""
    return MemoryTaskRepository()

@pytest.fixture
def clean_task_service(clean_repository):
    """Proporciona un servicio de tareas limpio para tests."""
    return TaskService(clean_repository)