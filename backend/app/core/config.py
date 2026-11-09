import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base backend directory
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = BACKEND_DIR.parent

class Settings(BaseSettings):
    APP_NAME: str = "INDUSERV - Intelligent Document Automation Platform"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str = "induserv_super_secret_local_key_change_in_production_2026"

    # Database
    DATABASE_URL: str = f"sqlite:///{BACKEND_DIR / 'induserv.db'}"

    # Storage paths
    STORAGE_BASE_DIR: Path = PROJECT_ROOT / "storage"
    UPLOAD_DIR: Path = PROJECT_ROOT / "storage" / "uploads"
    GENERATED_DIR: Path = PROJECT_ROOT / "storage" / "generated"
    TEMPLATES_DIR: Path = PROJECT_ROOT / "storage" / "templates"

    # AI Provider Defaults
    DEFAULT_AI_PROVIDER: str = "free_api"  # "free_api", "ollama", "openai_compatible"
    FREE_API_BASE_URL: str = "https://openrouter.ai/api/v1"
    FREE_API_KEY: str = ""
    FREE_API_DEFAULT_MODEL: str = "meta-llama/llama-3.3-70b-instruct:free"

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_DEFAULT_MODEL: str = "llama3.2:latest"

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    def ensure_storage_dirs(self):
        """Ensure all storage directories exist."""
        for path in [self.STORAGE_BASE_DIR, self.UPLOAD_DIR, self.GENERATED_DIR, self.TEMPLATES_DIR]:
            path.mkdir(parents=True, exist_ok=True)

settings = Settings()
settings.ensure_storage_dirs()

