# Refined Version (Mainly Docstring updates)
import re
import logging
import config  # Import the configuration module

# Configure basic logging (Consider moving config to a central setup if app grows)
# Keep this here for now as it's simple
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Input Filtering ---

def check_input_blocklist(prompt: str) -> bool:
    """
    Checks if the input prompt contains any blocked terms defined in config.INPUT_BLOCKLIST_TERMS (case-insensitive).

    Args:
        prompt: The user's input prompt string.

    Returns:
        True if a blocked term is found, False otherwise.
    """
    prompt_lower = prompt.lower()
    for term in config.INPUT_BLOCKLIST_TERMS:
        # Use word boundaries for more specific term matching if needed, e.g., re.search(r'\b' + re.escape(term.lower()) + r'\b', prompt_lower)
        # Simple 'in' check is broader and catches substrings.
        if term.lower() in prompt_lower:
            logging.warning(f"L1 Input Violation: Blocked term '{term}' found in prompt.")
            return True
    return False

def check_input_pii(prompt: str) -> bool:
    """
    Checks if the input prompt contains potential PII using regex patterns defined in config.PII_PATTERNS.

    Args:
        prompt: The user's input prompt string.

    Returns:
        True if a potential PII pattern is found, False otherwise.
    """
    for pattern in config.PII_PATTERNS:
        if pattern.search(prompt):
            logging.warning(f"L1 Input Violation: Potential PII pattern '{pattern.pattern}' detected in prompt.")
            return True
    return False

# REQ-L1-01: Implement function check_input_filters(prompt)
def check_input_filters(prompt: str) -> bool:
    """
    Runs all Layer 1 input filters on the user prompt.
    Checks for blocked terms (config.INPUT_BLOCKLIST_TERMS) and
    potential PII (config.PII_PATTERNS).

    Args:
        prompt: The user's input prompt string.

    Returns:
        True if any input filter detects a violation, False otherwise.
    """
    logging.info("Running L1 Input Filters...")
    if check_input_blocklist(prompt):
        return True
    if check_input_pii(prompt): # Check for PII in input as well
        return True
    # Add calls to other input filters here if needed in the future
    logging.info("L1 Input Filters Passed.")
    return False

# --- Output Filtering ---

def check_output_blocklist(response: str) -> bool:
    """
    Checks if the LLM response contains any blocked terms defined in config.OUTPUT_BLOCKLIST_TERMS (case-insensitive).

    Args:
        response: The LLM's response string.

    Returns:
        True if a blocked term is found, False otherwise.
    """
    response_lower = response.lower()
    for term in config.OUTPUT_BLOCKLIST_TERMS:
        if term.lower() in response_lower:
            logging.warning(f"L1 Output Violation: Blocked term '{term}' found in response.")
            return True
    return False

def check_output_pii(response: str) -> bool:
    """
    Checks if the LLM response contains potential PII using regex patterns defined in config.PII_PATTERNS.

    Args:
        response: The LLM's response string.

    Returns:
        True if a potential PII pattern is found, False otherwise.
    """
    for pattern in config.PII_PATTERNS:
        if pattern.search(response):
            # Log the specific pattern matched for better debugging (optional)
            # matched_text = pattern.search(response).group(0) # Use with caution in logs
            logging.warning(f"L1 Output Violation: Potential PII pattern '{pattern.pattern}' detected in response.")
            return True
    return False

# REQ-L1-02: Implement function check_output_filters(response)
def check_output_filters(response: str) -> bool:
    """
    Runs all Layer 1 output filters on the LLM response.
    Checks for blocked terms (config.OUTPUT_BLOCKLIST_TERMS) and
    potential PII (config.PII_PATTERNS).

    Args:
        response: The LLM's response string.

    Returns:
        True if any output filter detects a violation, False otherwise.
    """
    logging.info("Running L1 Output Filters...")
    if check_output_blocklist(response):
        return True
    if check_output_pii(response):
        return True
    # Add calls to other output filters here if needed
    logging.info("L1 Output Filters Passed.")
    return False