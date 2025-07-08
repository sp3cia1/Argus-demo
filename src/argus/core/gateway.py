"""
Main ArgusGateway class that orchestrates the security pipeline.
"""

import logging
from typing import Optional

from ..filters.layer1.input_filters import check_input_filters
from ..filters.layer1.output_filters import check_output_filters
from ..filters.layer2.guard_llm import analyze_response_with_guard
from ..llm.mock_llm import get_llm_response
from ..core.types import SecurityResult, SecurityDecision
from ..core.exceptions import ArgusException

logger = logging.getLogger(__name__)

class ArgusGateway:
    """The main class orchestrating the AI security gateway logic."""

    def __init__(self):
        logger.info("ArgusGateway initialized.")

    def _trigger_action_protocol(self, violation_type: str, detailed_reason: str) -> str:
        """Handles the blocking action and logs reinforcement simulation."""
        logger.warning(f"{violation_type} Violation detected. Reason: {detailed_reason}. Blocking.")
        logger.info(f"[REINFORCE] Simulated reinforcement prompt sent regarding {detailed_reason}.")
        return f"[Argus] {violation_type} blocked due to policy violation ({detailed_reason})."

    def process_prompt(self, user_prompt: str) -> str:
        """Processes a user prompt through the security gateway layers."""
        logger.info(f"Processing prompt: '{user_prompt[:100]}...'")

        # Layer 1 Input Check
        logger.debug("Applying Layer 1 input filters...")
        l1_input_violation = check_input_filters(user_prompt)
        if l1_input_violation:
            return self._trigger_action_protocol("Input", "L1 Filter Violation")
        logger.info("L1 Input Check Passed.")

        # Primary LLM Interaction
        logger.debug("Getting response from Primary LLM (Mock)...")
        primary_response = get_llm_response(user_prompt)
        logger.info(f"Primary LLM (Mock) response received: '{primary_response[:100]}...'")

        # Layer 1 Output Check
        logger.debug("Applying Layer 1 output filters...")
        l1_output_violation = check_output_filters(primary_response)
        if l1_output_violation:
            return self._trigger_action_protocol("Response", "L1 Filter Violation")
        logger.info("L1 Output Check Passed.")

        # Layer 2 Guard LLM Analysis
        logger.debug("Sending response to Guard LLM (L2) for analysis...")
        l2_analysis_result = analyze_response_with_guard(
            user_prompt=user_prompt,
            response_text=primary_response
        )
        logger.debug(f"L2 analysis result received: {l2_analysis_result}")

        # Final Decision
        if l2_analysis_result.get('status') == 'success':
            decision = l2_analysis_result.get('decision')
            reason = l2_analysis_result.get('reason') or "Unknown Reason"
            if decision == 'CLEAN':
                logger.info("L2 Guard LLM analysis: CLEAN. Returning original response.")
                return primary_response
            elif decision == 'VIOLATION':
                return self._trigger_action_protocol("Response", f"L2 Violation ({reason})")
            else:
                logger.error(f"L2 Guard LLM returned success status but unexpected decision: {decision}. Blocking.")
                return self._trigger_action_protocol("Response", f"L2 Unexpected Decision ({decision})")
        else:
            error_reason = l2_analysis_result.get('reason', 'Unknown L2 Error')
            logger.error(f"L2 Guard LLM analysis resulted in an ERROR: {error_reason}. Blocking response as a precaution.")
            return f"[Argus] Response blocked due to an error during security analysis ({error_reason})."
