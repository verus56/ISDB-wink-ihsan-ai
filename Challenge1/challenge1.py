import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from vector_store import get_vector_store, split_documents
from langchain_openai import ChatOpenAI
from pprint import pprint

# API key setup (you should use environment variables or a .env file in production)
os.environ["GOOGLE_API_KEY"] = "AIzaSyBVdL1c0gq0vztjKwKMar2Ns6PoULzEK9w"
os.environ["OPENAI_API_KEY"] = "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"


# Function to initialize the appropriate LLM based on user choice
def initialize_llm(model_choice="gemini"):
    if model_choice.lower() == "openai":
        # Initialize OpenAI GPT-4 Turbo
        return ChatOpenAI(
            model="gpt-4o",
            temperature=0.1,  # Lower temperature for more deterministic outputs
        )
    else:
        # Initialize Gemini (default)
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.1,  # Lower temperature for more precise calculations
            max_output_tokens=4096,
        )


# Enhanced vector store setup with better search parameters
def setup_vector_store(embedding_provider="openai", force_recreate=False):
    # Get the vector store with chosen embedding provider
    vector_store = get_vector_store(
        force_recreate=force_recreate,
        embedding_provider=embedding_provider
    )

    # Configure retriever with improved search parameters
    retriever = vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 12,  # Retrieve more documents to ensure comprehensive coverage
            "fetch_k": 20,  # Consider more candidates for diversity
            "lambda_mult": 0.6,  # Better balance between relevance and diversity
            "filter": None
        }
    )
    return retriever


# Debug function to examine retrieved context
def debug_retrieval(retriever, question):
    docs = retriever.get_relevant_documents(question)
    print(f"\n[DEBUG] Retrieved {len(docs)} documents")
    print(f"[DEBUG] Top document similarity scores:")
    for i, doc in enumerate(docs[:5]):  # Show more top docs in debug
        print(f"[DEBUG] Doc {i + 1} ({len(doc.page_content)} chars): {doc.page_content[:200]}...")
    return docs


# Enhanced prompt with very specific calculation instructions
ENHANCED_PROMPT_TEMPLATE = """
You are an expert in Islamic Finance accounting following AAOIFI standards. Your task is to provide a detailed, step-by-step answer based ONLY on the context provided below.

CONTEXT:
{context}

QUESTION:
{question}

Follow these specific calculation instructions precisely:

1. First, identify which Islamic finance contract is being described (Murabaha, Ijarah, etc.)

2. Determine which AAOIFI Financial Accounting Standard applies (FAS 4, FAS 28, FAS 32, etc.)

3. For Ijarah MBT (FAS 32), calculate EXACTLY in this order:
   a. Prime cost of the asset (purchase price + all additional costs)
   b. Right-of-Use (ROU) asset calculation: Prime cost MINUS the purchase option price
   c. Total Ijarah payments (rental amount × lease term)
   d. Deferred Ijarah Cost: Total Ijarah payments MINUS ROU asset value
   e. Amortizable amount: ROU asset MINUS (residual value - purchase price)
   f. Annual amortization: Amortizable amount ÷ lease term

4. For Murabaha (FAS 28), calculate EXACTLY in this order:
   a. Prime cost of the asset (purchase price + all additional costs)
   b. Total selling price (including profit mark-up)
   c. Deferred profit = Total selling price - Prime cost
   d. Profit recognition schedule using either:
      - Proportionate allocation method or
      - Time-apportioned method

5. For every calculation, show the full equation with numbers before giving the result
   Example: "Prime cost = Purchase price + Import tax + Freight = 450,000 + 12,000 + 30,000 = 492,000"

6. Provide complete journal entries with:
   - Dr. (Debit accounts and amounts)
   - Cr. (Credit accounts and amounts)
   - Clear narrations explaining each entry

7. Create an amortization/profit recognition table showing the allocation over the contract term

Remember that in Ijarah MBT, the ROU asset is calculated by subtracting the PURCHASE PRICE (not the residual value) from the prime cost. The amortizable amount is then calculated by subtracting the difference between residual value and purchase price from the ROU asset.

Answer:
"""


# Create enhanced RAG chain with better debugging
def create_enhanced_rag_chain(embedding_provider="openai", model_choice="gemini"):
    retriever = setup_vector_store(embedding_provider)
    prompt = ChatPromptTemplate.from_template(ENHANCED_PROMPT_TEMPLATE)

    # Initialize the LLM based on user choice
    selected_llm = initialize_llm(model_choice)
    model_name = "OpenAI GPT-4 Turbo" if model_choice.lower() == "openai" else "Google Gemini"

    def process_with_debug(input_query):
        # Debug retrieval
        print("Retrieving relevant documents...")
        retrieved_docs = debug_retrieval(retriever, input_query)
        context_text = "\n\n".join([doc.page_content for doc in retrieved_docs])

        # Process with LLM
        print(f"Processing with {model_name}...")
        response = prompt.invoke({
            "context": context_text,
            "question": input_query
        })
        llm_response = selected_llm.invoke(response)
        return StrOutputParser().invoke(llm_response)

    # Return both the chain and the debugging function
    rag_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | selected_llm
            | StrOutputParser()
    )

    return rag_chain, process_with_debug


# Improved contract-specific question preprocessing
def enhanced_preprocess_question(question):
    """Add relevant keywords and formulas to improve retrieval"""

    # Define mapping of keywords, standards, and calculation formulas
    key_terms = {
        "ijarah": [
            "FAS 32", "Ijarah", "lease", "right of use", "ROU",
            "deferred ijarah cost", "amortizable amount", "prime cost",
            "ROU = Prime cost - Purchase price",
            "Deferred Ijarah Cost = Total rentals - ROU"
        ],
        "murabaha": [
            "FAS 28", "FAS 4", "Murabaha", "cost plus", "deferred payment",
            "deferred profit", "profit recognition", "cost recovery",
            "Deferred profit = Selling price - Cost"
        ],
        "salam": [
            "FAS 7", "Salam", "advance payment", "Salam capital",
            "parallel salam", "Salam inventory"
        ],
        "istisna": [
            "FAS 10", "Istisna'a", "manufacturing", "construction",
            "percentage of completion", "parallel istisna"
        ],
    }

    # Check if question mentions specific contracts
    matched_term = None
    for term, keywords in key_terms.items():
        if term.lower() in question.lower():
            matched_term = term
            break

    if not matched_term:
        # Try to match by keywords if no direct contract mention
        for term, keywords in key_terms.items():
            for keyword in keywords:
                if keyword.lower() in question.lower():
                    matched_term = term
                    break
            if matched_term:
                break

    # Add specific context based on contract type
    if matched_term:
        if matched_term == "ijarah":
            enriched_question = f"""
{question}

SEARCH CONTEXT: 
Islamic finance contract: Ijarah Muntahia Bittamleek (Ijarah MBT)
Relevant standard: AAOIFI FAS 32
Key calculations needed:
- Prime cost = Purchase price + Import tax + Freight
- ROU asset = Prime cost - Purchase price
- Total rentals = Annual rental × Lease term
- Deferred Ijarah Cost = Total rentals - ROU asset
- Amortizable amount = ROU asset - (Residual value - Purchase price)
- Annual amortization = Amortizable amount ÷ Lease term
"""
        elif matched_term == "murabaha":
            enriched_question = f"""
{question}

SEARCH CONTEXT:
Islamic finance contract: Murabaha
Relevant standard: AAOIFI FAS 28 (previously FAS 4)
Key calculations needed:
- Prime cost = Purchase price + Additional costs
- Deferred profit = Selling price - Prime cost
- Profit recognition methods: proportionate allocation or time-apportioned
"""
        else:
            # Generic enrichment for other contract types
            enriched_question = f"""{question}

SEARCH CONTEXT: 
Islamic finance contract: {matched_term}
Relevant standards: {', '.join(key_terms[matched_term][:2])}
"""
    else:
        # No specific contract identified
        enriched_question = question

    return enriched_question


# Main function
def main():
    print("\nEnhanced Islamic Finance Accounting Calculator (AAOIFI Standards)")
    print("=" * 80)

    # Ask user to choose LLM model
    print("\nChoose LLM model:")
    print("1. OpenAI (GPT-4 Turbo)")
    print("2. Google (Gemini-2.0-flash)")
    model_choice = input("Enter your choice (1 or 2, default is 2): ")
    llm_provider = "openai" if model_choice == "1" else "gemini"

    # Ask user to choose embedding provider
    print("\nChoose embedding provider:")
    print("1. OpenAI (text-embedding-3-large)")
    print("2. Gemini (models/gemini-embedding-exp-03-07)")
    embedding_choice = input("Enter your choice (1 or 2, default is 1): ")
    embedding_provider = "gemini" if embedding_choice == "2" else "openai"

    # Ask if vector store should be recreated
    recreate = input("\nForce recreation of vector store? (y/n, default n): ").lower() == 'y'

    # Create enhanced RAG chain with chosen settings
    rag_chain, debug_process = create_enhanced_rag_chain(embedding_provider, llm_provider)

    # Load example question from JSON file
    try:
        with open('example.json', 'r') as file:
            data = json.load(file)
            example_question = data.get('example_question', 'No example question found in JSON file.')
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading example question: {e}")
        example_question = "No example question available."

    # Run the example question with debug info
    print("\n\n" + "=" * 80)
    print("EXAMPLE QUESTION:")
    print(example_question)
    print("=" * 80 + "\n")

    print("Generating answer with debug info... (this may take a moment)")

    # Preprocess question for better retrieval
    processed_question = enhanced_preprocess_question(example_question)

    # Use debug process
    example_answer = debug_process(processed_question)

    print("\n" + "=" * 80)
    print("ANSWER:")
    print(example_answer)
    print("=" * 80 + "\n")

    # Interactive mode
    print("\nEnter your questions about Islamic banking (type 'exit' to quit):")

    while True:
        user_question = input("\nQuestion: ")
        if user_question.lower() == 'exit':
            break

        if not user_question.strip():
            continue

        # Preprocess user question
        processed_user_question = enhanced_preprocess_question(user_question)

        print("Generating answer... (this may take a moment)")
        answer = debug_process(processed_user_question)

        print("\n" + "=" * 80)
        print("ANSWER:")
        print(answer)
        print("=" * 80)


if __name__ == "__main__":
    main()
