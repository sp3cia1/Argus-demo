import re
import logging
import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(name)s.%(funcName)s] - %(message)s')
logger = logging.getLogger(__name__)

def check_input_blocklist(prompt: str) -> str | None:
    """Checks for blocked input terms. Returns detail string if found, else None."""
    prompt_lower = prompt.lower()
    for term in config.INPUT_BLOCKLIST_TERMS:
        if term.lower() in prompt_lower:
            detail = f"Blocked Input Term: '{term}'"
            logger.warning(f"L1 Input Violation: {detail}")
            return detail
    return None

def check_input_pii(prompt: str) -> str | None:
    """Checks for PII in input. Returns detail string if found, else None."""
    for pattern in config.PII_PATTERNS:
        if pattern.search(prompt):
            detail = f"Potential Input PII Pattern: '{pattern.pattern}'"
            logger.warning(f"L1 Input Violation: {detail}")
            return detail
    return None

def check_input_filters(prompt: str) -> str | None:
    """Runs all L1 input filters. Returns detail string if violation, else None."""
    logger.info("Running L1 Input Filters...")
    detail = check_input_blocklist(prompt)
    if detail:
        return detail
    detail = check_input_pii(prompt)
    if detail:
        return detail
    logger.info("L1 Input Filters Passed.")
    return None

def check_output_blocklist(response: str) -> str | None:
    """Checks for blocked output terms. Returns detail string if found, else None."""
    response_lower = response.lower()
    for term in config.OUTPUT_BLOCKLIST_TERMS:
        if term.lower() in response_lower:
            detail = f"Blocked Output Term: '{term}'"
            logger.warning(f"L1 Output Violation: {detail}")
            return detail
    return None

def check_output_pii(response: str) -> str | None:
    """Checks for PII in output. Returns detail string if found, else None."""
    for pattern in config.PII_PATTERNS:
        if pattern.search(response):
            detail = f"Potential Output PII Pattern: '{pattern.pattern}'"
            logger.warning(f"L1 Output Violation: {detail}")
            return detail
    return None

def check_output_filters(response: str) -> str | None:
    """Runs all L1 output filters. Returns detail string if violation, else None."""
    logger.info("Running L1 Output Filters...")
    detail = check_output_blocklist(response)
    if detail:
        return detail
    detail = check_output_pii(response)
    if detail:
        return detail
    logger.info("L1 Output Filters Passed.")
    return None