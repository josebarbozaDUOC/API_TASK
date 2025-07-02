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

**¿Por qué SQLAlchemy ORM vs SQL crudo?**
- Problema inicial: El repositorio SQLite usaba SQL crudo con queries manuales, propenso a SQL injection y difícil de mantener con cambios de esquema.
- Opción 1: Mantener SQL crudo → Control total, pero más código boilerplate y riesgo de errores
- Opción 2: Usar un micro-ORM (como raw queries con pandas) → Más simple que SQL puro, pero limitado
- Opción 3: ORM completo (SQLAlchemy) → Abstracción robusta, type safety, migraciones
- **Decisión tomada**: SQLAlchemy ORM con modelos separados (Task para dominio, TaskORM para persistencia). Mantiene la arquitectura limpia mientras provee seguridad contra SQL injection, queries type-safe, y facilita migraciones futuras.

**¿Por qué modelos separados (Task + TaskORM) vs modelo único?**
- Problema inicial: Mezclar responsabilidades de dominio y persistencia en una sola clase viola el principio de responsabilidad única.
- Opción 1: Un solo modelo que herede de SQLAlchemy Base → Más simple, pero acopla el dominio a la BD
- Opción 2: Modelos separados con conversión manual → Más código, pero desacoplado
- Opción 3: SQLModel (próximo experimento) → Promete unificar Pydantic + SQLAlchemy en un modelo
- **Decisión tomada**: Modelos separados por ahora. Task permanece como entidad de dominio pura, TaskORM maneja persistencia. Permite cambiar de ORM sin afectar la lógica de negocio.

**¿Por qué explorar SQLModel como alternativa?**
- SQLModel unifica validación (Pydantic) + ORM (SQLAlchemy) + serialización en un solo modelo
- Creado por el mismo autor de FastAPI, diseñado para integrarse perfectamente
- Reduce código duplicado manteniendo type safety
- **Próximo experimento**: Implementar con SQLModel en rama separada para comparar complejidad vs beneficios antes de decidir el approach final.

**¿Por qué PostgreSQL con Docker y soporte multi-bases?**
- PostgreSQL es una base robusta, open source y lista para producción, mientras que SQLite es ideal para desarrollo ágil.
- Mantener soporte para múltiples motores permite usar SQLite en desarrollo, PostgreSQL en staging y producción, o incluso MySQL si se requiere.
- El testing se adapta a cada nivel (memoria, SQLite, PostgreSQL) y permite migraciones sin tocar la lógica de negocio.
- Se implementa un Factory pattern que selecciona el repositorio según .env, manteniendo un único código base.
- Todo se despliega fácilmente con Docker Compose, garantizando entornos consistentes y sin instalaciones manuales.

**¿Por qué reintentos de conexión en MySQL?**
- Problema inicial: En Docker Compose, el backend iniciaba antes de que MySQL completara su inicialización, causando errores de conexión al intentar crear las tablas.
- Opción 1: Usar `depends_on` con healthcheck → Requiere configuración adicional de healthcheck en docker-compose
- Opción 2: Script de espera externo (wait-for-it) → Agrega dependencias externas
- Opción 3: Reintentos en el código → Solución simple y autocontenida
- **Decisión tomada**: Implementar reintentos con backoff en el repositorio MySQL. El backend intenta conectarse hasta 30 veces con 2 segundos entre intentos, suficiente para que MySQL complete su inicialización. Solución pragmática que no requiere cambios en Docker Compose ni scripts adicionales.

**¿Por qué lazy loading + multi-environment + testing containerizado?**
- Problema: El servicio se conectaba a BD al importar, bloqueando tests con MySQL/PostgreSQL. Además, cambiar entre BDs requería modificar código.
- **Solución integrada**:
  - Lazy loading: `task_service = create_task_service` (sin paréntesis) + `@lru_cache()`. Conecta solo al usar, no al importar.
  - Factory pattern: Selecciona repositorio según `ENVIRONMENT` y `TEST_REPOSITORY_TYPE` del .env
  - Testing dual: Local con SQLite (rápido) o containerizado con `docker-compose.test.yml` (completo, múltiples BDs)
- **Resultado**: Un código base que se adapta automáticamente a desarrollo (SQLite), testing (configurable), staging/producción (PostgreSQL/MySQL). Los tests corren sin bloqueos y cada desarrollador usa su BD preferida.

**¿Por qué un Factory Pattern explícito para repositorios?**
- Problema inicial: La lógica de creación de repositorios estaba mezclada con la inyección de dependencias en `dependencies.py`, violando el principio de responsabilidad única.
- Opción 1: Enum con mapeo (implementación original) → Funcional pero mezclaba responsabilidades
- Opción 2: Factory con diccionario → Simple, explícito y fácil de extender
- Opción 3: Auto-descubrimiento → Más "mágico" pero viola "explicit is better than implicit" de Python
- **Decisión tomada**: Factory dedicado (`repository_factory.py`) con diccionario de tipos. Centraliza la creación, soporta alias (postgres/postgresql), facilita testing con mocks, y mantiene `dependencies.py` enfocado solo en inyección. Patrón clásico que cualquier desarrollador reconoce inmediatamente.