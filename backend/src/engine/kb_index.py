"""
KB Index: Builds compiled regex and Aho-Corasick trie from KB entries.
SIH 25162 - AOI IC Verification System
Author: Saif (CommitSaif11)

"""

from __future__ import annotations
import re
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass

try:
    import ahocorasick  # pyahocorasick
except ImportError:  # Graceful fallback if not installed
    ahocorasick = None

from .kb_loader import KBEntry, load_kb


@dataclass
class CompiledPatterns:
    """Holds compiled regex patterns for a part."""
    part_code: re.Pattern
    date_code: re.Pattern
    lot_code: re.Pattern


class KBIndex:
    """
    Provides:
      - compiled regex map per part_id
      - Aho-Corasick automaton for fast substring hits (part_number tokens, logo hints, alternatives)
    """

    def __init__(self, entries: List[KBEntry], case_insensitive: bool = True):
        self.entries = entries
        self.regex_map: Dict[str, CompiledPatterns] = {}
        self.token_parts_map: Dict[str, Set[str]] = {}  # token -> set(part_id)
        self.automaton = None

        flags = re.IGNORECASE if case_insensitive else 0
        self._compile_regex(flags)
        self._extract_tokens(case_insensitive)
        self._build_automaton()

    def _compile_regex(self, flags: int) -> None:
        """Compile all regex patterns for each KB entry."""
        for e in self.entries:
            self.regex_map[e.part_id] = CompiledPatterns(
                part_code=re.compile(e.patterns["part_code"], flags=flags),
                date_code=re.compile(e.patterns["date_code"], flags=flags),
                lot_code=re.compile(e.patterns["lot_code"], flags=flags),
            )

    def _extract_tokens(self, case_insensitive: bool) -> None:
        """
        Create plain literal tokens for Aho-Corasick:
          - Split part_number on ' / ' to get alternatives
          - Extract alternatives from part_code pattern if it uses (A|B)
          - Extract simple literals from part_code patterns like \\bSTM32F030C8T6\\b
          - Include logo_hint
        """
        for e in self.entries:
            part_tokens = self._split_part_number(e.part_number)
            alt_tokens = self._extract_alternatives(e.patterns["part_code"])
            simple_token = self._extract_simple_literal(e.patterns["part_code"])
            logo_token = [e.logo_hint] if e.logo_hint else []

            # Combine all tokens
            all_tokens = set(part_tokens + alt_tokens + logo_token)
            if simple_token:
                all_tokens.add(simple_token)

            for token in all_tokens:
                tk = token.lower() if case_insensitive else token
                self.token_parts_map.setdefault(tk, set()).add(e.part_id)

    @staticmethod
    def _split_part_number(part_number: str) -> List[str]:
        """Splits by ' / ' (space slash space) to preserve full tokens."""
        return [t.strip() for t in part_number.split(" / ") if t.strip()]

    @staticmethod
    def _extract_alternatives(part_code_pattern: str) -> List[str]:
        """
        Extract alternatives from patterns like \\b(74HC14|74HCT14)\\b.
        Keep literal content only; no regex meta in tokens.
        If no parentheses or '|', return empty list.
        """
        # Simple heuristic; not full regex parser:
        m = re.search(r"\(([^)]+)\)", part_code_pattern)
        if not m:
            return []
        inside = m.group(1)
        if "|" not in inside:
            return []
        return [seg.strip() for seg in inside.split("|") if seg.strip()]

    @staticmethod
    def _extract_simple_literal(part_code_pattern: str) -> str:
        """
        Extract simple literal from patterns like \\bSTM32F030C8T6\\b.
        
        If pattern contains alternatives (|) or complex regex, return empty string.
        Otherwise, strip common regex anchors (\\b, ^, $) and return literal.
        
        Examples:
          - "\\bSTM32F030C8T6\\b" → "STM32F030C8T6"
          - "\\bINA219\\b" → "INA219"
          - "\\b(74HC14|74HCT14)\\b" → "" (handled by _extract_alternatives)
        """
        # Skip if contains alternatives
        if "|" in part_code_pattern or "(" in part_code_pattern:
            return ""
        
        # Remove common regex anchors and word boundaries
        cleaned = part_code_pattern.replace("\\b", "").replace("^", "").replace("$", "").strip()
        
        # Check if result is alphanumeric (no remaining regex special chars)
        # Allow only letters, numbers, and common IC chars like underscores/hyphens
        if re.match(r'^[A-Za-z0-9_\-]+$', cleaned):
            return cleaned
        
        return ""

    def _build_automaton(self) -> None:
        """Build Aho-Corasick automaton from token map."""
        if ahocorasick is None:
            # Library not installed; skip building automaton.
            return

        automaton = ahocorasick.Automaton()
        for token, part_ids in self.token_parts_map.items():
            automaton.add_word(token, (token, part_ids))
        automaton.make_automaton()
        self.automaton = automaton

    def aho_search(self, text: str) -> Dict[str, Set[str]]:
        """
        Run Aho-Corasick over normalized text.
        Returns mapping token -> set(part_ids).
        """
        if self.automaton is None:
            # Fallback: regex-based word boundary matching (more precise than substring)
            result: Dict[str, Set[str]] = {}
            lowered = text.lower()
            
            for token, part_ids in self.token_parts_map.items():
                # Use word boundary regex for safer matching
                pattern = r'\b' + re.escape(token) + r'\b'
                if re.search(pattern, lowered):
                    result[token] = part_ids
            
            return result

        # Use Aho-Corasick automaton
        matches: Dict[str, Set[str]] = {}
        for _, (token, part_ids) in self.automaton.iter(text.lower()):
            if token not in matches:
                matches[token] = set()
            matches[token].update(part_ids)
        return matches

    def verify_part(self, text: str, part_id: str) -> Dict[str, bool]:
        """
        Apply part_code/date_code/lot_code regex for a single part_id on given text.
        Return dict of boolean matches.
        """
        if part_id not in self.regex_map:
            raise ValueError(f"Unknown part_id: {part_id}")
        
        cp = self.regex_map[part_id]
        return {
            "part_code_match": bool(cp.part_code.search(text)),
            "date_code_match": bool(cp.date_code.search(text)),
            "lot_code_match": bool(cp.lot_code.search(text)),
        }

    def candidate_part_ids(self, text: str) -> Set[str]:
        """
        Derive candidate part IDs using Aho-Corasick token matches.
        """
        hits = self.aho_search(text)
        candidates: Set[str] = set()
        for _, pids in hits.items():
            candidates.update(pids)
        return candidates


def load_kb_index(case_insensitive: bool = True) -> KBIndex:
    """Load KB and build searchable index."""
    entries = load_kb()
    return KBIndex(entries, case_insensitive=case_insensitive)