"""
Verification Orchestrator - Public API
SIH 25162 - AOI IC Verification System
Author: Saif (CommitSaif11)

"""

from typing import Dict, Optional, Any
from engine.kb_index import KBIndex
from .scoring import VerificationResult
from .regex_verify import verify_with_regex_logic
from .aho_verify import verify_with_aho_logic


def verify_with_regex(
    ocr_results: Dict[str, Dict[str, Any]],
    part_id: str,
    kb_index: KBIndex
) -> VerificationResult:
    """
    Verify IC using RegEx-based direct pattern matching
    
    Use when: Operator knows which IC is being scanned
    
    Args:
        ocr_results: Multi-pass OCR results from ocr.run_ocr_multi_pass()
        part_id: User-specified IC part identifier
        kb_index: Loaded KB index
    
    Returns:
        VerificationResult with verdict and confidence
    
    Example for Saif:
        ```python
        ocr_results = run_ocr_multi_pass(cropped_image)
        result = verify_with_regex(ocr_results, "stm32f030c8t6", kb_index)
        print(f"{result.verdict}: {result.confidence_score:.2f}")
        ```
    """
    return verify_with_regex_logic(ocr_results, part_id, kb_index)


def verify_with_aho(
    ocr_results: Dict[str, Dict[str, Any]],
    part_id: Optional[str],
    kb_index: KBIndex
) -> VerificationResult:
    """
    Verify IC using Aho-Corasick-based auto-detection
    
    Use when: Fully automated mode or operator unsure of IC type
    
    Args:
        ocr_results: Multi-pass OCR results from ocr.run_ocr_multi_pass()
        part_id: Optional user hint (can be None for full automation)
        kb_index: Loaded KB index
    
    Returns:
        VerificationResult with auto-detected part or candidates
    
    Example for Saif (Fully Automated):
        ```python
        ocr_results = run_ocr_multi_pass(cropped_image)
        result = verify_with_aho(ocr_results, None, kb_index)
        print(f"Detected: {result.candidate_parts[0]['part_id']}")
        print(f"{result.verdict}: {result.confidence_score:.2f}")
        ```
    
    Example for Saif (With User Hint):
        ```python
        result = verify_with_aho(ocr_results, "stm32f030c8t6", kb_index)
        # Verifies user selection is correct
        ```
    """
    return verify_with_aho_logic(ocr_results, part_id, kb_index)