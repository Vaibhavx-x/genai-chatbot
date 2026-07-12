import logging

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("chatbot.log"),  # Logs to a file
        logging.StreamHandler()  # Also logs to console
    ]
)

# Get logger instance
logger = logging.getLogger("chatbot_logger")
