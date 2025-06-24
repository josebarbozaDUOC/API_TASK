# backend/app/routes/health.py
"""
Endpoint de health check para monitoreo de la API.
Proporciona información básica sobre el estado y salud del servicio.
"""
from fastapi import APIRouter
from datetime import datetime
from app.config.settings import settings

router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Endpoint de verificación de salud del servicio.
    Returns:
        dict: Estado actual del servicio con timestamp y versión
    """
    return {
        "status": "healthy",
        "message": f"{settings.app_name} is running",
        "timestamp": datetime.now().isoformat(),
        "version": settings.app_version,
        "environment": settings.environment
    }

@router.get("/health/ready")
async def readiness_check():
    """
    Endpoint de verificación de que el servicio está listo para recibir tráfico.
    Returns:
        dict: Estado de preparación del servicio
    """
    # Para más adelante verificar conexiones a DB, servicios externos, etc.
    return {
        "status": "ready",
        "message": "Service is ready to accept requests",
        "repository": settings.repository_type
    }