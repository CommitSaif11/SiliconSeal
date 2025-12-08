"""
API Request and Response Schemas
Pydantic models for FastAPI validation
SIH 25162 - AOI IC Verification System
Author: Saif (CommitSaif11)

"""

from datetime import datetime, timezone  # UPDATED
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator


# ============================================================
# REQUEST SCHEMAS (Input Validation)
# ============================================================

class ScanRequest(BaseModel):
    """
    Request schema for /scan endpoint
    
    Note for Saif:
        Validates incoming scan requests
    """
    part_id: Optional[str] = Field(None, description="IC part identifier (optional for auto-detection)")
    algorithm: str = Field("aho_corasick", description="'regex' or 'aho_corasick'")
    ocr_psm: int = Field(6, ge=0, le=13, description="Tesseract PSM mode")
    
    @validator('algorithm')
    def validate_algorithm(cls, v):
        if v not in ["regex", "aho_corasick"]:
            raise ValueError("algorithm must be 'regex' or 'aho_corasick'")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "part_id": "stm32f030c8t6",
                "algorithm": "aho_corasick",
                "ocr_psm": 6
            }
        }


class BatchScanRequest(BaseModel):
    """Request schema for /scan/batch endpoint"""
    part_id: str = Field(..., description="IC part identifier for all images")
    algorithm: str = Field("regex", description="'regex' or 'aho_corasick'")
    
    @validator('algorithm')
    def validate_algorithm(cls, v):
        if v not in ["regex", "aho_corasick"]:
            raise ValueError("algorithm must be 'regex' or 'aho_corasick'")
        return v


class FrameScanRequest(BaseModel):
    """Request schema for /scan/frame endpoint"""
    frame: str = Field(..., description="Base64 encoded image")
    part_id: Optional[str] = Field(None, description="IC part identifier")
    algorithm: str = Field("aho_corasick", description="'regex' or 'aho_corasick'")


# ============================================================
# RESPONSE SCHEMAS (Output Validation)
# ============================================================

class VerificationResponse(BaseModel):
    """
    Response schema for verification results
    
    Note for Saif:
        Standardized output for all verification endpoints
    """
    status: str = "success"
    verdict: str = Field(..., description="GENUINE, FAKE, UNCERTAIN, MULTIPLE_CANDIDATES")
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    matches: Dict[str, bool]
    extracted_fields: Dict[str, Any]
    oem_info: Optional[Dict[str, str]] = None
    algorithm_used: str
    flags: List[str] = []
    requires_admin_review: bool = False
    candidate_parts: Optional[List[Dict[str, Any]]] = None
    processing_time_ms: Optional[float] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  # CHANGED
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
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
                    "part_number": "STM32F030C8T6",
                    "package": "LQFP-48"
                },
                "algorithm_used": "aho_corasick",
                "flags": ["LOGO_VERIFIED"],
                "processing_time_ms": 856.3
            }
        }


class PartsListResponse(BaseModel):
    """Response schema for /parts endpoint"""
    status: str = "success"
    count: int
    parts: List[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "count": 16,
                "parts": ["stm32f030c8t6", "w25q64jvs1q", "ina219"]
            }
        }


class KBEntryResponse(BaseModel):
    """Response schema for /kb/{part_id} endpoint"""
    status: str = "success"
    access: str = "admin"
    part_id: str
    data: Dict[str, Any]
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "access": "admin",
                "part_id": "stm32f030c8t6",
                "data": {
                    "oem": "STMicroelectronics",
                    "part_number": "STM32F030C8T6",
                    "patterns": {}
                }
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response schema"""
    status: str = "error"
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  # CHANGED