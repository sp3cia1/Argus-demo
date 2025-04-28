# --- Location: app.py ---

import gradio as gr
import time
import logging

# Import our Aegis components
from gateway import AegisGateway
import config
# --- MODIFICATION: Import demo data ---
from demo_data import scenarios, prompt_to_response_map, label_to_prompt_map

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(name)s.%(funcName)s] - %(message)s')
logger = logging.getLogger(__name__)

# Instantiate the gateway
try:
    gateway = AegisGateway()
    logger.info("AegisGateway instantiated successfully for Gradio app.")
except Exception as e:
    logger.critical(f"Failed to instantiate AegisGateway: {e}", exc_info=True)
    gateway = None

# --- Processing Function Placeholder (We will implement this fully in the next step) ---
def placeholder_process(button_label_clicked):
    """Placeholder function - Now looks up prompt using button label"""
    full_prompt = label_to_prompt_map.get(button_label_clicked, "ERROR: Prompt not found!")
    logger.info(f"Button '{button_label_clicked}' clicked, mapped to prompt: '{full_prompt[:50]}...'")
    # In the next step, this function will use 'full_prompt' to call the gateway, etc.
    # For now, just return empty updates
    return [], [], gr.Accordion(visible=False), ""


# --- Gradio UI Definition ---
theme = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="sky"
)

with gr.Blocks(theme=theme, title="Aegis AI Gateway Demo") as demo:
    gr.Markdown("# Aegis AI Gateway Demo")
    gr.Markdown("Demonstrating LLM Security with and without Aegis Protection")

    with gr.Row():
        # Column 1: Prompt Selection Area
        with gr.Column(scale=1, min_width=250):
            gr.Markdown("## Select a Demo Scenario")

            # --- MODIFICATION: Dynamically create buttons ---
            prompt_buttons = [] # Keep track of buttons if needed later
            button_inputs = []
            for scenario in scenarios:
                
                button = gr.Button(
                    value=scenario["button_label"]
                )
                prompt_buttons.append(button)
                button_inputs.append(button)
            # --- END MODIFICATION ---

        # Column 2: Chatbot Display Area
        with gr.Column(scale=3):
            gr.Markdown("## Interaction Comparison")
            with gr.Row():
                chatbot_no_aegis = gr.Chatbot(label="Without Aegis Protection", height=500, show_copy_button=True)
                chatbot_with_aegis = gr.Chatbot(label="With Aegis Protection", height=500, show_copy_button=True)

            with gr.Accordion("Guard LLM Reasoning", visible=False) as reasoning_accordion:
                 reasoning_display = gr.Markdown("*(Reasoning will appear here when an L2 block occurs)*")

    # --- Connect Buttons to Placeholder Function (Temporary) ---
    # We will replace 'placeholder_process' with the real logic in the next step
    outputs_to_update = [
        chatbot_no_aegis,
        chatbot_with_aegis,
        reasoning_accordion,
        reasoning_display
    ]
    for btn in prompt_buttons:
        # When a button is clicked, call the function, passing the button's value (the prompt)
        # The function's return values will update the components listed in outputs_to_update
        btn.click(fn=placeholder_process, inputs=btn, outputs=outputs_to_update)


# --- Launch the Gradio App ---
if __name__ == "__main__":
    if gateway is None:
         print("ERROR: AegisGateway could not be initialized. Gradio app cannot run.")
         logger.critical("Aborting Gradio launch due to Gateway initialization failure.")
    else:
        logger.info("Launching Gradio interface...")
        demo.launch(debug=True)
        logger.info("Gradio interface stopped.")