# tests/test_schemas.py

"""
Pruebas unitarias para los schemas Pydantic del modelo Task.

Este módulo contiene pruebas basadas en pytest que siguen el patrón AAA 
(Arrange, Act, Assert) para validar el comportamiento y la validación de 
los schemas TaskCreate, TaskUpdate y TaskResponse.

Tests implementados:
- test_task_create_valid_data: Creación válida con título y descripción
- test_task_create_only_title: Creación válida solo con título
- test_task_create_empty_title_fails: Validación de título vacío
- test_task_create_title_too_long_fails: Validación de título muy largo
- test_task_create_description_too_long_fails: Validación de descripción muy larga
- test_task_create_missing_title_fails: Validación al omitir título
- test_task_update_partial_data: Actualización parcial de campos
- test_task_update_all_fields: Actualización completa de campos
- test_task_update_empty_values: Campos opcionales vacíos permitidos
- test_task_update_empty_title_fails: Título vacío inválido en actualización
- test_task_update_title_too_long_fails: Título muy largo en actualización
- test_task_response_complete_data: Construcción válida de respuesta completa
- test_task_response_without_description: Respuesta sin descripción
- test_task_response_serialization: Serialización a diccionario
- test_task_response_required_fields: Validación de campos requeridos
- test_task_response_invalid_types: Validación de tipos incorrectos
- test_task_create_extra_fields_ignored: Ignora campos extra en creación
- test_schemas_handle_none_correctly: Manejo correcto de valores None

Schemas probados:
- TaskCreate: Para crear nuevas tareas
- TaskUpdate: Para actualizar tareas existentes  
- TaskResponse: Para respuestas estructuradas de la API

Ejecución:
    python -m pytest tests/test_schemas.py -v
    python -m pytest tests/test_schemas.py --cov=app.schemas.task -v
"""

import pytest
from datetime import datetime
from pydantic import ValidationError
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse

class TestTaskSchemas:
    """Tests para schemas de Task."""

    # Tests para TaskCreate
    def test_task_create_valid_data(self):
        """Debe crear TaskCreate con datos válidos."""
        data = {"title": "Test task", "description": "Test description"}
        task_create = TaskCreate(**data)
        
        assert task_create.title == "Test task"
        assert task_create.description == "Test description"

    def test_task_create_only_title(self):
        """Debe crear TaskCreate solo con título."""
        task_create = TaskCreate(title="Solo título")
        
        assert task_create.title == "Solo título"
        assert task_create.description is None

    def test_task_create_empty_title_fails(self):
        """Debe fallar con título vacío."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="")
        
        error_str = str(exc_info.value)
        assert "String should have at least 1 character" in error_str
        assert "string_too_short" in error_str

    def test_task_create_title_too_long_fails(self):
        """Debe fallar con título muy largo."""
        long_title = "x" * 101
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title=long_title)
        
        error_str = str(exc_info.value)
        assert "string_too_long" in error_str

    def test_task_create_description_too_long_fails(self):
        """Debe fallar con descripción muy larga."""
        long_description = "x" * 501
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="Valid", description=long_description)
        
        error_str = str(exc_info.value)
        assert "string_too_long" in error_str

    def test_task_create_missing_title_fails(self):
        """Debe fallar sin título."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(**{"description": "Solo descripción"})  # type: ignore
        
        error_str = str(exc_info.value)
        assert "Field required" in error_str

    # Tests para TaskUpdate
    def test_task_update_partial_data(self):
        """Debe crear TaskUpdate con datos parciales."""
        update = TaskUpdate(completed=True)
        assert update.completed is True
        assert update.title is None
        assert update.description is None

    def test_task_update_all_fields(self):
        """Debe crear TaskUpdate con todos los campos."""
        update = TaskUpdate(
            title="Updated title",
            description="Updated description",
            completed=True
        )
        assert update.title == "Updated title"
        assert update.description == "Updated description"
        assert update.completed is True

    def test_task_update_empty_values(self):
        """Debe permitir valores vacíos en TaskUpdate."""
        update = TaskUpdate()
        assert update.title is None
        assert update.description is None
        assert update.completed is None

    def test_task_update_empty_title_fails(self):
        """TaskUpdate debe fallar con título vacío (si se proporciona)."""
        with pytest.raises(ValidationError) as exc_info:
            TaskUpdate(title="")
        
        error_str = str(exc_info.value)
        assert "String should have at least 1 character" in error_str

    def test_task_update_title_too_long_fails(self):
        """TaskUpdate debe fallar con título muy largo."""
        long_title = "x" * 101
        with pytest.raises(ValidationError):
            TaskUpdate(title=long_title)

    # Tests para TaskResponse
    def test_task_response_complete_data(self):
        """Debe crear TaskResponse con datos completos."""
        now = datetime.now()
        response = TaskResponse(
            id=1,
            title="Response task",
            description="Response description",
            completed=False,
            created_at=now
        )
        
        assert response.id == 1
        assert response.title == "Response task"
        assert response.description == "Response description"
        assert response.completed is False
        assert response.created_at == now

    def test_task_response_without_description(self):
        """Debe crear TaskResponse sin descripción."""
        now = datetime.now()
        response = TaskResponse(
            id=1,
            title="Response task",
            description=None,
            completed=False,
            created_at=now
        )
        
        assert response.description is None

    def test_task_response_serialization(self):
        """Debe serializar correctamente a dict."""
        now = datetime.now()
        response = TaskResponse(
            id=1,
            title="Test",
            description=None,
            completed=True,
            created_at=now
        )
        
        data = response.model_dump()
        assert data["id"] == 1
        assert data["title"] == "Test"
        assert data["description"] is None
        assert data["completed"] is True
        assert data["created_at"] == now

    def test_task_response_required_fields(self):
        """Debe fallar si faltan campos requeridos en TaskResponse."""
        incomplete_data = {"title": "Test"}
        
        with pytest.raises(ValidationError) as exc_info:
            TaskResponse(**incomplete_data)  # type: ignore
        
        error_str = str(exc_info.value)
        assert "Field required" in error_str

    def test_task_response_invalid_types(self):
        """Debe fallar con tipos de datos incorrectos."""
        now = datetime.now()
        
        # ID debe ser entero
        invalid_id_data = {
            "id": "not_an_int",
            "title": "Test",
            "description": None,
            "completed": False,
            "created_at": now
        }
        
        with pytest.raises(ValidationError) as exc_info:
            TaskResponse(**invalid_id_data)  # type: ignore
        
        error_str = str(exc_info.value)
        assert "Input should be a valid integer" in error_str or "int_parsing" in error_str
        
        # completed debe ser boolean
        invalid_bool_data = {
            "id": 1,
            "title": "Test", 
            "description": None,
            "completed": "not_bool",
            "created_at": now
        }
        
        with pytest.raises(ValidationError) as exc_info:
            TaskResponse(**invalid_bool_data)  # type: ignore
        
        error_str = str(exc_info.value)
        assert "Input should be a valid boolean" in error_str or "bool_parsing" in error_str

    # Tests adicionales de validación
    def test_task_create_extra_fields_ignored(self):
        """Debe ignorar campos extra en TaskCreate."""
        task_data = {
            "title": "Test",
            "description": "Test desc",
            "extra_field": "should be ignored"
        }
        task_create = TaskCreate(**task_data)
        
        assert task_create.title == "Test"
        assert task_create.description == "Test desc"
        # extra_field no debe estar presente
        assert not hasattr(task_create, 'extra_field')

    def test_schemas_handle_none_correctly(self):
        """Debe verificar manejo correcto de valores None."""
        # TaskCreate con description None
        task_create = TaskCreate(title="Test", description=None)
        assert task_create.description is None
        
        # TaskUpdate con todos los campos None
        task_update = TaskUpdate()
        assert task_update.title is None
        assert task_update.description is None
        assert task_update.completed is None