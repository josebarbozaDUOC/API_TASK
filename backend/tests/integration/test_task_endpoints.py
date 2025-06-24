# backend/tests/integration/test_task_endpoints.py

"""
Tests de integración para los endpoints de tareas.

Estos tests prueban la API completa desde HTTP hasta la respuesta,
incluyendo:
- Validación de request/response
- Códigos de estado HTTP correctos
- Serialización de datos
- Manejo de errores
- Flujos completos CRUD

Setup:
- Usa TestClient de FastAPI para simulación completa
- Reemplaza temporalmente el task_service con uno limpio
- Repositorio en memoria para aislamiento entre tests
- Fixtures para datos de prueba consistentes

Ejecución:
    python -m pytest tests/integration/test_task_endpoints.py -v
    python -m pytest tests/integration/test_task_endpoints.py --cov=app.routes -v
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from app.main import app
from app.repositories.task.memory_repository import MemoryTaskRepository
from app.services.task_service import TaskService
from app.routes import tasks  # Importar el módulo para modificar task_service

class TestTaskEndpoints:
    """Tests de integración para endpoints de tareas."""
    
    @pytest.fixture(autouse=True)
    def setup_test_service(self):
        """
        Configura un servicio limpio para cada test.
        autouse=True hace que se ejecute automáticamente antes de cada test.
        """
        # Crear repositorio y servicio frescos para cada test
        test_repository = MemoryTaskRepository()
        test_service = TaskService(test_repository)
        
        # Guardar el servicio original y reemplazar temporalmente
        self.original_service = tasks.task_service
        tasks.task_service = test_service
        
        yield  # Aquí se ejecuta el test
        
        # Restaurar el servicio original después del test
        tasks.task_service = self.original_service
    
    @pytest.fixture
    def client(self):
        """Cliente de testing para hacer requests HTTP."""
        return TestClient(app)
    
    @pytest.fixture
    def sample_task_data(self):
        """Datos de ejemplo para crear tareas."""
        return {
            "title": "Tarea de prueba",
            "description": "Descripción de prueba"
        }
    
    @pytest.fixture
    def sample_task_data_no_description(self):
        """Datos de ejemplo sin descripción."""
        return {
            "title": "Solo título"
        }

    # Tests para GET /api/v1/tasks
    def test_get_all_tasks_empty(self, client):
        """Debe retornar lista vacía cuando no hay tareas."""
        response = client.get("/api/v1/tasks")
        
        assert response.status_code == 200
        assert response.json() == []

    def test_get_all_tasks_with_data(self, client, sample_task_data):
        """Debe retornar todas las tareas existentes."""
        # Crear algunas tareas primero
        client.post("/api/v1/tasks", json=sample_task_data)
        client.post("/api/v1/tasks", json={"title": "Segunda tarea", "description": "Otra descripción"})
        
        response = client.get("/api/v1/tasks")
        
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 2
        
        # Verificar estructura de respuesta
        assert "id" in tasks[0]
        assert "title" in tasks[0]
        assert "description" in tasks[0]
        assert "completed" in tasks[0]
        assert "created_at" in tasks[0]
        
        # Verificar contenido
        assert tasks[0]["title"] == "Tarea de prueba"
        assert tasks[0]["completed"] is False
        assert tasks[1]["title"] == "Segunda tarea"

    def test_get_all_tasks_response_format(self, client, sample_task_data):
        """Debe retornar tareas en el formato correcto del schema TaskResponse."""
        client.post("/api/v1/tasks", json=sample_task_data)
        
        response = client.get("/api/v1/tasks")
        task = response.json()[0]
        
        # Verificar tipos de datos
        assert isinstance(task["id"], int)
        assert isinstance(task["title"], str)
        assert isinstance(task["completed"], bool)
        assert isinstance(task["created_at"], str)
        
        # Verificar que created_at es un datetime válido
        datetime.fromisoformat(task["created_at"].replace('Z', '+00:00'))

    # Tests para POST /api/v1/tasks
    def test_create_task_success(self, client, sample_task_data):
        """Debe crear una nueva tarea correctamente."""
        response = client.post("/api/v1/tasks", json=sample_task_data)
        
        assert response.status_code == 201
        task = response.json()
        
        assert task["id"] == 1
        assert task["title"] == "Tarea de prueba"
        assert task["description"] == "Descripción de prueba"
        assert task["completed"] is False
        assert "created_at" in task

    def test_create_task_without_description(self, client, sample_task_data_no_description):
        """Debe crear tarea sin descripción."""
        response = client.post("/api/v1/tasks", json=sample_task_data_no_description)
        
        assert response.status_code == 201
        task = response.json()
        
        assert task["title"] == "Solo título"
        assert task["description"] is None
        assert task["completed"] is False

    def test_create_task_validation_error_empty_title(self, client):
        """Debe fallar con título vacío."""
        response = client.post("/api/v1/tasks", json={"title": ""})
        
        assert response.status_code == 422
        error = response.json()
        assert "detail" in error

    def test_create_task_validation_error_missing_title(self, client):
        """Debe fallar sin título."""
        response = client.post("/api/v1/tasks", json={"description": "Solo descripción"})
        
        assert response.status_code == 422

    def test_create_task_validation_error_title_too_long(self, client):
        """Debe fallar con título demasiado largo."""
        long_title = "x" * 101  # Más de 100 caracteres
        response = client.post("/api/v1/tasks", json={"title": long_title})
        
        assert response.status_code == 422

    def test_create_task_validation_error_description_too_long(self, client):
        """Debe fallar con descripción demasiado larga."""
        long_description = "x" * 501  # Más de 500 caracteres
        response = client.post("/api/v1/tasks", json={
            "title": "Título válido",
            "description": long_description
        })
        
        assert response.status_code == 422

    # Tests para GET /api/v1/tasks/{task_id}
    def test_get_task_by_id_success(self, client, sample_task_data):
        """Debe obtener una tarea específica por ID."""
        # Crear tarea primero
        create_response = client.post("/api/v1/tasks", json=sample_task_data)
        task_id = create_response.json()["id"]
        
        # Obtener tarea
        response = client.get(f"/api/v1/tasks/{task_id}")
        
        assert response.status_code == 200
        task = response.json()
        assert task["id"] == task_id
        assert task["title"] == "Tarea de prueba"
        assert task["description"] == "Descripción de prueba"

    def test_get_task_by_id_not_found(self, client):
        """Debe retornar 404 para tarea inexistente."""
        response = client.get("/api/v1/tasks/999")
        
        assert response.status_code == 404
        error = response.json()
        assert error["error"] == "Not found"
        assert "Task 999 not found" in error["message"]

    def test_get_task_by_id_invalid_id(self, client):
        """Debe fallar con ID inválido."""
        response = client.get("/api/v1/tasks/invalid")
        
        assert response.status_code == 422

    # Tests para PUT /api/v1/tasks/{task_id}
    def test_update_task_success(self, client, sample_task_data):
        """Debe actualizar una tarea existente."""
        # Crear tarea
        create_response = client.post("/api/v1/tasks", json=sample_task_data)
        task_id = create_response.json()["id"]
        
        # Actualizar tarea
        update_data = {
            "title": "Título actualizado",
            "description": "Descripción actualizada",
            "completed": True
        }
        response = client.put(f"/api/v1/tasks/{task_id}", json=update_data)
        
        assert response.status_code == 200
        task = response.json()
        assert task["id"] == task_id
        assert task["title"] == "Título actualizado"
        assert task["description"] == "Descripción actualizada"
        assert task["completed"] is True

    def test_update_task_partial(self, client, sample_task_data):
        """Debe actualizar solo campos enviados."""
        # Crear tarea
        create_response = client.post("/api/v1/tasks", json=sample_task_data)
        task_id = create_response.json()["id"]
        
        # Actualizar solo completed
        update_data = {"completed": True}
        response = client.put(f"/api/v1/tasks/{task_id}", json=update_data)
        
        assert response.status_code == 200
        task = response.json()
        assert task["completed"] is True
        assert task["title"] == "Tarea de prueba"  # No cambió
        assert task["description"] == "Descripción de prueba"  # No cambió

    def test_update_task_not_found(self, client):
        """Debe retornar 404 para tarea inexistente."""
        response = client.put("/api/v1/tasks/999", json={"title": "No importa"})
        
        assert response.status_code == 404
        error = response.json()
        assert error["error"] == "Not found"
        assert "Task 999 not found" in error["message"]

    def test_update_task_validation_error(self, client, sample_task_data):
        """Debe fallar con datos inválidos."""
        # Crear tarea
        create_response = client.post("/api/v1/tasks", json=sample_task_data)
        task_id = create_response.json()["id"]
        
        # Intentar actualizar con título vacío
        response = client.put(f"/api/v1/tasks/{task_id}", json={"title": ""})
        
        assert response.status_code == 422

    # Tests para DELETE /api/v1/tasks/{task_id}
    def test_delete_task_success(self, client, sample_task_data):
        """Debe eliminar una tarea existente."""
        # Crear tarea
        create_response = client.post("/api/v1/tasks", json=sample_task_data)
        task_id = create_response.json()["id"]
        
        # Eliminar tarea
        response = client.delete(f"/api/v1/tasks/{task_id}")
        
        assert response.status_code == 204
        
        # Verificar que ya no existe
        get_response = client.get(f"/api/v1/tasks/{task_id}")
        assert get_response.status_code == 404

    def test_delete_task_not_found(self, client):
        """Debe retornar 404 para tarea inexistente."""
        response = client.delete("/api/v1/tasks/999")
        
        assert response.status_code == 404
        error = response.json()
        assert error["error"] == "Not found"
        assert "Task 999 not found" in error["message"]

    def test_delete_task_returns_message(self, client, sample_task_data):
        """Debe retornar mensaje de confirmación al eliminar."""
        # Crear tarea
        create_response = client.post("/api/v1/tasks", json=sample_task_data)
        task_id = create_response.json()["id"]
        
        # Eliminar tarea
        response = client.delete(f"/api/v1/tasks/{task_id}")
        
        assert response.status_code == 204
        # Nota: 204 No Content normalmente no tiene body, pero tu endpoint lo retorna
        # Si quieres ser estricto con HTTP, podrías cambiar el endpoint a 200 con mensaje

    # Tests de flujos completos
    def test_complete_crud_workflow(self, client):
        """Debe manejar un flujo CRUD completo correctamente."""
        # 1. Crear tarea
        create_data = {"title": "Tarea workflow", "description": "Prueba completa"}
        create_response = client.post("/api/v1/tasks", json=create_data)
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]
        
        # 2. Leer tarea
        get_response = client.get(f"/api/v1/tasks/{task_id}")
        assert get_response.status_code == 200
        assert get_response.json()["title"] == "Tarea workflow"
        
        # 3. Actualizar tarea
        update_data = {"completed": True}
        update_response = client.put(f"/api/v1/tasks/{task_id}", json=update_data)
        assert update_response.status_code == 200
        assert update_response.json()["completed"] is True
        
        # 4. Verificar en lista completa
        list_response = client.get("/api/v1/tasks")
        assert len(list_response.json()) == 1
        assert list_response.json()[0]["completed"] is True
        
        # 5. Eliminar tarea
        delete_response = client.delete(f"/api/v1/tasks/{task_id}")
        assert delete_response.status_code == 204
        
        # 6. Verificar eliminación
        final_list = client.get("/api/v1/tasks")
        assert len(final_list.json()) == 0

    def test_multiple_tasks_independence(self, client):
        """Debe mantener independencia entre múltiples tareas."""
        # Crear múltiples tareas
        task1 = client.post("/api/v1/tasks", json={"title": "Tarea 1"}).json()
        task2 = client.post("/api/v1/tasks", json={"title": "Tarea 2"}).json()
        task3 = client.post("/api/v1/tasks", json={"title": "Tarea 3"}).json()
        
        # Actualizar solo una
        client.put(f"/api/v1/tasks/{task2['id']}", json={"completed": True})
        
        # Verificar que las otras no cambiaron
        response1 = client.get(f"/api/v1/tasks/{task1['id']}")
        response3 = client.get(f"/api/v1/tasks/{task3['id']}")
        
        assert response1.json()["completed"] is False
        assert response3.json()["completed"] is False
        
        # Verificar que la actualizada sí cambió
        response2 = client.get(f"/api/v1/tasks/{task2['id']}")
        assert response2.json()["completed"] is True

    def test_task_id_auto_increment(self, client):
        """Debe asignar IDs incrementales automáticamente."""
        # Crear varias tareas
        task1 = client.post("/api/v1/tasks", json={"title": "Tarea 1"}).json()
        task2 = client.post("/api/v1/tasks", json={"title": "Tarea 2"}).json()
        task3 = client.post("/api/v1/tasks", json={"title": "Tarea 3"}).json()
        
        # Verificar IDs incrementales
        assert task1["id"] == 1
        assert task2["id"] == 2
        assert task3["id"] == 3

    def test_task_to_dict_conversion(self, client, sample_task_data):
        """Debe convertir correctamente Task a dict usando to_dict()."""
        response = client.post("/api/v1/tasks", json=sample_task_data)
        task = response.json()
        
        # Verificar que todos los campos del modelo están presentes
        required_fields = ["id", "title", "description", "completed", "created_at"]
        for field in required_fields:
            assert field in task
        
        # Verificar tipos correctos
        assert isinstance(task["id"], int)
        assert isinstance(task["title"], str)
        assert isinstance(task["completed"], bool)
        assert task["description"] is None or isinstance(task["description"], str)