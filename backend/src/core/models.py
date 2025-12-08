"""
Database Document Models
MongoDB collection schemas
SIH 25162 - AOI IC Verification System
Author: Saif (CommitSaif11)

"""

from datetime import datetime, timezone  # UPDATED
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class VerificationLog(BaseModel):
    """
    Audit log for every IC verification
    
    Stored in: verification_logs collection
    
    Note for Saif:
        Every /scan request creates one document
    """
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  # CHANGED
    
    part_id: Optional[str] = None
    algorithm_used: str
    ocr_text: str
    ocr_confidence: float
    verdict: str
    confidence_score: float
    matches: Dict[str, bool]
    extracted_fields: Dict[str, Any]
    oem_info: Optional[Dict[str, str]] = None
    flags: List[str] = []
    requires_admin_review: bool = False
    image_filename: Optional[str] = None
    processing_time_ms: Optional[float] = None
    user_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2025-11-26T03:45:00Z",
                "part_id": "stm32f030c8t6",
                "algorithm_used": "aho_corasick",
                "ocr_text": "STM32F030C8T6 2347 A3B5C",
                "ocr_confidence": 0.87,
                "verdict": "GENUINE",
                "confidence_score": 0.95,
                "matches": {
                    "part_code_match": True,
                    "date_code_match": True,
                    "lot_code_match": True
                },
                "extracted_fields": {
                    "part_code": "STM32F030C8T6",
                    "date_code": "2347",
                    "lot_code": "A3B5C"
                },
                "oem_info": {
                    "oem": "STMicroelectronics",
                    "part_number": "STM32F030C8T6"
                },
                "flags": ["LOGO_VERIFIED"],
                "processing_time_ms": 856.3
            }
        }


class KBEntryModel(BaseModel):
    """
    Knowledge Base entry stored in MongoDB
    
    Stored in: kb_entries collection
    
    Note for Saif:
        Synced with kb/kb.json file
        Can be added manually OR by agent
    """
    part_id: str = Field(..., description="Unique IC part identifier")
    oem: str = Field(..., description="Manufacturer name")
    part_number: str = Field(..., description="Full part number")
    package: str = Field(..., description="Package type")
    logo_hint: str = Field(..., description="Logo text hint")
    patterns: Dict[str, str] = Field(..., description="Verification patterns")
    source: str = Field(default="manual", description="'manual' or 'agent'")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  # CHANGED
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  # CHANGED
    datasheet_url: Optional[str] = None
    agent_confidence: Optional[float] = None
    verified_by_admin: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "part_id": "stm32f030c8t6",
                "oem": "STMicroelectronics",
                "part_number": "STM32F030C8T6",
                "package": "LQFP-48 / QFN-48",
                "logo_hint": "STMI",
                "patterns": {
                    "part_code": "\\\\bSTM32F030C8T6\\\\b",
                    "date_code": "\\\\b[0-9]{2}[0-5][0-9]\\\\b",
                    "lot_code": "\\\\b[0-9A-Z]{3,6}\\\\b"
                },
                "source": "manual",
                "verified_by_admin": True
            }
        }


class AgentLog(BaseModel):
    """
    Agent activity log for PDF scraping
    
    Stored in: agent_logs collection
    
    Note for Saif:
        Track all agent operations for debugging
    """
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  # CHANGED
    task_type: str
    status: str
    oem: Optional[str] = None
    part_number: Optional[str] = None
    datasheet_url: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    processing_time_ms: Optional[float] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2025-11-26T04:00:00Z",
                "task_type": "pattern_extraction",
                "status": "success",
                "oem": "STMicroelectronics",
                "part_number": "STM32F103C8T6",
                "datasheet_url": "https://www.st.com/resource/en/datasheet/stm32f103c8.pdf",
                "extracted_data": {
                    "part_code_pattern": "\\\\bSTM32F103C8T6\\\\b",
                    "date_code_pattern": "\\\\b[0-9]{4}\\\\b"
                },
                "processing_time_ms": 2340.5
            }
        }