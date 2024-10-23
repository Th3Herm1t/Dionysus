from dotenv import load_dotenv
import os
import logging

load_dotenv()  # Load environment variables from .env

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')


# Logging config

LOGGING_LEVEL = os.getenv('LOGGING_LEVEL', 'INFO').upper()

logging.basicConfig(
    level=LOGGING_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)