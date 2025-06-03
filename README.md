# API_TASK
```
API REST para gestión de tareas construida con FastAPI.
Arquitectura modular con separación clara de responsabilidades.
Por ahora usa almacenamiento en memoria, preparada para migrar a base de datos.
```

## Stack Tecnológico
- **FastAPI**     - Framework web async
- **Pydantic**    - Validación de datos
- **Python 3.8+** - Lenguaje base
- **Uvicorn**     - Servidor ASGI

## Arquitectura del Sistema
```
API Request → Routes → Services → Models → Response
     ↓           ↓         ↓         ↓
  Validación  Endpoints  Lógica   Entidades
  (Schemas)             Negocio
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
│   ├── main.py              # Punto de entrada
│   ├── models/
│   │   └── task.py          # Entidades de dominio
│   ├── schemas/
│   │   └── task.py          # Validación entrada/salida
│   ├── routes/
│   │   ├── health.py        # Health check
│   │   └── tasks.py         # Endpoints de tareas
│   └── services/
│       └── task_service.py  # Lógica de negocio
├── requirements.txt         # Dependencias
└── README.md
```


## Componentes Principales

### 1. Models (app/models/task.py)
- Propósito: Representan las entidades de negocio.
- class Task:
- - Propiedades: id, title, description, completed, created_at
- - Métodos: mark_complete(), to_dict()
- Responsabilidad: Definir la estructura y comportamiento de una tarea.

### 2. Schemas (app/schemas/task.py)
- Propósito: Validación y serialización de datos.
- TaskCreate    `# ← Datos que llegan (input)`
- TaskResponse  `# → Datos que salen (output)`  
- TaskUpdate    `# ← Datos para actualizar`
- Responsabilidad: Garantizar que los datos sean correctos antes de procesarlos.

### 3. Services (app/services/task_service.py)
- Propósito: Lógica de negocio centralizada.
- class TaskService:
- - create_task(), get_all_tasks(), get_task_by_id()
- - update_task(), delete_task()
- Responsabilidad: Implementar las reglas de negocio. Actualmente usa memoria, fácil migrar a DB.

### 4. Routes (app/routes/tasks.py)
- Propósito: Definir endpoints HTTP.
- GET    /api/v1/tasks      `# Listar todas`
- POST   /api/v1/tasks      `# Crear nueva`
- GET    /api/v1/tasks/{id} `# Obtener por ID`
- PUT    /api/v1/tasks/{id} `# Actualizar`
- DELETE /api/v1/tasks/{id} `# Eliminar`
- Responsabilidad: Manejar peticiones HTTP y delegar al service.

### 5. Main (app/main.py)
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
- Tarea no encontrada → HTTP 404
- Datos inválidos → HTTP 422 (Pydantic automático)
- Errores internos → HTTP 500 (FastAPI automático)


## Configuración y Ejecución
```
Instalación:
pip install -r requirements.txt
Desarrollo:
python -m app.main
o
uvicorn app.main:app --reload

URLs importantes:
API: http://localhost:8000
Documentación: http://localhost:8000/docs
Health Check: http://localhost:8000/api/v1/health
```

## Testing Manual
```
Via Documentación (Recomendado):
- Ir a http://localhost:8000/docs
- Probar endpoints interactivamente

Via cURL:
# Crear tarea
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Nueva tarea"}'

Listar tareas  
curl http://localhost:8000/api/v1/tasks
```


## Decisiones de Diseño

¿Por qué FastAPI vs Flask/Django?**
- Validación automática con Pydantic
- Documentación auto-generada
- Type hints nativo
- Performance superior

¿Por qué memoria primero vs DB directo?**
- Iteración rápida en desarrollo
- Simplicidad para testing
- Fácil migración posterior (demostrada en TaskService)


## Próximos Pasos

Fase 2 - Persistencia:
- Migrar TaskService de memoria a SQLAlchemy
- Agregar base de datos PostgreSQL/SQLite
- Connection pooling

Fase 3 - Robustez:
- Testing automatizado
- Logging estructurado
- Rate limiting
- Docker containerization


## Guía para Desarrolladores

Agregar nuevo endpoint:
- Definir schema en schemas/
- Agregar método en TaskService
- Crear endpoint en routes/
- Probar en /docs

Modificar lógica de negocio:
- Todo en services/task_service.py
- Los endpoints solo delegan, no contienen lógica

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
- ¿Cambiar storage? → `services/`
- ¿Cambiar endpoints? → `routes/`
