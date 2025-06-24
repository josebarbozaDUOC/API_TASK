# backend/app/middleware/error_handler.py

"""
Sistema de manejo de errores centralizado para FastAPI.

Este módulo proporciona un conjunto de excepciones personalizadas y handlers
automáticos que convierten errores internos en respuestas HTTP consistentes.

Características:
- Excepciones específicas (NotFoundError, ValidationError)
- Conversión automática a respuestas JSON con códigos HTTP apropiados
- Handler catch-all para errores inesperados
- Funciones de conveniencia para lanzar errores fácilmente

Uso:
   # En main.py
   from app.middleware.error_handler import setup_error_handlers
   setup_error_handlers(app)
   
   # En servicios
   from app.middleware.error_handler import raise_not_found
   if not task:
       raise_not_found("Task", task_id)  # Automáticamente retorna 404

El middleware se encarga de capturar las excepciones y convertirlas
en respuestas HTTP apropiadas sin necesidad de try/except en los endpoints.
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from loguru import logger

# EXCEPCIONES SIMPLES
class NotFoundError(Exception):
    def __init__(self, resource: str, resource_id):
        self.resource = resource
        self.resource_id = resource_id
        super().__init__(f"{resource} {resource_id} not found")

class ValidationError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

# FUNCIONES FÁCILES DE USAR
def raise_not_found(resource: str, resource_id):
    """Lanza error 404"""
    raise NotFoundError(resource, resource_id)

def raise_validation_error(message: str):
    """Lanza error 400"""
    raise ValidationError(message)

# HANDLERS AUTOMÁTICOS
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=404,
        content={"error": "Not found", "message": str(exc)}
    )

async def validation_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=400,
        content={"error": "Validation error", "message": exc.message}
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "HTTP error", "message": exc.detail}
    )

async def generic_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )

# CONFIGURACIÓN AUTOMÁTICA
def setup_error_handlers(app):
    """Una sola función para configurar todo"""
    app.add_exception_handler(NotFoundError, not_found_handler)
    app.add_exception_handler(ValidationError, validation_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, generic_handler)
    print("✅ Error handlers configured")