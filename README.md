# Islamic Banking Q&A System

This project implements a question-answering system for Islamic banking scenarios using LangChain, LangGraph, and OpenAI. The system uses a vector store created from a PDF document to retrieve relevant information and generate detailed answers to questions about Islamic banking concepts, calculations, and scenarios, with a focus on accounting journal entries according to AAOIFI standards.

## Features

- PDF document processing and chunking
- Vector store creation using Chroma with cosine similarity
- Persistent storage of vector embeddings
- Question-answering workflow using LangGraph
- Interactive Q&A interface
- Specialized Islamic finance accounting prompt with AAOIFI standards
- Structured output format for journal entries

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`

## Setup

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Make sure the `resouce.pdf` file is in the project directory
4. Run the main script:
   ```
   python main.py
   ```

## Usage

When you run the script for the first time, it will:

1. Load and process the PDF document
2. Split the document into manageable chunks
3. Create a vector store from the document chunks and persist it to disk
4. Run an example question about an Ijarah MBT arrangement
5. Enter an interactive mode where you can ask your own questions

On subsequent runs, the script will:

1. Detect the existing vector store and skip the PDF processing step
2. Load the previously created vector store directly
3. Run the example question and enter interactive mode

This optimization ensures that the PDF is only processed once, making subsequent runs faster and more efficient.

In the interactive mode, you can type your questions about Islamic banking. Type 'exit' to quit the program.

## Example Question

The system comes with a pre-loaded example question about an Ijarah MBT arrangement:

```
On 1 January 2019 Alpha Islamic bank (Lessee) entered into an Ijarah MBT arrangement with 
Super Generators for Ijarah of a heavy-duty generator purchase by Super Generators at a price 
of USD 450,000. 
Super Generators has also paid USD 12,000 as import tax and US 30,000 for freight charges. 
The Ijarah Term is 02 years and expected residual value at the end USD 5,000. At the end of 
Ijarah Term, it is highly likely that the option of transfer of ownership of the underlying asset to 
the lessee shall be exercised through purchase at a price of USD 3,000. 
Alpha Islamic Bank will amortize the 'right of use' on yearly basis and it is required to pay yearly 
rental of USD 300,000.

Please provide the journal entries for the initial recognition and subsequent accounting treatment for this Ijarah arrangement according to AAOIFI standards.
```

The system will respond with properly formatted journal entries according to AAOIFI standards, specifically FAS 9 (Ijarah and Ijarah Muntahia Bittamleek) or FAS 32 (Ijarah), in a structured table format.

## How It Works

The project is organized into two main components:

1. **Vector Store Module** (`vector_store.py`):
   - Handles all PDF processing and vector store operations
   - On first run:
     - Loads the PDF document and splits it into manageable chunks
     - Embeds these chunks and stores them in a Chroma vector store with persistent storage
     - Saves the vector store to disk in the "./chroma_db" directory
   - On subsequent runs:
     - Detects the existing Chroma database in the "./chroma_db" directory
     - Loads the pre-processed vector store directly, skipping the PDF processing step

2. **Main Application** (`main.py`):
   - Imports the vector store functionality from the vector store module
   - Creates a retriever from the vector store
   - Implements the question-answering workflow using LangGraph
   - Handles user interaction

3. For all runs, when a question is asked, the system:
   - Retrieves the most relevant chunks from the vector store using cosine similarity
   - Passes these chunks along with the question to the LLM
   - Generates a detailed answer based on the retrieved information, formatted according to AAOIFI standards
   - Returns the answer to the user in a structured table format for journal entries

This modular approach ensures that:
- The resource-intensive PDF processing and embedding generation only happens once
- The code is more maintainable with clear separation of concerns
- The system is more efficient for repeated use
- High-quality text embeddings using OpenAI's text-embedding-3-large model

## Customization

You can modify the following parameters in the code:
- Chunk size and overlap in the `split_documents` function
- Number of retrieved documents and similarity threshold in the `retriever` creation
- The prompt template to customize which AAOIFI standards are included
- The persistence directory for the Chroma vector store
- The similarity function used for retrieval (currently set to cosine)
