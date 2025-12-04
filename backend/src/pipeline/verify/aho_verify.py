"""
Aho-Corasick-Based Verification Algorithm
Intelligent auto-detection of IC part
SIH 25162 - AOI IC Verification System
Author: Saif (CommitSaif11)
Mentor: Zoe 💙
"""

from typing import Dict, Set, List, Optional, Any, Tuple
from engine.kb_index import KBIndex
from .scoring import (
    VerificationResult,
    normalize_ocr_text,
    correct_ocr_confusion,
    AMBIGUITY_THRESHOLD,
    calculate_weighted_score
)
from .regex_verify import verify_with_regex_logic


def find_candidate_parts(
    ocr_results: Dict[str, Dict[str, Any]],
    kb_index: KBIndex,
    min_token_length: int = 5
) -> Set[str]:
    """
    Use Aho-Corasick to find candidate part IDs
    
    Args:
        ocr_results: Multi-pass OCR results
        kb_index: Loaded KB index
        min_token_length: Minimum token length for matching (Saif's filter)
    
    Returns:
        Set of candidate part_ids
    
    Note for Saif:
        Implements your minimum token length filter to avoid spurious matches
    """
    # Combine all OCR texts
    alphanum_text = normalize_ocr_text(ocr_results["full_alphanumeric"]["text"])
    alpha_text = correct_ocr_confusion(ocr_results["alpha_only"]["text"], "alpha")
    
    combined_text = f"{alphanum_text} {alpha_text}"
    
    # Run Aho-Corasick token search
    token_hits = kb_index.aho_search(combined_text)
    
    # Collect candidate part IDs
    candidates = set()
    for token, part_ids in token_hits.items():
        # Apply Saif's minimum token length filter
        # Exception: Logo hints can be 4 chars
        if len(token) >= min_token_length or len(token) >= 4:
            candidates.update(part_ids)
    
    return candidates


def score_candidate(
    ocr_results: Dict[str, Dict[str, Any]],
    part_id: str,
    kb_index: KBIndex
) -> Tuple[VerificationResult, float]:
    """
    Score a single candidate part using regex verification
    
    Args:
        ocr_results: Multi-pass OCR results
        part_id: Candidate part identifier
        kb_index: Loaded KB index
    
    Returns:
        (VerificationResult, weighted_score)
    
    Note for Saif:
        Reuses regex verification logic for consistency
    """
    # Run regex verification on this candidate
    result = verify_with_regex_logic(ocr_results, part_id, kb_index)
    
    # Calculate weighted score
    weighted_score = calculate_weighted_score(result.matches)
    
    return (result, weighted_score)


def filter_weak_candidates(
    scored_candidates: List[Tuple[str, VerificationResult, float]]
) -> List[Tuple[str, VerificationResult, float]]:
    """
    Remove candidates with insufficient evidence
    
    Args:
        scored_candidates: List of (part_id, result, score) tuples
    
    Returns:
        Filtered list of strong candidates
    
    Note for Saif:
        Implements your logo-only and generic lot code filtering
    """
    strong_candidates = []
    
    for part_id, result, score in scored_candidates:
        matches = result.matches
        
        # Require at least one of:
        # 1. Part code match (strongest evidence)
        # 2. Logo + Date + Lot combined
        # 3. Date + Lot (marginal but acceptable)
        
        if matches.get("part_code_match", False):
            # Strong evidence - keep
            strong_candidates.append((part_id, result, score))
        
        elif (matches.get("logo_hint_match", False) and
              matches.get("date_code_match", False) and
              matches.get("lot_code_match", False)):
            # Combined evidence - acceptable
            strong_candidates.append((part_id, result, score))
        
        elif (matches.get("date_code_match", False) and
              matches.get("lot_code_match", False)):
            # Marginal evidence - keep with flag
            result.flags.append("MARGINAL_EVIDENCE")
            strong_candidates.append((part_id, result, score))
    
    return strong_candidates


def verify_with_aho_logic(
    ocr_results: Dict[str, Dict[str, Any]],
    user_part_id: Optional[str],
    kb_index: KBIndex
) -> VerificationResult:
    """
    Main Aho-Corasick verification algorithm
    
    Args:
        ocr_results: Multi-pass OCR results
        user_part_id: Optional user-specified part (can be None for full automation)
        kb_index: Loaded KB index
    
    Returns:
        VerificationResult with auto-detected part or multiple candidates
    
    Workflow for Saif:
        1. Find candidate parts via Aho-Corasick token search
        2. If user_part_id provided, verify it's in candidates
        3. Score all candidates using regex verification
        4. Filter weak evidence candidates
        5. Return best match or flag ambiguity
    """
    # Step 1: Find candidates
    candidates = find_candidate_parts(ocr_results, kb_index)
    
    if not candidates:
        # No matches found
        return VerificationResult(
            verdict="FAKE",
            confidence_score=0.10,
            algorithm_used="aho_corasick",
            flags=["NO_CANDIDATES_FOUND"],
            matches={},
            extracted_fields={},
            candidate_parts=[]
        )
    
    # Step 2: If user specified part_id, check if it's in candidates
    user_override = False
    if user_part_id and user_part_id not in candidates:
        # User-specified part not in auto-detected candidates
        # Add it anyway but flag for review
        candidates.add(user_part_id)
        user_override = True
    
    # Step 3: Score all candidates
    scored_candidates = []
    for part_id in candidates:
        result, weighted_score = score_candidate(ocr_results, part_id, kb_index)
        scored_candidates.append((part_id, result, weighted_score))
    
    # Step 4: Filter weak evidence (Saif's requirement)
    strong_candidates = filter_weak_candidates(scored_candidates)
    
    if not strong_candidates:
        # All candidates had weak evidence
        return VerificationResult(
            verdict="UNCERTAIN",
            confidence_score=0.30,
            algorithm_used="aho_corasick",
            flags=["ALL_WEAK_EVIDENCE"],
            matches={},
            extracted_fields={},
            candidate_parts=[{
                "part_id": pid,
                "score": score
            } for pid, _, score in scored_candidates]
        )
    
    # Step 5: Sort by weighted score (descending)
    strong_candidates.sort(key=lambda x: x[2], reverse=True)
    
    best_part_id, best_result, best_score = strong_candidates[0]
    
    # Step 6: Check for ambiguity (industry standard 0.20 threshold)
    if len(strong_candidates) > 1:
        second_score = strong_candidates[1][2]
        score_diff = best_score - second_score
        
        if score_diff < AMBIGUITY_THRESHOLD:
            # Ambiguous - multiple candidates with similar scores
            all_candidates = [{
                "part_id": pid,
                "oem": result.oem_info.get("oem", "Unknown"),
                "part_number": result.oem_info.get("part_number", "Unknown"),
                "score": score,
                "confidence": result.confidence_score
            } for pid, result, score in strong_candidates[:3]]  # Top 3
            
            return VerificationResult(
                verdict="MULTIPLE_CANDIDATES",
                confidence_score=0.0,
                algorithm_used="aho_corasick",
                flags=["AMBIGUOUS_MATCH", f"SCORE_DIFF_{score_diff:.2f}"],
                matches=best_result.matches,
                extracted_fields=best_result.extracted_fields,
                oem_info={},
                candidate_parts=all_candidates,
                requires_admin_review=True
            )
    
    # Step 7: Single best candidate - return result
    best_result.algorithm_used = "aho_corasick"
    best_result.candidate_parts = [{
        "part_id": best_part_id,
        "oem": best_result.oem_info.get("oem", "Unknown"),
        "score": best_score,
        "confidence": best_result.confidence_score
    }]
    
    if user_override:
        best_result.flags.append("USER_OVERRIDE_NOT_IN_CANDIDATES")
    
    return best_result