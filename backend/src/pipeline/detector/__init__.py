"""
Detector Module - YOLOv8 IC Detection
SIH 25162 - AOI IC Verification System
Author: Saif (CommitSaif11)

"""

from .yolo_detector import YOLODetector
from .config import DetectorConfig

__all__ = ["YOLODetector", "DetectorConfig"]