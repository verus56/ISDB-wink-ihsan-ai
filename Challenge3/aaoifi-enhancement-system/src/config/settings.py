# filepath: aaoifi-enhancement-system/aaoifi-enhancement-system/src/config/settings.py

# Configuration settings for the AAOIFI Standards Enhancement System

import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# API keys and other sensitive information
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
FINANCIAL_DATA_SOURCE = os.getenv("FINANCIAL_DATA_SOURCE", "FAS4.pdf")

# OpenAI model configuration
MODEL_CONFIG = {
    "primary_model": "gpt-4o", 
    "secondary_model": "gpt-4-turbo",
    "temperature": 0.3,
    "max_tokens": 4000
}

# Application settings
AGENT_TIMEOUT = 30  # seconds
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Define paths for data storage
DATA_DIR = os.path.join(os.path.dirname(__file__), '../../data')
STANDARDS_DIR = os.path.join(DATA_DIR, 'standards')
OUTPUT_DIR = os.path.join(DATA_DIR, 'output')

# Ensure directories exist
os.makedirs(STANDARDS_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)