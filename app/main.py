# app/main.py

"""
Módulo principal de la aplicación FastAPI.

Configura la aplicación FastAPI con middleware, routers y configuración básica.
Incluye CORS para soporte de frontend web y proporciona endpoints de documentación.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import health, tasks

app = FastAPI(
    title="Todo API Task",
    description="API simple para gestión de tareas", 
    version="1.0.0"
)

# Preparado para frontend web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Endpoint raíz con información básica y navegación de la API."""
    return {
        "name":     "Todo API Task",
        "version":  "1.0.0",
        "docs":     "/docs",
        "redoc":    "/redoc",
        "health":   "/api/v1/health"
    }

app.include_router(health.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)