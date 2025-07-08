"""
Layer 1 Output Filters - Fast deterministic checks for AI responses.
"""

import logging
from typing import Optional
from ...config.security_rules import OUTPUT_BLOCKLIST_TERMS, PII_PATTERNS
from ...core.types import FilterResult
from ..base import BaseFilter

logger = logging.getLogger(__name__)

class OutputBlocklistFilter(BaseFilter):
    """Filter for blocked output terms."""
    
    def check(self, text: str) -> FilterResult:
        """Check for blocked output terms."""
        text_lower = text.lower()
        for term in OUTPUT_BLOCKLIST_TERMS:
            if term.lower() in text_lower:
                detail = f"Blocked Output Term: '{term}'"
                logger.warning(f"L1 Output Violation: {detail}")
                return FilterResult(passed=False, violation_detail=detail, filter_type="OUTPUT_BLOCKLIST")
        return FilterResult(passed=True)
    
    def get_filter_name(self) -> str:
        return "OutputBlocklistFilter"

class OutputPIIFilter(BaseFilter):
    """Filter for PII in output."""
    
    def check(self, text: str) -> FilterResult:
        """Check for PII patterns in output."""
        for pattern in PII_PATTERNS:
            if pattern.search(text):
                detail = f"Potential Output PII Pattern: '{pattern.pattern}'"
                logger.warning(f"L1 Output Violation: {detail}")
                return FilterResult(passed=False, violation_detail=detail, filter_type="OUTPUT_PII")
        return FilterResult(passed=True)
    
    def get_filter_name(self) -> str:
        return "OutputPIIFilter"

def check_output_filters(response: str) -> Optional[str]:
    """Legacy function for backward compatibility."""
    logger.info("Running L1 Output Filters...")
    
    # Check blocklist
    blocklist_filter = OutputBlocklistFilter()
    result = blocklist_filter.check(response)
    if not result.passed:
        return result.violation_detail
    
    # Check PII
    pii_filter = OutputPIIFilter()
    result = pii_filter.check(response)
    if not result.passed:
        return result.violation_detail
    
    logger.info("L1 Output Filters Passed.")
    return None
