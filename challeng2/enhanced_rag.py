from typing import List, Dict, Any, Tuple
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
import re
from vector_store import get_embeddings


class EnhancedRAG:
    """
    Enhanced RAG System for AAOIFI FAS Identification

    Implements a multi-stage retrieval pipeline:
    1. Domain Filtering - Identify relevant FAS domains
    2. Detailed Context Matching - Find specific requirements
    3. Contradictory Standards Check - Identify potential conflicts
    """

    def __init__(self, vector_store: Chroma, llm=None):
        """
        Initialize the Enhanced RAG system

        Args:
            vector_store: Chroma vector store containing FAS documents
            llm: Language model to use (if None, defaults to OpenAI)
        """
        self.vector_store = vector_store

        # Determine embedding provider based on LLM type
        embedding_provider = "openai"
        if isinstance(llm, ChatGoogleGenerativeAI):
            embedding_provider = "gemini"

        # Get appropriate embeddings based on LLM type
        self.embeddings = get_embeddings(embedding_provider)
        self.llm = llm if llm is not None else ChatOpenAI(model="gpt-4-turbo", temperature=0.1)

        # FAS taxonomy for classification
        self.fas_taxonomy = {
            "murabaha": ["FAS 4", "FAS 28"],
            "salam": ["FAS 7"],
            "istisna": ["FAS 10"],
            "ijarah": ["FAS 32"],
            "general": ["FAS 4", "FAS 7", "FAS 10", "FAS 28", "FAS 32"],
            "construction": ["FAS 10"],
            "reversal": ["FAS 10"],
            "contract_modification": ["FAS 10"],
            "equity_acquisition": ["FAS 4", "FAS 20", "FAS 32"],
            "banking_buyout": ["FAS 4", "FAS 20", "FAS 32"]
        }

        # Transaction type to FAS mapping - improved distinction between different types of buyouts
        self.transaction_type_mapping = {
            # Construction-related buyouts go to FAS 10
            "construction_buyout": ["FAS 10"],
            "construction": ["FAS 10"],
            "reversal": ["FAS 10"],
            "manufacturing": ["FAS 10"],
            "contract": ["FAS 10"],

            # Financial/equity buyouts go to FAS 4, FAS 20, FAS 32
            "equity_buyout": ["FAS 4", "FAS 20", "FAS 32"],
            "financial_buyout": ["FAS 4", "FAS 20", "FAS 32"],
            "banking_buyout": ["FAS 4", "FAS 20"],
            "buyout": ["FAS 4", "FAS 20", "FAS 32"],  # Generic buyout defaults to financial standards

            # Other transaction types
            "lease": ["FAS 32"],
            "sale": ["FAS 4", "FAS 28"],
            "deferred_payment": ["FAS 4", "FAS 28"],
            "advance_payment": ["FAS 7"]
        }

    def process_transaction(self, parsed_transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a parsed transaction through the multi-stage retrieval pipeline

        Args:
            parsed_transaction: Transaction data parsed by TransactionParser

        Returns:
            Dictionary containing retrieval results from all stages
        """
        # Stage 1: Domain Filtering
        domain_results = self._stage1_domain_filtering(parsed_transaction)

        # Stage 2: Detailed Context Matching
        context_results = self._stage2_detailed_context_matching(parsed_transaction, domain_results)

        # Stage 3: Contradictory Standards Check
        contradictory_results = self._stage3_contradictory_check(parsed_transaction, context_results)

        # Combine results from all stages
        return {
            "domain_filtering": domain_results,
            "detailed_context": context_results,
            "contradictory_check": contradictory_results
        }

    def _stage1_domain_filtering(self, parsed_transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Stage 1: Domain Filtering

        Query: Transaction type + accounting domain keywords
        Result: Subset of potentially relevant FAS documents

        Args:
            parsed_transaction: Transaction data parsed by TransactionParser

        Returns:
            Dictionary with relevant FAS domains and documents
        """
        # Extract transaction types and Islamic terms
        transaction_types = parsed_transaction.get("transaction_types", {})
        islamic_terms = parsed_transaction.get("islamic_terms", [])

        # Check for construction and reversal keywords
        transaction_text = parsed_transaction.get("raw_text", "").lower()
        journal_entries = parsed_transaction.get("journal_entries", [])

        # Detect transaction context indicators
        has_construction = any(term in transaction_text for term in
                               ["construction", "project", "development", "contract", "istisna"])
        has_reversal = any(term in transaction_text for term in
                           ["cancel", "revert", "reverse", "adjustment", "revised"])
        has_work_in_progress = any("work-in-progress" in entry.get("debit_account", "").lower() or
                                   "work-in-progress" in entry.get("credit_account", "").lower()
                                   for entry in journal_entries)

        # New: Detect banking/financial/equity buyout indicators
        has_bank = any(term in transaction_text for term in
                       ["bank", "financial", "finance", "equity", "stake", "ownership"])
        has_equity_transaction = any(term in transaction_text for term in
                                      ["equity", "stake", "share", "ownership", "acquisition"])

        # Check if there are equity-related journal entries (indicators of FAS 4/20)
        has_equity_journal = False
        for entry in journal_entries:
            debit_account = entry.get("debit_account", "").lower()
            credit_account = entry.get("credit_account", "").lower()
            if "equity" in debit_account or "equity" in credit_account:
                has_equity_journal = True
                break

        # Refine transaction types based on deeper context analysis
        if "buyout" in transaction_types:
            # Classify the type of buyout more specifically
            if has_construction or has_work_in_progress:
                # Construction-related buyout
                transaction_types["construction_buyout"] = transaction_types["buyout"] + 0.1
            elif has_bank or has_equity_transaction or has_equity_journal:
                # Financial/equity buyout - should prioritize FAS 4, FAS 20, FAS 32
                transaction_types["equity_buyout"] = transaction_types["buyout"] + 0.2
                transaction_types["financial_buyout"] = transaction_types["buyout"] + 0.15

                # If specifically a bank is involved, even higher confidence
                if has_bank and has_equity_transaction:
                    transaction_types["banking_buyout"] = transaction_types["buyout"] + 0.3

        # Add construction and reversal to transaction types if detected
        if has_construction and "construction" not in transaction_types:
            transaction_types["construction"] = 0.8

        if has_reversal and "reversal" not in transaction_types:
            transaction_types["reversal"] = 0.7

        if "contract" in transaction_text and "contract" not in transaction_types:
            transaction_types["contract"] = 0.7

        # Build domain query
        query_parts = []

        # Add transaction types to query
        if transaction_types:
            top_types = sorted(transaction_types.items(), key=lambda x: x[1], reverse=True)[:3]  # Top 3
            query_parts.extend([t_type for t_type, _ in top_types])

        # Add Islamic terms to query
        if islamic_terms:
            query_parts.extend(islamic_terms)

        # Add specific contextual terms to enhance query
        if has_construction:
            query_parts.extend(["construction contract", "istisna", "FAS 10"])

        if has_reversal:
            query_parts.extend(["contract reversal", "contract modification", "FAS 10"])

        if has_work_in_progress:
            query_parts.extend(["work-in-progress", "construction accounting", "FAS 10"])

        # NEW: Add financial/equity buyout terms
        if has_bank and "buyout" in transaction_types:
            query_parts.extend(["murabaha", "financing", "bank buyout", "FAS 4", "FAS 20"])

        if has_equity_transaction:
            query_parts.extend(["equity transaction", "ownership transfer", "FAS 4", "FAS 20"])

        if has_equity_journal:
            query_parts.extend(["equity accounting", "ownership change", "FAS 4", "FAS 20"])

        # Add accounting terms if available
        accounting_terms = parsed_transaction.get("accounting_terms", [])
        if accounting_terms:
            query_parts.extend(accounting_terms[:3])  # Add top 3 accounting terms

        # Create the domain query
        domain_query = " ".join(query_parts)
        if not domain_query:
            # Fallback to raw text if no structured elements found
            domain_query = parsed_transaction.get("raw_text", "")[:200]  # Use first 200 chars

        # For transactions involving construction or reversal, explicitly check for FAS 10
        if has_construction or has_reversal or has_work_in_progress:
            domain_query += " FAS 10 Istisna contract construction"

        # For transactions involving banking/equity, explicitly check for FAS 4, FAS 20
        if (has_bank or has_equity_transaction or has_equity_journal) and "buyout" in transaction_types:
            domain_query += " FAS 4 FAS 20 FAS 32 ownership bank equity financing"

        # Retrieve relevant documents
        retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 12}  # Increased from 10 to 12
        )
        domain_docs = retriever.get_relevant_documents(domain_query)

        # Identify potential FAS standards based on retrieved documents
        potential_standards = self._extract_fas_from_docs(domain_docs)

        # Also consider transaction type mapping
        mapped_standards = set()
        for t_type in transaction_types:
            if t_type in self.transaction_type_mapping:
                mapped_standards.update(self.transaction_type_mapping[t_type])

        # For construction/reversal, ensure FAS 10 is included
        if has_construction or has_reversal or has_work_in_progress:
            mapped_standards.add("FAS 10")

        # For banking/equity buyouts, ensure FAS 4, FAS 20 are included
        if (has_bank or has_equity_transaction or has_equity_journal) and "buyout" in transaction_types:
            mapped_standards.add("FAS 4")
            mapped_standards.add("FAS 20")
            mapped_standards.add("FAS 32")

        # Combine both sources
        all_potential_standards = list(set(potential_standards) | mapped_standards)

        return {
            "query": domain_query,
            "potential_standards": all_potential_standards,
            "documents": domain_docs
        }

    def _stage2_detailed_context_matching(self,
                                          parsed_transaction: Dict[str, Any],
                                          domain_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Stage 2: Detailed Context Matching

        Query: Accounting treatments + journal entry patterns + specific transaction details
        Result: Highly relevant FAS passages with specific requirements

        Args:
            parsed_transaction: Transaction data parsed by TransactionParser
            domain_results: Results from Stage 1

        Returns:
            Dictionary with detailed context matches
        """
        # Extract journal entries and context
        journal_entries = parsed_transaction.get("journal_entries", [])
        context_info = parsed_transaction.get("context", {})

        # Build detailed query
        query_parts = []

        # Add journal entry information if available
        if journal_entries:
            for entry in journal_entries[:2]:  # Use first 2 entries
                debit = entry.get("debit_account", "")
                credit = entry.get("credit_account", "")
                if debit and credit:
                    query_parts.append(f"journal entry: debit {debit} credit {credit}")

        # Add context information
        if context_info:
            industry = context_info.get("industry")
            if industry:
                query_parts.append(f"industry: {industry}")

            purpose = context_info.get("purpose")
            if purpose:
                query_parts.append(f"purpose: {purpose}")

        # Add transaction types with weights
        transaction_types = parsed_transaction.get("transaction_types", {})
        if transaction_types:
            for t_type, weight in transaction_types.items():
                query_parts.append(f"transaction type: {t_type} (weight: {weight:.2f})")

        # Create the detailed query
        detailed_query = " ".join(query_parts)
        if not detailed_query:
            # Fallback to domain query if no structured elements found
            detailed_query = domain_results.get("query", "")

        # Filter retrieval to focus on potential standards from Stage 1
        potential_standards = domain_results.get("potential_standards", [])

        # Create a metadata filter if we have potential standards
        metadata_filter = None
        if potential_standards:
            # Use $in operator instead of $regex (which is not supported by Chroma)
            metadata_filter = {"content": {"$in": potential_standards}}

        # Retrieve detailed context documents
        retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={
                "k": 8,
                "filter": metadata_filter
            }
        )
        detailed_docs = retriever.get_relevant_documents(detailed_query)

        # Extract specific requirements from documents
        requirements = self._extract_requirements(detailed_docs)

        return {
            "query": detailed_query,
            "documents": detailed_docs,
            "requirements": requirements
        }

    def _stage3_contradictory_check(self,
                                    parsed_transaction: Dict[str, Any],
                                    context_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Stage 3: Contradictory Standards Check

        Query: Specific accounting challenge in context
        Result: Passages that might present alternative treatments

        Args:
            parsed_transaction: Transaction data parsed by TransactionParser
            context_results: Results from Stage 2

        Returns:
            Dictionary with potential contradictions or alternative treatments
        """
        # Extract requirements from Stage 2
        requirements = context_results.get("requirements", {})

        # If no requirements found, skip this stage
        if not requirements:
            return {
                "contradictions_found": False,
                "alternative_treatments": []
            }

        # Create a query to find potential contradictions
        contradiction_query = self._generate_contradiction_query(parsed_transaction, requirements)

        # Retrieve potential contradictory documents
        retriever = self.vector_store.as_retriever(
            search_type="mmr",  # Use Maximum Marginal Relevance for diversity
            search_kwargs={"k": 5, "fetch_k": 15}
        )
        contradictory_docs = retriever.get_relevant_documents(contradiction_query)

        # Use LLM to analyze potential contradictions
        contradictions = self._analyze_contradictions(parsed_transaction, requirements, contradictory_docs)

        return contradictions

    def _extract_fas_from_docs(self, docs: List[Document]) -> List[str]:
        """Extract FAS standard references from documents"""
        fas_pattern = re.compile(r'FAS\s+\d+', re.IGNORECASE)
        standards = set()

        for doc in docs:
            matches = fas_pattern.findall(doc.page_content)
            standards.update([match.upper() for match in matches])

        return list(standards)

    def _extract_requirements(self, docs: List[Document]) -> Dict[str, List[str]]:
        """Extract specific requirements from documents by FAS standard"""
        requirements = {}
        fas_pattern = re.compile(r'(FAS\s+\d+)', re.IGNORECASE)

        for doc in docs:
            content = doc.page_content

            # Find all FAS references in this document
            matches = fas_pattern.findall(content)

            for match in matches:
                fas = match.upper()
                if fas not in requirements:
                    requirements[fas] = []

                # Extract sentences containing requirements
                sentences = re.split(r'(?<=[.!?])\s+', content)
                for sentence in sentences:
                    if fas in sentence.upper() and any(req_word in sentence.lower() for req_word in
                                                       ["must", "should", "require", "necessary", "need", "shall"]):
                        requirements[fas].append(sentence.strip())

        return requirements

    def _generate_contradiction_query(self,
                                      parsed_transaction: Dict[str, Any],
                                      requirements: Dict[str, List[str]]) -> str:
        """Generate a query to find potential contradictions"""
        # Create a prompt for the LLM to generate a contradiction query
        prompt_template = ChatPromptTemplate.from_template(
            """
            I need to find potential contradictions or alternative treatments in Islamic finance accounting standards.

            Transaction details:
            {transaction_summary}

            Current identified requirements:
            {requirements_summary}

            Please generate a search query that would help find potential contradictions or alternative treatments
            for this transaction. Focus on aspects where different standards might have different approaches.

            Query:
            """
        )

        # Create a summary of the transaction
        transaction_summary = parsed_transaction.get("raw_text", "")[:300]  # First 300 chars

        # Create a summary of requirements
        requirements_summary = ""
        for fas, reqs in requirements.items():
            requirements_summary += f"{fas}:\n"
            for req in reqs[:3]:  # Limit to first 3 requirements per standard
                requirements_summary += f"- {req}\n"

        # Create the chain
        chain = LLMChain(llm=self.llm, prompt=prompt_template)

        # Run the chain
        query = chain.run(
            transaction_summary=transaction_summary,
            requirements_summary=requirements_summary
        )

        return query.strip()

    def _analyze_contradictions(self,
                                parsed_transaction: Dict[str, Any],
                                requirements: Dict[str, List[str]],
                                contradictory_docs: List[Document]) -> Dict[str, Any]:
        """Analyze potential contradictions using LLM"""
        # If no contradictory docs found, return empty result
        if not contradictory_docs:
            return {
                "contradictions_found": False,
                "alternative_treatments": []
            }

        # Create a prompt for the LLM to analyze contradictions
        prompt_template = ChatPromptTemplate.from_template(
            """
            Analyze the following transaction and identify if there are any contradictions or alternative treatments
            in the AAOIFI Financial Accounting Standards (FAS) that could apply.

            Transaction:
            {transaction}

            Current identified requirements:
            {requirements_summary}

            Potential alternative passages:
            {alternative_passages}

            Please identify:
            1. Are there any contradictions between different standards for this transaction? (Yes/No)
            2. If yes, what are the specific alternative treatments?
            3. Which standards contain these alternative treatments?

            Format your response as a JSON object with the following structure:
            {{
                "contradictions_found": true/false,
                "alternative_treatments": [
                    {{
                        "standard": "FAS X",
                        "treatment": "Description of alternative treatment",
                        "conflicts_with": ["FAS Y", "FAS Z"]
                    }}
                ]
            }}

            Response:
            """
        )

        # Create a summary of requirements
        requirements_summary = ""
        for fas, reqs in requirements.items():
            requirements_summary += f"{fas}:\n"
            for req in reqs[:3]:  # Limit to first 3 requirements per standard
                requirements_summary += f"- {req}\n"

        # Combine contradictory docs
        alternative_passages = "\n\n".join([doc.page_content for doc in contradictory_docs])

        # Create the chain
        chain = LLMChain(llm=self.llm, prompt=prompt_template)

        # Run the chain
        response = chain.run(
            transaction=parsed_transaction.get("raw_text", ""),
            requirements_summary=requirements_summary,
            alternative_passages=alternative_passages
        )

        # Parse the JSON response
        try:
            import json
            result = json.loads(response)
            return result
        except:
            # Fallback if JSON parsing fails
            return {
                "contradictions_found": False,
                "alternative_treatments": [],
                "error": "Failed to parse LLM response"
            }
