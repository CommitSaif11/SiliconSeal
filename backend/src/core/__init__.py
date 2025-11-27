"""
Core Module - Configuration, Database, Schemas
SIH 25162 - AOI IC Verification System
Author: Saif (CommitSaif11)
Mentor: Zoe 💙
"""

from .config import settings, get_kb_dir, get_static_dir
from . database import Database, get_database
from .schemas import (
    ScanRequest,
    BatchScanRequest,
    FrameScanRequest,
    VerificationResponse,
    PartsListResponse,
    KBEntryResponse,
    ErrorResponse
)
from .models import VerificationLog, KBEntryModel, AgentLog

__all__ = [
    # Config
    "settings",
    "get_kb_dir",
    "get_static_dir",
    
    # Database
    "Database",
    "get_database",
    
    # Request schemas
    "ScanRequest",
    "BatchScanRequest",
    "FrameScanRequest",
    
    # Response schemas
    "VerificationResponse",
    "PartsListResponse",
    "KBEntryResponse",
    "ErrorResponse",
    
    # Database models
    "VerificationLog",
    "KBEntryModel",
    "AgentLog",
]