"""
Configuration Management
Loads environment variables from .env file
SIH 25162 - AOI IC Verification System
Author: Saif (CommitSaif11)

"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import Optional

# Get project root directory (where .env is located)
PROJECT_ROOT = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    # App
    APP_NAME: str = "SIH 25162 - AOI IC Verification"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # YOLO
    YOLO_MODEL_PATH: str = "https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt"
    YOLO_CONFIDENCE: float = 0.25
    YOLO_DEVICE: str = "cpu"

    # Security (JWT)
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD_HASH: str = ""

    # Upload limits
    MAX_UPLOAD_SIZE_MB: int = 10
    MAX_BATCH_FILES: int = 20

    # Mouser API
    MOUSER_API_KEY: str = ""

    # AI Agent
    GROQ_API_KEY: str = ""
    AI_MODEL: str = "llama-3.3-70b-versatile"
    AI_ENABLED: bool = True

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True
    )


# Global settings instance for Saif's app
settings = Settings()


def get_kb_dir() -> Path:
    """Get path to knowledge base directory"""
    return PROJECT_ROOT / "src" / "kb"


def get_static_dir() -> Path:
    """Get path to static assets directory"""
    return PROJECT_ROOT / "src" / "static"