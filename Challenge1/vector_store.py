import os
import pathlib
import tiktoken
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

# Set API keys
os.environ["OPENAI_API_KEY"] = "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"
os.environ["GOOGLE_API_KEY"] = "AIzaSyBVdL1c0gq0vztjKwKMar2Ns6PoULzEK9w"

# Define the persistent directory for Chroma
CHROMA_PERSIST_DIR = "./chroma_db"

# Load PDF document with metadata
def load_pdf(file_path):
    print(f"Loading PDF from {file_path}...")
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    # Extract filename without extension for metadata
    import os
    filename = os.path.basename(file_path)
    filename_without_ext = os.path.splitext(filename)[0]

    # Add metadata to each document
    for doc in documents:
        # Initialize metadata if it doesn't exist
        if not hasattr(doc, 'metadata') or doc.metadata is None:
            doc.metadata = {}

        # Add source file information
        doc.metadata['source'] = filename
        doc.metadata['source_name'] = filename_without_ext

        # Detect and tag financial standards
        content = doc.page_content.lower()

        # Tag AAOIFI Financial Accounting Standards
        if 'fas ' in content or 'financial accounting standard' in content:
            doc.metadata['document_type'] = 'financial_standard'

            # Try to identify specific FAS standards
            fas_standards = {
                'fas 4': 'murabaha',
                'fas 7': 'salam',
                'fas 10': 'istisna',
                'fas 28': 'murabaha_deferred_payment',
                'fas 32': 'ijarah'
            }

            for standard, topic in fas_standards.items():
                if standard in content:
                    doc.metadata['standard'] = standard
                    doc.metadata['topic'] = topic

        # Tag journal entries and examples
        if 'journal entry' in content or 'example' in content:
            doc.metadata['contains_examples'] = True

        # Tag by Islamic finance contract types
        contract_types = ['murabaha', 'ijarah', 'salam', 'istisna', 'musharakah', 
                         'mudarabah', 'wakala', 'takaful', 'sukuk', 'qard']

        for contract in contract_types:
            if contract in content:
                doc.metadata['contract_type'] = contract
                break

    print(f"Loaded {len(documents)} pages from PDF with metadata")
    return documents

# Split documents into chunks using semantic chunking
def split_documents(documents):
    print("Splitting documents into chunks using semantic chunking...")

    # Define separators that respect semantic boundaries
    # Order matters: it will try to split by the first separator, then the second, etc.
    separators = [
        # First try to split by sections/headers
        "\n## ", "\n### ", "\n#### ", "\n# ", "CHAPTER ", "Section ",

        # Then by semantic boundaries like examples, formulas, etc.
        "\nExample:", "\nFormula:", "\nCalculation:", "\nCase Study:", "\nIllustration:",

        # Financial and Islamic finance specific terms and standards
        "\nJournal Entry:", "\nAccounting Treatment:", "\nDisclosure Requirements:",
        "\nFAS ", "Financial Accounting Standard ", "Shari'ah Standard ",

        # Islamic finance contract types
        "\nMurabaha:", "\nIjarah:", "\nSalam:", "\nIstisna'a:", "\nMusharakah:",
        "\nMudarabah:", "\nWakala:", "\nTakaful:", "\nSukuk:", "\nQard:",

        # Accounting-specific terms
        "\nBalance Sheet:", "\nIncome Statement:", "\nCash Flow:", "\nProfit Recognition:",
        "\nAsset Valuation:", "\nAmortization Schedule:", "\nDeferred Payment:",

        # Mathematical and calculation indicators
        "Table ", "Figure ", "Equation ", "Formula: ", "= ", "USD ", "% ",

        # Then by double newlines (paragraphs)
        "\n\n",

        # Then by single newlines
        "\n",

        # Finally by sentences if needed
        ". ", "? ", "! ", "; ",

        # Last resort: split by characters
        ""
    ]

    # Use RecursiveCharacterTextSplitter with tiktoken encoder for more accurate token counting
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        separators=separators,
        chunk_size=1200,  # Larger chunk size to keep related content together
        chunk_overlap=200,  # Increased overlap to maintain context between chunks
        encoding_name="cl100k_base"  # The encoding used by OpenAI models
    )

    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks using semantic boundaries")

    # Additional logging to help understand the chunking
    avg_chunk_size = sum(len(chunk.page_content) for chunk in chunks) / len(chunks) if chunks else 0
    print(f"Average chunk size: {avg_chunk_size:.2f} characters")

    # Enhance metadata for each chunk based on content
    for chunk in chunks:
        content = chunk.page_content.lower()

        # If not already tagged, check for standards in the chunk content
        if 'standard' not in chunk.metadata:
            fas_standards = {
                'fas 4': 'murabaha',
                'fas 7': 'salam',
                'fas 10': 'istisna',
                'fas 28': 'murabaha_deferred_payment',
                'fas 32': 'ijarah'
            }

            for standard, topic in fas_standards.items():
                if standard in content:
                    chunk.metadata['standard'] = standard
                    chunk.metadata['topic'] = topic
                    break

        # Tag journal entries and examples if not already tagged
        if 'contains_examples' not in chunk.metadata and ('journal entry' in content or 'example' in content):
            chunk.metadata['contains_examples'] = True

        # Tag by Islamic finance contract types if not already tagged
        if 'contract_type' not in chunk.metadata:
            contract_types = ['murabaha', 'ijarah', 'salam', 'istisna', 'musharakah', 
                             'mudarabah', 'wakala', 'takaful', 'sukuk', 'qard']

            for contract in contract_types:
                if contract in content:
                    chunk.metadata['contract_type'] = contract
                    break

    print("Enhanced metadata for all chunks based on content")
    return chunks

# Check if Chroma database exists
def chroma_db_exists():
    db_path = pathlib.Path(CHROMA_PERSIST_DIR)
    return db_path.exists() and any(db_path.iterdir())

# Delete existing Chroma database
def delete_chroma_db():
    import shutil
    import time
    db_path = pathlib.Path(CHROMA_PERSIST_DIR)
    if db_path.exists():
        confirmation = input(f"Voulez-vous supprimer la base de données Chroma existante à {CHROMA_PERSIST_DIR}? (oui/non): ")
        if confirmation.lower() in ['oui', 'o', 'yes', 'y']:
            print(f"Deleting existing Chroma database at {CHROMA_PERSIST_DIR}...")

            # Try to delete with retries in case of file locks
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    shutil.rmtree(db_path)
                    print("Existing database deleted successfully.")
                    return True
                except PermissionError as e:
                    if attempt < max_retries - 1:
                        print(f"Permission error: {e}. Retrying in 2 seconds...")
                        time.sleep(2)  # Wait before retrying
                    else:
                        print(f"Failed to delete database after {max_retries} attempts: {e}")
                        print("Please close any applications that might be using the database and try again.")
                        return False
                except Exception as e:
                    print(f"Error deleting database: {e}")
                    return False
        else:
            print("Suppression annulée.")
            return False
    else:
        print("No existing database found to delete.")
        return True  # No database to delete is considered success

# Get embeddings based on provider choice
def get_embeddings(embedding_provider="openai"):
    if embedding_provider.lower() == "gemini":
        print("Using Gemini embeddings (models/gemini-embedding-exp-03-07)...")
        return GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-exp-03-07")
    else:
        print("Using OpenAI embeddings (text-embedding-3-large)...")
        return OpenAIEmbeddings(model="text-embedding-3-large")

# Load existing Chroma database
def load_existing_vector_store(embedding_provider="openai"):
    print("Loading existing Chroma vector store...")
    # Get embeddings based on provider choice
    embeddings = get_embeddings(embedding_provider)

    vector_store = Chroma(
        persist_directory=CHROMA_PERSIST_DIR,
        embedding_function=embeddings
    )
    print("Existing Chroma vector store loaded successfully")
    return vector_store

# Create new vector store
def create_vector_store(chunks, embedding_provider="openai"):
    print("Creating new Chroma vector store...")
    # Get embeddings based on provider choice
    embeddings = get_embeddings(embedding_provider)
    # Use Chroma with persist_directory to save the vector store
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PERSIST_DIR
    )
    # Persist the vector store to disk
    vector_store.persist()
    print("New Chroma vector store created and persisted successfully")
    return vector_store

# Main function to get vector store (either load existing or create new)
def get_vector_store(pdf_paths=["resouce.pdf", "Shari'ah Standards.pdf", "AAOIFI FAS_ Journal Entry Examples.pdf", "Journal Entries for AAOIFI Financial Accounting Standards.pdf",], force_recreate=False, embedding_provider="openai"):
    """
    Get a vector store, either by loading an existing one or creating a new one.

    Args:
        pdf_paths: List of PDF paths to process if creating a new vector store
        force_recreate: Whether to force recreation of the database
        embedding_provider: Which embedding provider to use ("openai" or "gemini")

    Returns:
        A Chroma vector store
    """
    # Check if we should force recreation of the database
    deletion_successful = True
    if force_recreate and chroma_db_exists():
        deletion_successful = delete_chroma_db()
        # If deletion failed or was cancelled, check if we should still try to recreate
        if not deletion_successful and chroma_db_exists():
            print("Warning: Could not delete existing database. Will try to use it instead.")
            force_recreate = False

    # Check if Chroma database already exists
    if chroma_db_exists() and (not force_recreate or not deletion_successful):
        print("Existing Chroma database found. Skipping PDF processing...")
        return load_existing_vector_store(embedding_provider)
    else:
        print("Processing PDFs to create new vector store...")
        # Load and process all PDFs
        all_documents = []
        for pdf_path in pdf_paths:
            try:
                documents = load_pdf(pdf_path)
                all_documents.extend(documents)
            except Exception as e:
                print(f"Error loading {pdf_path}: {e}")

        if not all_documents:
            raise ValueError("No documents were successfully loaded. Please check the PDF paths.")

        print(f"Processing {len(all_documents)} documents with semantic chunking...")
        chunks = split_documents(all_documents)
        return create_vector_store(chunks, embedding_provider)
