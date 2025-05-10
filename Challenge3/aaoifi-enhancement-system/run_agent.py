#!/usr/bin/env python3
# A simple script to run the AAOIFI Enhancement System

import os
import sys

# Add the project root directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.main import main
from src.config.settings import FINANCIAL_DATA_SOURCE, OPENAI_API_KEY, GOOGLE_API_KEY

def check_environment():
    """Check if environment is properly set up before running"""
    print("Checking environment setup...")
    
    # Check API Keys
    if not OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY is not set in .env file.")
        return False
        
    if not GOOGLE_API_KEY:
        print("Warning: GOOGLE_API_KEY is not set in .env file. Some functionality may be limited.")
    
    # Check if the PDF file exists
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    pdf_path = os.path.join(data_dir, FINANCIAL_DATA_SOURCE)
    
    if not os.path.exists(pdf_path):
        print(f"Error: Financial data source '{FINANCIAL_DATA_SOURCE}' not found at {pdf_path}")
        print(f"Please place your PDF file at {pdf_path}")
        return False
    
    print(f"Financial data source found: {pdf_path}")
    print("Environment setup looks good!")
    return True

if __name__ == "__main__":
    print("AAOIFI Standards Enhancement System")
    print("==================================")
    
    if check_environment():
        print("\nStarting the system...\n")
        main()
    else:
        print("\nEnvironment setup failed. Please fix the issues and try again.")
        sys.exit(1)
