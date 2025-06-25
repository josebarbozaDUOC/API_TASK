# backend/tests/integration/test_health_endpoints.py

"""
Tests de integración para endpoints de health check.

Tests simples para verificar que los endpoints de salud
respondan correctamente y proporcionen la información esperada.

Ejecución:
    python -m pytest tests/integration/test_health_endpoints.py -v
    python -m pytest tests/integration/test_health_endpoints.py --cov=app.routes -v
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from src.main import app

class TestHealthEndpoints:
    """Tests para endpoints de health check."""
    
    @pytest.fixture
    def client(self):
        """Cliente de testing para hacer requests HTTP."""
        return TestClient(app)

    def test_health_check_success(self, client):
        """Debe retornar estado de salud correcto."""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar estructura de respuesta
        assert "status" in data
        assert "message" in data
        assert "timestamp" in data
        assert "version" in data
        
        # Verificar contenido
        assert data["status"] == "healthy"
        assert data["message"] == "Todo API Task is running"
        assert data["version"] == "1.0.0"
        
        # Verificar que timestamp es válido
        timestamp = datetime.fromisoformat(data["timestamp"])
        assert isinstance(timestamp, datetime)

    def test_readiness_check_success(self, client):
        """Debe retornar estado de preparación correcto."""
        response = client.get("/api/v1/health/ready")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar estructura y contenido
        assert data["status"] == "ready"
        assert data["message"] == "Service is ready to accept requests"

    def test_health_endpoints_are_fast(self, client):
        """Los endpoints de health deben ser rápidos."""
        import time
        
        # Medir tiempo de respuesta
        start = time.time()
        response = client.get("/api/v1/health")
        end = time.time()
        
        assert response.status_code == 200
        assert (end - start) < 0.1  # Debe responder en menos de 100ms
        
        # Lo mismo para readiness
        start = time.time()
        response = client.get("/api/v1/health/ready")
        end = time.time()
        
        assert response.status_code == 200
        assert (end - start) < 0.1

    def test_root_endpoint(self, client):
        """Debe retornar información básica de la API."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar estructura de respuesta
        assert "name" in data
        assert "version" in data
        assert "docs" in data
        assert "redoc" in data
        assert "health" in data
        
        # Verificar contenido
        assert data["name"] == "Todo API Task"
        assert data["version"] == "1.0.0"
        assert data["docs"] == "/docs"
        assert data["redoc"] == "/redoc"
        assert data["health"] == "/api/v1/health"