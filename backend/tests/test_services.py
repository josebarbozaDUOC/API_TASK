# backend/tests/test_services.py

"""
Pruebas unitarias para TaskService.

Este módulo prueba la lógica de negocio del servicio de tareas,
usando mocks para el repositorio para aislar las pruebas del
almacenamiento específico.

Tests implementados:
- test_create_task: Creación básica de tareas
- test_create_task_calls_repository: Verificación de llamada al repositorio
- test_create_task_with_description: Creación con descripción opcional
- test_create_task_without_description: Creación sin descripción
- test_get_all_tasks: Obtener todas las tareas
- test_get_all_tasks_empty: Obtener lista vacía
- test_get_task_by_id_existing: Obtener tarea existente por ID
- test_get_task_by_id_not_found: Obtener tarea inexistente
- test_update_task_complete: Actualización completa de tarea
- test_update_task_partial_title: Actualización parcial (solo título)
- test_update_task_partial_completed: Actualización parcial (solo completed)
- test_update_task_partial_description: Actualización parcial (solo descripción)
- test_update_task_multiple_fields: Actualización de múltiples campos
- test_update_task_not_found: Actualización de tarea inexistente
- test_update_task_exclude_unset: Verificar exclude_unset en schemas
- test_delete_task_existing: Eliminación de tarea existente
- test_delete_task_not_found: Eliminación de tarea inexistente
- test_repository_dependency_injection: Verificar inyección de dependencias

Configuración:
- Usa pytest fixtures para setup limpio
- Mock del repositorio para aislamiento completo
- Verificación de interacciones con mock.assert_called_with()
- Tests de casos edge y manejo de errores

Ejecución:
    python -m pytest tests/test_services.py -v
    python -m pytest tests/test_services.py --cov=app.services.task_service -v
"""

import pytest
from unittest.mock import Mock, call
from datetime import datetime
from app.services.task_service import TaskService
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate
from app.repositories.task.base_repository import TaskRepository


class TestTaskService:
    """Pruebas para el servicio de tareas."""
    
    @pytest.fixture
    def mock_repository(self):
        """Crea un mock del repositorio para las pruebas."""
        return Mock(spec=TaskRepository)
    
    @pytest.fixture
    def task_service(self, mock_repository):
        """Crea una instancia del servicio con repositorio mock."""
        return TaskService(mock_repository)
    
    @pytest.fixture
    def sample_task(self):
        """Proporciona una tarea de ejemplo."""
        return Task(
            id=1,
            title="Tarea de prueba",
            description="Descripción de prueba",
            completed=False,
            created_at=datetime.now()
        )
    
    @pytest.fixture
    def sample_task_create(self):
        """Proporciona datos para crear una tarea."""
        return TaskCreate(
            title="Nueva tarea",
            description="Nueva descripción"
        )
    
    @pytest.fixture
    def sample_task_update(self):
        """Proporciona datos para actualizar una tarea."""
        return TaskUpdate(
            title="Título actualizado",
            completed=True
        )

    # Tests de creación
    def test_create_task(self, task_service, mock_repository, sample_task_create):
        """Debe crear una nueva tarea correctamente."""
        # Configurar mock
        expected_task = Task(
            id=1,
            title="Nueva tarea",
            description="Nueva descripción",
            completed=False,
            created_at=datetime.now()
        )
        mock_repository.create.return_value = expected_task
        
        # Ejecutar
        result = task_service.create_task(sample_task_create)
        
        # Verificar resultado
        assert result == expected_task
        assert result.title == "Nueva tarea"
        assert result.description == "Nueva descripción"
        assert result.completed is False
        
        # Verificar que se llamó al repositorio correctamente
        mock_repository.create.assert_called_once()
        call_args = mock_repository.create.call_args[0][0]  # Primer argumento
        assert isinstance(call_args, Task)
        assert call_args.title == "Nueva tarea"
        assert call_args.description == "Nueva descripción"
        assert call_args.completed is False
        assert call_args.id is None  # No debe tener ID antes de crear

    def test_create_task_calls_repository(self, task_service, mock_repository):
        """Debe llamar al repositorio con los datos correctos."""
        task_data = TaskCreate(title="Test Task", description="Test Description")
        expected_task = Task(id=1, title="Test Task", description="Test Description")
        mock_repository.create.return_value = expected_task
        
        task_service.create_task(task_data)
        
        # Verificar que se llamó create exactamente una vez
        mock_repository.create.assert_called_once()

    def test_create_task_with_description(self, task_service, mock_repository):
        """Debe crear tarea con descripción opcional."""
        task_data = TaskCreate(title="Tarea con descripción", description="Mi descripción")
        expected_task = Task(id=1, title="Tarea con descripción", description="Mi descripción")
        mock_repository.create.return_value = expected_task
        
        result = task_service.create_task(task_data)
        
        assert result.description == "Mi descripción"

    def test_create_task_without_description(self, task_service, mock_repository):
        """Debe crear tarea sin descripción (None)."""
        task_data = TaskCreate(title="Solo título")
        expected_task = Task(id=1, title="Solo título", description=None)
        mock_repository.create.return_value = expected_task
        
        result = task_service.create_task(task_data)
        
        assert result.description is None

    # Tests de lectura
    def test_get_all_tasks(self, task_service, mock_repository):
        """Debe obtener todas las tareas del repositorio."""
        expected_tasks = [
            Task(id=1, title="Tarea 1", completed=False),
            Task(id=2, title="Tarea 2", completed=True),
        ]
        mock_repository.get_all.return_value = expected_tasks
        
        result = task_service.get_all_tasks()
        
        assert result == expected_tasks
        assert len(result) == 2
        mock_repository.get_all.assert_called_once()

    def test_get_all_tasks_empty(self, task_service, mock_repository):
        """Debe manejar lista vacía correctamente."""
        mock_repository.get_all.return_value = []
        
        result = task_service.get_all_tasks()
        
        assert result == []
        assert len(result) == 0
        mock_repository.get_all.assert_called_once()

    def test_get_task_by_id_existing(self, task_service, mock_repository, sample_task):
        """Debe obtener una tarea existente por ID."""
        mock_repository.get_by_id.return_value = sample_task
        
        result = task_service.get_task_by_id(1)
        
        assert result == sample_task
        assert result.id == 1
        mock_repository.get_by_id.assert_called_once_with(1)

    def test_get_task_by_id_not_found(self, task_service, mock_repository):
        """Debe lanzar NotFoundError para tarea inexistente."""
        from app.middleware.error_handler import NotFoundError
        
        mock_repository.get_by_id.return_value = None
        
        with pytest.raises(NotFoundError) as exc_info:
            task_service.get_task_by_id(999)
        
        assert "Task 999 not found" in str(exc_info.value)
        mock_repository.get_by_id.assert_called_once_with(999)

    # Tests de actualización
    def test_update_task_complete(self, task_service, mock_repository):
        """Debe actualizar una tarea con todos los campos."""
        existing_task = Task(id=1, title="Original", description="Original desc", completed=False)
        mock_repository.get_by_id.return_value = existing_task
        
        updated_task = Task(id=1, title="Actualizado", description="Nueva desc", completed=True)
        mock_repository.update.return_value = updated_task
        
        update_data = TaskUpdate(
            title="Actualizado",
            description="Nueva desc",
            completed=True
        )
        
        result = task_service.update_task(1, update_data)
        
        assert result == updated_task
        assert result.title == "Actualizado"
        assert result.description == "Nueva desc"
        assert result.completed is True
        
        # Verificar llamadas al repositorio
        mock_repository.get_by_id.assert_called_once_with(1)
        mock_repository.update.assert_called_once_with(1, existing_task)

    def test_update_task_partial_title(self, task_service, mock_repository):
        """Debe actualizar solo el título de una tarea."""
        existing_task = Task(id=1, title="Original", description="Desc original", completed=False)
        mock_repository.get_by_id.return_value = existing_task
        
        # Simular que el repositorio retorna la tarea actualizada
        updated_task = Task(id=1, title="Nuevo título", description="Desc original", completed=False)
        mock_repository.update.return_value = updated_task
        
        update_data = TaskUpdate(title="Nuevo título")  # Solo título
        
        result = task_service.update_task(1, update_data)
        
        assert result.title == "Nuevo título"
        assert result.description == "Desc original"  # No cambió
        assert result.completed is False  # No cambió
        
        # Verificar que se actualizó solo el título en el objeto existente
        mock_repository.update.assert_called_once()
        updated_existing_task = mock_repository.update.call_args[0][1]
        assert updated_existing_task.title == "Nuevo título"

    def test_update_task_partial_completed(self, task_service, mock_repository):
        """Debe actualizar solo el estado completed de una tarea."""
        existing_task = Task(id=1, title="Título", description="Descripción", completed=False)
        mock_repository.get_by_id.return_value = existing_task
        
        updated_task = Task(id=1, title="Título", description="Descripción", completed=True)
        mock_repository.update.return_value = updated_task
        
        update_data = TaskUpdate(completed=True)  # Solo completed
        
        result = task_service.update_task(1, update_data)
        
        assert result.completed is True
        assert result.title == "Título"  # No cambió
        assert result.description == "Descripción"  # No cambió

    def test_update_task_partial_description(self, task_service, mock_repository):
        """Debe actualizar solo la descripción de una tarea."""
        existing_task = Task(id=1, title="Título", description="Original", completed=False)
        mock_repository.get_by_id.return_value = existing_task
        
        updated_task = Task(id=1, title="Título", description="Nueva descripción", completed=False)
        mock_repository.update.return_value = updated_task
        
        update_data = TaskUpdate(description="Nueva descripción")  # Solo descripción
        
        result = task_service.update_task(1, update_data)
        
        assert result.description == "Nueva descripción"
        assert result.title == "Título"  # No cambió
        assert result.completed is False  # No cambió

    def test_update_task_multiple_fields(self, task_service, mock_repository):
        """Debe actualizar múltiples campos correctamente."""
        existing_task = Task(id=1, title="Original", description="Original", completed=False)
        mock_repository.get_by_id.return_value = existing_task
        
        updated_task = Task(id=1, title="Nuevo", description="Original", completed=True)
        mock_repository.update.return_value = updated_task
        
        update_data = TaskUpdate(title="Nuevo", completed=True)  # Título y completed
        
        result = task_service.update_task(1, update_data)
        
        assert result.title == "Nuevo"
        assert result.completed is True
        assert result.description == "Original"  # No cambió

    def test_update_task_not_found(self, task_service, mock_repository):
        """Debe lanzar NotFoundError si la tarea a actualizar no existe."""
        from app.middleware.error_handler import NotFoundError
        
        mock_repository.get_by_id.return_value = None
        
        update_data = TaskUpdate(title="No importa")
        
        with pytest.raises(NotFoundError) as exc_info:
            task_service.update_task(999, update_data)
        
        assert "Task 999 not found" in str(exc_info.value)
        mock_repository.get_by_id.assert_called_once_with(999)
        # No debe llamar update si no existe la tarea
        mock_repository.update.assert_not_called()

    def test_update_task_exclude_unset(self, task_service, mock_repository):
        """Debe usar exclude_unset=True para actualizar solo campos enviados."""
        existing_task = Task(id=1, title="Original", description="Original", completed=False)
        mock_repository.get_by_id.return_value = existing_task
        mock_repository.update.return_value = existing_task
        
        # Crear TaskUpdate con solo un campo
        update_data = TaskUpdate(title="Solo título")
        
        task_service.update_task(1, update_data)
        
        # Verificar que solo se actualizó el título
        updated_task = mock_repository.update.call_args[0][1]
        assert updated_task.title == "Solo título"
        assert updated_task.description == "Original"  # Debe mantener valor original
        assert updated_task.completed is False  # Debe mantener valor original

    # Tests de eliminación
    def test_delete_task_existing(self, task_service, mock_repository):
        """Debe eliminar una tarea existente."""
        mock_repository.delete.return_value = True
        
        result = task_service.delete_task(1)
        
        assert result is True
        mock_repository.delete.assert_called_once_with(1)

    def test_delete_task_not_found(self, task_service, mock_repository):
        """Debe retornar False si la tarea a eliminar no existe."""
        mock_repository.delete.return_value = False
        
        result = task_service.delete_task(999)
        
        assert result is False
        mock_repository.delete.assert_called_once_with(999)

    # Tests de inyección de dependencias
    def test_repository_dependency_injection(self, mock_repository):
        """Debe usar el repositorio inyectado correctamente."""
        service = TaskService(mock_repository)
        
        assert service.repository == mock_repository
        assert service.repository is mock_repository

    def test_service_isolation_between_instances(self):
        """Debe mantener aislamiento entre diferentes instancias del servicio."""
        repo1 = Mock(spec=TaskRepository)
        repo2 = Mock(spec=TaskRepository)
        
        service1 = TaskService(repo1)
        service2 = TaskService(repo2)
        
        assert service1.repository is repo1
        assert service2.repository is repo2
        assert service1.repository is not service2.repository

    def test_model_dump_behavior(self, task_service, mock_repository):
        """Debe comportarse correctamente con model_dump(exclude_unset=True)."""
        existing_task = Task(id=1, title="Original", description="Original", completed=False)
        mock_repository.get_by_id.return_value = existing_task
        mock_repository.update.return_value = existing_task
        
        # TaskUpdate solo con completed
        update_data = TaskUpdate(completed=True)
        
        # Verificar que model_dump(exclude_unset=True) solo incluye completed
        dump_data = update_data.model_dump(exclude_unset=True)
        expected_dump = {"completed": True}
        assert dump_data == expected_dump
        
        # Ejecutar update
        task_service.update_task(1, update_data)
        
        # Verificar que solo se modificó el campo completed
        updated_task = mock_repository.update.call_args[0][1]
        assert updated_task.completed is True
        assert updated_task.title == "Original"  # No modificado
        assert updated_task.description == "Original"  # No modificado