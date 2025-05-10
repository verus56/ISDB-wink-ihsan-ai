# Challenge 2: AAOIFI FAS Identification System

## Overview

This project implements an advanced system to analyze financial transactions and identify the most applicable AAOIFI Financial Accounting Standards (FAS) for Islamic finance. It uses a multi-stage Retrieval Augmented Generation (RAG) pipeline, advanced parsing, and probabilistic ranking to provide detailed, explainable results.

---

## How It Works

### 1. Input

- The user provides a transaction scenario (e.g., a buyout, equity transfer, construction contract, etc.).
- The system can be run interactively or with a sample transaction.

### 2. Parsing

- The `TransactionParser` extracts structured data from the scenario:
  - Financial values, dates, accounts
  - Accounting and Islamic finance terms
  - Transaction types (with confidence scores)
  - Journal entries
  - Context (industry, parties, purpose, timeframe)

### 3. Multi-Stage RAG Retrieval

- **Stage 1: Domain Filtering**
  - Uses transaction types and keywords to retrieve relevant FAS domains from a vector database of AAOIFI standards.
- **Stage 2: Detailed Context Matching**
  - Matches journal entry patterns, context, and transaction details to find specific FAS requirements.
- **Stage 3: Contradictory Standards Check**
  - Searches for alternative treatments or contradictions between standards.

### 4. Multi-Perspective Analysis

- The `AnalysisEngine`:
  - Matches transaction features to FAS requirements.
  - Scores and ranks standards using a weighted probabilistic framework.
  - Uses an LLM to generate structured reasoning for each recommended standard.
  - Handles edge cases (e.g., construction contracts, banking buyouts).

### 5. Response Generation

- The `ResponseGenerator` formats the results:
  - Prioritized list of applicable standards with probabilities.
  - Detailed reasoning for each standard.
  - Highlights of potential conflicts or alternative treatments.

---

## System Components

- **parser_module.py**: Extracts structured elements from transaction text.
- **enhanced_rag.py**: Multi-stage retrieval pipeline for relevant FAS content.
- **analysis_engine.py**: Probabilistic ranking and reasoning for standard selection.
- **vector_store.py**: Loads and manages the vector database of AAOIFI standards.
- **main.py**: Orchestrates the workflow and provides the CLI interface.

---

## Example Workflow

1. **User Input**:
   ```
   Context: GreenTech exits in Year 3, and Al Baraka Bank buys out its stake.
   Adjustments:  
   Buyout Price: $1,750,000 
   Bank Ownership: 100% 
   Accounting Treatment:  
   Derecognition of GreenTech’s equity 
   Recognition of acquisition expense 
   Journal Entry for Buyout: 
   Dr. GreenTech Equity      
   Cr. Cash              
   $1,750,000   
   $1,750,000   
   ```

2. **System Output**:
   - Identifies likely standards (e.g., FAS 4, FAS 20) with probabilities.
   - Provides reasoning for each, referencing transaction features and FAS requirements.
   - Highlights if there are alternative treatments or contradictions.

---

## Usage

1. **Install dependencies** (see requirements in the main README).
2. **Run the system**:
   ```bash
   python main.py
   ```
3. **Follow prompts** to enter your transaction scenario and select the LLM model.

---

## Details & Advanced Features

- **LLM Choice**: Supports both OpenAI GPT-4 and Google Gemini for reasoning and retrieval.
- **Embeddings**: Vector search can use OpenAI or Gemini embeddings.
- **Semantic Chunking**: Documents are split by semantic boundaries for better retrieval.
- **Probabilistic Ranking**: Standards are ranked using weighted features (transaction type, journal patterns, context).
- **Edge Case Handling**: Special logic for construction contracts, reversals, and banking/equity buyouts.
- **Explainability**: Every recommendation is accompanied by structured, LLM-generated reasoning.

---

## File Structure

- `main.py` — Entry point, CLI, and workflow orchestration
- `parser_module.py` — Transaction parsing and structuring
- `enhanced_rag.py` — Multi-stage retrieval logic
- `analysis_engine.py` — Ranking and reasoning
- `vector_store.py` — Vector DB management

---

## Support

For questions or issues, please open an issue in the repository.

