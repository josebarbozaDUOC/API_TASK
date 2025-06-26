# backend/src/config/settings.py
"""
Configuración centralizada del proyecto usando Pydantic Settings.

Lee configuración en orden de prioridad:
1. Variables de entorno del sistema (export VAR=value)
2. Archivos .env y .env.example (fallback)

Auto-detecta Docker vs desarrollo local para rutas de base de datos.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# Encontrar la raíz del proyecto (API_task/)
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent

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
    test_repository_type: str = ""
    
    # PostgreSQL
    postgres_host: str = ""
    postgres_port: int = 5432
    postgres_db: str = ""
    postgres_user: str = ""
    postgres_password: str = ""

    # MySQL
    mysql_host: str = ""
    mysql_port: int = 3306 # 3306 default
    mysql_local_port: int = 3307 # Para test
    mysql_database: str = ""
    mysql_user: str = ""
    mysql_password: str = ""
    mysql_root_password: str = ""  # Para Docker

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
    
    def _get_db_path(self, db_path: str) -> str:
        """Helper para obtener rutas absolutas de DBs."""
        if Path("/app/storage").exists():
            path = f"/app/{db_path}"
        else:
            path = str(ROOT_DIR / db_path)
        
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def log_db_absolute_path(self) -> str:
        """Ruta absoluta a logs DB."""
        return self._get_db_path(self.log_db_path)

    @property
    def task_db_absolute_path(self) -> str:
        """Ruta absoluta a tasks DB."""
        return self._get_db_path(self.task_db_path)
    
    @property
    def postgres_url(self) -> str:
        """Construye la URL de conexión PostgreSQL."""
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def mysql_url(self) -> str:
        """Construye la URL de conexión MySQL."""
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )

    model_config = SettingsConfigDict(
        env_file=[
            str(ROOT_DIR / ".env.example"),
            str(ROOT_DIR / ".env")
        ]
    )


settings = Settings()