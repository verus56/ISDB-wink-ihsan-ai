import os
import PyPDF2
import re
from src.config.settings import STANDARDS_DIR, DATA_DIR

# Add new helper function for AAOIFI document processing
def extract_and_analyze_aaoifi_content(content):
    """
    Extract and analyze AAOIFI-specific content from document text.
    
    Args:
        content (str): The extracted document content
        
    Returns:
        dict: Extracted AAOIFI-specific metadata
    """
    aaoifi_metadata = {}
    
    # Check for FAS standard number
    fas_match = re.search(r'FAS\s*(\d+)', content)
    if fas_match:
        aaoifi_metadata['standard_number'] = fas_match.group(1)
    
    # Try to extract standard title
    title_patterns = [
        r'(?i)Financial Accounting Standard\s+\d+\s*[:\-–—]\s*([^\n]+)',
        r'(?i)FAS\s+\d+\s*[:\-–—]\s*([^\n]+)'
    ]
    
    for pattern in title_patterns:
        title_match = re.search(pattern, content)
        if title_match:
            aaoifi_metadata['standard_title'] = title_match.group(1).strip()
            break
    
    # Try to extract effective date
    date_patterns = [
        r'(?i)effective\s+date\s*[:\-–—]\s*([^\n]+)',
        r'(?i)effective\s+from\s*[:\-–—]?\s*([^\n]+)'
    ]
    
    for pattern in date_patterns:
        date_match = re.search(pattern, content)
        if date_match:
            aaoifi_metadata['effective_date'] = date_match.group(1).strip()
            break
    
    # Check for key sections of a standard
    key_sections = {
        'objective': r'(?i)\b(objective|objectives|purpose)\b[^.]*[.:]',
        'scope': r'(?i)\b(scope|application|applicability)\b[^.]*[.:]',
        'definitions': r'(?i)\b(definition|definitions|terms)\b[^.]*[.:]',
        'recognition': r'(?i)\b(recognition|measurement)\b[^.]*[.:]',
        'disclosure': r'(?i)\b(disclosure|disclosures|presentation)\b[^.]*[.:]',
        'effective_date': r'(?i)\b(effective\s+date)\b[^.]*[.:]'
    }
    
    aaoifi_metadata['sections_present'] = {}
    for section, pattern in key_sections.items():
        if re.search(pattern, content):
            aaoifi_metadata['sections_present'][section] = True
        else:
            aaoifi_metadata['sections_present'][section] = False
    
    return aaoifi_metadata

def load_document(filepath):
    """
    Load and parse a document from the given filepath.
    Supports PDF files.

    Args:
        filepath (str): The path to the document file.

    Returns:
        dict: A structured representation of the document's content.
    """
    _, file_extension = os.path.splitext(filepath)
    
    if file_extension.lower() == '.pdf':
        return load_pdf_document(filepath)
    else:
        # Text file handling (default)
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            
            structured_data = {
                'content': content,
                'metadata': {
                    'filepath': filepath,
                    'length': len(content),
                    'type': 'text'
                }
            }
            
            # Check if this might be an AAOIFI standard in text format
            if "AAOIFI" in content or "FAS" in content or "Financial Accounting Standard" in content:
                aaoifi_metadata = extract_and_analyze_aaoifi_content(content)
                structured_data['metadata']['document_type'] = "AAOIFI_Standard"
                structured_data['metadata'].update(aaoifi_metadata)
            
            return structured_data
        except UnicodeDecodeError:
            # If it fails with utf-8, try binary mode
            return load_pdf_document(filepath)

def load_pdf_document(filepath):
    """
    Load and parse a PDF document with enhanced extraction for AAOIFI standards.

    Args:
        filepath (str): Path to the PDF file.
        
    Returns:
        dict: Structured data containing the PDF content and metadata.
    """
    content = ""
    try:
        with open(filepath, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)
            
            # Extract document information if available
            title = "Unknown"
            author = "Unknown"
            subject = "Unknown"
            
            if pdf_reader.metadata:
                if hasattr(pdf_reader.metadata, 'title') and pdf_reader.metadata.title:
                    title = pdf_reader.metadata.title
                if hasattr(pdf_reader.metadata, 'author') and pdf_reader.metadata.author:
                    author = pdf_reader.metadata.author
                if hasattr(pdf_reader.metadata, 'subject') and pdf_reader.metadata.subject:
                    subject = pdf_reader.metadata.subject
            
            # Enhanced text extraction for AAOIFI standards
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                
                if page_text:
                    # Add page number for better context
                    content += f"--- Page {page_num + 1} ---\n"
                    content += page_text + "\n\n"
                else:
                    content += f"--- Page {page_num + 1} (No extractable text) ---\n\n"
            
            # Structure the data with enhanced metadata for Islamic finance standards analysis
            structured_data = {
                'content': content.strip(),
                'metadata': {
                    'filepath': filepath,
                    'title': title,
                    'author': author,
                    'subject': subject,
                    'num_pages': num_pages,
                    'length': len(content),
                    'type': 'pdf'
                }
            }
            
            # Try to identify if this is an AAOIFI standard from content
            if "AAOIFI" in content or "FAS" in content or "Financial Accounting Standard" in content:
                structured_data['metadata']['document_type'] = "AAOIFI_Standard"
                
                # Extract AAOIFI-specific metadata
                aaoifi_metadata = extract_and_analyze_aaoifi_content(content)
                structured_data['metadata'].update(aaoifi_metadata)
            
            return structured_data
    except Exception as e:
        print(f"Error loading PDF document {filepath}: {e}")
        
        # Try alternative parsing method for corrupt PDFs
        try:
            import fitz  # PyMuPDF - install with 'pip install PyMuPDF' if needed
            print(f"Attempting alternative PDF extraction with PyMuPDF for {filepath}")
            
            content = ""
            doc = fitz.open(filepath)
            num_pages = len(doc)
            
            for page_num in range(num_pages):
                page = doc[page_num]
                content += page.get_text() + "\n\n"
                
            doc.close()
            
            return {
                'content': content.strip(),
                'metadata': {
                    'filepath': filepath,
                    'num_pages': num_pages,
                    'length': len(content),
                    'type': 'pdf',
                    'extraction_method': 'pymupdf_fallback'
                }
            }
        except ImportError:
            print("PyMuPDF not installed. Consider installing for better PDF extraction.")
            # Continue with the error case
        except Exception as fallback_error:
            print(f"Alternative PDF extraction also failed: {fallback_error}")
            
        return {
            'content': f"Error loading document: {str(e)}",
            'metadata': {
                'filepath': filepath,
                'error': str(e),
                'type': 'error'
            }
        }

def load_multiple_documents(filepaths):
    """
    Load and parse multiple standard documents from the given list of filepaths.

    Args:
        filepaths (list): A list of paths to the document files.

    Returns:
        list: A list of structured representations of the documents' content.
    """
    documents = []
    for filepath in filepaths:
        documents.append(load_document(filepath))
    return documents

def load_documents():
    """
    Load all documents needed for analysis, prioritizing the file specified in FINANCIAL_DATA_SOURCE.
    Provides enhanced processing for AAOIFI standards.

    Returns:
        list: A list of structured document data
    """
    # Use the FINANCIAL_DATA_SOURCE from settings
    from src.config.settings import FINANCIAL_DATA_SOURCE
    
    # Check if there's a specific resource file in the data directory
    resource_path = os.path.join(DATA_DIR, FINANCIAL_DATA_SOURCE)
    
    if os.path.exists(resource_path):
        print(f"Loading financial data from: {resource_path}")
        document = load_document(resource_path)
        
        # Enhanced processing for AAOIFI standards
        content = document.get('content', '')
        if "AAOIFI" in content or "FAS" in content or "Financial Accounting Standard" in content:
            print("Detected AAOIFI Financial Accounting Standard")
            
            # Extract FAS identification information
            fas_info = extract_and_analyze_aaoifi_content(content)
            
            # Log detected information
            if 'standard_number' in fas_info:
                print(f"Identified as FAS {fas_info['standard_number']}")
            if 'standard_title' in fas_info:
                print(f"Title: {fas_info['standard_title']}")
            if 'effective_date' in fas_info:
                print(f"Effective date: {fas_info['effective_date']}")
                
            # Check for key sections of a standard and report missing sections
            sections = fas_info.get('sections_present', {})
            missing_sections = [k for k, v in sections.items() if not v]
            if missing_sections:
                print(f"WARNING: Document may be missing these key sections: {', '.join(missing_sections)}")
        
        return [document]
    
    # Otherwise load from standards directory
    print("No specific data source found. Loading all files from standards directory.")
    documents = []
    for filename in os.listdir(STANDARDS_DIR):
        filepath = os.path.join(STANDARDS_DIR, filename)
        if os.path.isfile(filepath):
            documents.append(load_document(filepath))
            
    return documents