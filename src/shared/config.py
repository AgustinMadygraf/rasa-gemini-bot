"""
Path: src/shared/config.py
"""

import os
from dotenv import load_dotenv

load_dotenv()

def get_config():
    "Load configuration from environment variables"

    config = {
        "GOOGLE_GEMINI_MODEL": os.getenv('GOOGLE_GEMINI_MODEL'),
        "GOOGLE_GEMINI_API_KEY": os.getenv('GOOGLE_GEMINI_API_KEY'),
        "LOG_LEVEL": os.getenv('LOG_LEVEL', 'DEBUG'),
        "SYSTEM_INSTRUCTIONS_PATH": os.getenv('SYSTEM_INSTRUCTIONS_PATH')
    }

    return config
