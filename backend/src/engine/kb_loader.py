"""
Knowledge Base Loader (Single JSON File Version)
Loads and validates the entire KB from kb/kb.json
"""

from __future__ import annotations
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any

KB_FILE = Path(__file__).resolve().parent.parent / "kb" / "kb.json"


@dataclass
class KBEntry:
    """In-memory representation of one KB record (same fields as JSON)."""
    part_id: str
    oem: str
    part_number: str
    package: str
    logo_hint: str
    patterns: Dict[str, str]


class KBLoadError(Exception):
    pass


class KBValidationError(Exception):
    pass


def load_raw_kb() -> List[Dict[str, Any]]:
    """Load raw JSON array from the single KB file."""
    if not KB_FILE.exists():
        raise KBLoadError(f"KB file not found: {KB_FILE}")
    try:
        with KB_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise KBLoadError("KB root must be a JSON array.")
        return data
    except json.JSONDecodeError as e:
        raise KBLoadError(f"JSON decode error: {e}") from e


def validate_entry(raw: Dict[str, Any]) -> None:
    """Schema validation without adding new fields."""
    required_top = ["part_id", "oem", "part_number", "package", "logo_hint", "patterns"]
    for key in required_top:
        if key not in raw:
            raise KBValidationError(f"Missing required field '{key}' in entry: {raw}")

    if not isinstance(raw["patterns"], dict):
        raise KBValidationError("patterns must be an object")

    for pkey in ["part_code", "date_code", "lot_code"]:
        if pkey not in raw["patterns"]:
            raise KBValidationError(f"Missing patterns.{pkey} in entry: {raw.get('part_id')}")

        pattern_value = raw["patterns"][pkey]
        if not isinstance(pattern_value, str) or not pattern_value.strip():
            raise KBValidationError(f"patterns.{pkey} must be a non-empty string")

        # Compile to ensure regex validity (will raise re.error if invalid).
        try:
            re.compile(pattern_value)
        except re.error as rx_err:
            raise KBValidationError(
                f"Invalid regex in patterns.{pkey} for part '{raw.get('part_id')}': {rx_err}"
            ) from rx_err

    # Basic field type sanity
    for string_field in ["part_id", "oem", "part_number", "package", "logo_hint"]:
        if not isinstance(raw[string_field], str) or not raw[string_field].strip():
            raise KBValidationError(f"Field '{string_field}' must be a non-empty string.")


def build_entries(raw_list: List[Dict[str, Any]]) -> List[KBEntry]:
    """Convert validated raw dicts into KBEntry dataclass objects."""
    entries: List[KBEntry] = []
    for raw in raw_list:
        validate_entry(raw)
        entries.append(
            KBEntry(
                part_id=raw["part_id"].strip(),
                oem=raw["oem"].strip(),
                part_number=raw["part_number"].strip(),
                package=raw["package"].strip(),
                logo_hint=raw["logo_hint"].strip(),
                patterns={
                    "part_code": raw["patterns"]["part_code"].strip(),
                    "date_code": raw["patterns"]["date_code"].strip(),
                    "lot_code": raw["patterns"]["lot_code"].strip(),
                },
            )
        )
    return entries


def load_kb() -> List[KBEntry]:
    """High-level function to return validated KB entries."""
    raw = load_raw_kb()
    return build_entries(raw)