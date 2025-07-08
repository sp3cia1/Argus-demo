"""
Layer 2 Guard LLM - AI-powered contextual analysis.
"""

import logging
import json
from typing import Dict
from openai import OpenAI, APIConnectionError, AuthenticationError, RateLimitError, APIStatusError

from ...config.settings import settings
from ...config.prompts import GUARD_LLM_SYSTEM_PROMPT, GUARD_LLM_ANALYSIS_PROMPT_TEMPLATE
from ...config.security_rules import PRIMARY_LLM_ROLE_DESCRIPTION, VIOLATION_REASONS
from ...core.types import SecurityResult, SecurityDecision, ViolationReason
from ...core.exceptions import LLMError

logger = logging.getLogger(__name__)

class GuardLLMClient:
    """Client for interacting with the Guard LLM via OpenRouter."""
    
    def __init__(self):
        self.client = None
        if settings.openrouter_api_key:
            try:
                self.client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=settings.openrouter_api_key,
                    timeout=settings.guard_llm_timeout,
                )
                logger.info("OpenAI client initialized successfully for OpenRouter.")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}", exc_info=True)
                self.client = None
        else:
            logger.error("OpenRouter API Key not found in configuration. Guard LLM handler will be disabled.")
    
    def analyze(self, user_prompt: str, response_text: str) -> SecurityResult:
        """Analyze the primary LLM's response using the Guard LLM."""
        if not self.client:
            logger.error("Guard LLM client not initialized. Cannot perform analysis.")
            return SecurityResult(
                decision=SecurityDecision.ERROR,
                details="Client not initialized"
            )
        
        logger.info("Sending interaction to Guard LLM for analysis.")
        logger.debug(f"User Prompt (L2 Input): '{user_prompt[:100]}...'")
        logger.debug(f"Primary Response (L2 Input): '{response_text[:100]}...'")
        
        try:
            analysis_prompt = GUARD_LLM_ANALYSIS_PROMPT_TEMPLATE.format(
                user_prompt=user_prompt,
                primary_role=PRIMARY_LLM_ROLE_DESCRIPTION,
                response_text=response_text
            )
        except KeyError as e:
            logger.error(f"Missing key in GUARD_LLM_ANALYSIS_PROMPT_TEMPLATE: {e}")
            return SecurityResult(
                decision=SecurityDecision.ERROR,
                details=f"Prompt template formatting error: Missing key {e}"
            )
        except Exception as format_err:
            logger.error(f"Error formatting analysis prompt: {format_err}", exc_info=True)
            return SecurityResult(
                decision=SecurityDecision.ERROR,
                details="Prompt template formatting error"
            )
        
        messages = [
            {"role": "system", "content": GUARD_LLM_SYSTEM_PROMPT},
            {"role": "user", "content": analysis_prompt}
        ]
        
        try:
            completion = self.client.chat.completions.create(
                model=settings.guard_llm_model,
                messages=messages,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens,
                extra_headers={
                    "HTTP-Referer": settings.site_url,
                    "X-Title": settings.site_name,
                },
                extra_body={
                    "provider": {
                        "order": ["Nineteen"],
                        "quantizations": ["bf16"],
                    }
                }
            )
            
            if completion.choices[0].message.reasoning:
                guard_reasoning_content = completion.choices[0].message.reasoning.strip()
                logger.info(f"Guard LLM reasoning: '{guard_reasoning_content}'")
            else:
                logger.info("Guard LLM reasoning: NO REASONING")
            
            guard_response_content = completion.choices[0].message.content.strip()
            logger.info(f"Guard LLM raw response content: '{guard_response_content}'")
            
            # Clean the response
            cleaned_content = guard_response_content
            if cleaned_content.startswith("```json"):
                cleaned_content = cleaned_content[len("```json"):].strip()
            if cleaned_content.endswith("```"):
                cleaned_content = cleaned_content[:-len("```")].strip()
            
            # Parse JSON response
            try:
                analysis_result = json.loads(cleaned_content)
                decision = analysis_result.get("decision")
                reason = analysis_result.get("reason")
                
                if decision == "CLEAN":
                    logger.info("Guard LLM analysis result: CLEAN")
                    return SecurityResult(decision=SecurityDecision.CLEAN)
                elif decision == "VIOLATION":
                    if reason in VIOLATION_REASONS.values():
                        logger.warning(f"Guard LLM analysis result: VIOLATION (Reason: {reason})")
                        return SecurityResult(
                            decision=SecurityDecision.VIOLATION,
                            reason=ViolationReason(reason),
                            details=reason
                        )
                    else:
                        logger.warning(f"Guard LLM returned VIOLATION with unknown reason code: '{reason}'. Defaulting reason.")
                        return SecurityResult(
                            decision=SecurityDecision.VIOLATION,
                            reason=ViolationReason.UNKNOWN_VIOLATION,
                            details=VIOLATION_REASONS["UNKNOWN"]
                        )
                else:
                    logger.warning(f"Guard LLM JSON response had unexpected decision value: '{decision}'. Defaulting to VIOLATION.")
                    return SecurityResult(
                        decision=SecurityDecision.VIOLATION,
                        reason=ViolationReason.UNKNOWN_VIOLATION,
                        details=VIOLATION_REASONS["UNKNOWN"]
                    )
                    
            except json.JSONDecodeError as json_err:
                logger.error(f"Failed to parse Guard LLM JSON response: '{guard_response_content}'. Error: {json_err}")
                return SecurityResult(
                    decision=SecurityDecision.ERROR,
                    details="Invalid JSON response format"
                )
            except Exception as parse_err:
                logger.error(f"Error processing Guard LLM response structure: {parse_err}", exc_info=True)
                return SecurityResult(
                    decision=SecurityDecision.ERROR,
                    details="Error processing response structure"
                )
                
        except AuthenticationError as e:
            logger.error(f"Guard LLM API Error: Authentication failed. Check API Key. Details: {e}")
            return SecurityResult(
                decision=SecurityDecision.ERROR,
                details="Authentication Error"
            )
        except Exception as e:
            logger.error(f"An unexpected error occurred during Guard LLM analysis: {e}", exc_info=True)
            return SecurityResult(
                decision=SecurityDecision.ERROR,
                details=f"Unexpected Error: {type(e).__name__}"
            )

def analyze_response_with_guard(user_prompt: str, response_text: str) -> Dict:
    """Legacy function for backward compatibility."""
    client = GuardLLMClient()
    result = client.analyze(user_prompt, response_text)
    
    # Convert to legacy format
    if result.decision == SecurityDecision.CLEAN:
        return {'status': 'success', 'decision': 'CLEAN', 'reason': None}
    elif result.decision == SecurityDecision.VIOLATION:
        return {'status': 'success', 'decision': 'VIOLATION', 'reason': result.details}
    else:
        return {'status': 'error', 'decision': 'ERROR', 'reason': result.details}
