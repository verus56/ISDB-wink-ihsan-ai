# Challenge 1: Islamic Finance Accounting Calculator (AAOIFI Standards)

## Overview

This project is an advanced Retrieval-Augmented Generation (RAG) system designed to answer complex questions about Islamic finance accounting, specifically following AAOIFI standards. It leverages state-of-the-art language models and vector search to provide step-by-step calculations, journal entries, and explanations for contracts like Murabaha and Ijarah.

## System Architecture

- **Document Ingestion**: Loads and parses PDF documents containing AAOIFI standards and examples.
- **Semantic Chunking**: Splits documents into meaningful chunks using custom rules and enriches them with metadata (e.g., contract type, standard).
- **Vector Embedding**: Converts chunks into vector representations using OpenAI or Gemini embeddings.
- **Vector Store (ChromaDB)**: Stores and indexes embeddings for fast similarity search.
- **Retriever**: Finds the most relevant chunks for a user query using Maximum Marginal Relevance (MMR).
- **Prompt Engineering**: Crafts a detailed prompt with context and calculation instructions for the LLM.
- **LLM Reasoning**: Uses OpenAI GPT-4 Turbo or Google Gemini to generate step-by-step answers, calculations, and journal entries.
- **User Interface**: Command-line interface for interactive Q&A.

## How the System Works

1. **PDF Ingestion & Metadata Extraction**
   - The system loads multiple PDF documents containing AAOIFI standards, journal entry examples, and related resources.
   - Each PDF is parsed into pages, and metadata is extracted (e.g., contract type, standard number, presence of examples).

2. **Semantic Chunking**
   - Documents are split into semantically meaningful chunks using custom separators (headers, contract types, accounting terms).
   - Each chunk is further enriched with metadata for more accurate retrieval.

3. **Vector Store Creation**
   - Chunks are embedded using either OpenAI or Google Gemini embedding models.
   - Embeddings are stored in a persistent Chroma vector database for fast similarity search.

4. **Retrieval-Augmented Generation (RAG)**
   - When a user asks a question, the system retrieves the most relevant document chunks using Maximum Marginal Relevance (MMR) for diversity and relevance.
   - The retrieved context is passed to a language model (OpenAI GPT-4 Turbo or Google Gemini) along with a detailed prompt template.

5. **LLM Reasoning & Calculation**
   - The language model is instructed to:
     - Identify the contract and relevant AAOIFI standard.
     - Perform step-by-step calculations (e.g., prime cost, deferred profit, ROU asset).
     - Generate full journal entries with narrations.
     - Create amortization or profit recognition tables.
   - All answers are strictly based on the retrieved context to ensure accuracy.

6. **Interactive Q&A**
   - Users can interactively ask questions about Islamic finance contracts and receive detailed, context-grounded answers.

## Vector Store Deep Dive

The vector store is a critical component of our RAG system, enabling efficient semantic search across AAOIFI standards and Islamic finance documents:

1. **Embedding Generation**:
   - Document chunks are transformed into high-dimensional vectors (embeddings) that capture semantic meaning
   - The system supports two embedding models:
     - OpenAI's `text-embedding-3-large`: 3072-dimensional embeddings optimized for semantic similarity
     - Google's `models/gemini-embedding-exp-03-07`: Advanced embedding model from Gemini's experimental line

2. **Chroma Database Implementation**:
   - The system uses ChromaDB, an open-source vector database, stored in the `./chroma_db` directory
   - Each document chunk is stored alongside its:
     - Vector embedding
     - Original text content
     - Rich metadata (document source, contract type, standard number, etc.)

3. **Metadata-Enhanced Search**:
   - When retrieving context, the system can filter by metadata to focus on specific:
     - Contract types (Murabaha, Ijarah, Salam, etc.)
     - Standards (specific FAS numbers)
     - Document types (examples, standards documentation)
   - This metadata filtering dramatically improves retrieval precision for specific Islamic finance calculations

4. **Similarity Search Mechanisms**:
   - The system employs cosine similarity to measure the distance between query vectors and document vectors
   - Maximum Marginal Relevance (MMR) balances relevance with diversity to avoid redundant information
   - Search parameters are optimized for Islamic finance terminology and AAOIFI-specific concepts

5. **Persistence and Reusability**:
   - Vector embeddings are persisted to disk, avoiding costly re-embedding of documents
   - The system checks for an existing Chroma database before processing PDFs
   - Users can force recreation of the database when new documents are added

6. **Embedding Provider Selection**:
   - Users can choose between OpenAI and Google Gemini embedding models
   - This flexibility allows for performance comparison and adaptation to API availability

7. **Technical Implementation**:
   - Vector dimensionality: 3072 (OpenAI) or model-specific (Gemini)
   - Distance metric: Cosine similarity
   - Storage: Local disk with persistence
   - Queries: Hybrid search with metadata filters and semantic similarity

This vector store implementation enables the system to quickly identify the most relevant AAOIFI standards, calculation methods, and journal entry examples for any Islamic finance accounting query, ensuring accurate and contextually appropriate responses.

## Technologies Used

- **Python**: Core programming language.
- **LangChain**: Framework for building LLM-powered applications, used for chaining retrieval and generation steps.
- **Chroma**: Open-source vector database for storing and searching document embeddings.
- **OpenAI API**: For text embeddings (`text-embedding-3-large`) and LLM (GPT-4 Turbo).
- **Google Gemini API**: For embeddings (`models/gemini-embedding-exp-03-07`) and LLM (Gemini-2.0-flash).
- **tiktoken**: For accurate token counting during chunking.
- **PyPDFLoader**: For extracting text from PDF documents.
- **RecursiveCharacterTextSplitter**: For semantic document chunking.
- **Pprint**: For debug output formatting.

## File Structure

- `challenggemini.py`: Main application logic, user interface, and RAG pipeline.
- `vector_store.py`: Handles PDF loading, chunking, metadata extraction, embedding, and vector store management.
- `challgen1.md`: This documentation file.

## User Flow

1. **Startup**: User runs the script and selects the LLM (OpenAI or Gemini) and embedding provider.
2. **Vector Store**: System checks for an existing Chroma vector store. If not found or if forced, it processes PDFs and creates a new store.
3. **Question Input**: User enters a question (e.g., "How to account for a Murabaha contract under AAOIFI FAS 28?").
4. **Retrieval**: The system retrieves relevant document chunks from the vector store.
5. **LLM Generation**: The LLM generates a detailed, step-by-step answer with calculations and journal entries.
6. **Output**: The answer is displayed to the user.
7. **Repeat**: User can continue asking questions interactively.

## Example Workflow

1. **Startup**: User selects the LLM and embedding provider.
2. **Vector Store**: System loads or creates a Chroma vector store from PDFs.
3. **Question Input**: User enters a question (e.g.,").
4. **Retrieval**: Relevant document chunks are retrieved from the vector store.
5. **LLM Generation**: The LLM generates a detailed, step-by-step answer with calculations and journal entries.
6. **Output**: The answer is displayed to the user.

## Example Question

```
Ghurair Corporation is the largest producer of Palm Oil in Saudi Arabia.
It approached an Islamic Financial Institution (IFI) to finance an Oil Seed flanker machine on the basis of
Murabaha on 1st February, 2024 with a deferred repayment arrangement.
The machine was purchased for SR 150,000 by the IFI on 1st March, 2024. The IFI also incurred SR 15,000 for
transportation, takaful and other expenses to bring the asset to the present condition and location.
The machine was sold onwards on the same date on a credit period of 5 Months. The selling price was
agreed at SR 175,000 which Ghurair Corporation agreed to repay on 31st July, 2024.
```

## Example Output

ANSWER:
### 1. Identify the Islamic Finance Contract
The contract described is an **Ijarah Muntahia Bittamleek (Ijarah MBT)**.

### 2. Determine the Applicable AAOIFI Financial Accounting Standard
The applicable standard is **AAOIFI FAS 32**.

### 3. Calculations for Ijarah MBT (FAS 32)

#### a. Prime Cost of the Asset
Prime cost = Purchase price + Import tax + Freight  
\[ \text{Prime cost} = 450,000 + 12,000 + 30,000 = 492,000 \]

#### b. Right-of-Use (ROU) Asset Calculation
ROU asset = Prime cost - Purchase option price  
\[ \text{ROU asset} = 492,000 - 3,000 = 489,000 \]

#### c. Total Ijarah Payments
Total rentals = Annual rental × Lease term  
\[ \text{Total rentals} = 300,000 \times 2 = 600,000 \]

#### d. Deferred Ijarah Cost
Deferred Ijarah Cost = Total rentals - ROU asset  
\[ \text{Deferred Ijarah Cost} = 600,000 - 489,000 = 111,000 \]

#### e. Amortizable Amount
Amortizable amount = ROU asset - (Residual value - Purchase price)  
\[ \text{Amortizable amount} = 489,000 - (5,000 - 3,000) = 487,000 \]

#### f. Annual Amortization
Annual amortization = Amortizable amount ÷ Lease term  
\[ \text{Annual amortization} = \frac{487,000}{2} = 243,500 \]

### 4. Journal Entries

#### Initial Recognition on 1 January 2019
- **Dr. Right-of-Use Asset** 489,000  
- **Cr. Ijarah Liability** 600,000  
- **Dr. Deferred Ijarah Cost** 111,000  
  - *Narration: To record the initial recognition of the right-of-use asset and Ijarah liability.*

#### Annual Amortization Entry (End of Year 1 and Year 2)
- **Dr. Amortization Expense** 243,500  
- **Cr. Accumulated Amortization** 243,500  
  - *Narration: To record the annual amortization of the right-of-use asset.*

#### Rental Payment Entry (End of Year 1 and Year 2)
- **Dr. Ijarah Liability** 300,000  
- **Cr. Cash/Bank** 300,000  
  - *Narration: To record the payment of annual Ijarah rental.*

## Extensibility

- **Adding New Contracts**: To support more Islamic finance contracts, add relevant PDFs and update the metadata extraction logic in `vector_store.py`.
- **Supporting More LLMs**: The system can be extended to support other LLM providers by adding new initialization logic.
- **Custom Prompts**: Prompt templates can be modified for different calculation or reporting requirements.

## Troubleshooting

- **Chroma Database Issues**: If you encounter errors with the vector store, try deleting the `chroma_db` directory and recreating it.
- **API Keys**: Ensure your OpenAI and Google Gemini API keys are set as environment variables or directly in the script.
- **PDF Loading Errors**: Check that all PDF files are present in the project directory and are not corrupted.

## How to Run

1. Install dependencies:
   ```
   pip install langchain langchain-openai langchain-google-genai chromadb tiktoken pypdf
   ```
2. Place your PDF resources in the project directory.
3. Run the main script:
   ```
   python challenggemini.py
   ```
4. Follow the prompts to select LLM, embedding provider, and ask questions.

## Notes

- API keys for OpenAI and Google Gemini must be set as environment variables or in the script.
- The system is designed for educational and research purposes.

## License

MIT License

`