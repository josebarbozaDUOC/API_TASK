## Estructura de Archivos

```
API_task/
├── backend/
│   ├── src/
│   │   ├── __init__.py                   # Inicializaciones 
│   │   ├── main.py                       # Punto de entrada
│   │   ├── config/
│   │   │   ├── dependencies.py           # Inyección de dependencias
│   │   │   └── settings.py               # Configuración centralizada
│   │   ├── database/
│   │   │   ├── base.py                   # Configuración SQLAlchemy ORM
│   │   ├── logging/
│   │   │   └── logging_system.py         # Configura logging (loguru)
│   │   ├── middleware/
│   │   │   └── error_handler.py          # Manejador de errores
│   │   ├── models/
│   │   │   └── task.py                   # Entidades de dominio
│   │   │   └── task_orm.py               # Modelo ORM para Task
│   │   ├── repositories/
│   │   │   └── task/
│   │   │       ├── repository_factory.py     # Factory pattern para repositorios
│   │   │       ├── base_repository.py        # Interface TaskRepository
│   │   │       ├── memory_repository.py      # MemoryTaskRepository
│   │   │       └── sqlite_repository.py      # SqliteTaskRepository
│   │   │       └── postgresql_repository.py  # PostgresqlTaskRepository
│   │   │       └── mysql_repository.py       # MysqlTaskRepository
│   │   ├── routes/
│   │   │   ├── health.py                 # Health check
│   │   │   └── tasks.py                  # Endpoints de tareas
│   │   ├── schemas/
│   │   │   └── task.py                   # Validación entrada/salida
│   │   └── services/
│   │       └── task_service.py           # Lógica de negocio
│   │ 
│   ├── tests/
│   │   ├── integration/                  # Test de Endpoints
│   │   │   ├── test_health_endpoints.py
│   │   │   └── test_task_endpoints.py 
│   │   ├── repositories/                 # Test de Repositorios
│   │   │   ├── test_repository_factory.py
│   │   │   ├── test_memory_repository.py
│   │   │   └── test_sqlite_repository.py
│   │   │   └── test_postgresql_repository.py
│   │   │   └── test_mysql_repository.py
│   │   ├── conftest.py                   # Configuraciones de test
│   │   ├── test_models.py                # Test de model Task
│   │   ├── test_schemas.py               # Test de esquema Pydantic
│   │   └── test_services.py              # Test de task_service
│   │
│   ├── Dockerfile                        # Imagen Docker de backend con healthcheck
│   ├── Dockerfile.test                   # Imagen para ejecutar test en Docker
│   ├── requirements.txt                  # Dependencias Python
│   └── coverage.svg                      # % Cobertura de los tests
│
├── storage/                              # Base de datos compartidas
│   ├── logs.db
│   └── tasks.db
│
├── docs/                                 # Documentación del proyecto
│   ├── quick_start.txt                   # Guía rápida
│   ├── ROADMAP.md                        # Sprints & Stories
│   └── solid-principles.md               # Guía principios SOLID
│
├── .env                                  # Variables de entorno (local)
├── .env.example                          # Configuración por defecto
├── .gitignore
├── docker-compose.yml                    # Orquestador de servicios
├── docker-compose.test.yml               # SOLO TEST
└── README.md
```