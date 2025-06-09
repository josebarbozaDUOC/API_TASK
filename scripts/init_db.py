# scripts/init_db.py

"""
Script de inicialización de base de datos.

Prepara el entorno de base de datos para el proyecto:
- Crea el directorio storage/ si no existe
- Opcionalmente puede poblar la BD con datos de ejemplo

Uso:
   python scripts/init_db.py
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.repositories.task.sqlite_repository import SqliteTaskRepository
from app.models.task import Task

def init_database():
    """Inicializa la BD con datos de ejemplo"""
    # Asegurarse de que existe el directorio storage
    os.makedirs('storage', exist_ok=True)
    
    # Crear repositorio (esto crea la tabla)
    repo = SqliteTaskRepository()
    
    # Agregar tareas de ejemplo
    sample_tasks = [
        Task(title="Configurar proyecto", description="Setup inicial con FastAPI"),
        Task(title="Implementar CRUD", description="Endpoints básicos"),
        Task(title="Agregar tests", description="Coverage > 80%"),
    ]
    
    for task in sample_tasks:
        repo.create(task)
    
    print("✅ Base de datos inicializada con datos de ejemplo")
    print(f"📁 Ubicación: {repo.db_path}")
    print(f"📊 Tareas creadas: {len(repo.get_all())}")

if __name__ == "__main__":
    init_database()