# backend/app/config/settings.py
"""
Configuración centralizada del proyecto usando Pydantic Settings.

Lee configuración en orden de prioridad:
1. Variables de entorno del sistema (export VAR=value)
2. Archivos .env y .env.example (fallback)

Auto-detecta Docker vs desarrollo local para rutas de base de datos.

Referencias:
   - FastAPI Settings: https://fastapi.tiangolo.com/advanced/settings/
   - Pydantic Settings: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    """Configuración del proyecto Todo API Task."""
    
    # Application
    app_name: str = ""
    app_version: str = ""
    environment: str = ""
    
    # Server
    host: str = ""
    port: int = 0
    
    # Database paths
    log_db_path: str = ""
    task_db_path: str = ""
    
    # Repository
    repository_type: str = ""
    
    # Logging
    log_level: str = ""
    
    # CORS
    cors_origins: str = ""
    
    # Secrets
    secret_key: str = ""
    jwt_secret: str = ""
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Convierte CORS origins string a lista."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def is_development(self) -> bool:
        """Verifica si está en desarrollo."""
        return self.environment == "development"
    
    @property
    def log_db_absolute_path(self) -> str:
        """Ruta absoluta a logs DB. Auto-detecta Docker vs local."""
        if Path("/app/storage").exists():
            path = f"/app/{self.log_db_path}"
        else:
            project_root = Path(__file__).parent.parent.parent.parent
            path = str(project_root / self.log_db_path)
        
        # ✅ Auto-crear directorio si no existe
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def task_db_absolute_path(self) -> str:
        """Ruta absoluta a tasks DB. Auto-detecta Docker vs local."""
        if Path("/app/storage").exists():
            path = f"/app/{self.task_db_path}"
        else:
            project_root = Path(__file__).parent.parent.parent.parent
            path = str(project_root / self.task_db_path)
        
        # ✅ Auto-crear directorio si no existe  
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        return path

    model_config = SettingsConfigDict(
        env_file=[".env.example", ".env"]
    )


settings = Settings()