# API_TASK — Gestión de tareas con FastAPI
```
API REST para la gestión de tareas, construida con FastAPI.  
Diseño modular con separación clara de responsabilidades.  
Usa SQLite por defecto, con arquitectura modular que permite cambiar fácilmente entre diferentes tipos de almacenamiento.
```

## Stack Tecnológico
- **Python 3.8+** - Lenguaje base
- **FastAPI**     - Framework web async
- **Pydantic**    - Validación de datos
- **Uvicorn**     - Servidor ASGI
- **SQLite**      - Base de datos
- **Loguru**      - Logging estructurado
- **Pytest**      - Testing framework

## Estado del Proyecto
**Actualmente**: Sprint 2 completo
- CRUD completo con SQLite `LISTO`
- Suite de testing implementada `LISTO`
- Sistema de logging estructurado `LISTO`
- Manejo de errores `LISTO`
**Siguiente**: Migración a SQLAlchemy y soporte multi-database


## Arquitectura del Sistema
```
API Request → Routes → Service → Repository → Models → Response
     ↓           ↓        ↓           ↓          ↓
  Validación  Endpoints Lógica   Abstracción Entidades
  (Schemas)            Negocio   (Interface)
```

## Flujo de una petición típica:
- Cliente envía POST /api/v1/tasks con JSON
- FastAPI valida el JSON contra TaskCreate schema
- Router (tasks.py) recibe la petición válida
- Service (task_service.py) ejecuta la lógica de negocio
- Model (Task) representa la entidad creada
- Respuesta se serializa usando TaskResponse schema


## Estructura de Archivos
```
API_task/
├── app/
│   ├── __init__.py                   # Inicializaciones 
│   ├── main.py                       # Punto de entrada
│   ├── config.py                     # Configuración
│   ├── logging/
│   │   └── logging_system.py         # Configura loguru
│   ├── middleware/
│   │   └── error_handler.py          # Manejador de errores
│   ├── models/
│   │   └── task.py                   # Entidades de dominio
│   ├── repositories/
│   │   ├── task/
│   │   │   ├── base_repository.py    # Interface TaskRepository
│   │   │   ├── memory_repository.py  # MemoryTaskRepository
│   │   │   └── sqlite_repository.py  # SqliteTaskRepository
│   ├── routes/
│   │   ├── health.py                 # Health check
│   │   └── tasks.py                  # Endpoints de tareas
│   ├── schemas/
│   │   └── task.py                   # Validación entrada/salida
│   └── services/
│       └── task_service.py           # Lógica de negocio
├── scripts/
│   └── init_db.py                    # Prepara entorno con db
├── storage/                          # Archivos DB locales
│   ├── logs.db
│   └── tasks.db
├── test/
│   ├── integration/                  # Test de Endpoints
│   │   ├── test_health_endpoints.py
│   │   └── test_task_endpoints.py 
│   ├── repositories/                 # Test de Repositorios
│   │   ├── test_memory_repository.py
│   │   └── test_sqlite_repository.py
│   ├── conftest.py                   # Configuraciones de test
│   ├── test_models.py                # Test de model Task
│   ├── test_schemas.py               # Test de esquema Pydantic
│   └── test_services.py              # Test de task_service
├── coverage.svg                      # % Cobertura de los test
├── quick_start.txt                   # Guia rápida
├── requirements.txt                  # Dependencias
└── README.md
```


## Componentes Principales

### 0. Config (app/config.py)
- Propósito: Inicializar dependencias (repositorio) según entorno/configuración.
- Responsabilidad: Inyectar una instancia de TaskRepository en el TaskService.

### 1. Logging (app/logging/logging_system.py)
- Propósito: Sistema de logging centralizado y estructurado.
- SQLiteHandler personalizado para persistencia en BD
- Configuración automática con contexto (.bind()) 
- Responsabilidad: Capturar operaciones CRUD, errores y eventos del sistema con metadata estructurada.

### 2. Models (app/models/task.py)
- Propósito: Representan las entidades de negocio.
- class Task:
- - Propiedades: id, title, description, completed, created_at
- - Métodos: mark_complete(), to_dict()
- Responsabilidad: Definir la estructura y comportamiento de una tarea.

### 3. Schemas (app/schemas/task.py)
- Propósito: Validación y serialización de datos.
- TaskCreate    `# ← Datos que llegan (input)`
- TaskResponse  `# → Datos que salen (output)`  
- TaskUpdate    `# ← Datos para actualizar`
- Responsabilidad: Garantizar que los datos sean correctos antes de procesarlos.

### 4. Repositories (app/repositories/...)
- Propósito: Abstraer el acceso a datos detrás de una interfaz común.
- - base_repository.py: `Interfaz que define contrato implementado por los demás repositorios.`
- - memory_repository.py: `Implementa TaskRepository en memoria (una lista). Útil para desarrollo rápido y testing sin persistencia real.`
- - sqlite_repository.py: `Implementa TaskRepository usando SQLite nativo. Provee persistencia local sin dependencias externas.`
- Responsabilidad: Proveer operaciones CRUD sin exponer detalles del almacenamiento (memoria, SQLite, etc).

### 5. Services (app/services/task_service.py)
- Propósito: Lógica de negocio centralizada.
- class TaskService:
- - create_task(), get_all_tasks(), get_task_by_id()
- - update_task(), delete_task()
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

Crear Tarea (POST /api/v1/tasks)
1. Cliente envía: {"title": "Comprar pan"}
2. Pydantic valida contra TaskCreate
3. Router llama: task_service.create_task(task_data)
4. Service crea Task y la almacena
5. Task se convierte a dict con to_dict()
6. Respuesta: {"id": 1, "title": "Comprar pan", "completed": false, ...}

Error Handling
- Tarea no encontrada → HTTP 404 (via NotFoundError)
- Datos inválidos → HTTP 422 (Pydantic automático)
- Errores internos → HTTP 500 (via middleware centralizado)


## Configuración y Ejecución

Instalación:
```pip install -r requirements.txt```

Prepara entorno con db:
```python scripts/init_db.py```

Desarrollo:
```python -m app.main```
o
```uvicorn app.main:app --reload```

URLs importantes:
API: ```http://localhost:8000```
Documentación: ```http://localhost:8000/docs```
Health Check: ```http://localhost:8000/api/v1/health```


## Test

![coverage](coverage.svg)


## Testing Manual

Via Documentación (Recomendado):
- Ir a ```http://localhost:8000/docs```
- Probar endpoints interactivamente

Via cURL (Crear tarea):
```curl -X POST http://localhost:8000/api/v1/tasks \ -H "Content-Type: application/json" \ -d '{"title": "Nueva tarea"}'```

Via cURL (Listar tareas)
```curl http://localhost:8000/api/v1/tasks```


## Decisiones de Diseño

**¿Por qué FastAPI vs Flask/Django?**
- Validación automática con Pydantic
- Documentación auto-generada
- Type hints nativo
- Performance superior

**¿Por qué memoria primero vs DB directo?**
- Iteración rápida en desarrollo
- Simplicidad para testing
- Fácil migración posterior (demostrada en TaskService)

**¿Cómo desacoplar task_service.py para cumplir con SOLID?**
- Problema inicial: TaskService manejaba directamente una lista en memoria (self.tasks: List[Task] = []), violando el principio de responsabilidad única - mezclaba lógica de negocio con almacenamiento. Cambiar de memoria a DB requería reescribir todo el servicio.
- Opción 1: Trabajar directamente con listas de tareas
- - Simple, pero acopla la lógica al almacenamiento
- - No escalable si cambiamos el backend (DB, API externa)
- Opción 2: Crear un wrapper para listas (adapter)
- - Encapsula un poco más
- - Sigue siendo específico para listas, no es una solución general
- Opción 3: Abstraer el repositorio e inyectarlo en el servicio
- - Desacople total entre lógica y almacenamiento
- - Permite cambiar fácilmente de almacenamiento (memoria → SQLite)
- - Favorece testeo y extensibilidad
- **Decisión tomada**: esta opción sigue el principio de inversión de dependencias (D de SOLID) y permite que `TaskService` dependa de una **interfaz genérica**, no de una implementación concreta. Ahora TaskService recibe el repositorio por inyección de dependencias en lugar de crear su propia lista.

**¿Por qué Loguru vs logging estándar/custom?**
- Menor tiempo de desarrollo vs implementación propia
- Sintaxis simple sin configuración verbose
- Comunidad activa y mantenimiento garantizado
- Logs estructurados en SQLite para auditoría
- Serialización automática de excepciones

**¿Por qué middleware centralizado vs try/catch distribuido?**
- Problema inicial: Cada endpoint manejaba errores manualmente con if not task: raise HTTPException(404), generando código repetitivo y respuestas inconsistentes.
- Opción 1: Try/catch en cada route
- - Control granular pero código duplicado
- - Inconsistencia en formato de errores
- - Mantenimiento complejo al escalar
- Opción 2: Middleware centralizado + excepciones de negocio
- - Separación clara: Services lanzan excepciones, middleware convierte a HTTP
- - Código limpio en routes (sin try/catch)
- - Formato consistente de respuestas de error
- - Escalable y mantenible
- **Decisión tomada**: Middleware con excepciones personalizadas (NotFoundError, ValidationError) que se convierten automáticamente a respuestas HTTP apropiadas. Los services manejan lógica de negocio y errores específicos, mientras el middleware maneja la traducción a HTTP, siguiendo el principio de responsabilidad única.


## Guía para Desarrolladores

Agregar nuevo endpoint:
- Definir schema en schemas/
- Agregar método en TaskService
- Crear endpoint en routes/
- Probar en /docs

Modificar lógica de negocio:
- Todo en services/task_service.py
- Los endpoints solo delegan, no contienen lógica

Modificar storage (repositorios):
- Agregar nuevos en repositories/
- Cambiar ACTIVE_REPOSITORY en config.py (MEMORY/SQLITE)

Cambiar validaciones:
- Modificar schemas en schemas/task.py
- Pydantic se encarga del resto

Debugging:
- Logs aparecen en consola
- /docs muestra errores de validación
- FastAPI devuelve stack traces en desarrollo


## Principio clave: 
**Cada archivo tiene una responsabilidad clara.**
- ¿Cambiar validaciones? → `schemas/`
- ¿Cambiar endpoints? → `routes/`
- ¿Agregar storage? → `repositories/`
- ¿Cambiar storage? → `config.py`
