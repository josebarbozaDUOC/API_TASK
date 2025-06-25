# backend/tests/repositories/test_sqlite_repository.py

"""
Pruebas unitarias para SqliteTaskRepository.

Este módulo contiene pruebas específicas para la implementación de SqliteTaskRepository,
validando que todas las operaciones CRUD funcionen correctamente con SQLite y que
mantenga la persistencia de datos adecuadamente.

Tests implementados:
- test_create_task: Creación básica de tareas
- test_create_task_assigns_auto_id: Asignación automática de ID incremental
- test_get_all_empty: Obtener lista vacía inicial
- test_get_all_with_tasks: Obtener todas las tareas creadas
- test_get_all_maintains_order: Verificar orden por ID ascendente
- test_get_by_id_existing: Obtener tarea existente por ID
- test_get_by_id_not_found: Obtener tarea inexistente (retorna None)
- test_update_existing_task: Actualizar tarea existente con persistencia
- test_update_not_found: Actualizar tarea inexistente (retorna None)
- test_delete_existing_task: Eliminar tarea existente correctamente
- test_delete_not_found: Eliminar tarea inexistente (retorna False)
- test_database_persistence: Persistencia entre diferentes instancias del repositorio
- test_datetime_precision: Preservación de precisión de microsegundos en fechas
- test_boolean_field_storage: Almacenamiento y recuperación correcta de booleanos
- test_null_description_handling: Manejo correcto de campos nulos
- test_database_initialization: Creación automática de tabla al instanciar

Configuración:
- Cada test usa una base de datos SQLite temporal completamente aislada
- Cleanup automático de archivos temporales (compatible con Windows)
- Fixtures específicas para casos que requieren BD inexistente inicialmente

Ejecución:
    python -m pytest tests/repositories/test_sqlite_repository.py -v
    python -m pytest tests/repositories/test_sqlite_repository.py --cov=app.repositories.sqlite_repository -v
    python -m pytest tests/repositories/test_sqlite_repository.py::TestSqliteTaskRepository::test_create_task -v
"""

import pytest
import tempfile
import os
from datetime import datetime
from src.repositories.task.sqlite_repository import SqliteTaskRepository
from src.models.task import Task

class TestSqliteTaskRepository:
    """Pruebas para la implementación SqliteTaskRepository."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Crea un archivo temporal para la base de datos de test."""
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)  # Cerramos inmediatamente el descriptor
        yield path
        # Cleanup más robusto para Windows
        try:
            if os.path.exists(path):
                os.unlink(path)
        except PermissionError:
            # En Windows, a veces SQLite mantiene el archivo abierto
            pass
    
    @pytest.fixture
    def repository(self, temp_db_path):
        """Crea una instancia de SqliteTaskRepository con BD temporal."""
        return SqliteTaskRepository(db_path=temp_db_path)  # Directamente usar la ruta
    
    @pytest.fixture
    def fresh_db_path(self):
        """Crea una ruta para BD que NO existe (para test de inicialización)."""
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        os.unlink(path)  # Eliminar el archivo, solo queremos la ruta
        yield path
        # Cleanup
        try:
            if os.path.exists(path):
                os.unlink(path)
        except PermissionError:
            pass
    
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
        
        assert task1.id is not None
        assert task2.id is not None
        assert task3.id is not None
        assert task2.id > task1.id
        assert task3.id > task2.id

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
        """Debe retornar las tareas ordenadas por ID."""
        repository.create(Task(title="Tarea A"))
        repository.create(Task(title="Tarea B"))
        repository.create(Task(title="Tarea C"))
        
        tasks = repository.get_all()
        
        assert len(tasks) == 3
        assert tasks[0].id < tasks[1].id < tasks[2].id
        assert tasks[0].title == "Tarea A"
        assert tasks[1].title == "Tarea B"
        assert tasks[2].title == "Tarea C"

    def test_get_by_id_existing(self, repository, sample_task):
        """Debe encontrar una tarea existente por ID."""
        created_task = repository.create(sample_task)
        
        assert created_task.id is not None  # Fix del type hint
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
        
        assert created_task.id is not None  # Fix del type hint
        result = repository.update(created_task.id, updated_task)
        
        assert result is not None
        assert result.id == created_task.id
        assert result.title == "Título actualizado"
        assert result.description == "Descripción actualizada"
        assert result.completed is True
        
        # Verificar que el cambio se persistió en la BD
        from_db = repository.get_by_id(created_task.id)
        assert from_db.title == "Título actualizado"
        assert from_db.completed is True

    def test_update_not_found(self, repository):
        """Debe retornar None al intentar actualizar tarea inexistente."""
        task = Task(title="No existe", description="Test")
        
        result = repository.update(999, task)
        
        assert result is None

    # Tests de eliminación
    def test_delete_existing_task(self, repository, sample_task):
        """Debe eliminar una tarea existente correctamente."""
        created_task = repository.create(sample_task)
        
        assert created_task.id is not None  # Fix del type hint
        result = repository.delete(created_task.id)
        
        assert result is True
        assert repository.get_by_id(created_task.id) is None

    def test_delete_not_found(self, repository):
        """Debe retornar False al intentar eliminar tarea inexistente."""
        result = repository.delete(999)
        
        assert result is False

    # Tests específicos de SQLite
    def test_database_persistence(self, temp_db_path):
        """Debe persistir datos entre diferentes instancias del repositorio."""
        # Crear tarea con primera instancia
        repo1 = SqliteTaskRepository(db_path=temp_db_path)
        task = Task(title="Tarea persistente", description="Test persistencia")
        created_task = repo1.create(task)
        
        assert created_task.id is not None  # Fix del type hint
        
        # Verificar con segunda instancia
        repo2 = SqliteTaskRepository(db_path=temp_db_path)
        found_task = repo2.get_by_id(created_task.id)
        
        assert found_task is not None
        assert found_task.title == "Tarea persistente"
        assert found_task.description == "Test persistencia"

    def test_datetime_precision(self, repository):
        """Debe preservar la precisión de microsegundos en fechas."""
        precise_datetime = datetime(2025, 1, 1, 12, 0, 0, 123456)
        task = Task(title="Precisión temporal", created_at=precise_datetime)
        
        created_task = repository.create(task)
        assert created_task.id is not None  # Fix del type hint
        found_task = repository.get_by_id(created_task.id)
        
        assert found_task.created_at == precise_datetime

    def test_boolean_field_storage(self, repository):
        """Debe almacenar y recuperar correctamente los campos booleanos."""
        completed_task = Task(title="Tarea completada", completed=True)
        incomplete_task = Task(title="Tarea incompleta", completed=False)
        
        created_completed = repository.create(completed_task)
        created_incomplete = repository.create(incomplete_task)
        
        assert created_completed.id is not None  # Fix del type hint
        assert created_incomplete.id is not None  # Fix del type hint
        
        found_completed = repository.get_by_id(created_completed.id)
        found_incomplete = repository.get_by_id(created_incomplete.id)
        
        assert found_completed.completed is True
        assert found_incomplete.completed is False

    def test_null_description_handling(self, repository):
        """Debe manejar correctamente descripciones nulas."""
        task_with_null_desc = Task(title="Sin descripción", description=None)
        
        created_task = repository.create(task_with_null_desc)
        assert created_task.id is not None  # Fix del type hint
        found_task = repository.get_by_id(created_task.id)
        
        assert found_task.description is None

    def test_database_initialization(self, fresh_db_path):
        """Debe crear automáticamente la tabla al inicializar el repositorio."""
        # Verificar que el archivo no existe inicialmente
        assert not os.path.exists(fresh_db_path)
        
        # Crear repositorio (debería crear la BD y tabla)
        repository = SqliteTaskRepository(db_path=fresh_db_path)
        
        # Verificar que la base de datos se creó
        assert os.path.exists(fresh_db_path)
        
        # Verificar que podemos crear tareas (tabla existe y funciona)
        task = Task(title="Test inicialización BD")
        created_task = repository.create(task)
        assert created_task.id is not None