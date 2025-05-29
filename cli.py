"""
cli.py
------
Command-Line Interface for the Argus AI Gateway MVP.

Handles user input, interacts with the ArgusGateway, and displays results.
This is the main entry point for running the application.

Fulfills PRD requirements: REQ-CLI-01, REQ-CLI-02, REQ-CLI-03, REQ-CLI-04, REQ-LOG-01
"""

import logging
from gateway import ArgusGateway

log_level = logging.INFO
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(levelname)s - [%(name)s.%(funcName)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def main():
    """Main function to run the CLI application."""
    logger.info("Initializing Argus AI Gateway...")
    try:
        gateway = ArgusGateway()
        logger.info("Gateway initialized successfully.")
    except Exception as e:
        logger.critical(f"Failed to initialize ArgusGateway: {e}", exc_info=True)
        print("[Argus CLI] Critical Error: Could not initialize the gateway. Exiting.")
        return

    print("\n--- Argus AI Gateway CLI ---")
    print("Type your prompt or 'quit' to exit.")

    while True:
        try:
            user_input = input("\n>>> User: ")

            if user_input.strip().lower() == 'quit':
                logger.info("User requested to quit.")
                break

            if not user_input.strip():
                print("[Argus CLI] Please enter a prompt.")
                continue

            logger.debug(f"Sending prompt to gateway: '{user_input[:100]}...'")
            final_output = gateway.process_prompt(user_input)
            logger.debug(f"Received final output from gateway: '{final_output[:100]}...'")

            print(f"<<< Argus: {final_output}")

        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt received. Exiting.")
            break
        except EOFError:
             logger.info("EOFError received. Exiting.")
             break
        except Exception as e:
            logger.error(f"An unexpected error occurred in the main loop: {e}", exc_info=True)
            print(f"[Argus CLI] An unexpected error occurred: {e}")

    print("\n--- Exiting Argus AI Gateway CLI ---")
    logger.info("Argus AI Gateway CLI stopped.")

if __name__ == "__main__":
    main()