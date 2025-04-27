"""
guard_llm_handler.py
--------------------
Handles the interaction with the Layer 2 Guard LLM via the OpenRouter API.
It takes the primary LLM's response, sends it to the Guard LLM for analysis
based on configured prompts, and parses the structured JSON result.

Fulfills PRD requirements: REQ-L2-01 to REQ-L2-05, incorporating robustness improvements.
"""

import logging
import json # Import the json library for parsing
from openai import OpenAI, APIConnectionError, AuthenticationError, RateLimitError, APIStatusError
import config # Assuming config.py contains API keys, prompts, model names, etc.

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the OpenAI client for OpenRouter
client = None
if config.OPENROUTER_API_KEY:
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=config.OPENROUTER_API_KEY,
            timeout=20.0, # Sensible timeout
        )
        logging.info("OpenAI client initialized successfully for OpenRouter.")
    except Exception as e:
        logging.error(f"Failed to initialize OpenAI client: {e}", exc_info=True)
        # client remains None
else:
    logging.error("OpenRouter API Key not found in configuration. Guard LLM handler will be disabled.")


# REQ-L2-01: Implement function analyze_response_with_guard(response)
def analyze_response_with_guard(user_prompt: str, response_text: str) -> dict:
    """
    Analyzes the primary LLM's response using the Guard LLM via OpenRouter,
    considering the context of the user's prompt.

    Args:
        user_prompt: The original prompt text from the user.
        response_text: The text response from the primary LLM.

    Returns:
        A dictionary containing the analysis result:
        {'status': 'success', 'decision': 'CLEAN', 'reason': None}
        {'status': 'success', 'decision': 'VIOLATION', 'reason': 'REASON_CODE'}
        {'status': 'error', 'decision': 'ERROR', 'reason': 'Error message'}
    """
    default_error_return = {'status': 'error', 'decision': 'ERROR', 'reason': 'Analysis failed'}
    if not client:
        logging.error("Guard LLM client not initialized. Cannot perform analysis.")
        return {**default_error_return, 'reason': 'Client not initialized'}

    # Log both prompt and response being sent for analysis
    logging.info(f"Sending interaction to Guard LLM for analysis.")
    logging.debug(f"User Prompt (L2 Input): '{user_prompt[:100]}...'")
    logging.debug(f"Primary Response (L2 Input): '{response_text[:100]}...'")

    # REQ-L2-02: Construct prompt for Guard LLM using configured role and template
    # IMPROVED: Includes user_prompt in the format call
    try:
        analysis_prompt = config.GUARD_LLM_ANALYSIS_PROMPT_TEMPLATE.format(
            user_prompt=user_prompt, # Pass the user prompt
            primary_role=config.PRIMARY_LLM_ROLE_DESCRIPTION,
            response_text=response_text
        )
    except KeyError as e:
         logging.error(f"Missing key in GUARD_LLM_ANALYSIS_PROMPT_TEMPLATE: {e}. Check config.py placeholders.", exc_info=True)
         return {**default_error_return, 'reason': f'Prompt template formatting error: Missing key {e}'}
    except Exception as format_err: # Catch other potential formatting issues
        logging.error(f"Error formatting analysis prompt: {format_err}", exc_info=True)
        return {**default_error_return, 'reason': 'Prompt template formatting error'}


    messages = [
        {"role": "system", "content": config.GUARD_LLM_SYSTEM_PROMPT},
        {"role": "user", "content": analysis_prompt}
    ]

    try:
        # REQ-L2-03: Call OpenRouter API using the standard method
        completion = client.chat.completions.create(
            model=config.GUARD_LLM_MODEL,
            messages=messages,
            temperature=0.1,
            max_tokens=6000, # Keep low for concise JSON output
            extra_headers={
                "HTTP-Referer": config.YOUR_SITE_URL,
                "X-Title": config.YOUR_SITE_NAME,
            },
            response_format={"type": "json_object"}
            # reasoning_effort="low"
        )

        if (completion.choices[0].message.reasoning):
            guard_reasoning_content = completion.choices[0].message.reasoning.strip()
            logging.info(f"Guard LLM reasoning:- '{guard_reasoning_content}'")
        else:
            logging.info(f"Guard LLM reasoning:- NO REASONING")
        # REQ-L2-04: Parse the structured JSON response
        guard_response_content = completion.choices[0].message.content.strip()
        logging.info(f"Guard LLM raw response content: '{guard_response_content}'")


        cleaned_content = guard_response_content
        if cleaned_content.startswith("```json"):
            cleaned_content = cleaned_content[len("```json"):].strip() # Remove prefix and strip
        if cleaned_content.endswith("```"):
            cleaned_content = cleaned_content[:-len("```")].strip() # Remove suffix and strip


        # ... (JSON parsing and validation logic remains the same as the previous improved version) ...
        # Attempt to parse the JSON response
        try:
            analysis_result = json.loads(cleaned_content)

            # Validate the structure and content of the parsed JSON
            decision = analysis_result.get("decision")
            reason = analysis_result.get("reason") # Can be None or empty string

            if decision == "CLEAN":
                logging.info("Guard LLM analysis result: CLEAN")
                return {'status': 'success', 'decision': 'CLEAN', 'reason': None}
            elif decision == "VIOLATION":
                # Validate the reason code against known reasons
                if reason in config.VIOLATION_REASONS.values():
                    logging.warning(f"Guard LLM analysis result: VIOLATION (Reason: {reason})")
                    return {'status': 'success', 'decision': 'VIOLATION', 'reason': reason}
                else:
                    logging.warning(f"Guard LLM returned VIOLATION with unknown reason code: '{reason}'. Defaulting reason.")
                    return {'status': 'success', 'decision': 'VIOLATION', 'reason': config.VIOLATION_REASONS["UNKNOWN"]}
            else:
                logging.warning(f"Guard LLM JSON response had unexpected decision value: '{decision}'. Defaulting to VIOLATION.")
                return {'status': 'success', 'decision': 'VIOLATION', 'reason': config.VIOLATION_REASONS["UNKNOWN"]}

        except json.JSONDecodeError as json_err:
            logging.error(f"Failed to parse Guard LLM JSON response: '{guard_response_content}'. Error: {json_err}")
            return {**default_error_return, 'reason': 'Invalid JSON response format'}
        except Exception as parse_err:
             logging.error(f"Error processing Guard LLM response structure: {parse_err}", exc_info=True)
             return {**default_error_return, 'reason': 'Error processing response structure'}

    # ... (API Error handling remains the same as the previous improved version) ...
    except AuthenticationError as e:
        logging.error(f"Guard LLM API Error: Authentication failed. Check API Key. Details: {e}")
        return {**default_error_return, 'reason': 'Authentication Error'}
    # ... other except blocks ...
    except Exception as e:
        logging.error(f"An unexpected error occurred during Guard LLM analysis: {e}", exc_info=True)
        return {**default_error_return, 'reason': f'Unexpected Error: {type(e).__name__}'}


# ... (if __name__ == "__main__": block - update test calls if needed to pass a dummy user_prompt) ...
# Example update for test block:
if __name__ == "__main__":
    print("--- Testing Guard LLM Handler (Improved with Context) ---")
    if not client:
        print("OpenAI client not initialized. Cannot run tests. Ensure OPENROUTER_API_KEY is set in .env")
    else:
        test_interactions = {
            "safe": {"prompt": "Tell me about photosynthesis.", "response": "Photosynthesis is a process used by plants."},
            "pii": {"prompt": "What is the customer email?", "response": "The customer's email is test@example.com and their Aadhaar is 1234 5678 9012."},
            "confidential_contextual": {"prompt": "What is our internal testing protocol?", "response": "The cybersecurity protocol involves bi-weekly penetration testing using Cobalt Strike simulations."},
            "confidential_no_context": {"prompt": "What is Cobalt Strike?", "response": "Cobalt Strike is a commercial penetration testing tool."}, # Should be CLEAN if judged correctly
        }
        for category, data in test_interactions.items():
            print(f"\nAnalyzing ({category}): User:'{data['prompt'][:60]}...' | Response:'{data['response'][:60]}...'")
            result = analyze_response_with_guard(data['prompt'], data['response']) # Pass both prompt and response
            print(f"Result Dictionary: {result}")
    print("\n--- Test Complete ---")