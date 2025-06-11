# Principios SOLID en API_TASK

## Los 5 Principios SOLID

- **S** - Single Responsibility Principle: Una clase debe tener una sola razón para cambiar
- **O** - Open/Closed Principle: Abierto para extensión, cerrado para modificación  
- **L** - Liskov Substitution Principle: Los objetos deben ser reemplazables por instancias de sus subtipos
- **I** - Interface Segregation Principle: Los clientes no deben depender de interfaces que no usan
- **D** - Dependency Inversion Principle: Depender de abstracciones, no de concreciones


> **Contexto**: Este documento explica cómo se implementaron los principios SOLID en el proyecto API_TASK, con ejemplos concretos del código y las decisiones tomadas durante el desarrollo.

## Resumen Ejecutivo
La aplicación de los principios SOLID permitió:
- ✅ Migración transparente: Cambiar de almacenamiento en memoria a SQLite sin modificar lógica de negocio
- ✅ Extensibilidad: Agregar nuevos repositorios (PostgreSQL, Redis) sin tocar código existente
- ✅ Testing simplificado: Repositorios intercambiables para tests rápidos vs persistencia real
- ✅ Arquitectura limpia: Separación clara de responsabilidades por capas (HTTP → Service → Repository)
- ✅ Flexibilidad: Cambio de repositorio con una línea en config.py


**Arquitectura Resultante**
```
HTTP Request → Routes → Service → Repository Interface → Implementation
    ↓            ↓         ↓              ↓                    ↓
Validación   Endpoints  Lógica      Abstracción         SQLite/Memory
(Schemas)             Negocio       (Contract)         (Concrete)
```

**Principio clave aplicado**: Cada capa depende de abstracciones, no de implementaciones concretas.

---

## S - Single Responsibility Principle

### ✅ Implementación

"Una clase debe tener una sola razón para cambiar" - Cada clase en el proyecto tiene una responsabilidad específica y bien definida:

```
| Clase                  | Responsabilidad Única                    | Archivo                             |
|------------------------|------------------------------------------|-------------------------------------|
| `Task`                 | Representar entidad de negocio           | `models/task.py`                    |
| `TaskService`          | Lógica de negocio de tareas              | `services/task_service.py`          |
| `TaskRepository`       | Contrato de acceso a datos               | `repositories/base_repository.py`   |
| `SqliteTaskRepository` | Implementación SQLite específica         | `repositories/sqlite_repository.py` |
| `MemoryTaskRepository` | Implementación en memoria específica     | `repositories/memory_repository.py` |
| `TaskCreate`           | Validación de datos de entrada           | `schemas/task.py`                   |
| `TaskUpdate`           | Validación de datos de actualización     | `schemas/task.py`                   |
| `TaskResponse`         | Formato de respuesta HTTP                | `schemas/task.py`                   |
| `Router`               | Manejar endpoints HTTP                   | `routes/tasks.py`                   |
```

### 🔧 Refactoring Aplicado

**Antes - Violaba SRP:**
```
class TaskService:
    def __init__(self):
        self.tasks: List[Task] = []  # ❌ Responsabilidad mixta:
                                     #    1. Lógica de negocio  
                                     #    2. Almacenamiento
    def create_task(self, task_data):
        task = Task(...)
        self.tasks.append(task)      # ❌ Maneja persistencia directamente
```

**Después - Cumple SRP:**
```
class TaskService:
    def __init__(self, repository: TaskRepository):
        self.repository = repository         # ✅ Solo lógica de negocio
    
    def create_task(self, task_data):
        task = Task(...)                     # Crear entidad (su responsabilidad)
        return self.repository.create(task)  # Delegar almacenamiento
```

**💡 Beneficio Obtenido**
- Cambio de storage: 0 líneas modificadas en TaskService al migrar a SQLite
- Testing más limpio: Mock del repositorio vs mock de toda la lógica
- Código más legible: Cada archivo tiene un propósito claro
- Mantenimiento: Cambiar validación → schemas/, cambiar endpoints → routes/

**🎯 Ejemplo Práctico**
```
class Task:
    # ✅ SOLO se encarga de representar una tarea
    def mark_complete(self):     # Comportamiento de tarea
    def to_dict(self):          # Serialización de tarea
    
    # ❌ NO hace:
    # - Validación HTTP
    # - Persistencia en DB  
    # - Lógica de negocio compleja
```

---

## O - Open/Closed Principle

### ✅ Implementación

"Las clases deben estar abiertas para extensión, pero cerradas para modificación" - La arquitectura permite agregar funcionalidad sin tocar código existente:

### 🔧 Refactoring Aplicado

**Antes - Violaba OCP:**
```
class TaskService:
    def __init__(self):
        self.tasks: List[Task] = []  # ❌ Hard-coded storage
    
    # Para cambiar a SQLite → modificar toda la clase
```

**Después - Cumple OCP:**
```
class TaskService:
    def __init__(self, repository: TaskRepository):
        self.repository = repository  # ✅ Inyección de dependencias
    
    def create_task(self, task_data):
        # ✅ Código NUNCA cambia, sin importar qué repositorio uses
        task = Task(...)
        return self.repository.create(task)
```

**💡 Beneficio Obtenido**
- TaskService cerrado: Sus 50+ líneas nunca necesitan modificación
- Sistema abierto: Nuevos repositorios se "enchufan" automáticamente
- Extensión limpia: Agregar PostgreSQL = crear 1 archivo + 1 línea en enum

**🎯 Punto de Extensión**
```
# En config.py - El único lugar que cambia
class RepoType(Enum):
    MEMORY = MemoryTaskRepository
    SQLITE = SqliteTaskRepository
    # POSTGRESQL = PostgreSQLTaskRepository  # ← Futuro

ACTIVE_REPOSITORY = RepoType.SQLITE  # ← Un solo cambio
```

---

## L - Liskov Substitution Principle

### ✅ Implementación

"Los objetos deben ser reemplazables por instancias de sus subtipos" - Cualquier implementación de TaskRepository debe comportarse exactamente igual desde la perspectiva del TaskService:

### 🔧 Refactoring Aplicado

**Antes - Violaba LSP:**
```
class TaskService:
    def __init__(self):
        self.tasks = []  # ❌ Acoplado a implementación específica
    
    def get_task_by_id(self, task_id):
        # ❌ Comportamiento hard-coded para lista
        return next((task for task in self.tasks if task.id == task_id), None)
```

**Después - Cumple LSP:**
```
class TaskService:
    def __init__(self, repository: TaskRepository):
        self.repository = repository  # ✅ Funciona con cualquier implementación
    
    def get_task_by_id(self, task_id):
        # ✅ Mismo comportamiento garantizado por el contrato
        return self.repository.get_by_id(task_id)
```

**💡 Beneficio Obtenido**
- Intercambiabilidad perfecta: MemoryTaskRepository ↔ SqliteTaskRepository sin código adicional
- Comportamiento consistente: Ambas implementaciones devuelven None cuando no encuentran, IDs únicos, etc.
- Testing confiable: Tests con Memory se comportan igual que producción con SQLite

**🎯 Ejemplo Práctico**
```
# ✅ Estas dos líneas producen exactamente el mismo resultado:
task_service = TaskService(MemoryTaskRepository())   # Para tests
task_service = TaskService(SqliteTaskRepository())   # Para producción

# El TaskService no sabe ni le importa cuál está usando
task = task_service.get_task_by_id(1)  # Comportamiento idéntico
```

**🔑 Contrato Garantizado**
```
# Ambas implementaciones respetan exactamente este contrato:
def get_by_id(self, task_id: int) -> Optional[Task]:
    # ✅ Retorna Task si existe, None si no existe
    # ✅ Nunca lanza excepciones
    # ✅ IDs son únicos y secuenciales
```

---

## I - Interface Segregation Principle

### ✅ Implementación

"Los clientes no deben depender de interfaces que no usan" - Cada componente usa solo las interfaces específicas que necesita, sin métodos innecesarios:

### 🔧 Refactoring Aplicado

**Antes - Violaba ISP:**
```
# ❌ Schema monolítico - todos los endpoints usan todo
class TaskSchema(BaseModel):
    id: Optional[int]           # Solo para respuestas
    title: str                  # Requerido para crear
    description: Optional[str]  # Opcional para crear
    completed: bool             # Solo para actualizar
    created_at: Optional[datetime]  # Solo para respuestas
```

**Después - Cumple ISP:**
```
# ✅ Interfaces segregadas - cada endpoint usa solo lo que necesita
class TaskCreate(BaseModel):    # POST /tasks
    title: str
    description: Optional[str]

class TaskUpdate(BaseModel):    # PUT /tasks/{id}  
    title: Optional[str]
    description: Optional[str]
    completed: Optional[bool]

class TaskResponse(BaseModel):  # Respuestas GET
    id: int
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
```

**💡 Beneficio Obtenido**
- Validación específica: Endpoint de creación no acepta id ni created_at
- Flexibilidad: Updates parciales sin campos obligatorios innecesarios
- Documentación clara: OpenAPI muestra exactamente qué acepta cada endpoint
- Evolución independiente: Cambiar formato de respuesta no afecta validación de entrada

**🎯 Ejemplo Práctico**
```
# ✅ Cada endpoint consume exactamente lo que necesita:

@router.post("/tasks", response_model=TaskResponse)
async def create_task(task_data: TaskCreate):  # Solo title + description
    pass

@router.put("/tasks/{id}", response_model=TaskResponse)  
async def update_task(task_id: int, task_data: TaskUpdate):  # Campos opcionales
    pass

@router.get("/tasks/{id}", response_model=TaskResponse)
async def get_task(task_id: int):  # Solo para respuesta
    pass
```

**🔑 Repositorio Limpio**
```
# ✅ TaskRepository solo expone operaciones esenciales:
class TaskRepository(ABC):
    def create(self, task: Task) -> Task        # CRUD básico
    def get_all(self) -> List[Task]             # Sin métodos como:
    def get_by_id(self, task_id: int) -> Task   # - send_email()
    def update(self, task_id: int, task: Task)  # - generate_report()  
    def delete(self, task_id: int) -> bool      # - backup_data()
```

---

## D - Dependency Inversion Principle

### ✅ Implementación

"Depender de abstracciones, no de concreciones" - Los módulos de alto nivel (Service) no dependen de módulos de bajo nivel (SQLite), ambos dependen de abstracciones (TaskRepository):

### 🔧 Refactoring Aplicado

**Antes - Violaba DIP:**
```
from app.repositories.sqlite_repository import SqliteTaskRepository

class TaskService:
    def __init__(self):
        self.repository = SqliteTaskRepository()  # ❌ Depende de implementación concreta
        
# ❌ Alto nivel (Service) → Bajo nivel (SQLite)
```

**Después - Cumple DIP:**
```
from app.repositories.base_repository import TaskRepository

class TaskService:
    def __init__(self, repository: TaskRepository):  # ✅ Depende de abstracción
        self.repository = repository

# ✅ Alto nivel (Service) → Abstracción ← Bajo nivel (SQLite)
```

**💡 Beneficio Obtenido**
- Inversión de control: La dependencia se inyecta desde afuera (config.py)
- Desacoplamiento total: TaskService no conoce SQLite, Memory, ni PostgreSQL
- Testing simplificado: Inyectar mocks es trivial
- Flexibilidad máxima: Cambiar implementación = cambiar configuración

**🎯 Ejemplo Práctico**
```
# ✅ Inyección de dependencias en config.py
repository = ACTIVE_REPOSITORY.value()        # Crea implementación concreta
task_service = TaskService(repository)         # Inyecta abstracción

# El TaskService nunca hace:
# self.repository = SqliteTaskRepository()     # ❌ Acoplamiento
# self.repository = MemoryTaskRepository()     # ❌ Hard-coded
```

**🔑 Flujo de Dependencias**
```
# ✅ Arquitectura invertida:
TaskService(repository: TaskRepository)       # Alto nivel usa abstracción
    ↑
TaskRepository (ABC)                          # Abstracción define contrato  
    ↑
SqliteTaskRepository(TaskRepository)          # Bajo nivel implementa abstracción
MemoryTaskRepository(TaskRepository)          # Bajo nivel implementa abstracción
```

**🚀 El Poder de DIP**
- Un cambio en config.py → Todo el sistema usa diferente almacenamiento
- Zero modificaciones en lógica de negocio, endpoints, o validaciones
- Arquitectura plug-and-play → Nuevos repositorios se "enchufan" automáticamente

---

## Conclusión

La implementación de SOLID en API_TASK demostró que:

### ✅ Resultados Tangibles
- **0 líneas modificadas** en TaskService al migrar de Memory a SQLite
- **1 línea en config.py** para cambiar todo el sistema de almacenamiento  
- **Arquitectura plug-and-play** lista para PostgreSQL, Redis, o cualquier nuevo repositorio

### 🎯 Lecciones Clave
- **S**: Cada clase tiene una razón clara para existir
- **O**: TaskService cerrado, sistema abierto para extensión
- **L**: Repositorios perfectamente intercambiables
- **I**: Schemas específicos vs monolíticos
- **D**: Inyección de dependencias = flexibilidad máxima

### 🚀 Beneficio Principal
**Cambio de tecnología sin cambio de arquitectura** - La base sólida permite evolucionar el sistema sin reescribir código existente.