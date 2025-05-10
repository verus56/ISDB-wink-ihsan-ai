from typing import Dict, List, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

class ResponseGenerator:
    """
    Response Generator for AAOIFI FAS Identification System

    Components:
    1. Weighted Probability Output - Format standards with confidence scores
    2. Explanation Generator - Generate multi-level explanations with citations
    """

    def __init__(self, llm=None):
        """
        Initialize the Response Generator

        Args:
            llm: Language model to use (if None, defaults to OpenAI)
        """
        self.llm = llm if llm is not None else ChatOpenAI(model="gpt-4-turbo", temperature=0.1)

    def generate_response(self, 
                         parsed_transaction: Dict[str, Any],
                         rag_results: Dict[str, Any],
                         analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive response for the transaction analysis

        Args:
            parsed_transaction: Transaction data parsed by TransactionParser
            rag_results: Results from the Enhanced RAG system
            analysis_results: Results from the Analysis Engine

        Returns:
            Dictionary with formatted response
        """
        # Extract applicable standards from analysis results
        applicable_standards = analysis_results.get("applicable_standards", [])

        # If no applicable standards found, generate a fallback response
        if not applicable_standards:
            return self._generate_fallback_response(parsed_transaction)

        # Generate the weighted probability output
        weighted_output = self._format_weighted_probabilities(applicable_standards)

        # Generate detailed explanations
        detailed_explanations = self._generate_detailed_explanations(
            parsed_transaction, 
            rag_results, 
            applicable_standards
        )

        # Generate summary explanation
        summary_explanation = self._generate_summary_explanation(
            parsed_transaction, 
            applicable_standards
        )

        # Check for contradictions
        contradictions = rag_results.get("contradictory_check", {})
        contradiction_explanation = self._format_contradictions(contradictions)

        # Combine all components into the final response
        return {
            "weighted_probabilities": weighted_output,
            "summary_explanation": summary_explanation,
            "detailed_explanations": detailed_explanations,
            "contradictions": contradiction_explanation,
            "transaction_analysis": analysis_results.get("transaction_analysis", {})
        }

    def format_response_as_text(self, response: Dict[str, Any]) -> str:
        """
        Format the response as a human-readable text

        Args:
            response: Response dictionary from generate_response

        Returns:
            Formatted text response
        """
        # Start with the summary explanation
        formatted_text = "# AAOIFI FAS STANDARD IDENTIFICATION ANALYSIS\n\n"

        # Add summary explanation
        formatted_text += "## SUMMARY\n"
        formatted_text += response.get("summary_explanation", "No summary available.") + "\n\n"

        # Add weighted probabilities table
        formatted_text += "## APPLICABLE STANDARDS WITH CONFIDENCE SCORES\n"
        formatted_text += "| FAS Number | Probability | \n"
        formatted_text += "|------------|-------------|\n"

        for standard in response.get("weighted_probabilities", []):
            formatted_text += f"| {standard['standard']} | {standard['probability_percentage']} |\n"

        formatted_text += "\n"

        # Add detailed explanations
        formatted_text += "## DETAILED ANALYSIS\n\n"

        for explanation in response.get("detailed_explanations", []):
            formatted_text += f"### {explanation['standard']}\n"
            formatted_text += explanation["explanation"] + "\n\n"

            # Add citations if available
            if "citations" in explanation and explanation["citations"]:
                formatted_text += "**Citations:**\n"
                for citation in explanation["citations"]:
                    formatted_text += f"- {citation}\n"
                formatted_text += "\n"

        # Add contradictions if any
        contradictions = response.get("contradictions", {})
        if contradictions.get("contradictions_found", False):
            formatted_text += "## POTENTIAL ALTERNATIVE TREATMENTS\n\n"
            formatted_text += contradictions.get("explanation", "No details available.") + "\n\n"

        # Add transaction analysis summary
        transaction_analysis = response.get("transaction_analysis", {})
        if transaction_analysis:
            formatted_text += "## TRANSACTION ELEMENTS IDENTIFIED\n\n"

            # Add transaction types
            transaction_types = transaction_analysis.get("transaction_types", {})
            if transaction_types:
                formatted_text += "**Transaction Types:**\n"
                for t_type, confidence in transaction_types.items():
                    formatted_text += f"- {t_type} (confidence: {confidence:.2f})\n"
                formatted_text += "\n"

            # Add Islamic terms
            islamic_terms = transaction_analysis.get("islamic_terms", [])
            if islamic_terms:
                formatted_text += "**Islamic Finance Terms:**\n"
                for term in islamic_terms:
                    formatted_text += f"- {term}\n"
                formatted_text += "\n"

            # Add journal entries
            journal_entries = transaction_analysis.get("journal_entries", [])
            if journal_entries:
                formatted_text += "**Journal Entries:**\n"
                for entry in journal_entries:
                    debit = entry.get("debit_account", "")
                    credit = entry.get("credit_account", "")
                    debit_amount = entry.get("debit_amount", "")
                    credit_amount = entry.get("credit_amount", "")

                    entry_text = f"Dr. {debit}"
                    if debit_amount:
                        entry_text += f" {debit_amount}"
                    entry_text += f" / Cr. {credit}"
                    if credit_amount:
                        entry_text += f" {credit_amount}"

                    formatted_text += f"- {entry_text}\n"
                formatted_text += "\n"

        return formatted_text

    def _format_weighted_probabilities(self, applicable_standards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format the weighted probabilities output

        Args:
            applicable_standards: List of applicable standards with probabilities

        Returns:
            Formatted list of standards with probabilities
        """
        # Create a copy to avoid modifying the original
        formatted_standards = []

        for standard in applicable_standards:
            formatted_standards.append({
                "standard": standard["standard"],
                "probability": standard["probability"],
                "probability_percentage": standard["probability_percentage"],
                "reasoning": standard.get("reasoning", "")
            })

        return formatted_standards

    def _generate_detailed_explanations(self, 
                                       parsed_transaction: Dict[str, Any],
                                       rag_results: Dict[str, Any],
                                       applicable_standards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate detailed explanations for each applicable standard

        Args:
            parsed_transaction: Transaction data parsed by TransactionParser
            rag_results: Results from the Enhanced RAG system
            applicable_standards: List of applicable standards with probabilities

        Returns:
            List of dictionaries with detailed explanations
        """
        detailed_explanations = []

        # Extract requirements from RAG results
        requirements = rag_results.get("detailed_context", {}).get("requirements", {})

        # Create a prompt template for detailed explanations
        prompt_template = ChatPromptTemplate.from_template(
            """
            Generate a detailed explanation for why the following AAOIFI Financial Accounting Standard (FAS)
            is applicable to this transaction. Include specific citations from the standard where possible.

            Transaction:
            {transaction}

            Standard: {standard}

            Standard Requirements:
            {requirements}

            Initial Reasoning:
            {reasoning}

            Please provide a comprehensive explanation that:
            1. Explains the core purpose and scope of this standard
            2. Identifies specific elements in the transaction that trigger this standard
            3. Explains how the accounting treatment should be applied
            4. Cites specific clauses or paragraphs from the standard where relevant

            Format your response as a detailed explanation suitable for financial professionals.
            Do not use bullet points or numbered lists - write in cohesive paragraphs.

            Explanation:
            """
        )

        # Create the chain
        chain = LLMChain(llm=self.llm, prompt=prompt_template)

        # Generate detailed explanation for each standard
        for standard_info in applicable_standards:
            standard = standard_info["standard"]
            reasoning = standard_info.get("reasoning", "")

            # Get requirements for this standard
            standard_requirements = requirements.get(standard, [])
            requirements_text = "\n".join([f"- {req}" for req in standard_requirements])
            if not requirements_text:
                requirements_text = "No specific requirements found in the retrieved documents."

            # Run the chain
            explanation = chain.run(
                transaction=parsed_transaction.get("raw_text", ""),
                standard=standard,
                requirements=requirements_text,
                reasoning=reasoning
            )

            # Extract citations from the explanation
            citations = self._extract_citations(explanation)

            # Add to detailed explanations
            detailed_explanations.append({
                "standard": standard,
                "explanation": explanation.strip(),
                "citations": citations
            })

        return detailed_explanations

    def _generate_summary_explanation(self, 
                                     parsed_transaction: Dict[str, Any],
                                     applicable_standards: List[Dict[str, Any]]) -> str:
        """
        Generate a summary explanation for the transaction analysis

        Args:
            parsed_transaction: Transaction data parsed by TransactionParser
            applicable_standards: List of applicable standards with probabilities

        Returns:
            Summary explanation text
        """
        # If no applicable standards, return empty string
        if not applicable_standards:
            return ""

        # Get the top standard
        top_standard = applicable_standards[0]

        # Create a prompt template for summary explanation
        prompt_template = ChatPromptTemplate.from_template(
            """
            Generate a concise summary explanation for the analysis of this Islamic finance transaction.

            Transaction:
            {transaction}

            Primary Applicable Standard: {primary_standard} ({primary_probability})

            Other Applicable Standards:
            {other_standards}

            Please provide a brief summary (3-5 sentences) that:
            1. Identifies the main type of transaction
            2. Explains why the primary standard is most applicable
            3. Mentions any other relevant standards if applicable

            Write in a clear, professional tone suitable for financial reporting.

            Summary:
            """
        )

        # Format other standards
        other_standards_text = ""
        for standard in applicable_standards[1:3]:  # Include only the next 2 standards
            other_standards_text += f"- {standard['standard']} ({standard['probability_percentage']})\n"

        if not other_standards_text:
            other_standards_text = "None"

        # Create the chain
        chain = LLMChain(llm=self.llm, prompt=prompt_template)

        # Run the chain
        summary = chain.run(
            transaction=parsed_transaction.get("raw_text", ""),
            primary_standard=top_standard["standard"],
            primary_probability=top_standard["probability_percentage"],
            other_standards=other_standards_text
        )

        return summary.strip()

    def _format_contradictions(self, contradictions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format contradictions information

        Args:
            contradictions: Contradictions data from RAG results

        Returns:
            Formatted contradictions information
        """
        # If no contradictions found, return empty result
        if not contradictions or not contradictions.get("contradictions_found", False):
            return {
                "contradictions_found": False,
                "explanation": "No alternative treatments or contradictions identified."
            }

        # Create a prompt template for formatting contradictions
        prompt_template = ChatPromptTemplate.from_template(
            """
            Explain the following alternative treatments or contradictions in AAOIFI Financial Accounting Standards
            that might apply to this transaction.

            Alternative Treatments:
            {alternative_treatments}

            Please provide a clear explanation of:
            1. What aspects of the transaction could be treated differently
            2. Which standards offer alternative approaches
            3. How these alternatives might impact the accounting treatment

            Format your response as a concise explanation suitable for financial professionals.

            Explanation:
            """
        )

        # Format alternative treatments
        alternative_treatments = contradictions.get("alternative_treatments", [])
        alternative_treatments_text = ""

        for treatment in alternative_treatments:
            standard = treatment.get("standard", "")
            treatment_desc = treatment.get("treatment", "")
            conflicts = treatment.get("conflicts_with", [])

            alternative_treatments_text += f"- {standard}: {treatment_desc}\n"
            if conflicts:
                alternative_treatments_text += f"  Conflicts with: {', '.join(conflicts)}\n"

        if not alternative_treatments_text:
            alternative_treatments_text = "No specific alternative treatments identified."

        # Create the chain
        chain = LLMChain(llm=self.llm, prompt=prompt_template)

        # Run the chain
        explanation = chain.run(
            alternative_treatments=alternative_treatments_text
        )

        return {
            "contradictions_found": True,
            "explanation": explanation.strip(),
            "alternative_treatments": alternative_treatments
        }

    def _generate_fallback_response(self, parsed_transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a fallback response when no applicable standards are found

        Args:
            parsed_transaction: Transaction data parsed by TransactionParser

        Returns:
            Fallback response dictionary
        """
        # Create a prompt template for fallback response
        prompt_template = ChatPromptTemplate.from_template(
            """
            Generate a response for a transaction where no clear AAOIFI Financial Accounting Standards (FAS) 
            could be identified with high confidence.

            Transaction:
            {transaction}

            Please provide:
            1. An explanation of why it might be difficult to identify applicable standards
            2. Suggestions for additional information that might help in the analysis
            3. Potential standards that might be relevant with more context

            Format your response as a helpful explanation for financial professionals.

            Response:
            """
        )

        # Create the chain
        chain = LLMChain(llm=self.llm, prompt=prompt_template)

        # Run the chain
        fallback_explanation = chain.run(
            transaction=parsed_transaction.get("raw_text", "")
        )

        return {
            "weighted_probabilities": [],
            "summary_explanation": "No applicable standards could be identified with high confidence.",
            "detailed_explanations": [],
            "contradictions": {
                "contradictions_found": False,
                "explanation": "No alternative treatments identified."
            },
            "fallback_explanation": fallback_explanation.strip(),
            "transaction_analysis": {
                "transaction_types": parsed_transaction.get("transaction_types", {}),
                "islamic_terms": parsed_transaction.get("islamic_terms", []),
                "accounting_terms": parsed_transaction.get("accounting_terms", []),
                "journal_entries": parsed_transaction.get("journal_entries", [])
            }
        }

    def _extract_citations(self, explanation: str) -> List[str]:
        """
        Extract citations from explanation text

        Args:
            explanation: Explanation text

        Returns:
            List of citation strings
        """
        import re

        # Look for patterns like "paragraph X", "section Y", "clause Z"
        citation_patterns = [
            r'paragraph\s+\d+(?:\.\d+)*',
            r'section\s+\d+(?:\.\d+)*',
            r'clause\s+\d+(?:\.\d+)*',
            r'chapter\s+\d+(?:\.\d+)*',
            r'FAS\s+\d+\.\d+',
            r'FAS\s+\d+\s+paragraph\s+\d+'
        ]

        citations = []

        for pattern in citation_patterns:
            matches = re.findall(pattern, explanation, re.IGNORECASE)
            citations.extend(matches)

        # Remove duplicates and sort
        unique_citations = list(set(citations))
        unique_citations.sort()

        return unique_citations
