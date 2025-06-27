# backend/tests/repositories/test_repository_factory.py

"""
Tests para el factory de repositorios.

Este módulo valida el comportamiento del RepositoryFactory, que es responsable
de crear instancias de repositorios según el tipo especificado o la configuración
del entorno.

Los tests verifican:
- Creación correcta de cada tipo de repositorio (memory, sqlite, postgres, mysql)
- Manejo de alias (postgresql -> postgres)
- Validación de tipos inválidos
- Comportamiento case-insensitive
- Integración con configuración del entorno
- Modo testing vs otros modos

Nota: Los tests de repositorios que requieren conexión a BD (PostgreSQL, MySQL)
utilizan mocks para evitar dependencias externas y hacer los tests más rápidos
y confiables.

Ejecución:
   python -m pytest tests/repositories/test_repository_factory.py -v
   python -m pytest tests/repositories/test_repository_factory.py::TestRepositoryFactory::test_create_memory_repository -v
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
from src.repositories.task.repository_factory import RepositoryFactory
from src.repositories.task.memory_repository import MemoryTaskRepository
from src.repositories.task.sqlite_repository import SqliteTaskRepository
from src.repositories.task.postgresql_repository import PostgresqlTaskRepository
from src.repositories.task.mysql_repository import MysqlTaskRepository


class TestRepositoryFactory:
   """Tests para RepositoryFactory."""
   
   def test_create_memory_repository(self):
       """Debe crear repositorio de memoria."""
       repo = RepositoryFactory.create("memory")
       assert isinstance(repo, MemoryTaskRepository)
   
   def test_create_sqlite_repository(self):
       """Debe crear repositorio SQLite."""
       repo = RepositoryFactory.create("sqlite")
       assert isinstance(repo, SqliteTaskRepository)
   
   @patch('src.repositories.task.postgresql_repository.PostgresqlTaskRepository.__init__')
   def test_create_postgresql_repository(self, mock_init):
       """Debe crear repositorio PostgreSQL."""
       # Mock del __init__ para evitar conexión real
       mock_init.return_value = None
       
       repo = RepositoryFactory.create("postgres")
       assert isinstance(repo, PostgresqlTaskRepository)
       mock_init.assert_called_once()
   
   @patch('src.repositories.task.postgresql_repository.PostgresqlTaskRepository.__init__')
   def test_create_postgresql_with_alias(self, mock_init):
       """Debe aceptar 'postgresql' como alias de 'postgres'."""
       # Mock del __init__ para evitar conexión real
       mock_init.return_value = None
       
       repo = RepositoryFactory.create("postgresql")
       assert isinstance(repo, PostgresqlTaskRepository)
       mock_init.assert_called_once()
   
   @patch('src.repositories.task.mysql_repository.MysqlTaskRepository.__init__')
   def test_create_mysql_repository(self, mock_init):
       """Debe crear repositorio MySQL."""
       # Mock del __init__ para evitar conexión real
       mock_init.return_value = None
       
       repo = RepositoryFactory.create("mysql")
       assert isinstance(repo, MysqlTaskRepository)
       mock_init.assert_called_once()
   
   def test_invalid_repository_type(self):
       """Debe lanzar error con tipo inválido."""
       with pytest.raises(ValueError) as exc_info:
           RepositoryFactory.create("mongodb")
       
       error_msg = str(exc_info.value)
       assert "not supported" in error_msg
       assert "Available types:" in error_msg
       # Verificar que lista los tipos disponibles
       assert "memory" in error_msg
       assert "sqlite" in error_msg
       assert "postgres" in error_msg
       assert "mysql" in error_msg
   
   def test_case_insensitive(self):
       """Debe ser insensible a mayúsculas."""
       repo1 = RepositoryFactory.create("MEMORY")
       repo2 = RepositoryFactory.create("Memory")
       repo3 = RepositoryFactory.create("memory")
       
       assert all(isinstance(r, MemoryTaskRepository) for r in [repo1, repo2, repo3])
   
   @patch('src.repositories.task.repository_factory.settings')
   def test_create_from_settings(self, mock_settings):
       """Debe usar configuración cuando no se especifica tipo."""
       # Configurar mock
       mock_settings.repository_type = "memory"
       mock_settings.environment = "development"
       mock_settings.test_repository_type = "sqlite"  # No debería usarse
       
       repo = RepositoryFactory.create()
       assert isinstance(repo, MemoryTaskRepository)
   
   @patch('src.repositories.task.repository_factory.settings')
   def test_create_from_test_settings(self, mock_settings):
       """Debe usar configuración de test en ambiente TESTING."""
       # Configurar mock
       mock_settings.repository_type = "postgres"  # No debería usarse
       mock_settings.test_repository_type = "memory"
       mock_settings.environment = "TESTING"
       
       repo = RepositoryFactory.create()
       assert isinstance(repo, MemoryTaskRepository)
   
   def test_get_available_types(self):
       """Debe retornar todos los tipos disponibles."""
       types = RepositoryFactory.get_available_types()
       
       # Verificar que contiene todos los tipos esperados
       assert isinstance(types, list)
       assert len(types) >= 5  # Al menos 5 tipos (incluyendo alias)
       assert "memory" in types
       assert "sqlite" in types
       assert "postgres" in types
       assert "postgresql" in types
       assert "mysql" in types
   
   @patch('src.repositories.task.repository_factory.settings')
   def test_environment_case_insensitive(self, mock_settings):
       """El ambiente debe ser case-insensitive (TESTING, testing, Testing)."""
       mock_settings.repository_type = "sqlite"
       mock_settings.test_repository_type = "memory"
       
       # Probar diferentes variaciones de "testing"
       for env in ["TESTING", "testing", "Testing", "TeStInG"]:
           mock_settings.environment = env
           repo = RepositoryFactory.create()
           assert isinstance(repo, MemoryTaskRepository), f"Failed for environment: {env}"