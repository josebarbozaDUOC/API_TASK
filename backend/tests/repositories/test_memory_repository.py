# backend/tests/repositories/test_memory_repository.py

"""
Pruebas unitarias para MemoryTaskRepository.

Este módulo contiene pruebas específicas para la implementación de MemoryTaskRepository,
validando que todas las operaciones CRUD funcionen correctamente con almacenamiento
en memoria y que mantenga el aislamiento entre instancias.

Tests implementados:
- test_create_task: Creación básica de tareas
- test_create_task_assigns_auto_id: Asignación automática de ID incremental
- test_get_all_empty: Obtener lista vacía inicial
- test_get_all_with_tasks: Obtener todas las tareas creadas
- test_get_all_maintains_order: Verificar orden de inserción
- test_get_all_returns_copy: Verificar que retorna copia (inmutable)
- test_get_by_id_existing: Obtener tarea existente por ID
- test_get_by_id_not_found: Obtener tarea inexistente (retorna None)
- test_update_existing_task: Actualizar tarea existente
- test_update_not_found: Actualizar tarea inexistente (retorna None)
- test_update_preserves_id: Verificar que el ID se mantiene al actualizar
- test_delete_existing_task: Eliminar tarea existente correctamente
- test_delete_not_found: Eliminar tarea inexistente (retorna False)
- test_memory_isolation: Aislamiento entre diferentes instancias
- test_id_increment_sequence: Secuencia correcta de IDs incrementales
- test_task_independence: Independencia de objetos Task en memoria

Configuración:
- Cada test usa una instancia fresca de MemoryTaskRepository
- No requiere configuración externa ni cleanup
- Tests específicos para verificar comportamiento en memoria

Ejecución:
    python -m pytest tests/repositories/test_memory_repository.py -v
    python -m pytest tests/repositories/test_memory_repository.py --cov=app.repositories.memory_repository -v
    python -m pytest tests/repositories/test_memory_repository.py::TestMemoryTaskRepository::test_create_task -v
"""

import pytest
from datetime import datetime
from src.repositories.task.memory_repository import MemoryTaskRepository
from src.models.task import Task


class TestMemoryTaskRepository:
    """Pruebas para la implementación MemoryTaskRepository."""
    
    @pytest.fixture
    def repository(self):
        """Crea una instancia fresca de MemoryTaskRepository."""
        return MemoryTaskRepository()
    
    @pytest.fixture
    def sample_task(self):
        """Proporciona una tarea de ejemplo para tests."""
        return Task(
            title="Tarea de prueba",
            description="Descripción de prueba",
            completed=False
        )

    # Tests de creación
    def test_create_task(self, repository, sample_task):
        """Debe crear una nueva tarea correctamente."""
        created_task = repository.create(sample_task)
        
        assert created_task.id is not None
        assert isinstance(created_task.id, int)
        assert created_task.title == sample_task.title
        assert created_task.description == sample_task.description
        assert created_task.completed == sample_task.completed
        assert isinstance(created_task.created_at, datetime)

    def test_create_task_assigns_auto_id(self, repository):
        """Debe asignar automáticamente IDs incrementales."""
        task1 = repository.create(Task(title="Primera tarea"))
        task2 = repository.create(Task(title="Segunda tarea"))
        task3 = repository.create(Task(title="Tercera tarea"))
        
        assert task1.id == 1
        assert task2.id == 2
        assert task3.id == 3

    # Tests de lectura
    def test_get_all_empty(self, repository):
        """Debe retornar lista vacía cuando no hay tareas."""
        tasks = repository.get_all()
        
        assert tasks == []
        assert isinstance(tasks, list)

    def test_get_all_with_tasks(self, repository):
        """Debe retornar todas las tareas creadas."""
        task1 = repository.create(Task(title="Primera tarea"))
        task2 = repository.create(Task(title="Segunda tarea"))
        
        tasks = repository.get_all()
        
        assert len(tasks) == 2
        assert any(task.id == task1.id for task in tasks)
        assert any(task.id == task2.id for task in tasks)

    def test_get_all_maintains_order(self, repository):
        """Debe retornar las tareas en orden de inserción."""
        task1 = repository.create(Task(title="Tarea A"))
        task2 = repository.create(Task(title="Tarea B"))
        task3 = repository.create(Task(title="Tarea C"))
        
        tasks = repository.get_all()
        
        assert len(tasks) == 3
        assert tasks[0].id == task1.id
        assert tasks[1].id == task2.id
        assert tasks[2].id == task3.id
        assert tasks[0].title == "Tarea A"
        assert tasks[1].title == "Tarea B"
        assert tasks[2].title == "Tarea C"

    def test_get_all_returns_copy(self, repository):
        """Debe retornar una copia para evitar modificaciones externas."""
        repository.create(Task(title="Tarea original"))
        
        tasks1 = repository.get_all()
        tasks2 = repository.get_all()
        
        # Verificar que son objetos diferentes
        assert tasks1 is not tasks2
        
        # Modificar una copia no debe afectar la otra
        tasks1.append(Task(title="Tarea falsa"))
        
        assert len(tasks1) == 2
        assert len(tasks2) == 1
        assert len(repository.get_all()) == 1

    def test_get_by_id_existing(self, repository, sample_task):
        """Debe encontrar una tarea existente por ID."""
        created_task = repository.create(sample_task)
        
        assert created_task.id is not None
        found_task = repository.get_by_id(created_task.id)
        
        assert found_task is not None
        assert found_task.id == created_task.id
        assert found_task.title == created_task.title
        assert found_task.description == created_task.description
        assert found_task.completed == created_task.completed

    def test_get_by_id_not_found(self, repository):
        """Debe retornar None para ID inexistente."""
        found_task = repository.get_by_id(999)
        
        assert found_task is None

    # Tests de actualización
    def test_update_existing_task(self, repository, sample_task):
        """Debe actualizar una tarea existente correctamente."""
        created_task = repository.create(sample_task)
        
        updated_task = Task(
            title="Título actualizado",
            description="Descripción actualizada",
            completed=True
        )
        
        assert created_task.id is not None
        result = repository.update(created_task.id, updated_task)
        
        assert result is not None
        assert result.id == created_task.id
        assert result.title == "Título actualizado"
        assert result.description == "Descripción actualizada"
        assert result.completed is True
        
        # Verificar que el cambio se reflejó en el repositorio
        from_repo = repository.get_by_id(created_task.id)
        assert from_repo.title == "Título actualizado"
        assert from_repo.completed is True

    def test_update_not_found(self, repository):
        """Debe retornar None al intentar actualizar tarea inexistente."""
        task = Task(title="No existe", description="Test")
        
        result = repository.update(999, task)
        
        assert result is None

    def test_update_preserves_id(self, repository):
        """Debe preservar el ID original al actualizar."""
        original_task = repository.create(Task(title="Original"))
        original_id = original_task.id
        
        updated_task = Task(title="Actualizada", id=999)  # ID diferente
        
        assert original_id is not None
        result = repository.update(original_id, updated_task)
        
        assert result is not None
        assert result.id == original_id  # Debe mantener el ID original
        assert result.title == "Actualizada"

    # Tests de eliminación
    def test_delete_existing_task(self, repository, sample_task):
        """Debe eliminar una tarea existente correctamente."""
        created_task = repository.create(sample_task)
        
        assert created_task.id is not None
        result = repository.delete(created_task.id)
        
        assert result is True
        assert repository.get_by_id(created_task.id) is None
        assert len(repository.get_all()) == 0

    def test_delete_not_found(self, repository):
        """Debe retornar False al intentar eliminar tarea inexistente."""
        result = repository.delete(999)
        
        assert result is False

    # Tests específicos de MemoryRepository
    def test_memory_isolation(self):
        """Debe mantener aislamiento entre diferentes instancias."""
        repo1 = MemoryTaskRepository()
        repo2 = MemoryTaskRepository()
        
        task1 = Task(title="Repo 1")
        task2 = Task(title="Repo 2")
        
        created1 = repo1.create(task1)
        created2 = repo2.create(task2)
        
        # Cada repositorio debe tener solo su tarea
        assert len(repo1.get_all()) == 1
        assert len(repo2.get_all()) == 1
        assert repo1.get_all()[0].title == "Repo 1"
        assert repo2.get_all()[0].title == "Repo 2"
        
        # IDs deben empezar desde 1 en cada instancia
        assert created1.id == 1
        assert created2.id == 1

    def test_id_increment_sequence(self, repository):
        """Debe mantener secuencia correcta de IDs incluso después de eliminaciones."""
        task1 = repository.create(Task(title="Tarea 1"))
        task2 = repository.create(Task(title="Tarea 2"))
        task3 = repository.create(Task(title="Tarea 3"))
        
        # Eliminar la tarea del medio
        assert task2.id is not None
        repository.delete(task2.id)
        
        # Crear nueva tarea debe continuar la secuencia
        task4 = repository.create(Task(title="Tarea 4"))
        
        assert task1.id == 1
        assert task3.id == 3
        assert task4.id == 4  # Debe continuar la secuencia, no reutilizar el 2

    def test_task_independence(self, repository):
        """Debe mantener independencia entre objetos Task."""
        original_task = Task(title="Original", description="Descripción original")
        created_task = repository.create(original_task)
        
        # Modificar el objeto original no debe afectar el almacenado
        original_task.title = "Modificado externamente"
        original_task.completed = True
        
        assert created_task.id is not None
        stored_task = repository.get_by_id(created_task.id)
        
        assert stored_task.title == "Original"  # No debe haber cambiado
        assert stored_task.completed is False  # No debe haber cambiado

    def test_multiple_operations_workflow(self, repository):
        """Debe manejar correctamente un flujo completo de operaciones."""
        # Crear múltiples tareas
        task1 = repository.create(Task(title="Tarea 1"))
        task2 = repository.create(Task(title="Tarea 2"))
        task3 = repository.create(Task(title="Tarea 3"))
        
        # Verificar estado inicial
        assert len(repository.get_all()) == 3
        
        # Actualizar una tarea
        assert task2.id is not None
        updated_task = Task(title="Tarea 2 Actualizada", completed=True)
        repository.update(task2.id, updated_task)
        
        # Eliminar una tarea
        assert task1.id is not None
        repository.delete(task1.id)
        
        # Crear una nueva tarea
        task4 = repository.create(Task(title="Tarea 4"))
        
        # Verificar estado final
        final_tasks = repository.get_all()
        assert len(final_tasks) == 3
        
        # Verificar que task1 no existe
        assert repository.get_by_id(task1.id) is None
        
        # Verificar que task2 se actualizó
        found_task2 = repository.get_by_id(task2.id)
        assert found_task2.title == "Tarea 2 Actualizada"
        assert found_task2.completed is True
        
        # Verificar que task3 sigue igual
        assert task3.id is not None
        found_task3 = repository.get_by_id(task3.id)
        assert found_task3.title == "Tarea 3"
        
        # Verificar que task4 se creó con ID correcto
        assert task4.id == 4