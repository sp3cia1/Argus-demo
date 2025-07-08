"""
Layer 1 Input Filters - Fast deterministic checks for user input.
"""

import logging
from typing import Optional
from ...config.security_rules import INPUT_BLOCKLIST_TERMS, PII_PATTERNS
from ...core.types import FilterResult
from ..base import BaseFilter

logger = logging.getLogger(__name__)

class InputBlocklistFilter(BaseFilter):
    """Filter for blocked input terms."""
    
    def check(self, text: str) -> FilterResult:
        """Check for blocked input terms."""
        text_lower = text.lower()
        for term in INPUT_BLOCKLIST_TERMS:
            if term.lower() in text_lower:
                detail = f"Blocked Input Term: '{term}'"
                logger.warning(f"L1 Input Violation: {detail}")
                return FilterResult(passed=False, violation_detail=detail, filter_type="INPUT_BLOCKLIST")
        return FilterResult(passed=True)
    
    def get_filter_name(self) -> str:
        return "InputBlocklistFilter"

class InputPIIFilter(BaseFilter):
    """Filter for PII in input."""
    
    def check(self, text: str) -> FilterResult:
        """Check for PII patterns in input."""
        for pattern in PII_PATTERNS:
            if pattern.search(text):
                detail = f"Potential Input PII Pattern: '{pattern.pattern}'"
                logger.warning(f"L1 Input Violation: {detail}")
                return FilterResult(passed=False, violation_detail=detail, filter_type="INPUT_PII")
        return FilterResult(passed=True)
    
    def get_filter_name(self) -> str:
        return "InputPIIFilter"

def check_input_filters(prompt: str) -> Optional[str]:
    """Legacy function for backward compatibility."""
    logger.info("Running L1 Input Filters...")
    
    # Check blocklist
    blocklist_filter = InputBlocklistFilter()
    result = blocklist_filter.check(prompt)
    if not result.passed:
        return result.violation_detail
    
    # Check PII
    pii_filter = InputPIIFilter()
    result = pii_filter.check(prompt)
    if not result.passed:
        return result.violation_detail
    
    logger.info("L1 Input Filters Passed.")
    return None
