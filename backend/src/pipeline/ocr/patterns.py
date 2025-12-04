"""
IC Part Code Pattern Database
SIH 25162 - AOI IC Verification System
Author: Saif (CommitSaif11)
Mentor: Zoe 💙

Regex patterns for intelligent multi-line part code merging. 
Covers top 15 IC manufacturers (~85% market share).
"""

import re
from typing import Tuple, Optional


# ============================================================================
# PART CODE PATTERNS
# ============================================================================

IC_PATTERNS = {
    # STMicroelectronics
    "STM32": r"^STM32[A-Z][0-9]{1,3}[A-Z0-9]{4,8}$",
    "STM8": r"^STM8[A-Z][0-9]{2,4}[A-Z0-9]{2,6}$",
    
    # Microchip/Atmel
    "ATMEGA": r"^ATMEGA[0-9]{2,4}[A-Z]{0,3}[0-9]{0,2}$",
    "ATTINY": r"^ATTINY[0-9]{2,4}[A-Z]{0,2}$",
    "PIC": r"^PIC[0-9]{2}[A-Z][0-9]{2,4}[A-Z]{0,2}$",
    "DSPIC": r"^DSPIC[0-9]{2}[A-Z]{1,2}[0-9]{3,4}$",
    
    # Espressif
    "ESP32": r"^ESP32[A-Z0-9\-]{0,10}$",
    "ESP8266": r"^ESP8266[A-Z0-9]{0,6}$",
    
    # Nordic Semiconductor
    "NRF": r"^NRF[0-9]{4,5}[A-Z0-9]{0,4}$",
    
    # Texas Instruments
    "TPS": r"^TPS[0-9]{4,5}[A-Z0-9]{0,4}$",
    "TLV": r"^TLV[0-9]{3,5}[A-Z0-9]{0,3}$",
    "MSP430": r"^MSP430[A-Z0-9]{4,8}$",
    
    # NXP
    "LPC": r"^LPC[0-9]{3,4}[A-Z0-9]{0,4}$",
    "MK": r"^MK[0-9]{2}[A-Z]{2}[0-9]{3,5}[A-Z]{0,3}$",
    
    # Analog Devices
    "AD": r"^AD[0-9]{3,5}[A-Z]{0,4}$",
    "ADXL": r"^ADXL[0-9]{3}[A-Z0-9]{0,3}$",
    
    # Infineon
    "XMC": r"^XMC[0-9]{4}[A-Z0-9]{0,6}$",
    
    # Cypress
    "CY": r"^CY[0-9]{4,5}[A-Z0-9]{0,4}$",
    
    # Renesas
    "R5F": r"^R5F[0-9]{4,5}[A-Z0-9]{0,4}$",
    
    # Silicon Labs
    "EFM32": r"^EFM32[A-Z]{2}[0-9]{3}[A-Z0-9]{0,4}$",
}


# ============================================================================
# PATTERN MATCHING FUNCTIONS
# ============================================================================

def matches_known_pattern(text: str) -> Tuple[bool, Optional[str]]:
    """
    Check if text matches any known IC part code pattern.
    
    Args:
        text: Candidate part code string (e.g., "STM32F030C8T6")
        
    Returns:
        (matched, pattern_name)
        - matched: True if any pattern matches
        - pattern_name: Name of matched pattern (e.g., "STM32") or None
        
    Example:
        >>> matches_known_pattern("STM32F030C8T6")
        (True, "STM32")
        
        >>> matches_known_pattern("UNKNOWN123")
        (False, None)
    """
    text_clean = text.strip().upper().replace(" ", "")
    
    for pattern_name, regex in IC_PATTERNS.items():
        if re.match(regex, text_clean, re.IGNORECASE):
            return True, pattern_name
    
    return False, None


def is_valid_part_code_format(text: str, min_length: int = 6) -> bool:
    """
    Check if text has valid part code characteristics.
    
    Validates:
    - Minimum length
    - Alphanumeric only
    - Contains both letters and numbers
    - Starts with letter
    
    Args:
        text: Text to validate
        min_length: Minimum required length (default: 6)
        
    Returns:
        True if text resembles a part code
        
    Example:
        >>> is_valid_part_code_format("STM32F")
        True
        
        >>> is_valid_part_code_format("123")
        False (no letters)
    """
    text_clean = text.strip().replace(" ", "")
    
    # Length check
    if len(text_clean) < min_length:
        return False
    
    # Must be alphanumeric
    if not text_clean.isalnum():
        return False
    
    # Must start with letter (manufacturer prefix)
    if not text_clean[0].isalpha():
        return False
    
    # Must contain both letters and numbers
    has_letter = any(c.isalpha() for c in text_clean)
    has_number = any(c.isdigit() for c in text_clean)
    
    if not (has_letter and has_number):
        return False
    
    return True


def get_manufacturer_prefix(part_code: str) -> Optional[str]:
    """
    Extract manufacturer prefix from part code. 
    
    Args:
        part_code: Full part code (e.g., "STM32F030C8T6")
        
    Returns:
        Manufacturer prefix (e.g., "STM32") or None
        
    Example:
        >>> get_manufacturer_prefix("STM32F030C8T6")
        "STM32"
        
        >>> get_manufacturer_prefix("ATMEGA328P")
        "ATMEGA"
    """
    matched, pattern_name = matches_known_pattern(part_code)
    
    if matched:
        return pattern_name
    
    # Fallback: extract leading alphabetic characters
    prefix = ""
    for char in part_code:
        if char.isalpha():
            prefix += char
        else:
            break
    
    return prefix if len(prefix) >= 2 else None


# ============================================================================
# TESTING (Remove in production)
# ============================================================================

if __name__ == "__main__":
    # Test cases
    test_codes = [
        "STM32F030C8T6",
        "ATMEGA328P",
        "ESP32-WROOM",
        "NRF52840",
        "PIC16F877A",
        "UNKNOWN123",
    ]
    
    print("Pattern Matching Tests:")
    print("=" * 60)
    for code in test_codes:
        matched, pattern = matches_known_pattern(code)
        valid = is_valid_part_code_format(code)
        prefix = get_manufacturer_prefix(code)
        
        print(f"{code:<20} | Match: {matched:<5} | Pattern: {pattern or 'None':<10} | Prefix: {prefix or 'None'}")
    print("=" * 60)