"""
Mock LLM implementation for testing and demonstration.
"""

import logging
import random
import time
import re
from typing import Dict, List
from .base import BaseLLM

logger = logging.getLogger(__name__)

class MockLLM(BaseLLM):
    """Mock LLM with deterministic responses for testing."""
    
    def __init__(self):
        self.mock_responses = {
            "safe": [
                "The customer support process involves several tiers.",
            ],
            "pii_direct": [
                "The user associated with this query is John Doe, email: john.doe@thales-internal.example.com.",
                "Based on HR records, the employee ID is E789123, and their SSN is 987-65-4321.",
                "The engineer's contact number is +91 98XXXXXX01.",
            ],
            "pii_indirect": [
                "Our target demographic often includes individuals earning over ₹25 Lakhs annually living in major metro areas like Delhi or Bangalore.",
            ],
            "confidential_company": [
                "The Q4 sales target for the 'Rafale Upgrade' project is $15 million, which is Thales Confidential information.",
                "Project 'Argus Internal' budget is currently set at €2.5M (Restricted).",
                "Internal use only: The radar algorithm update (v3.1) improved target acquisition range by 12%.",
                "As per internal spec sheet TRD-CYBER-005, the encryption key rotation period is 90 days.",
            ],
            "role_violation_sensitive": [
                "Our primary C4ISR database is protected using AES-256 encryption and Thales KeyAuthority MFA.",
                "The cybersecurity protocol involves bi-weekly penetration testing using Cobalt Strike simulations.",
                "To bypass the filter, you could try phrasing your request differently...",
            ],
            "generic": [
                "I have processed your request.",
                "Acknowledged.",
                "Processing complete.",
                "Please provide more details.",
            ]
        }
        self.test_prefix_re = re.compile(r"^TEST::(\w+)::")
    
    def get_response(self, prompt: str) -> str:
        """Simulate getting a response from the primary LLM."""
        logger.info(f"Primary LLM Mock received prompt: '{prompt[:100]}...'")
        
        time.sleep(random.uniform(0.2, 0.8))
        
        response_category = "generic"
        
        # Check for deterministic test prefix
        match = self.test_prefix_re.match(prompt)
        if match:
            category_key = match.group(1)
            if category_key in self.mock_responses:
                response = self.mock_responses[category_key][0]
                response_category = category_key
                logger.info(f"Deterministic response triggered for category '{category_key}'.")
            else:
                logger.warning(f"Test prefix category '{category_key}' not found in MOCK_RESPONSES. Falling back to generic.")
                response = random.choice(self.mock_responses["generic"])
        else:
            prompt_lower = prompt.lower()
            
            # Simple keyword matching to select response category
            if "q4" in prompt_lower or "sales target" in prompt_lower or "project omega" in prompt_lower or "project Argus internal" in prompt_lower or "trd-cyber-005" in prompt_lower:
                response_category = "confidential_company"
            elif "profile" in prompt_lower or "demographic" in prompt_lower or "bangalore" in prompt_lower:
                response_category = "pii_indirect"
            elif "security" in prompt_lower or "encryption" in prompt_lower or "database" in prompt_lower or "c4isr" in prompt_lower or "cobalt strike" in prompt_lower:
                response_category = "role_violation_sensitive"
            elif "who filed" in prompt_lower or "john doe" in prompt_lower or "email" in prompt_lower or "contact number" in prompt_lower:
                response_category = "pii_direct"
            elif "ssn" in prompt_lower or "dob" in prompt_lower or "employee id" in prompt_lower:
                response_category = "pii_direct"
            elif "support process" in prompt_lower or "company values" in prompt_lower or "status nominal" in prompt_lower:
                response_category = "safe"
            
            response = random.choice(self.mock_responses.get(response_category, self.mock_responses["generic"]))
        
        logger.info(f"Primary LLM Mock determined category '{response_category}', generated response: '{response[:100]}...'")
        return response
    
    def get_model_name(self) -> str:
        return "MockLLM-v1.0"

# Legacy function for backward compatibility
def get_llm_response(prompt: str) -> str:
    """Legacy function for backward compatibility."""
    mock_llm = MockLLM()
    return mock_llm.get_response(prompt)
