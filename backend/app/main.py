# backend/app/main.py
"""
Módulo principal de la aplicación FastAPI.

Configura la aplicación FastAPI con middleware, routers y configuración básica.
Incluye CORS para soporte de frontend web y proporciona endpoints de documentación.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from app.config.settings import settings
from .routes import health, tasks
from app.middleware.error_handler import setup_error_handlers

logger.debug("Entrada a main")

app = FastAPI(
    title=settings.app_name,
    description="API simple para gestión de tareas", 
    version=settings.app_version
)

setup_error_handlers(app)

# Preparado para frontend web
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Endpoint raíz con información básica y navegación de la API."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/api/v1/health"
    }

app.include_router(health.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=False)