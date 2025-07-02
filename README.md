# API_TASK — Gestión de tareas con FastAPI

    API REST modular para gestión de tareas, creada como proyecto personal de aprendizaje con enfoque profesional.

    Diseñada para practicar arquitectura limpia, principios SOLID y patrones desacoplados usando FastAPI, Docker y SQLAlchemy. El proyecto integra herramientas modernas de validación, logging, testing y configuración basada en `.env`.

    Su objetivo es convertirse en una plantilla técnica mantenible y extensible, apta para entornos reales y evolución hacia microservicios.

Incluye:

- 🧱 Principios **SOLID** y **Clean Code**
- 🧪 Testing con **Pytest** (>90% cobertura)
- 🐳 Containerización con **Docker** y Compose
- 🧠 Validación con **Pydantic**
- 📄 Logging estructurado con **Loguru**
- 🗃️ Repositorios para **SQLite**, **PostgreSQL** y **MySQL**
- 🔄 Integración con **SQLAlchemy** ORM (evaluando **SQLModel**)
- 🧪 Middleware y manejo centralizado de errores
- 🌱 Exploración inicial de **12factor** y **PEP8**

Ideal para construir APIs reales, como base de nuevos proyectos o para tu portafolio técnico.


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
**Completados**: 
- Sprint 1: BASE SÓLIDA
- Sprint 2: PERSISTENCIA REAL
- Sprint 3: CONTAINERIZACIÓN BÁSICA

**Actualmente**: 
- Sprint 4 - SQLALCHEMY & RELACIONALES
  - ✅ STORY 15: Migración a SQLAlchemy ORM
  - ✅ STORY 16: PostgreSQL Repository + Docker Compose
  - ✅ STORY 17: MySQL Repository + Docker Compose
  - ✅ STORY 18: Database Factory Pattern
  - 🔄STORY 19: Connection Pooling y Async
  - STORY 20: Revisión y Documentación

[Ver RoadMap completo](docs/ROADMAP.md)


## Arquitectura del Sistema
```
API Request → Routes → Service → Repository → Models → Response
     ↓           ↓        ↓           ↓          ↓
  Validación  Endpoints Lógica   Abstracción Entidades
  (Schemas)            Negocio   (Interface)
```


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


## Estructura de Archivos
[Ver Estructura completa comentada](docs/structure.md)


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
  - postgresql_repository.py: `Implementa TaskRepository para PostgreSQL.`
  - mysql_repository.py: `Implementa TaskRepository para MySQL con reintentos.`
  - repository_factory.py: `Factory que crea el repositorio correcto según configuración.`
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


## Configuración y Ejecución

**Configuración**
```
# Revisa .env.example para todas las opciones de configuración disponibles.
# Copiar archivo de configuración
cp .env.example .env

# Editar credenciales para uso de PostgreSQL
# POSTGRES_USER, POSTGRES_PASSWORD, etc.
```

**Docker (Recomendado):**
```
docker-compose up --build
```

**Local:**
```
cd backend/
pip install -r requirements.txt
uvicorn src.main:app --reload
```

**Verificar:**
- API: ```http://localhost:8000```
- Documentación: ```http://localhost:8000/docs```
- Health Check: ```http://localhost:8000/api/v1/health```


## Guía para Desarrolladores

**Cambiar configuración:**
- Todo en `.env.example` (fuente única de verdad)
- `.env` para credenciales y secretos
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
- Registrar en `repository_factory.py`
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


## Test

![coverage](backend/coverage.svg)

**Test suite completo con pytest:**

- ✅ Tests unitarios (models, schemas, services)
- ✅ Tests de repositorios (memory, SQLite, PostgreSQL, MySQL)
- ✅ Tests de integración (endpoints)
- ✅ Cobertura >90%

**Ejecutar tests localmente:**
```
cd backend/
python -m pytest tests/ -v                                    # Tests básicos
python -m pytest tests/ --cov=src --cov-report=term-missing   # Con cobertura

# Generar badge
python -m pytest tests/ --cov=src --cov-report=term-missing --cov-report=xml -v
python -m coverage_badge -o coverage.svg -f
```

**Ejecutar tests en Docker:**
```
docker-compose -f docker-compose.yml -f docker-compose.test.yml up --abort-on-container-exit --build
```
- nota: revisar el `docker-compose.test.yml`

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
[Ver Decisiones de Diseño](docs/design_decisions.md)