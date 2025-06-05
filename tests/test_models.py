# tests/test_models.py

"""
Test basado en pytest: Arrange (Preparar), Act (Actuar), Assert (Afirmar)

Este módulo prueba el modelo Task mediante casos unitarios que validan:
- Creación de tareas con solo los campos requeridos.
- Creación de tareas con todos los campos especificados.
- Cambios de estado: marcar tareas como completadas o incompletas.
- Conversión del modelo a diccionario con formato ISO 8601 para fechas.
- Generación automática del campo created_at si no se proporciona.

Ejecutar en powershell (estando en root): 
python -m pytest tests/ -v

python -m pytest --cov=app tests/
"""

import pytest
from datetime import datetime
from app.models.task import Task

class TestTask:
    """Tests para el modelo Task"""
    
    def test_create_task_with_required_fields_only(self):
        """Test: crear una tarea solo con campos requeridos"""
        # Arrange (Preparar)
        title = "Mi primera tarea"
        
        # Act (Actuar)
        task = Task(title=title)
        
        # Assert (Afirmar)
        assert task.title == title
        assert task.description is None
        assert task.id is None
        assert task.completed is False
        assert isinstance(task.created_at, datetime)
    
    def test_create_task_with_all_fields(self):
        """Test: crear una tarea con todos los campos"""
        # Arrange
        task_data = {
            "id": 1,
            "title": "Tarea completa",
            "description": "Una descripción",
            "completed": True,
            "created_at": datetime(2024, 1, 1, 12, 0, 0)
        }
        
        # Act
        task = Task(**task_data)
        
        # Assert
        assert task.id == 1
        assert task.title == "Tarea completa"
        assert task.description == "Una descripción"
        assert task.completed is True
        assert task.created_at == datetime(2024, 1, 1, 12, 0, 0)
    
    def test_mark_complete(self):
        """Test: marcar una tarea como completada"""
        # Arrange
        task = Task(title="Tarea por completar")
        assert task.completed is False  # Verificar estado inicial
        
        # Act
        task.mark_complete()
        
        # Assert
        assert task.completed is True
    
    def test_mark_incomplete(self):
        """Test: marcar una tarea como no completada"""
        # Arrange
        task = Task(title="Tarea", completed=True)
        assert task.completed is True  # Verificar estado inicial
        
        # Act
        task.mark_incomplete()
        
        # Assert
        assert task.completed is False
    
    def test_to_dict(self):
        """Test: convertir tarea a diccionario"""
        # Arrange
        created_at = datetime(2024, 6, 5, 10, 30, 0)
        task = Task(
            id=1,
            title="Test task",
            description="Test description",
            completed=True,
            created_at=created_at
        )
        
        # Act
        result = task.to_dict()
        
        # Assert
        assert result == {
            "id": 1,
            "title": "Test task",
            "description": "Test description",
            "completed": True,
            "created_at": "2024-06-05T10:30:00"
        }
    
    def test_created_at_auto_generated(self):
        """Test: created_at se genera automáticamente si no se provee"""
        # Arrange
        before = datetime.now()
        
        # Act
        task = Task(title="Nueva tarea")
        after = datetime.now()
        
        # Assert
        assert before <= task.created_at <= after