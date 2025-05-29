# --- Location: app.py ---

import gradio as gr
import time
import logging

import layer1_filters
import guard_llm_handler
import config
from demo_data import scenarios, prompt_to_response_map, label_to_prompt_map, get_simulated_reasoning

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(name)s.%(funcName)s] - %(message)s')
logger = logging.getLogger(__name__)

def run_Argus_demo(button_label_clicked: str, history_no_Argus: list, history_with_Argus: list):
    """Runs the full Argus pipeline AND simulates the unprotected response stream."""
    logger.info(f"--- Argus Running ---")

    full_prompt = label_to_prompt_map.get(button_label_clicked, "ERROR: Prompt not found!")
    unfiltered_response = prompt_to_response_map.get(full_prompt, "ERROR: Unfiltered response not found!")
    simulated_reasoning = ""
    reasoning_visible = gr.Accordion(visible=False)
    status_update = "Initiating..."
    Argus_message = ""
    Argus_final_decision = None
    block_reason_detail = ""

    # Add user prompt to both histories immediately
    history_no_Argus.append((full_prompt, None))
    history_with_Argus.append((full_prompt, None))
    yield history_no_Argus, history_with_Argus, status_update, reasoning_visible, simulated_reasoning

    # Start "Without Argus" Streaming Setup
    streaming_active = True
    streamed_text_no_Argus = ""
    unfiltered_len = len(unfiltered_response)
    char_index = 0
    delay_before_stream = config.SIMULATED_UNPROTECTED_DELAY if hasattr(config, 'SIMULATED_UNPROTECTED_DELAY') else 0.5
    stream_delay_no_Argus = config.STREAMING_DELAY_NO_Argus if hasattr(config, 'STREAMING_DELAY_NO_Argus') else 0.025

    stream_start_time = time.time() + delay_before_stream

    # Argus Pipeline Execution
    try:
        # L1 Input Check
        status_update = "Running L1 Input Filter..."
        yield history_no_Argus, history_with_Argus, status_update, reasoning_visible, simulated_reasoning
        time.sleep(0.1)

        l1_input_violation_detail = layer1_filters.check_input_filters(full_prompt)
        if l1_input_violation_detail:
            block_reason_detail = f"L1 Input: {l1_input_violation_detail}"
            status_update = f"Blocked by L1 Input Filter. Reinforcement Simulated."
            Argus_message = f"[Argus] Input blocked due to policy violation ({block_reason_detail})."
            logger.warning(f"L1 Input Violation: {block_reason_detail}. Blocking.")
            logger.info(f"[REINFORCE] Simulated reinforcement prompt sent regarding {block_reason_detail}.")
            history_with_Argus[-1] = (full_prompt, Argus_message)
            Argus_final_decision = "BLOCKED"
            streaming_active = True

        else:
            status_update = "L1 Input OK. Processing..."
            yield history_no_Argus, history_with_Argus, status_update, reasoning_visible, simulated_reasoning

            primary_response_to_check = unfiltered_response

            # L1 Output Check
            status_update = "Running L1 Output Filter..."
            yield history_no_Argus, history_with_Argus, status_update, reasoning_visible, simulated_reasoning
            time.sleep(0.1)

            l1_output_violation_detail = layer1_filters.check_output_filters(primary_response_to_check)
            if l1_output_violation_detail:
                block_reason_detail = f"L1 Output: {l1_output_violation_detail}"
                status_update = f"Blocked by L1 Output Filter. Reinforcement Simulated."
                Argus_message = f"[Argus] Response blocked due to policy violation ({block_reason_detail})."
                logger.warning(f"L1 Output Violation: {block_reason_detail}. Blocking.")
                logger.info(f"[REINFORCE] Simulated reinforcement prompt sent regarding {block_reason_detail}.")
                history_with_Argus[-1] = (full_prompt, Argus_message)
                Argus_final_decision = "BLOCKED"

            else:
                # L2 Guard LLM Analysis
                status_update = "L1 Output OK. Analyzing with Guard LLM (L2)... (This may take a few seconds)"
                yield history_no_Argus, history_with_Argus, status_update, reasoning_visible, simulated_reasoning
                l2_analysis_result = guard_llm_handler.analyze_response_with_guard(full_prompt, primary_response_to_check)
                logger.debug(f"L2 analysis result received: {l2_analysis_result}")

                # Process L2 Result
                if l2_analysis_result.get('status') == 'success':
                    decision = l2_analysis_result.get('decision')
                    reason = l2_analysis_result.get('reason')

                    if decision == 'CLEAN':
                        status_update = "Analysis Complete: CLEAN"
                        Argus_message = primary_response_to_check
                        logger.info("L2 Guard LLM analysis: CLEAN.")
                        Argus_final_decision = "CLEAN"
                    elif decision == 'VIOLATION':
                        reason_code = reason or config.VIOLATION_REASONS["UNKNOWN"]
                        block_reason_detail = f"L2 Violation ({reason_code})"
                        status_update = f"Analysis Complete: BLOCKED by L2 ({reason_code}). Reinforcement Simulated."
                        Argus_message = f"[Argus] Response blocked due to policy violation ({block_reason_detail})."
                        logger.warning(f"L2 Guard LLM analysis: VIOLATION (Reason: {reason_code}). Blocking.")
                        logger.info(f"[REINFORCE] Simulated reinforcement prompt sent regarding {block_reason_detail}.")
                        simulated_reasoning = get_simulated_reasoning(reason_code)
                        reasoning_visible = gr.Accordion(visible=True)
                        history_with_Argus[-1] = (full_prompt, Argus_message)
                        Argus_final_decision = "BLOCKED"
                    else:
                        block_reason_detail = f"L2 Unexpected Decision ({decision})"
                        status_update = f"Analysis Complete: L2 Unexpected Decision ({decision}). Blocking."
                        Argus_message = f"[Argus] Response blocked due to unexpected analysis outcome ({block_reason_detail})."
                        logger.error(f"{status_update}")
                        history_with_Argus[-1] = (full_prompt, Argus_message)
                        Argus_final_decision = "BLOCKED"

                else:
                    error_reason = l2_analysis_result.get('reason', 'Unknown L2 Error')
                    block_reason_detail = f"L2 ERROR: {error_reason}"
                    status_update = f"Analysis Failed: {block_reason_detail}. Blocking."
                    Argus_message = f"[Argus] Response blocked due to error during security analysis ({error_reason})."
                    logger.error(f"{status_update}")
                    history_with_Argus[-1] = (full_prompt, Argus_message)
                    Argus_final_decision = "ERROR"

    except Exception as e:
        logger.error(f"Error during Argus processing for '{button_label_clicked}': {e}", exc_info=True)
        status_update = f"ERROR: {e}"
        error_message = f"[Argus Internal Error] Failed to process: {e}"
        history_no_Argus[-1] = (full_prompt, error_message)
        history_with_Argus[-1] = (full_prompt, error_message)
        Argus_final_decision = "ERROR"
        streaming_active = False

    # Combined Streaming & Final Update Loop
    logger.info("Entering combined streaming/update loop...")
    streamed_text_with_Argus = ""
    Argus_response_len = len(Argus_message) if Argus_final_decision == "CLEAN" else 0
    Argus_char_index = 0
    stream_delay_with_Argus = config.STREAMING_DELAY_WITH_Argus if hasattr(config, 'STREAMING_DELAY_WITH_Argus') else 0.010

    while streaming_active or (Argus_final_decision == "CLEAN" and Argus_char_index < Argus_response_len):

        stream_yield_occurred = False

        # Stream "Without Argus"
        if streaming_active and time.time() >= stream_start_time and char_index < unfiltered_len:
            streamed_text_no_Argus += unfiltered_response[char_index]
            history_no_Argus[-1] = (full_prompt, streamed_text_no_Argus)
            char_index += 1
            if char_index >= unfiltered_len:
                streaming_active = False
                logger.info("'Without Argus' streaming complete.")
            stream_yield_occurred = True

        # Stream "With Argus" only if decision was CLEAN
        if Argus_final_decision == "CLEAN" and Argus_char_index < Argus_response_len:
            streamed_text_with_Argus += Argus_message[Argus_char_index]
            history_with_Argus[-1] = (full_prompt, streamed_text_with_Argus)
            Argus_char_index += 1
            if Argus_char_index >= Argus_response_len:
                 logger.info("'With Argus' streaming complete.")
            stream_yield_occurred = True

        if stream_yield_occurred:
             yield history_no_Argus, history_with_Argus, status_update, reasoning_visible, simulated_reasoning
        elif not streaming_active and not (Argus_final_decision == "CLEAN" and Argus_char_index < Argus_response_len):
             break

        loop_delay = min(stream_delay_no_Argus if streaming_active else 1.0,
                         stream_delay_with_Argus if (Argus_final_decision == "CLEAN" and Argus_char_index < Argus_response_len) else 1.0)
        if loop_delay >= 1.0 and (streaming_active or (Argus_final_decision == "CLEAN" and Argus_char_index < Argus_response_len)):
             loop_delay = 0.05

        time.sleep(loop_delay)

    # Final yield
    logger.info("Final UI update yield.")
    final_no_Argus_text = streamed_text_no_Argus if char_index == unfiltered_len else unfiltered_response
    history_no_Argus[-1] = (full_prompt, final_no_Argus_text)

    final_with_Argus_text = ""
    if Argus_final_decision == "CLEAN":
        final_with_Argus_text = streamed_text_with_Argus if Argus_char_index == Argus_response_len else Argus_message
    else:
        final_with_Argus_text = Argus_message
    history_with_Argus[-1] = (full_prompt, final_with_Argus_text)

    yield history_no_Argus, history_with_Argus, status_update, reasoning_visible, simulated_reasoning

    logger.info(f"--- Argus Completed Running ---")

theme = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="sky"
)

with gr.Blocks(theme=theme, title="Argus AI Gateway Demo", css=".gradio-container { max-width: 95% !important; }") as demo:
    gr.Markdown("# Argus AI Gateway Demo")
    gr.Markdown("Demonstrating LLM Security with and without Argus Protection")

    with gr.Row():
        with gr.Column(scale=1, min_width=300):
            gr.Markdown("## Select a Demo Scenario")
            prompt_buttons = []
            for scenario in scenarios:
                button = gr.Button(value=scenario["button_label"])
                prompt_buttons.append(button)

        with gr.Column(scale=3):
            gr.Markdown("## Interaction Comparison")
            with gr.Row():
                chatbot_no_Argus = gr.Chatbot(label="Without Argus Protection", height=700, show_copy_button=True, scale=1)
                chatbot_with_Argus = gr.Chatbot(label="With Argus Protection", height=700, show_copy_button=True, scale=1)

            status_indicator = gr.Markdown("<span style='font-size: 20px;'>Status: Idle</span>", elem_classes="status-indicator")

            with gr.Accordion("Guard LLM Reasoning", visible=False) as reasoning_accordion:
                 reasoning_display = gr.Markdown("*(Reasoning will appear here when an L2 block occurs)*")

    outputs_to_update = [
        chatbot_no_Argus,
        chatbot_with_Argus,
        status_indicator,
        reasoning_accordion,
        reasoning_display
    ]
    inputs_for_function = [
        chatbot_no_Argus,
        chatbot_with_Argus
    ]

    for btn in prompt_buttons:
        btn.click(
            fn=run_Argus_demo,
            inputs=[btn] + inputs_for_function,
            outputs=outputs_to_update
        )

if __name__ == "__main__":
    logger.info("Launching Gradio interface...")
    demo.launch(debug=True, share=True)
    logger.info("Gradio interface stopped.")