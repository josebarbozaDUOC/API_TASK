# backend/app/models/task_orm.py

"""
Modelo ORM para Task.

Define la estructura de la tabla 'tasks' usando SQLAlchemy.
Incluye métodos para convertir entre el modelo ORM y el modelo de dominio.

Referencias:
- https://docs.sqlalchemy.org/en/20/orm/quickstart.html
- https://docs.sqlalchemy.org/en/20/orm/mapping_styles.html
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.database.base import Base
from app.models.task import Task
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from datetime import datetime

class TaskORM(Base):
    """Modelo SQLAlchemy para la tabla tasks."""
    
    __tablename__ = "tasks"

    # Definición de columnas con tipos correctos para Pylance
    id:         Mapped[Optional[int]]   = mapped_column(Integer, primary_key=True, index=True)
    title:      Mapped[str]             = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]]  = mapped_column(String(500), default="")
    completed:  Mapped[bool]            = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime]        = mapped_column(DateTime, nullable=False)
   
    def to_domain_model(self) -> Task:
        """Convierte el modelo ORM a modelo de dominio Task."""
        return Task(
            id=self.id,
            title=self.title,
            description=self.description,
            completed=self.completed,
            created_at=self.created_at
        )
    
    @staticmethod
    def from_domain_model(task: Task) -> 'TaskORM':
        """Convierte el modelo de dominio Task a modelo ORM."""
        return TaskORM(
            id=task.id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            created_at=task.created_at
        )