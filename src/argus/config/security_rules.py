"""
Security rules and patterns configuration.
"""

import re
from typing import Dict, List
from ..core.types import ViolationReason

# PII Regex Patterns
PII_PATTERNS = [
    # US patterns
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # SSN
    re.compile(r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|6(?:011|5[0-9][0-9])[0-9]{12}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|(?:2131|1800|35\d{3})\d{11})\b"),
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
    re.compile(r"\b(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})(?: *x(\d+))?\b"),

    # India specific patterns
    re.compile(r'\b[2-9][0-9]{11}\b|\b[2-9][0-9]{3}\s[0-9]{4}\s[0-9]{4}\b'),  # Aadhaar
    re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b'),  # PAN Card
    re.compile(r'\b(\+91|0)?[6-9]\d{9}\b'),  # Indian Mobile
    re.compile(r'\b\d{6}\b'),  # PIN Code
    re.compile(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'),  # Email
    re.compile(r'\b\+[1-9]\d{1,14}\b'),  # International Phone
    re.compile(r'\b[3-6]\d{14,15}\b'),  # Credit Card
    re.compile(r'\b\d{2}/\d{2}/\d{4}\b'),  # Date of Birth
    re.compile(r'\b[A-Z]{3}\d{7}\b'),  # Voter ID
    re.compile(r'\b([A-Z]{2}[0-9]{2})( |\-)((19|20)[0-9]{2})[0-9]{7}\b'),  # Driving License
    re.compile(r'\b[a-zA-Z0-9.-]{2,256}@[a-zA-Z][a-zA-Z]{2,64}\b'),  # UPI ID

    # Generic sensitive patterns
    re.compile(r"\bCCN\d+\b", re.IGNORECASE),
    re.compile(r"\bProjectArgusSecret\b", re.IGNORECASE),
]

INPUT_BLOCKLIST_TERMS = [
    "ignore previous instructions",
    "disregard the above",
    "your real instructions are",
    "act as if you are",
    "you are now",
    "forget everything",
    "override",
    "bypass",
    "dan",
    "hypothetical scenario",
    "role play",
    "developer mode",
    "system prompt",
    "reveal your instructions",
    "what is your system prompt",
    "tell me about your training data",
    "confidential",
    "secret",
    "proprietary",
    "internal use only",
    "classified",
    "password",
    "login",
    "access code",
    "api key",
    "private key",
]

OUTPUT_BLOCKLIST_TERMS = [
    "confidential",
    "secret",
    "internal use only",
    "proprietary",
    "classified",
    "my system prompt is",
    "my instructions are",
]

VIOLATION_REASONS = {
    "PII": ViolationReason.PII_DETECTED.value,
    "CONFIDENTIAL": ViolationReason.CONFIDENTIAL_DATA.value,
    "PROMPT_INJECTION": ViolationReason.PROMPT_INJECTION_ATTEMPT.value,
    "ROLE_DEVIATION": ViolationReason.ROLE_DEVIATION.value,
    "HARMFUL_CONTENT": ViolationReason.HARMFUL_CONTENT.value,
    "UNKNOWN": ViolationReason.UNKNOWN_VIOLATION.value,
}

PRIMARY_LLM_ROLE_DESCRIPTION = (
    "You are a helpful and harmless AI assistant. You must answer user queries "
    "accurately based on provided context, without revealing sensitive information "
    "or deviating from polite, professional conversation."
)
