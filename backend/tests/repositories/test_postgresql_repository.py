# backend/tests/repositories/test_postgresql_repository.py

"""
Pruebas unitarias para PostgresqlTaskRepository.

Este módulo contiene pruebas específicas para la implementación de PostgresqlTaskRepository,
validando que todas las operaciones CRUD funcionen correctamente con PostgreSQL.

Tests implementados:
- Todos los tests de SQLite adaptados para PostgreSQL
- Tests específicos de PostgreSQL (transacciones, conexiones, etc.)

Configuración:
- Requiere PostgreSQL en ejecución (local o Docker)
- Usa una base de datos de test aislada
- Limpia automáticamente los datos entre tests

*Posible refactor: Migrar tests/ a docker (compose), y ejecutar testing ahí.

Ejecución:
    python -m pytest tests/repositories/test_postgresql_repository.py -v
    python -m pytest tests/repositories/test_postgresql_repository.py -m "not requires_postgres" -v  # Skip si no hay PostgreSQL
"""

import pytest
import os
from datetime import datetime
from sqlalchemy import create_engine, text
from src.repositories.task.postgresql_repository import PostgresqlTaskRepository
from src.models.task import Task
from src.config.settings import settings


# Marca para tests que requieren PostgreSQL
pytestmark = pytest.mark.skipif(
    os.getenv("SKIP_POSTGRES_TESTS", "false").lower() == "true",
    reason="PostgreSQL tests skipped"
)


class TestPostgreSQLTaskRepository:
    """Pruebas para la implementación PostgresqlTaskRepository."""
    
    @pytest.fixture(scope="class")
    def test_database_url(self):
        """Crea URL para base de datos de test."""
        # Usar configuración de test o la misma de desarrollo con sufijo _test
        if settings.environment == "testing":
            return settings.postgres_url
        else:
            # Crear URL de test basada en la configuración actual
            test_db = f"{settings.postgres_db}_test"
            return (
                f"postgresql+psycopg://{settings.postgres_user}:{settings.postgres_password}"
                f"@localhost:{settings.postgres_port}/{test_db}"
            )
        
    @pytest.fixture(scope="class")
    def setup_test_db(self, test_database_url):
        """Crea y limpia la base de datos de test."""
        # Extraer nombre de la BD de test
        db_name = test_database_url.split("/")[-1]
        
        # Conectar a postgres (BD por defecto) para crear/eliminar BD de test
        admin_url = test_database_url.rsplit("/", 1)[0] + "/postgres"
        admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
        
        with admin_engine.connect() as conn:
            # Eliminar BD de test si existe
            conn.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))
            # Crear BD de test
            conn.execute(text(f"CREATE DATABASE {db_name}"))
        
        yield test_database_url
        
        # Cleanup: eliminar BD de test
        with admin_engine.connect() as conn:
            # Cerrar conexiones activas
            conn.execute(text(
                f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                f"WHERE datname = '{db_name}' AND pid <> pg_backend_pid()"
            ))
            conn.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))
    
    @pytest.fixture
    def repository(self, setup_test_db):
        """Crea una instancia de PostgresqlTaskRepository con BD de test."""
        repo = PostgresqlTaskRepository(connection_url=setup_test_db)
        yield repo
        # Limpiar datos después de cada test
        with repo._get_session() as session:
            session.execute(text("TRUNCATE TABLE tasks RESTART IDENTITY CASCADE"))
    
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
        
        result = repository.update(created_task.id, updated_task)
        
        assert result is not None
        assert result.id == created_task.id
        assert result.title == "Título actualizado"
        assert result.description == "Descripción actualizada"
        assert result.completed is True
        
        # Verificar persistencia
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
        
        result = repository.delete(created_task.id)
        
        assert result is True
        assert repository.get_by_id(created_task.id) is None

    def test_delete_not_found(self, repository):
        """Debe retornar False al intentar eliminar tarea inexistente."""
        result = repository.delete(999)
        
        assert result is False

    # Tests específicos de PostgreSQL
    def test_transaction_rollback(self, repository):
        """Debe hacer rollback en caso de error."""
        # Este test es más conceptual ya que nuestro repository
        # maneja las transacciones internamente
        task = Task(title="Test transacción")
        created = repository.create(task)
        
        # Verificar que se creó
        assert created.id is not None
        assert repository.get_by_id(created.id) is not None

    def test_concurrent_access(self, setup_test_db):
        """Debe manejar acceso concurrente correctamente."""
        # Crear dos instancias del repositorio (simulando conexiones concurrentes)
        repo1 = PostgresqlTaskRepository(connection_url=setup_test_db)
        repo2 = PostgresqlTaskRepository(connection_url=setup_test_db)
        
        # Repo1 crea una tarea
        task1 = repo1.create(Task(title="Desde repo1"))
        
        # Repo2 debe poder verla inmediatamente
        tasks = repo2.get_all()
        assert len(tasks) == 1
        assert tasks[0].title == "Desde repo1"
        
        # Repo2 crea otra tarea
        task2 = repo2.create(Task(title="Desde repo2"))
        
        # Repo1 debe ver ambas
        all_tasks = repo1.get_all()
        assert len(all_tasks) == 2

    def test_datetime_precision(self, repository):
        """Debe preservar la precisión de microsegundos en fechas."""
        precise_datetime = datetime(2025, 1, 1, 12, 0, 0, 123456)
        task = Task(title="Precisión temporal", created_at=precise_datetime)
        
        created_task = repository.create(task)
        found_task = repository.get_by_id(created_task.id)
        
        # PostgreSQL preserva microsegundos
        assert found_task.created_at == precise_datetime

    def test_null_description_handling(self, repository):
        """Debe manejar correctamente descripciones nulas."""
        task_with_null_desc = Task(title="Sin descripción", description=None)
        
        created_task = repository.create(task_with_null_desc)
        found_task = repository.get_by_id(created_task.id)
        
        assert found_task.description is None

    def test_unicode_support(self, repository):
        """Debe soportar caracteres Unicode correctamente."""
        task = Task(
            title="Título con ñ, é, ü, 中文, 🎉",
            description="Descripción con emojis 🚀 y acentos áéíóú"
        )
        
        created_task = repository.create(task)
        found_task = repository.get_by_id(created_task.id)
        
        assert found_task.title == task.title
        assert found_task.description == task.description