#!/usr/bin/env python3
# Test script to validate PDF loading

import os
from src.tools.document_loader import load_document
from src.config.settings import DATA_DIR, FINANCIAL_DATA_SOURCE

def test_pdf_loading():
    print("Testing PDF loading functionality...")
    
    # Set the path to the PDF file
    pdf_path = os.path.join(DATA_DIR, FINANCIAL_DATA_SOURCE)
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at {pdf_path}")
        return False
    
    print(f"Found PDF file: {pdf_path}")
    
    try:
        # Try to load the PDF
        result = load_document(pdf_path)
        
        if 'content' not in result:
            print("Error: Failed to extract content from PDF")
            return False
        
        content_length = len(result['content'])
        if content_length < 10:
            print(f"Warning: PDF content seems too short ({content_length} characters)")
            return False
            
        print(f"Successfully loaded PDF with {content_length} characters of content")
        print(f"PDF metadata: {result['metadata']}")
        print(f"First 100 characters of content: {result['content'][:100]}...")
        return True
        
    except Exception as e:
        print(f"Error loading PDF: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_pdf_loading()
    if success:
        print("\nPDF loading test passed successfully!")
    else:
        print("\nPDF loading test failed.")
