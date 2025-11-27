"""
Verification Module - IC Authenticity Verification
SIH 25162 - AOI IC Verification System
Author: Saif (CommitSaif11)
Mentor: Zoe 💙
"""

from .verify import verify_with_regex, verify_with_aho
from .scoring import VerificationResult

__all__ = ["verify_with_regex", "verify_with_aho", "VerificationResult"]