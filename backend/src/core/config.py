"""
Configuration Management
Loads environment variables from .env file
SIH 25162 - AOI IC Verification System
Author: Saif (CommitSaif11)
Mentor: Zoe 💙
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import Optional

# Get project root directory (where .env is located)
PROJECT_ROOT = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    """
    Application settings loaded from .env file
    
    Note for Saif:
        All config values come from backend/.env
        No hardcoded secrets in code!
    """
    
    # App Settings
    APP_NAME: str = "SIH 25162 - AOI IC Verification"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # MongoDB Settings
    MONGODB_URL: str
    MONGODB_DB_NAME: str = "sih_aoi_system"
    
    # YOLO Settings
    YOLO_MODEL_PATH: str
    YOLO_CONFIDENCE: float = 0.25
    YOLO_DEVICE: str = "cpu"
    
    # Tesseract Settings
    TESSERACT_CMD: str = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    
    # Ollama Settings (for agent - later)
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama2"
    
    # Security Settings (JWT - later)
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Model configuration
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