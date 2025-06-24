# API_TASK — Gestión de tareas con FastAPI
```
API REST moderna para gestión de tareas, construida con FastAPI.
Diseño modular, containerizada y lista para producción. 
Con separación clara de responsabilidades y diseño extensible.
```

## Stack Tecnológico
- **Python 3.13** - Lenguaje base
- **FastAPI** - Framework web async
- **Pydantic** - Validación y serialización
- **Uvicorn** - Servidor ASGI
- **SQLAlchemy** - ORM y manejo de BD
- **Loguru** - Logging estructurado
- **Docker** - Containerización
- **Pytest** - Testing framework

## Estado del Proyecto
**Actualmente**: Sprint 3 completo
- Docker implementado `LISTO`
- Configuración centralizada `LISTO`

**Siguiente**: Migración a SQLAlchemy y soporte multi-database


## Arquitectura del Sistema
```
API Request → Routes → Service → Repository → Models → Response
     ↓           ↓        ↓           ↓          ↓
  Validación  Endpoints Lógica   Abstracción Entidades
  (Schemas)            Negocio   (Interface)
```

## Estructura de Archivos
```
API_task/
├── backend/
│   ├── app/
│   │   ├── __init__.py                   # Inicializaciones 
│   │   ├── main.py                       # Punto de entrada
│   │   ├── config/
│   │   │   ├── dependencies.py           # Inyección de dependencias
│   │   │   └── settings.py               # Configuración centralizada
│   │   ├── logging/
│   │   │   └── logging_system.py         # Configura logging (loguru)
│   │   ├── middleware/
│   │   │   └── error_handler.py          # Manejador de errores
│   │   ├── models/
│   │   │   └── task.py                   # Entidades de dominio
│   │   ├── repositories/
│   │   │   └── task/
│   │   │       ├── base_repository.py    # Interface TaskRepository
│   │   │       ├── memory_repository.py  # MemoryTaskRepository
│   │   │       └── sqlite_repository.py  # SqliteTaskRepository
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
│   │   │   ├── test_memory_repository.py
│   │   │   └── test_sqlite_repository.py
│   │   ├── conftest.py                   # Configuraciones de test
│   │   ├── test_models.py                # Test de model Task
│   │   ├── test_schemas.py               # Test de esquema Pydantic
│   │   └── test_services.py              # Test de task_service
│   │
│   ├── .env                              # Variables de entorno (local)
│   ├── .env.example                      # Configuración por defecto
│   ├── Dockerfile                        # Imagen Docker de backend con healthcheck
│   ├── requirements.txt                  # Dependencias Python
│   └── coverage.svg                      # % Cobertura de los tests
│
├── storage/                              # Base de datos compartidas
│   ├── logs.db
│   └── tasks.db
│
├── docs/                                 # Documentación del proyecto
│   └── quick_start.txt                   # Guía rápida
│
├── docker-compose.yml                    # Orquestador de servicios
├── .gitignore
├── quick_start.txt
└── README.md
```


## Componentes Principales

### 0. Config (app/config/)
- settings.py: Configuración centralizada con Pydantic Settings. Lee de .env.example como fuente única de verdad.
- dependencies.py: Inyección de dependencias. Inicializa repositorios según configuración.
- Responsabilidad: Proveer configuración y dependencias a toda la aplicación.

### 1. Logging (app/logging/logging_system.py)
- Propósito: Sistema de logging centralizado y estructurado.
- SQLiteHandler personalizado para persistencia en BD
- Configuración automática con contexto (.bind()) 
- Responsabilidad: Capturar operaciones CRUD, errores y eventos del sistema con metadata estructurada.

### 2. Models (app/models/task.py)
- Propósito: Representan las entidades de negocio.
- class Task:
  - Propiedades: id, title, description, completed, created_at
  - Métodos: mark_complete(), to_dict()
- Responsabilidad: Definir la estructura y comportamiento de una tarea.

### 3. Schemas (app/schemas/task.py)
- Propósito: Validación y serialización de datos.
- TaskCreate    `# ← Datos que llegan (input)`
- TaskResponse  `# → Datos que salen (output)`  
- TaskUpdate    `# ← Datos para actualizar`
- Responsabilidad: Garantizar que los datos sean correctos antes de procesarlos.

### 4. Repositories (app/repositories/...)
- Propósito: Abstraer el acceso a datos detrás de una interfaz común.
  - base_repository.py: `Interfaz que define contrato implementado por los demás repositorios.`
  - memory_repository.py: `Implementa TaskRepository en memoria (lista). Útil para desarrollo rápido y testing.`
  - sqlite_repository.py: `Implementa TaskRepository usando SQLite nativo. Persistencia local sin dependencias externas.`
- Responsabilidad: Proveer operaciones CRUD sin exponer detalles del almacenamiento.

### 5. Services (app/services/task_service.py)
- Propósito: Lógica de negocio centralizada.
- class TaskService:
  - create_task(), get_all_tasks(), get_task_by_id()
  - update_task(), delete_task()
- Responsabilidad: Implementar las reglas de negocio.

### 6. Routes (app/routes/tasks.py)
- Propósito: Definir endpoints HTTP.
- GET    /api/v1/tasks      `# Listar todas`
- POST   /api/v1/tasks      `# Crear nueva`
- GET    /api/v1/tasks/{id} `# Obtener por ID`
- PUT    /api/v1/tasks/{id} `# Actualizar`
- DELETE /api/v1/tasks/{id} `# Eliminar`
- Responsabilidad: Manejar peticiones HTTP y delegar al service.

### 7. Middleware (app/middleware/error_handler.py)
- Propósito: Manejo centralizado de errores y excepciones.
- NotFoundError, ValidationError, InternalServerError
- Exception handlers automáticos
- Responsabilidad: Convertir excepciones de negocio a respuestas HTTP consistentes.

### 8. Main (app/main.py)
- Propósito: Configuración y arranque de la aplicación.
- Responsabilidad: Crear la app FastAPI, registrar routers, configurar middleware.


## Flujos de Datos

**Crear Tarea (POST /api/v1/tasks)**
1. Cliente envía: {"title": "Comprar pan"}
2. FastAPI valida el JSON contra TaskCreate schema
3. Router (tasks.py) recibe la petición válida
4. Service (task_service.py) ejecuta la lógica de negocio via repository
5. Model (Task) representa la entidad creada
6. Respuesta se serializa usando TaskResponse schema
7. Cliente recibe: {"id": 1, "title": "Comprar pan", "completed": false, ...}

**Error Handling**
- Tarea no encontrada → HTTP 404 (via NotFoundError)
- Datos inválidos → HTTP 422 (Pydantic automático)
- Errores internos → HTTP 500 (via middleware centralizado)


## Configuración y Ejecución

**Docker (Recomendado):**
```docker-compose up --build```

**Local:**
```
cd backend/
cp .env.example .env  # Configurar variables si es necesario
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**URLs importantes:**
- API: ```http://localhost:8000```
- Documentación: ```http://localhost:8000/docs```
- Health Check: ```http://localhost:8000/api/v1/health```


## Test

![coverage](coverage.svg)

**Test suite completo con pytest:**

✅ Tests unitarios (models, schemas, services)
✅ Tests de repositorios (memory, SQLite)
✅ Tests de integración (endpoints)
✅ Cobertura >90%

**Ejecutar tests:**
```
cd backend/
python -m pytest tests/ -v                                    # Tests básicos
python -m pytest tests/ --cov=app --cov-report=term-missing   # Con cobertura
python -m coverage_badge -o coverage.svg                      # Generar badge
```

## Testing Manual

**Via Documentación (Recomendado):**
- Ir a ```http://localhost:8000/docs```
- Probar endpoints interactivamente

**Via cURL:**
```
# Crear tarea
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Nueva tarea"}'

# Listar tareas
curl http://localhost:8000/api/v1/tasks
```


## Decisiones de Diseño

**¿Por qué FastAPI vs Flask/Django?**
- Validación automática con Pydantic
- Documentación auto-generada
- Type hints nativo
- Performance superior

**¿Por qué arquitectura de repositorios para cumplir con SOLID?**
- Problema inicial: TaskService manejaba directamente una lista en memoria (self.tasks: List[Task] = []), violando el principio de responsabilidad única - mezclaba lógica de negocio con almacenamiento.
- Opción 1: Trabajar directamente con listas → Simple, pero acopla la lógica al almacenamiento
- Opción 2: Crear un wrapper para listas → Encapsula más, pero sigue siendo específico
- Opción 3: Abstraer el repositorio e inyectarlo en el servicio → Desacople total entre lógica y almacenamiento
- **Decisión tomada**: Patrón Repository con inyección de dependencias. TaskService depende de una interfaz genérica, no de una implementación concreta. Permite cambiar fácilmente de almacenamiento (memoria → SQLite → PostgreSQL) y favorece testing y extensibilidad.

**¿Por qué Loguru vs logging estándar?**
- Sintaxis simple sin configuración verbose
- Logs estructurados en SQLite para auditoría
- Serialización automática de excepciones
- Menor tiempo de desarrollo vs implementación propia

**¿Por qué middleware centralizado vs try/catch distribuido?**
- Problema inicial: Cada endpoint manejaba errores manualmente, generando código repetitivo y respuestas inconsistentes.
- **Decisión tomada**: Middleware con excepciones personalizadas (NotFoundError, ValidationError) que se convierten automáticamente a respuestas HTTP. Separación clara: Services lanzan excepciones de negocio, middleware las traduce a HTTP.

**¿Por qué Docker vs ambiente virtual tradicional?**
- Problema inicial: Desarrollo con venv requería configuración manual del entorno y dependencias del sistema.
- **Decisión tomada**: Arquitectura containerizada modular donde cada servicio (backend) tiene su propio Dockerfile. Docker-compose orquesta múltiples servicios con healthcheck automático, garantizando consistencia entre desarrollo/producción y facilitando escalabilidad futura.


## Guía para Desarrolladores

**Cambiar configuración:**
- Todo en `.env.example` (fuente única de verdad)
- `settings.py` lee automáticamente los valores

**Agregar nuevo endpoint:**
- Definir schema en `schemas/`
- Agregar método en `TaskService`
- Crear endpoint en `routes/`
- Probar en `/docs`

**Modificar lógica de negocio:**
- Todo en `services/task_service.py`
- Los endpoints solo delegan, no contienen lógica

**Modificar storage (repositorios):**
- Agregar nuevos en `repositories/`
- Registrar en `config/dependencies.py`
- Cambiar `REPOSITORY_TYPE` en `.env.example`

**Cambiar validaciones:**
- Modificar schemas en `schemas/task.py`
- Pydantic se encarga del resto automáticamente

**Debugging:**
- Logs aparecen en consola y `storage/logs.db`
- `/docs` muestra errores de validación interactivos
- FastAPI devuelve stack traces detallados en desarrollo
- Healthcheck en `/api/v1/health` para monitoreo

## Principio clave
**Cada archivo tiene una responsabilidad clara.**
- ¿Cambiar validaciones? → `schemas/`
- ¿Cambiar endpoints? → `routes/`
- ¿Agregar storage? → `repositories/`
- ¿Cambiar storage? → `config/dependencies.py`
- ¿Modificar configuración? → `.env.example`