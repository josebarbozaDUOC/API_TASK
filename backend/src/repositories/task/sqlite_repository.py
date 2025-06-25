# backend/src/repositories/task/sqlite_repository.py

"""
Repositorio SQLite para Task usando SQLAlchemy.

Implementa la interfaz TaskRepository usando SQLAlchemy ORM
en lugar de SQL crudo para mejor mantenibilidad.

Referencias:
- https://docs.sqlalchemy.org/en/20/orm/session_basics.html
"""

from typing import List, Optional
from contextlib import contextmanager
from sqlalchemy.orm import Session
from src.models.task import Task
from src.models.task_orm import TaskORM
from src.repositories.task.base_repository import TaskRepository
from src.database.base import Base, get_engine, get_session_factory
from src.config.settings import settings


class SqliteTaskRepository(TaskRepository):
    """Implementación que guarda las tareas en SQLite usando SQLAlchemy."""
    
    def __init__(self, db_path: str = settings.task_db_absolute_path):
        # Crear URL de conexión SQLite
        self.database_url = f"sqlite:///{db_path}"
        
        # Inicializar engine y sesiones
        self.engine = get_engine(self.database_url)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = get_session_factory(self.engine)
    
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