from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

from core.config import settings
from core.auth import require_admin
from pipeline.intelligence.ai_agent import analyze_verification, generate_kb_patterns

router = APIRouter(prefix="/ai", tags=["ai-agent"])


class AnalyzeRequest(BaseModel):
    verdict: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    matches: Dict[str, bool] = {}
    extracted_fields: Dict[str, Any] = {}
    oem_info: Dict[str, str] = {}
    flags: List[str] = []
    algorithm_used: str = "unknown"
    candidate_parts: List[Dict[str, Any]] = []


class PatternGenRequest(BaseModel):
    part_number: str
    oem: str
    package: str = ""


@router.post("/analyze")
async def ai_analyze(req: AnalyzeRequest):
    if not settings.AI_ENABLED:
        raise HTTPException(503, "AI analysis is disabled")
    if not settings.GROQ_API_KEY:
        raise HTTPException(503, "GROQ_API_KEY not configured")

    result = await analyze_verification(req.model_dump())

    if "error" in result:
        raise HTTPException(502, result["error"])

    return {"status": "success", "analysis": result}


@router.post("/generate-patterns")
async def ai_generate_patterns(
    req: PatternGenRequest,
    _user: dict = Depends(require_admin),
):
    if not settings.GROQ_API_KEY:
        raise HTTPException(503, "GROQ_API_KEY not configured")

    patterns = await generate_kb_patterns(
        part_number=req.part_number,
        oem=req.oem,
        package=req.package,
    )

    if patterns is None:
        raise HTTPException(502, "AI pattern generation failed")

    return {"status": "success", "generated_patterns": patterns}


@router.get("/status")
async def ai_status():
    return {
        "ai_enabled": settings.AI_ENABLED,
        "api_key_configured": bool(settings.GROQ_API_KEY),
        "model": settings.AI_MODEL,
        "provider": "groq",
    }
