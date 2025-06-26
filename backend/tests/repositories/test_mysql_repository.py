# backend/tests/repositories/test_mysql_repository.py

"""
Pruebas unitarias para MysqlTaskRepository.

Este módulo contiene pruebas específicas para la implementación de MysqlTaskRepository,
validando que todas las operaciones CRUD funcionen correctamente con MySQL.

Configuración:
- Requiere MySQL en ejecución (local o Docker)
- Usa una base de datos de test aislada
- Limpia automáticamente los datos entre tests

Ejecución:
    python -m pytest tests/repositories/test_mysql_repository.py -v
"""

import pytest
import os
from datetime import datetime
from sqlalchemy import create_engine, text
from src.repositories.task.mysql_repository import MysqlTaskRepository
from src.models.task import Task
from src.config.settings import settings


# Marca para tests que requieren MySQL
pytestmark = pytest.mark.skipif(
    os.getenv("SKIP_MYSQL_TESTS", "false").lower() == "true",
    reason="MySQL tests skipped"
)


class TestMySQLTaskRepository:
    @pytest.fixture(scope="class")
    def test_database_url(self):
        """Construye la URL de conexión para la base de datos de test."""
        test_db = f"{settings.mysql_database}_test"
        return (
            f"mysql+pymysql://{settings.mysql_user}:{settings.mysql_password}"
            f"@localhost:{settings.mysql_local_port}/{test_db}"
        )

    @pytest.fixture(scope="class")
    def setup_test_db(self, test_database_url):
        """Crea la base de datos de test antes de ejecutar las pruebas y la elimina al finalizar."""
        # Para crear la DB necesitamos usar root
        db_name = test_database_url.split("/")[-1]
        
        # URL con usuario root para crear la base de datos
        root_url = (
            f"mysql+pymysql://root:{settings.mysql_root_password}"
            f"@localhost:{settings.mysql_local_port}/mysql"
        )
        
        root_engine = create_engine(root_url)
        # Intentar conectar con reintentos
        max_retries = 5
        for attempt in range(max_retries):
            try:
                root_engine = create_engine(root_url)
                with root_engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2)
                else:
                    pytest.skip(f"MySQL not available: {e}")

        # Crear base de datos de test y dar permisos
        with root_engine.connect() as conn:
            # Fuera de transacción para operaciones DDL
            conn.execute(text("COMMIT"))
            conn.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))
            conn.execute(text(f"CREATE DATABASE {db_name}"))
            # Dar permisos al usuario
            conn.execute(text(
                f"GRANT ALL PRIVILEGES ON {db_name}.* TO '{settings.mysql_user}'@'%'"
            ))
            conn.execute(text("FLUSH PRIVILEGES"))

        yield test_database_url

        # Limpiar después de todos los tests
        with root_engine.connect() as conn:
            conn.execute(text("COMMIT"))
            conn.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))

    @pytest.fixture
    def repository(self, setup_test_db):
        """Proporciona un repositorio limpio para cada test."""
        repo = MysqlTaskRepository(connection_url=setup_test_db)
        # Limpiar ANTES de cada test también
        with repo._get_session() as session:
            session.execute(text("DELETE FROM tasks"))
            # Resetear el auto_increment para que IDs empiecen en 1
            session.execute(text("ALTER TABLE tasks AUTO_INCREMENT = 1"))
            session.commit()
        yield repo
        # Limpiar después de cada test
        with repo._get_session() as session:
            session.execute(text("DELETE FROM tasks"))
            session.commit()

    @pytest.fixture
    def sample_task(self):
        """Crea una tarea de ejemplo para usar en las pruebas."""
        return Task(
            title="Tarea de prueba",
            description="Descripción de prueba",
            completed=False
        )

    def test_create_task(self, repository, sample_task):
        """Verifica que se pueda crear una tarea correctamente."""
        created = repository.create(sample_task)

        assert created.id is not None
        assert created.title == sample_task.title
        assert created.description == sample_task.description
        assert created.completed == sample_task.completed
        assert isinstance(created.created_at, datetime)

    def test_create_task_assigns_auto_id(self, repository):
        """Verifica que los IDs se asignen secuencialmente."""
        t1 = repository.create(Task(title="Primera"))
        t2 = repository.create(Task(title="Segunda"))
        t3 = repository.create(Task(title="Tercera"))

        assert t1.id == 1
        assert t2.id == 2
        assert t3.id == 3

    def test_get_all_empty(self, repository):
        """Verifica que get_all retorne lista vacía cuando no hay tareas."""
        assert repository.get_all() == []

    def test_get_all_with_tasks(self, repository):
        """Verifica que get_all retorne todas las tareas existentes."""
        t1 = repository.create(Task(title="Una"))
        t2 = repository.create(Task(title="Otra"))

        tasks = repository.get_all()
        assert len(tasks) == 2
        assert any(t.id == t1.id for t in tasks)
        assert any(t.id == t2.id for t in tasks)

    def test_get_all_order(self, repository):
        """Verifica que las tareas se retornen en orden de creación."""
        repository.create(Task(title="A"))
        repository.create(Task(title="B"))
        repository.create(Task(title="C"))

        tasks = repository.get_all()
        assert tasks[0].title == "A"
        assert tasks[1].title == "B"
        assert tasks[2].title == "C"

    def test_get_by_id_existing(self, repository, sample_task):
        """Verifica que se pueda obtener una tarea por su ID."""
        created = repository.create(sample_task)
        found = repository.get_by_id(created.id)

        assert found is not None
        assert found.title == sample_task.title

    def test_get_by_id_not_found(self, repository):
        """Verifica que get_by_id retorne None para ID inexistente."""
        assert repository.get_by_id(9999) is None

    def test_update_existing(self, repository, sample_task):
        """Verifica que se pueda actualizar una tarea existente."""
        created = repository.create(sample_task)
        updated_data = Task(title="Actualizada", description="Cambiada", completed=True)

        updated = repository.update(created.id, updated_data)

        assert updated.title == "Actualizada"
        assert updated.completed is True

    def test_update_not_found(self, repository):
        """Verifica que update retorne None para ID inexistente."""
        result = repository.update(9999, Task(title="Nada"))
        assert result is None

    def test_delete_existing(self, repository, sample_task):
        """Verifica que se pueda eliminar una tarea existente."""
        created = repository.create(sample_task)
        deleted = repository.delete(created.id)

        assert deleted is True
        assert repository.get_by_id(created.id) is None

    def test_delete_not_found(self, repository):
        """Verifica que delete retorne False para ID inexistente."""
        assert repository.delete(9999) is False

    def test_unicode_support(self, repository):
        """Verifica el soporte para caracteres Unicode y emojis."""
        task = Task(title="Tarea ñ, é, 🎉", description="Descripción 🚀")
        created = repository.create(task)
        found = repository.get_by_id(created.id)

        assert found.title == task.title
        assert found.description == task.description

    def test_null_description(self, repository):
        """Verifica que se puedan crear tareas sin descripción."""
        task = Task(title="Sin descripción", description=None)
        created = repository.create(task)
        found = repository.get_by_id(created.id)

        assert found.description is None

    def test_datetime_precision(self, repository):
        """Verifica el manejo de fechas con precisión de segundos."""
        # MySQL por defecto no guarda microsegundos a menos que se especifique
        # DATETIME(6) en la columna. Como estamos usando DATETIME sin precisión,
        # MySQL trunca los microsegundos
        dt = datetime(2025, 1, 1, 12, 0, 0, 123456)
        task = Task(title="Con precisión", created_at=dt)
        created = repository.create(task)
        found = repository.get_by_id(created.id)

        # MySQL trunca microsegundos por defecto
        expected_dt = dt.replace(microsecond=0)
        assert found.created_at == expected_dt