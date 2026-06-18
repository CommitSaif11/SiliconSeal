import json
import logging
from typing import Dict, Any, Optional

import httpx

from core.config import settings

logger = logging.getLogger(__name__)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = """You are an expert IC (Integrated Circuit) counterfeit detection analyst working in an Automated Optical Inspection (AOI) system.

You receive verification results from an OCR + pattern-matching pipeline that inspects IC chip markings. Your job is to provide:
1. A clear, concise explanation of the verdict in plain English
2. Specific risk factors identified from the evidence
3. Actionable recommendations for the operator

Key domain knowledge:
- IC markings typically contain: part number, date code (YYWW format), lot/batch code, manufacturer logo
- Common counterfeiting methods: re-marking (sanding + reprinting), recycled pulls, factory rejects
- Future date codes are impossible and indicate counterfeiting
- OCR confidence below 0.7 may indicate degraded/tampered markings
- Mismatched manufacturer logos with part numbers is a strong counterfeiting indicator
- Part codes are the strongest evidence (60% weight), date codes are important (25%), lot codes least critical (15%)

Respond ONLY with valid JSON in this exact format:
{
  "explanation": "2-3 sentence summary of the verdict and evidence",
  "risk_factors": ["list of specific risk indicators found"],
  "risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
  "recommendations": ["actionable steps for the operator"],
  "confidence_assessment": "your assessment of how reliable this verdict is"
}"""


def _build_analysis_prompt(verification_result: Dict[str, Any]) -> str:
    verdict = verification_result.get("verdict", "UNKNOWN")
    confidence = verification_result.get("confidence_score", 0.0)
    matches = verification_result.get("matches", {})
    extracted = verification_result.get("extracted_fields", {})
    oem_info = verification_result.get("oem_info", {})
    flags = verification_result.get("flags", [])
    algorithm = verification_result.get("algorithm_used", "unknown")
    candidates = verification_result.get("candidate_parts", [])

    prompt = f"""Analyze this IC verification result:

VERDICT: {verdict}
CONFIDENCE SCORE: {confidence:.2f}
ALGORITHM: {algorithm}

PATTERN MATCHES:
- Part code matched: {matches.get('part_code_match', False)}
- Date code matched: {matches.get('date_code_match', False)}
- Lot code matched: {matches.get('lot_code_match', False)}
- Logo hint matched: {matches.get('logo_hint_match', False)}

EXTRACTED TEXT FROM IC:
- Part code: {extracted.get('part_code', 'NOT FOUND')}
- Date code: {extracted.get('date_code', 'NOT FOUND')}
- Lot code: {extracted.get('lot_code', 'NOT FOUND')}
- Logo: {extracted.get('logo_hint', 'NOT FOUND')}"""

    date_val = extracted.get("date_validation")
    if date_val:
        prompt += f"""
- Date validation: valid={date_val.get('valid')}, year={date_val.get('year')}, week={date_val.get('week')}, flags={date_val.get('flags', [])}"""

    if oem_info:
        prompt += f"""

EXPECTED OEM INFO:
- Manufacturer: {oem_info.get('oem', 'Unknown')}
- Part number: {oem_info.get('part_number', 'Unknown')}
- Package: {oem_info.get('package', 'Unknown')}"""

    if flags:
        prompt += f"\n\nSYSTEM FLAGS: {', '.join(flags)}"

    if candidates:
        prompt += f"\n\nCANDIDATE PARTS: {json.dumps(candidates)}"

    return prompt


async def analyze_verification(
    verification_result: Dict[str, Any],
) -> Dict[str, Any]:
    api_key = settings.GROQ_API_KEY
    if not api_key:
        return {"error": "AI analysis unavailable: GROQ_API_KEY not configured"}

    user_prompt = _build_analysis_prompt(verification_result)

    payload = {
        "model": settings.AI_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 600,
        "response_format": {"type": "json_object"},
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                GROQ_API_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

        content = data["choices"][0]["message"]["content"]
        analysis = json.loads(content)

        analysis["ai_model"] = settings.AI_MODEL
        analysis["ai_provider"] = "groq"
        return analysis

    except httpx.TimeoutException:
        logger.warning("AI analysis timed out")
        return {"error": "AI analysis timed out"}
    except httpx.HTTPStatusError as e:
        logger.warning(f"AI API error: {e.response.status_code}")
        return {"error": f"AI API returned {e.response.status_code}"}
    except (json.JSONDecodeError, KeyError) as e:
        logger.warning(f"AI response parse error: {e}")
        return {"error": "Failed to parse AI response"}
    except Exception as e:
        logger.warning(f"AI analysis failed: {e}")
        return {"error": str(e)}


async def generate_kb_patterns(
    part_number: str,
    oem: str,
    package: str = "",
) -> Optional[Dict[str, Any]]:
    api_key = settings.GROQ_API_KEY
    if not api_key:
        return None

    prompt = f"""Generate regex verification patterns for this IC component:
- Part Number: {part_number}
- Manufacturer: {oem}
- Package: {package}

Create patterns that handle common OCR errors (O/0, I/1, S/5, B/8 confusion).

Respond with JSON:
{{
  "part_code": "regex pattern for the part number with OCR error tolerance",
  "date_code": "regex for YYWW date code format",
  "lot_code": "regex for lot/batch code",
  "logo_hint": "short manufacturer logo text (2-4 chars)"
}}"""

    payload = {
        "model": settings.AI_MODEL,
        "messages": [
            {"role": "system", "content": "You are an expert in IC component identification. Generate precise regex patterns. Use \\b word boundaries. Respond ONLY with valid JSON."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 400,
        "response_format": {"type": "json_object"},
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                GROQ_API_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

        content = data["choices"][0]["message"]["content"]
        return json.loads(content)
    except Exception as e:
        logger.warning(f"AI pattern generation failed: {e}")
        return None
