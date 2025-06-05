# tests/test_models.py

"""
Pruebas unitarias para el modelo Task.

Este módulo contiene pruebas basadas en pytest que siguen el patrón AAA 
(Arrange, Act, Assert) para validar el comportamiento del modelo Task.

Tests implementados:
- test_create_task_with_required_fields_only: Creación con campos mínimos
- test_create_task_with_all_fields: Creación con todos los campos
- test_created_at_auto_generated: Generación automática de fecha
- test_created_at_allows_future_dates: Validación de fechas futuras
- test_mark_task_as_complete: Cambio de estado a completado
- test_mark_task_as_incomplete: Cambio de estado a no completado
- test_edit_title_and_description: Modificación de campos
- test_convert_to_dict: Serialización básica
- test_convert_to_dict_with_null_description: Serialización con campos nulos
- test_convert_to_dict_reflects_changes: Serialización tras modificaciones
- test_datetime_serialization_precision: Precisión en fechas
- test_multiple_instances_are_independent: Aislamiento entre instancias

Ejecución:
    python -m pytest tests/ -v
    python -m pytest --cov=app tests/
"""

import pytest
from datetime import datetime, timedelta
from app.models.task import Task


class TestTask:
    """Pruebas unitarias para el modelo Task."""
    
    # Tests de creación
    def test_create_task_with_required_fields_only(self):
        """Debe crear una tarea únicamente con el título."""
        title = "Mi primera tarea"
        
        task = Task(title=title)
        
        assert task.title == title
        assert task.description is None
        assert task.id is None
        assert task.completed is False
        assert isinstance(task.created_at, datetime)
    
    def test_create_task_with_all_fields(self):
        """Debe crear una tarea con todos los campos especificados."""
        task_data = {
            "id": 1,
            "title": "Tarea completa",
            "description": "Una descripción detallada",
            "completed": True,
            "created_at": datetime(2024, 1, 1, 12, 0, 0)
        }
        
        task = Task(**task_data)
        
        assert task.id == 1
        assert task.title == "Tarea completa"
        assert task.description == "Una descripción detallada"
        assert task.completed is True
        assert task.created_at == datetime(2024, 1, 1, 12, 0, 0)
    
    def test_created_at_auto_generated(self):
        """Debe generar automáticamente created_at si no se proporciona."""
        before = datetime.now()
        
        task = Task(title="Nueva tarea")
        after = datetime.now()
        
        assert before <= task.created_at <= after

    def test_created_at_allows_future_dates(self):
        """Debe permitir establecer created_at con fechas futuras."""
        future_date = datetime.now() + timedelta(days=10)
        
        task = Task(title="Tarea del futuro", created_at=future_date)
        
        assert task.created_at > datetime.now()

    # Tests de cambio de estado
    def test_mark_task_as_complete(self):
        """Debe cambiar el estado de una tarea a completada."""
        task = Task(title="Tarea por completar")
        
        task.mark_complete()
        
        assert task.completed is True
    
    def test_mark_task_as_incomplete(self):
        """Debe cambiar el estado de una tarea a no completada."""
        task = Task(title="Tarea completada", completed=True)
        
        task.mark_incomplete()
        
        assert task.completed is False

    # Tests de modificación
    def test_edit_title_and_description(self):
        """Debe permitir modificar el título y descripción después de la creación."""
        task = Task(title="Título inicial", description="Descripción inicial")
        
        task.title = "Título actualizado"
        task.description = "Nueva descripción"
        
        assert task.title == "Título actualizado"
        assert task.description == "Nueva descripción"

    # Tests de serialización
    def test_convert_to_dict(self):
        """Debe convertir correctamente la tarea a diccionario."""
        created_at = datetime(2024, 6, 5, 10, 30, 0)
        task = Task(
            id=1,
            title="Tarea de prueba",
            description="Descripción de prueba",
            completed=True,
            created_at=created_at
        )
        
        result = task.to_dict()
        
        assert result == {
            "id": 1,
            "title": "Tarea de prueba",
            "description": "Descripción de prueba",
            "completed": True,
            "created_at": "2024-06-05T10:30:00"
        }

    def test_convert_to_dict_with_null_description(self):
        """Debe incluir campos nulos en la serialización."""
        task = Task(id=2, title="Sin descripción", completed=False)
        
        result = task.to_dict()
        
        assert result["description"] is None

    def test_convert_to_dict_reflects_changes(self):
        """Debe reflejar los cambios realizados al objeto en la serialización."""
        task = Task(title="Título original", completed=False)
        task.title = "Título actualizado"
        task.mark_complete()
        
        result = task.to_dict()
        
        assert result["title"] == "Título actualizado"
        assert result["completed"] is True

    def test_datetime_serialization_precision(self):
        """Debe mantener la precisión de microsegundos en la serialización de fechas."""
        precise_datetime = datetime(2025, 1, 1, 12, 0, 0, 123456)
        task = Task(title="Precisión temporal", created_at=precise_datetime)
        
        result = task.to_dict()
        
        assert result["created_at"].endswith("123456")

    # Tests de aislamiento
    def test_multiple_instances_are_independent(self):
        """Debe mantener la independencia entre múltiples instancias."""
        task1 = Task(title="Primera tarea")
        task2 = Task(title="Segunda tarea")
        
        task1.mark_complete()
        
        assert task1.completed is True
        assert task2.completed is False

    # Tests pendientes
    @pytest.mark.skip(reason="Validación de título vacío pendiente de implementar")
    def test_title_should_not_be_empty(self):
        """Debe rechazar títulos vacíos."""
        # Este test se activará cuando se implemente la validación
        Task(title="")