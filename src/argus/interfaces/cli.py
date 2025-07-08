"""
Command-Line Interface for the Argus AI Gateway.
"""

import logging
from ..core.gateway import ArgusGateway
from ..config.settings import settings

def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format=settings.log_format,
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def main():
    """Main function to run the CLI application."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
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
