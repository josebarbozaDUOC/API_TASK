# backend/src/repositories/task/mysql_repository.py

"""
Repositorio MySQL para Task usando SQLAlchemy.

Implementa la interfaz TaskRepository usando SQLAlchemy ORM
con MySQL como backend de base de datos.

Incluye reintentos de conexión para manejar el caso cuando MySQL
aún no está listo durante el inicio de contenedores Docker.

Referencias:
- https://docs.sqlalchemy.org/en/20/dialects/mysql.html
- https://github.com/PyMySQL/PyMySQL
"""

from typing import List, Optional
from contextlib import contextmanager
import time
from sqlalchemy import Engine, text
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from src.models.task import Task
from src.models.task_orm import TaskORM
from src.repositories.task.base_repository import TaskRepository
from src.database.base import Base, get_engine, get_session_factory
from src.config.settings import settings
from loguru import logger


class MysqlTaskRepository(TaskRepository):
    """Implementación que guarda las tareas en MySQL usando SQLAlchemy."""
    
    def __init__(self, connection_url: Optional[str] = None):
        # Usar URL proporcionada o construir desde settings
        if connection_url:
            self.database_url = connection_url
        else:
            self.database_url = settings.mysql_url
        
        # Inicializar engine y sesiones con reintentos
        self.engine = self._create_engine_with_retry()
        Base.metadata.create_all(self.engine)
        self.SessionLocal = get_session_factory(self.engine)
    
    def _create_engine_with_retry(self, max_retries: int = 30, delay: int = 2) -> Engine:
        """
        Crea el engine con reintentos para esperar que MySQL esté listo.
        Necesario cuando el backend inicia antes que MySQL termine su inicialización en Docker Compose.
        """
        for attempt in range(max_retries):
            try:
                engine = get_engine(self.database_url)
                # Probar la conexión
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                logger.info(f"Connected to MySQL on attempt {attempt + 1}")
                return engine
            except OperationalError as e:
                if attempt < max_retries - 1:
                    logger.warning(f"MySQL not ready, retrying in {delay}s... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(delay)
                else:
                    logger.error("Failed to connect to MySQL after all retries")
                    raise
        
        # Esta línea nunca se ejecutará, pero ayuda con el type checker
        raise RuntimeError("Failed to create engine")
    
    @contextmanager
    def _get_session(self):
        """Context manager para manejar sesiones automáticamente."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
    
    def create(self, task: Task) -> Task:
        with self._get_session() as session:
            # Convertir Task a TaskORM
            task_orm = TaskORM.from_domain_model(task)
            
            # Guardar en BD
            session.add(task_orm)
            session.flush()  # Para obtener el ID generado
            
            # Retornar con ID actualizado
            return task_orm.to_domain_model()
    
    def get_all(self) -> List[Task]:
        with self._get_session() as session:
            # Query todas las tareas
            tasks_orm = session.query(TaskORM).order_by(TaskORM.id).all()
            
            # Convertir a modelo de dominio
            return [task_orm.to_domain_model() for task_orm in tasks_orm]
    
    def get_by_id(self, task_id: int) -> Optional[Task]:
        with self._get_session() as session:
            # Buscar por ID
            task_orm = session.query(TaskORM).filter(TaskORM.id == task_id).first()
            
            # Retornar None o Task convertida
            return task_orm.to_domain_model() if task_orm else None
    
    def update(self, task_id: int, task: Task) -> Optional[Task]:
        with self._get_session() as session:
            # Buscar tarea existente
            task_orm = session.query(TaskORM).filter(TaskORM.id == task_id).first()
            
            if not task_orm:
                return None
            
            # Actualizar campos
            task_orm.title = task.title
            task_orm.description = task.description
            task_orm.completed = task.completed
            
            # Retornar tarea actualizada
            return task_orm.to_domain_model()
    
    def delete(self, task_id: int) -> bool:
        with self._get_session() as session:
            # Buscar y eliminar
            task_orm = session.query(TaskORM).filter(TaskORM.id == task_id).first()
            
            if not task_orm:
                return False
            
            session.delete(task_orm)
            return True