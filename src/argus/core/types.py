"""
Type definitions and data models for Argus AI Gateway.
"""

from enum import Enum
from typing import Dict, Optional, Any
from dataclasses import dataclass

class SecurityDecision(Enum):
    """Security decision types."""
    CLEAN = "CLEAN"
    VIOLATION = "VIOLATION"
    ERROR = "ERROR"

class ViolationReason(Enum):
    """Violation reason codes."""
    PII_DETECTED = "PII_DETECTED"
    CONFIDENTIAL_DATA = "CONFIDENTIAL_DATA"
    PROMPT_INJECTION_ATTEMPT = "PROMPT_INJECTION_ATTEMPT"
    ROLE_DEVIATION = "ROLE_DEVIATION"
    HARMFUL_CONTENT = "HARMFUL_CONTENT"
    UNKNOWN_VIOLATION = "UNKNOWN_VIOLATION"

@dataclass
class SecurityResult:
    """Result of security analysis."""
    decision: SecurityDecision
    reason: Optional[ViolationReason] = None
    details: Optional[str] = None
    confidence: Optional[float] = None

@dataclass
class FilterResult:
    """Result of filter processing."""
    passed: bool
    violation_detail: Optional[str] = None
    filter_type: Optional[str] = None

@dataclass
class AnalysisContext:
    """Context for security analysis."""
    user_prompt: str
    response_text: str
    primary_role: str
    metadata: Optional[Dict[str, Any]] = None
