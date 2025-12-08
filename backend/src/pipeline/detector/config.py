"""
Detector Configuration
SIH 25162 - AOI IC Verification System
Author: Saif (CommitSaif11)

"""

from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional
import os

class DetectorConfig(BaseSettings):
    """
    Configuration for YOLO IC Detector
    Saif will train custom model in Google Colab and update the path
    """
    
    # Model Configuration
    MODEL_PATH: str = os.getenv(
        "YOLO_MODEL_PATH",
        "https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt"
    )
    
    # Detection Parameters
    CONFIDENCE_THRESHOLD: float = float(os.getenv("YOLO_CONFIDENCE", "0.25"))
    IOU_THRESHOLD: float = float(os.getenv("YOLO_IOU", "0.45"))
    MAX_DETECTIONS: int = int(os.getenv("YOLO_MAX_DET", "10"))
    
    # Image Processing
    INPUT_SIZE: int = int(os.getenv("YOLO_INPUT_SIZE", "640"))
    
    # Device Configuration
    DEVICE: str = os.getenv("YOLO_DEVICE", "cpu")  # "cpu" or "cuda" or "mps"
    
    # Local Model Cache Directory
    MODEL_CACHE_DIR: Path = Path(__file__).parent.parent.parent / "static" / "models"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global config instance for Saif's detector
detector_config = DetectorConfig()