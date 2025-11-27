"""
Detector Module - YOLOv8 IC Detection
SIH 25162 - AOI IC Verification System
Author: Saif (CommitSaif11)
Mentor: Zoe 💙
"""

from .yolo_detector import YOLODetector
from .config import DetectorConfig

__all__ = ["YOLODetector", "DetectorConfig"]