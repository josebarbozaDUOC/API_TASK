# backend/tests/conftest.py

"""
Configuración compartida para todos los tests.

Define fixtures y configuraciones que pueden ser usadas
por cualquier test en el proyecto.

Ejecución (todos los test):
    cd backend

    python -m pytest tests/ -v
    python -m pytest tests/ --cov=src --cov-report=term-missing -v

Generar medalla de cobertura:
    python -m pytest tests/ --cov=src --cov-report=term-missing --cov-report=xml -v
    python -m coverage_badge -o coverage.svg -f
    
HTML (entrar desde ruta file:///D:/PROYECTOS/API_TASK/htmlcov/function_index.html)
    python -m pytest tests/ --cov=src --cov-report=html -v
"""

import pytest
from src.repositories.task.memory_repository import MemoryTaskRepository
from src.repositories.task.sqlite_repository import SqliteTaskRepository
from src.repositories.task.postgresql_repository import PostgresqlTaskRepository
from src.repositories.task.mysql_repository import MysqlTaskRepository
from src.services.task_service import TaskService

# Fixture parametrizada que permite múltiples repos
@pytest.fixture(params=["memory", "sqlite", "postgres", "mysql"])
def repository(request):
    """Proporciona diferentes tipos de repositorios para tests."""
    repo_map = {
        "memory": MemoryTaskRepository,
        "sqlite": SqliteTaskRepository,
        "postgres": PostgresqlTaskRepository,
        "mysql": MysqlTaskRepository,
    }
    repo_class = repo_map[request.param]
    return repo_class()

@pytest.fixture
def task_service(repository):
    """Proporciona un servicio con el repositorio inyectado."""
    return TaskService(repository)