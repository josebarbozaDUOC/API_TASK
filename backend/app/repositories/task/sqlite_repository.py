# backend/app/repositories/task/sqlite_repository.py

"""
Repositorio SQLite solo para Task

Ejecuta consultas a DB de forma propia
"""

"""
*Refactor posible:
- Crear un archivo db_connection con el crud genérico sqlite, 
usando pandas como intermediario.
- O usar alguna ORM como SQLAlchemy, o SQLModel.

- Falta agregar logger para errores
"""

import sqlite3
from typing import List, Optional
from datetime import datetime
from app.models.task import Task
from app.repositories.task.base_repository import TaskRepository
from app.config.settings import settings


class SqliteTaskRepository(TaskRepository):
    """
    Implementación que guarda las tareas en SQLite.
    """
    def __init__(self, db_path: str = settings.task_db_absolute_path):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Crea la tabla de tareas si no existe"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    completed BOOLEAN NOT NULL DEFAULT 0,
                    created_at TIMESTAMP NOT NULL
                )
            ''')
            conn.commit()
    
    def _get_connection(self):
        """Retorna una conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Para acceder por nombre de columna
        return conn
    
    def _row_to_task(self, row) -> Task:
        """Convierte una fila de SQLite a objeto Task"""
        task = Task(
            title=row['title'],
            description=row['description'],
            id=row['id'],
            completed=bool(row['completed']),
            created_at=datetime.fromisoformat(row['created_at'])
        )
        return task
    
    def create(self, task: Task) -> Task:
        with self._get_connection() as conn:
            cursor = conn.execute(
                '''INSERT INTO tasks (title, description, completed, created_at) 
                   VALUES (?, ?, ?, ?)''',
                (task.title, task.description, task.completed, task.created_at.isoformat())
            )
            # Manejar el caso donde lastrowid podría ser None
            if cursor.lastrowid is not None:
                task.id = cursor.lastrowid
            conn.commit()
        return task
    
    def get_all(self) -> List[Task]:
        with self._get_connection() as conn:
            cursor = conn.execute('SELECT * FROM tasks ORDER BY id')
            return [self._row_to_task(row) for row in cursor.fetchall()]
    
    def get_by_id(self, task_id: int) -> Optional[Task]:
        with self._get_connection() as conn:
            cursor = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
            row = cursor.fetchone()
            return self._row_to_task(row) if row else None
    
    def update(self, task_id: int, task: Task) -> Optional[Task]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                '''UPDATE tasks 
                   SET title = ?, description = ?, completed = ?
                   WHERE id = ?''',
                (task.title, task.description, task.completed, task_id)
            )
            conn.commit()
            
            if cursor.rowcount > 0:
                task.id = task_id
                return task
            return None
    
    def delete(self, task_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
            conn.commit()
            return cursor.rowcount > 0