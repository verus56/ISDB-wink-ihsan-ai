# AAOIFI Islamic Finance Challenges

This repository contains solutions for three challenges in Islamic Finance, focusing on AAOIFI (Accounting and Auditing Organization for Islamic Financial Institutions) standards implementation, identification, and enhancement.

## Table of Contents

- [Challenge 1: Islamic Finance Accounting Calculator](#challenge-1-islamic-finance-accounting-calculator-aaoifi-standards)
- [Challenge 2: AAOIFI FAS Identification System](#challenge-2-aaoifi-fas-identification-system)
- [Challenge 3: AAOIFI Standards Enhancement System](#challenge-3-aaoifi-standards-enhancement-system)
- [Setup and Requirements](#setup-and-requirements)
- [Challenge Documentation](#challenge-documentation)

## Challenge 1: Islamic Finance Accounting Calculator (AAOIFI Standards)

### Overview

An advanced Retrieval-Augmented Generation (RAG) system designed to answer complex questions about Islamic finance accounting following AAOIFI standards. It provides step-by-step calculations, journal entries, and explanations for contracts like Murabaha and Ijarah.

### System Architecture

- **Document Ingestion**: Loads and parses PDF documents containing AAOIFI standards and examples.
- **Semantic Chunking**: Splits documents into meaningful chunks using custom rules and enriches them with metadata.
- **Vector Embedding**: Converts chunks into vector representations using OpenAI or Gemini embeddings.
- **Vector Store (ChromaDB)**: Stores and indexes embeddings for fast similarity search.
- **Retriever**: Finds the most relevant chunks for a user query using Maximum Marginal Relevance (MMR).
- **Prompt Engineering**: Crafts a detailed prompt with context and calculation instructions for the LLM.
- **LLM Reasoning**: Uses OpenAI GPT-4 Turbo or Google Gemini to generate answers, calculations, and journal entries.
- **User Interface**: Command-line interface for interactive Q&A.

### How the System Works

1. **PDF Ingestion & Metadata Extraction**
2. **Semantic Chunking**
3. **Vector Store Creation**
4. **Retrieval-Augmented Generation (RAG)**
5. **LLM Reasoning & Calculation**
6. **Interactive Q&A**

### Vector Store Deep Dive

The vector store enables efficient semantic search across AAOIFI standards:
- **Embedding Generation**: Using OpenAI's `text-embedding-3-large` or Google's Gemini embeddings
- **ChromaDB Implementation**: Storing vectors alongside rich metadata
- **Metadata-Enhanced Search**: Filtering by contract types, standards, document types
- **Similarity Search**: Using cosine similarity with Maximum Marginal Relevance
- **Persistence and Flexibility**: Supporting both OpenAI and Google Gemini models

### Example Usage

```
Ghurair Corporation is the largest producer of Palm Oil in Saudi Arabia.
It approached an Islamic Financial Institution (IFI) to finance an Oil Seed flanker machine on the basis of
Murabaha on 1st February, 2024 with a deferred repayment arrangement.
The machine was purchased for SR 150,000 by the IFI on 1st March, 2024. The IFI also incurred SR 15,000 for
transportation, takaful and other expenses to bring the asset to the present condition and location.
The machine was sold onwards on the same date on a credit period of 5 Months. The selling price was
agreed at SR 175,000 which Ghurair Corporation agreed to repay on 31st July, 2024.
```

## Challenge 2: AAOIFI FAS Identification System

### Overview

An advanced system to analyze financial transactions and identify the most applicable AAOIFI Financial Accounting Standards (FAS) for Islamic finance. It uses a multi-stage Retrieval Augmented Generation (RAG) pipeline, advanced parsing, and probabilistic ranking.

### How It Works

1. **Input**: User provides a transaction scenario
2. **Parsing**: `TransactionParser` extracts structured data from the scenario
3. **Multi-Stage RAG Retrieval**:
   - **Stage 1**: Domain filtering
   - **Stage 2**: Detailed context matching
   - **Stage 3**: Contradictory standards check
4. **Multi-Perspective Analysis**: Matches features, ranks standards, generates reasoning
5. **Response Generation**: Formats results with prioritized standards and reasoning

### System Components

- **parser_module.py**: Extracts structured elements from transaction text
- **enhanced_rag.py**: Multi-stage retrieval pipeline for relevant FAS content
- **analysis_engine.py**: Probabilistic ranking and reasoning for standard selection
- **vector_store.py**: Loads and manages the vector database of AAOIFI standards
- **main.py**: Orchestrates the workflow and provides the CLI interface

### Example Workflow

**User Input**:
```
Context: GreenTech exits in Year 3, and Al Baraka Bank buys out its stake.
Adjustments:  
Buyout Price: $1,750,000 
Bank Ownership: 100% 
Accounting Treatment:  
Derecognition of GreenTech's equity 
Recognition of acquisition expense 
Journal Entry for Buyout: 
Dr. GreenTech Equity      
Cr. Cash              
$1,750,000   
$1,750,000   
```

**System Output**:
- Identifies likely standards with probabilities
- Provides reasoning for each recommendation
- Highlights alternative treatments or contradictions

### Advanced Features

- **LLM Choice**: Supports both OpenAI GPT-4 and Google Gemini
- **Embeddings**: Vector search can use OpenAI or Gemini embeddings
- **Probabilistic Ranking**: Standards ranked using weighted features
- **Edge Case Handling**: Special logic for construction contracts, reversals, banking/equity buyouts
- **Explainability**: Every recommendation includes structured reasoning

## Challenge 3: AAOIFI Standards Enhancement System

### Overview

A multi-agent system designed to analyze and enhance the standards set by AAOIFI. The system leverages specialized agents powered by GPT-4o and GPT-4-turbo models to ensure comprehensive evaluation and compliance with Shariah principles.

### Key Features

- **Dual-Model Architecture**: Uses both GPT-4o (primary) and GPT-4-turbo (secondary)
- **Multi-Agent Collaboration**: Specialized agents for standards review, compliance checking, Shariah expertise, and financial analysis
- **Transparent Amendment Process**: All amendments include reasoning and sources
- **Enhanced Reporting**: Detailed reports with verification steps and confidence scores
- **Visualization**: Process flowcharts and confidence heatmaps

### How the System Works

1. **Document Loading and Processing**: Loads AAOIFI standard documents and extracts text using PyPDF2
2. **Dual-Model Analysis**: Primary analysis by GPT-4o, verification by GPT-4-turbo
3. **Multi-Agent Workflow**: Orchestrates four specialized agents:
   - **Standards Reviewer Agent**: Identifies enhancement opportunities
   - **Compliance Checker Agent**: Verifies Shariah alignment
   - **Shariah Expert Agent**: Provides Islamic jurisprudence insights
   - **Financial Analyst Agent**: Assesses financial implications
4. **Amendment Generation and Verification**: Formulates amendments with reasoning and sources
5. **Visualization and Reporting**: Generates reports and visual flowcharts

### System Architecture

```
                  ┌─────────────────┐
                  │ Coordinator     │
                  │ Agent           │
                  └─────────────────┘
                          │
            ┌─────────────┼─────────────┐
            │             │             │
  ┌─────────▼─────┐ ┌─────▼─────┐ ┌─────▼─────┐
  │ Standards     │ │ Shariah   │ │ Financial │
  │ Reviewer      │ │ Expert    │ │ Analyst   │
  └───────────────┘ └───────────┘ └───────────┘
            │             │             │
            └─────────────┼─────────────┘
                          │
                  ┌───────▼───────┐
                  │ Compliance    │
                  │ Checker       │
                  └───────────────┘
                          │
                  ┌───────▼───────┐
                  │ Report        │
                  │ Generator     │
                  └───────────────┘
```

### Project Structure

```
aaoifi-enhancement-system
├── src
│   ├── main.py                     # Entry point
│   ├── agents                      # Agent implementations
│   ├── tools                       # Utility tools
│   ├── memory                      # Conversation history
│   ├── config                      # Configuration settings
│   └── utils                       # Utility functions
├── data
│   ├── standards                   # Standard documents
│   └── output                      # Generated outputs
├── tests                           # Unit tests
├── requirements.txt                # Project dependencies
├── run_agent.py                    # Script to run the system
└── README.md                       # Project documentation
```

### Usage Examples

**Example 1: Standard Review and Enhancement**
```
python run_agent.py
```
Output includes detailed analysis, amendment proposals, visualization flowcharts, and a full report.

**Example 2: Custom Standard Analysis**
1. Place your PDF file in the data directory
2. Update the FINANCIAL_DATA_SOURCE environment variable
3. Run the system

## Setup and Requirements

### General Requirements

- Python 3.8+
- OpenAI API key
- Google API key (optional for Gemini models)

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd aaoifi-islamic-finance
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```
   OPENAI_API_KEY=your_openai_api_key
   GOOGLE_API_KEY=your_google_api_key  # if using Gemini models
   ```

### Running the Challenges

- **Challenge 1**:
  ```
  cd Challenge1
  python challenggemini.py
  ```

- **Challenge 2**:
  ```
  cd Challenge2
  python main.py
  ```

- **Challenge 3**:
  ```
  cd Challenge3/aaoifi-enhancement-system
  python run_agent.py
  ```

## Challenge Documentation

Each challenge has its own detailed README file that provides in-depth explanations, efficiency considerations, and specific requirements:

- **Challenge 1**: See `Challenge1/challgen1.md` for detailed documentation on the Islamic Finance Accounting Calculator, including system architecture, vector store implementation, and usage examples.

- **Challenge 2**: See `Challenge2/challgne2.md` for comprehensive information on the AAOIFI FAS Identification System, including the multi-stage RAG pipeline, parsing techniques, and example workflows.

- **Challenge 3**: See `Challenge3/aaoifi-enhancement-system/Challenge3.md` for extensive details on the AAOIFI Standards Enhancement System, including the multi-agent architecture, verification process, and visualization capabilities.

These individual README files contain valuable information about implementation details, algorithm efficiencies, and specific requirements for each challenge.
