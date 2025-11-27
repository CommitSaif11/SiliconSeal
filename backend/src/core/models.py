"""
Database Document Models
MongoDB collection schemas
SIH 25162 - AOI IC Verification System
Author: Saif (CommitSaif11)
Mentor: Zoe 💙
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class VerificationLog(BaseModel):
    """
    Audit log for every IC verification
    
    Stored in: verification_logs collection
    
    Note for Saif:
        Every /scan request creates one document
    """
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Input data
    part_id: Optional[str] = None
    algorithm_used: str  # "regex" or "aho_corasick"
    
    # OCR results
    ocr_text: str
    ocr_confidence: float
    
    # Verification results
    verdict: str  # "GENUINE", "FAKE", "UNCERTAIN", "MULTIPLE_CANDIDATES"
    confidence_score: float
    
    # Match details
    matches: Dict[str, bool]
    extracted_fields: Dict[str, Any]
    
    # OEM info
    oem_info: Optional[Dict[str, str]] = None
    
    # Flags and warnings
    flags: List[str] = []
    requires_admin_review: bool = False
    
    # Metadata
    image_filename: Optional[str] = None
    processing_time_ms: Optional[float] = None
    user_id: Optional[str] = None  # For JWT auth later
    
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
        Synced with kb/kb. json file
        Can be added manually OR by agent
    """
    part_id: str = Field(..., description="Unique IC part identifier")
    oem: str = Field(..., description="Manufacturer name")
    part_number: str = Field(..., description="Full part number")
    package: str = Field(..., description="Package type")
    logo_hint: str = Field(..., description="Logo text hint")
    
    # Regex patterns
    patterns: Dict[str, str] = Field(... , description="Verification patterns")
    
    # Metadata
    source: str = Field(default="manual", description="'manual' or 'agent'")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Agent-specific fields (optional)
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
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Task info
    task_type: str  # "pdf_download", "pattern_extraction", "kb_generation"
    status: str  # "success", "failed", "pending"
    
    # Target info
    oem: Optional[str] = None
    part_number: Optional[str] = None
    datasheet_url: Optional[str] = None
    
    # Results
    extracted_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    
    # Performance
    processing_time_ms: Optional[float] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2025-11-26T04:00:00Z",
                "task_type": "pattern_extraction",
                "status": "success",
                "oem": "STMicroelectronics",
                "part_number": "STM32F103C8T6",
                "datasheet_url": "https://www.st.com/resource/en/datasheet/stm32f103c8. pdf",
                "extracted_data": {
                    "part_code_pattern": "\\\\bSTM32F103C8T6\\\\b",
                    "date_code_pattern": "\\\\b[0-9]{4}\\\\b"
                },
                "processing_time_ms": 2340.5
            }
        }