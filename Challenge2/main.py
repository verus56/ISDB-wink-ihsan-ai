import os
from typing import Dict, Any, Optional
from parser_module import TransactionParser
from enhanced_rag import EnhancedRAG
from analysis_engine import AnalysisEngine
from response_generator import ResponseGenerator
from vector_store import get_vector_store
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

# Set API keys
os.environ[
    "OPENAI_API_KEY"] = "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"
os.environ["GOOGLE_API_KEY"] = "AIzaSyBVdL1c0gq0vztjKwKMar2Ns6PoULzEK9w"

# Function to initialize the appropriate LLM based on user choice
def initialize_llm(model_choice="openai"):
    if model_choice.lower() == "gemini":
        # Initialize Gemini
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.1,  # Lower temperature for more precise calculations
            max_output_tokens=4096,
        )
    else:
        # Initialize OpenAI (default)
        return ChatOpenAI(
            model="gpt-4-turbo",
            temperature=0.1,  # Lower temperature for more deterministic outputs
        )

class AAOIFIFASIdentifier:
    """
    AAOIFI FAS Identification System

    Analyzes financial transactions and identifies applicable AAOIFI Financial Accounting Standards (FAS)
    with weighted probabilities and reasoning.

    Flow Sequence:
    1. Receive transaction input
    2. Parse and extract structured elements
    3. Execute multi-stage RAG retrieval
    4. Apply multi-perspective analysis
    5. Generate prioritized standards with reasoned explanations
    6. Format and return response
    """

    def __init__(self, model_choice="openai"):
        """
        Initialize the AAOIFI FAS Identification System

        Args:
            model_choice: The LLM model to use ("openai" or "gemini")
        """
        # Load vector store with the same embedding provider as the LLM
        print("Initializing AAOIFI FAS Identification System...")
        embedding_provider = "gemini" if model_choice.lower() == "gemini" else "openai"
        self.vector_store = get_vector_store(embedding_provider=embedding_provider)
        self.model_choice = model_choice

        # Get the LLM based on user choice
        llm = initialize_llm(model_choice)
        print(f"Using {model_choice.upper()} as the language model and {embedding_provider.upper()} embeddings.")

        # Initialize components
        self.parser = TransactionParser()
        self.rag_system = EnhancedRAG(self.vector_store, llm)
        self.analysis_engine = AnalysisEngine(llm)
        self.response_generator = ResponseGenerator(llm)

        print("System initialized successfully.")

    def process_transaction(self, transaction_text: str) -> Dict[str, Any]:
        """
        Process a transaction and identify applicable AAOIFI FAS standards

        Args:
            transaction_text: The transaction scenario to analyze

        Returns:
            Dictionary with analysis results
        """
        print("\nProcessing transaction...")

        # Step 1: Parse and extract structured elements
        print("Step 1: Parsing transaction...")
        parsed_transaction = self.parser.parse(transaction_text)

        # Step 2: Execute multi-stage RAG retrieval
        print("Step 2: Executing multi-stage RAG retrieval...")
        rag_results = self.rag_system.process_transaction(parsed_transaction)

        # Step 3: Apply multi-perspective analysis
        print("Step 3: Applying multi-perspective analysis...")
        analysis_results = self.analysis_engine.analyze_transaction(parsed_transaction, rag_results)

        # Step 4: Generate response
        print("Step 4: Generating response...")
        response = self.response_generator.generate_response(
            parsed_transaction,
            rag_results,
            analysis_results
        )

        # Format response as text
        formatted_response = self.response_generator.format_response_as_text(response)

        print("Transaction processing complete.")

        return {
            "formatted_response": formatted_response,
            "raw_response": response,
            "parsed_transaction": parsed_transaction,
            "rag_results": rag_results,
            "analysis_results": analysis_results
        }

def get_user_input() -> str:
    """Get transaction scenario from user input"""
    print("\nPlease enter your transaction scenario (press Enter twice when finished):")
    lines = []
    while True:
        line = input()
        if line.strip() == "":
            break
        lines.append(line)
    return "\n".join(lines)

def main():
    """Main function to run the AAOIFI FAS Identification System"""
    print("=" * 80)
    print("AAOIFI FAS IDENTIFICATION SYSTEM")
    print("=" * 80)
    print("This system analyzes financial transactions and identifies applicable AAOIFI FAS standards")
    print("with weighted probabilities and reasoning.")
    print("-" * 80)

    # Ask user to choose LLM model
    print("\nChoose LLM model:")
    print("1. OpenAI (GPT-4 Turbo)")
    print("2. Google (Gemini-2.0-flash)")
    model_choice = input("Enter your choice (1 or 2, default is 1): ")
    llm_provider = "gemini" if model_choice == "2" else "openai"

    # Initialize the system with the chosen model
    print(f"\nInitializing system with {llm_provider.upper()} model...")
    system = AAOIFIFASIdentifier(model_choice=llm_provider)

    while True:
        # Get transaction input
        transaction_text = get_user_input()

        if not transaction_text.strip():
            print("No transaction provided. Please try again.")
            continue

        # Process the transaction
        results = system.process_transaction(transaction_text)

        # Display the formatted response
        print("\n" + "=" * 80)
        print("ANALYSIS RESULT:")
        print("-" * 80)
        print(results["formatted_response"])
        print("=" * 80)

        # Ask if the user wants to analyze another transaction
        choice = input("\nWould you like to analyze another transaction? (y/n): ").strip().lower()
        if choice != 'y':
            print("Thank you for using the AAOIFI FAS Identification System.")
            break

def process_sample_transaction(model_choice="openai") -> None:
    """
    Process a sample transaction for testing purposes

    Args:
        model_choice: The LLM model to use ("openai" or "gemini")
    """
    print(f"\nProcessing sample transaction using {model_choice.upper()} model...")
    system = AAOIFIFASIdentifier(model_choice=model_choice)

    print("\nPlease enter your sample transaction (press Enter twice when finished):")
    lines = []
    while True:
        line = input()
        if line.strip() == "":
            break
        lines.append(line)
    sample_transaction = "\n".join(lines)
    if not sample_transaction.strip():
        print("No sample transaction provided. Exiting sample transaction processing.")
        return

    results = system.process_transaction(sample_transaction)

    print("\n" + "=" * 80)
    print(" TRANSACTION ANALYSIS:")
    print("-" * 80)
    print(results["formatted_response"])
    print("=" * 80)

if __name__ == "__main__":
    # Ask user to choose LLM model for sample transaction
    print("=" * 80)
    print("AAOIFI FAS IDENTIFICATION SYSTEM")
    print("=" * 80)
    print("\nChoose LLM model for sample transaction:")
    print("1. OpenAI (GPT-4 Turbo)")
    print("2. Google (Gemini-2.0-flash)")
    model_choice = input("Enter your choice (1 or 2, default is 1): ")
    llm_provider = "gemini" if model_choice == "2" else "openai"

    # Test with a sample transaction
    process_sample_transaction(model_choice=llm_provider)

    # Run the main interactive program
    main()
