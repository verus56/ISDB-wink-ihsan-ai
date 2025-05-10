from typing import Dict, List, Any, Tuple
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
import json


class AnalysisEngine:
    """
    Multi-perspective Analysis Engine for AAOIFI FAS Identification

    Components:
    1. Applicable Standards Identification - Match transaction characteristics with FAS requirements
    2. Probabilistic Ranking Framework - Score and rank standards based on weighted features
    3. Reasoning Framework - Generate structured reasoning for standard justification
    """

    def __init__(self, llm=None):
        """
        Initialize the Analysis Engine

        Args:
            llm: Language model to use (if None, defaults to OpenAI)
        """
        self.llm = llm if llm is not None else ChatOpenAI(model="gpt-4-turbo", temperature=0.1)

        # Define feature weights for the probabilistic ranking
        self.feature_weights = {
            "transaction_type_match": 0.35,
            "journal_entry_match": 0.25,
            "accounting_treatment_similarity": 0.25,
            "industry_context_match": 0.15
        }

        # FAS-specific logic rules
        self.fas_rules = {
            "FAS 4": {
                "required_terms": ["murabaha", "purchase order", "cost plus", "bank", "finance", "ownership", "equity", "stake"],
                "excluded_terms": ["ijarah", "salam"],
                "journal_patterns": ["murabaha asset", "murabaha receivable", "equity", "cash"]
            },
            "FAS 7": {
                "required_terms": ["salam", "advance payment", "future delivery"],
                "excluded_terms": ["ijarah", "murabaha"],
                "journal_patterns": ["salam asset", "salam receivable"]
            },
            "FAS 10": {
                "required_terms": ["istisna", "manufacturing", "construction", "project", "development", "contract", "work-in-progress", "reversal"],
                "excluded_terms": [],
                "journal_patterns": ["istisna asset", "istisna receivable", "istisna payable", "work-in-progress", "accounts payable", "contract", "progress"]
            },
            "FAS 20": {
                "required_terms": ["investment", "equity", "ownership", "stake", "buyout", "acquisition", "derecognition"],
                "excluded_terms": [],
                "journal_patterns": ["investment", "equity", "stake", "cash", "ownership"]
            },
            "FAS 28": {
                "required_terms": ["deferred payment", "installment", "credit sale", "murabaha"],
                "excluded_terms": ["istisna", "ijarah", "salam"],
                "journal_patterns": ["deferred payment", "installment receivable"]
            },
            "FAS 32": {
                "required_terms": ["ijarah", "lease", "rental", "usufruct"],
                "excluded_terms": ["istisna", "murabaha", "salam"],
                "journal_patterns": ["ijarah asset", "ijarah receivable", "right of use"]
            }
        }

        # Excluded standards for certain transaction types
        self.excluded_standards = {
            "construction": ["FAS 8", "FAS 19", "FAS 23"],
            "reversal": ["FAS 8", "FAS 19", "FAS 23"],
            "contract_modification": ["FAS 8", "FAS 19", "FAS 23"]
        }

        # Priority standards for specific transaction types
        self.priority_standards = {
            "equity_buyout": ["FAS 4", "FAS 20", "FAS 32"],
            "banking_buyout": ["FAS 4", "FAS 20", "FAS 32"],
            "financial_buyout": ["FAS 4", "FAS 20", "FAS 32"]
        }

    def analyze_transaction(self,
                            parsed_transaction: Dict[str, Any],
                            rag_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a transaction using multi-perspective approach

        Args:
            parsed_transaction: Transaction data parsed by TransactionParser
            rag_results: Results from the Enhanced RAG system

        Returns:
            Dictionary with analysis results including applicable standards with probabilities
        """
        # Step 1: Identify applicable standards
        applicable_standards = self._identify_applicable_standards(parsed_transaction, rag_results)

        # Step 2: Apply probabilistic ranking
        ranked_standards = self._rank_standards(parsed_transaction, rag_results, applicable_standards)

        # Step 3: Generate reasoning
        reasoned_standards = self._generate_reasoning(parsed_transaction, rag_results, ranked_standards)

        # Step 4: Handle edge cases and scope limitations
        final_standards = self._apply_edge_case_rules(parsed_transaction, reasoned_standards)

        return {
            "applicable_standards": final_standards,
            "transaction_analysis": self._summarize_transaction_analysis(parsed_transaction)
        }

    def _identify_applicable_standards(self,
                                       parsed_transaction: Dict[str, Any],
                                       rag_results: Dict[str, Any]) -> List[str]:
        """
        Identify applicable standards based on transaction characteristics and RAG results

        Returns:
            List of potentially applicable FAS standards
        """
        # Get potential standards from RAG results
        domain_standards = rag_results.get("domain_filtering", {}).get("potential_standards", [])

        # Get standards with specific requirements from detailed context
        detailed_standards = list(rag_results.get("detailed_context", {}).get("requirements", {}).keys())

        # Combine both sources
        all_standards = set(domain_standards + detailed_standards)

        # Apply FAS-specific logic rules to filter standards
        filtered_standards = []

        # Extract transaction data
        transaction_text = parsed_transaction.get("raw_text", "").lower()
        islamic_terms = parsed_transaction.get("islamic_terms", [])
        transaction_types = parsed_transaction.get("transaction_types", {})
        journal_entries = parsed_transaction.get("journal_entries", [])

        # Explicitly check for construction and reversal related keywords
        has_construction = "construction" in transaction_types or any(term in transaction_text for term
                                                                      in ["construction", "project", "development",
                                                                          "contract"])
        has_reversal = "reversal" in transaction_types or any(term in transaction_text for term
                                                              in
                                                              ["cancel", "revert", "reverse", "adjustment", "revised"])
        has_work_in_progress = any("work-in-progress" in entry.get("debit_account", "").lower() or
                                   "work-in-progress" in entry.get("credit_account", "").lower()
                                   for entry in journal_entries)

        # If construction or reversal is detected, prioritize FAS 10
        if (has_construction or has_reversal or has_work_in_progress) and "FAS 10" not in filtered_standards:
            filtered_standards.append("FAS 10")

        # Detect banking/equity buyout indicators
        has_bank = any(term in transaction_text for term in
                      ["bank", "financial", "finance", "banking"])
        has_equity_transaction = any(term in transaction_text for term in
                                   ["equity", "stake", "share", "ownership", "acquisition"])

        # Check if there are equity-related journal entries
        has_equity_journal = False
        for entry in journal_entries:
            debit_account = entry.get("debit_account", "").lower()
            credit_account = entry.get("credit_account", "").lower()
            if "equity" in debit_account or "equity" in credit_account:
                has_equity_journal = True
                break

        # Special case: banking/financial buyout with equity transactions
        if "buyout" in transaction_types and (has_bank or has_equity_transaction or has_equity_journal):
            # For banking/equity buyouts, prioritize FAS 4, FAS 20, FAS 32
            for standard in ["FAS 4", "FAS 20", "FAS 32"]:
                if standard not in filtered_standards:
                    filtered_standards.append(standard)

        # If equity is being transferred with cash, strongly prioritize FAS 4/FAS 20
        if has_equity_journal and any("cash" in entry.get("credit_account", "").lower() for entry in journal_entries):
            for standard in ["FAS 4", "FAS 20"]:
                if standard not in filtered_standards:
                    filtered_standards.append(standard)

        # Check each standard against rules
        for standard in all_standards:
            if standard in self.fas_rules:
                rules = self.fas_rules[standard]

                # Check required terms
                required_terms_present = any(term in transaction_text for term in rules["required_terms"])

                # Check excluded terms
                excluded_terms_present = any(term in transaction_text for term in rules["excluded_terms"])

                # Check journal patterns
                journal_patterns_match = False
                for entry in journal_entries:
                    debit_account = entry.get("debit_account", "").lower()
                    credit_account = entry.get("credit_account", "").lower()
                    for pattern in rules["journal_patterns"]:
                        if pattern in debit_account or pattern in credit_account:
                            journal_patterns_match = True
                            break

                # Apply rule logic
                if required_terms_present and not excluded_terms_present:
                    if standard not in filtered_standards:
                        filtered_standards.append(standard)
                elif journal_patterns_match:
                    if standard not in filtered_standards:
                        filtered_standards.append(standard)
            else:
                # If no rules defined, include the standard
                if standard not in filtered_standards:
                    filtered_standards.append(standard)

        # Exclude certain standards based on transaction types
        for t_type, excluded in self.excluded_standards.items():
            if t_type in transaction_types or t_type in transaction_text:
                filtered_standards = [std for std in filtered_standards if std not in excluded]

        # If no standards found but we have construction/reversal indicators, force include FAS 10
        if not filtered_standards and (
                has_construction or has_reversal or has_work_in_progress or "istisna" in transaction_text):
            filtered_standards.append("FAS 10")

        return filtered_standards

    def _rank_standards(self,
                        parsed_transaction: Dict[str, Any],
                        rag_results: Dict[str, Any],
                        applicable_standards: List[str]) -> List[Dict[str, Any]]:
        """
        Rank applicable standards using the probabilistic ranking framework

        Returns:
            List of dictionaries with standard and probability score
        """
        # Initialize scores
        scores = {standard: 0.0 for standard in applicable_standards}

        # If no applicable standards, return empty list
        if not scores:
            return []

        # Extract transaction data for scoring
        transaction_types = parsed_transaction.get("transaction_types", {})
        journal_entries = parsed_transaction.get("journal_entries", [])
        accounting_terms = parsed_transaction.get("accounting_terms", [])
        context_info = parsed_transaction.get("context", {})

        # Detect banking/equity buyout indicators
        transaction_text = parsed_transaction.get("raw_text", "").lower()
        has_bank = any(term in transaction_text for term in
                      ["bank", "financial", "finance", "banking"])
        has_equity_transaction = any(term in transaction_text for term in
                                   ["equity", "stake", "share", "ownership", "acquisition"])

        # Check if there are equity-related journal entries
        has_equity_journal = False
        for entry in journal_entries:
            debit_account = entry.get("debit_account", "").lower()
            credit_account = entry.get("credit_account", "").lower()
            if "equity" in debit_account or "equity" in credit_account:
                has_equity_journal = True
                break

        # Boost scores for financial/banking standards in equity/bank buyouts
        if "buyout" in transaction_types and (has_bank or has_equity_transaction or has_equity_journal):
            priority_list = ["FAS 4", "FAS 20", "FAS 32"]

            for i, standard in enumerate(priority_list):
                if standard in scores:
                    # Give highest boost to FAS 4, then FAS 20, then FAS 32
                    boost = 0.5 - (i * 0.1)
                    scores[standard] += boost

        # Score each standard
        for standard in scores:
            # 1. Transaction type match (weight: 0.35)
            transaction_type_score = 0.0
            if standard in self.fas_rules:
                rules = self.fas_rules[standard]
                for t_type, confidence in transaction_types.items():
                    if any(term in t_type for term in rules["required_terms"]):
                        transaction_type_score += confidence
            scores[standard] += transaction_type_score * self.feature_weights["transaction_type_match"]

            # 2. Journal entry pattern match (weight: 0.25)
            journal_entry_score = 0.0
            if standard in self.fas_rules:
                rules = self.fas_rules[standard]
                for entry in journal_entries:
                    debit_account = entry.get("debit_account", "").lower()
                    credit_account = entry.get("credit_account", "").lower()
                    for pattern in rules["journal_patterns"]:
                        if pattern in debit_account or pattern in credit_account:
                            journal_entry_score += 0.5
            scores[standard] += journal_entry_score * self.feature_weights["journal_entry_match"]

            # 3. Accounting treatment semantic similarity (weight: 0.25)
            accounting_treatment_score = 0.0
            # Use requirements from RAG results to assess semantic similarity
            requirements = rag_results.get("detailed_context", {}).get("requirements", {}).get(standard, [])
            if requirements:
                accounting_treatment_score = min(len(requirements) * 0.2, 1.0)  # Cap at 1.0
            scores[standard] += accounting_treatment_score * self.feature_weights["accounting_treatment_similarity"]

            # 4. Industry/context match (weight: 0.15)
            industry_context_score = 0.0
            industry = context_info.get("industry")
            if industry:
                # Simple industry matching logic - can be enhanced
                if industry == "banking" and standard in ["FAS 4", "FAS 28"]:
                    industry_context_score += 0.5
                elif industry == "real_estate" and standard in ["FAS 10", "FAS 32"]:
                    industry_context_score += 0.5
                elif industry == "manufacturing" and standard == "FAS 10":
                    industry_context_score += 0.7
                elif industry == "agriculture" and standard == "FAS 7":
                    industry_context_score += 0.7
            scores[standard] += industry_context_score * self.feature_weights["industry_context_match"]

        # Normalize scores to sum to 1.0
        total_score = sum(scores.values())
        if total_score > 0:
            normalized_scores = {std: score / total_score for std, score in scores.items()}
        else:
            # If all scores are 0, assign equal probabilities
            normalized_scores = {std: 1.0 / len(scores) for std in scores}

        # Convert to list of dictionaries and sort by probability
        ranked_standards = [
            {"standard": std, "probability": prob}
            for std, prob in normalized_scores.items()
        ]
        ranked_standards.sort(key=lambda x: x["probability"], reverse=True)

        return ranked_standards

    def _generate_reasoning(self,
                            parsed_transaction: Dict[str, Any],
                            rag_results: Dict[str, Any],
                            ranked_standards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate structured reasoning for each applicable standard

        Returns:
            List of dictionaries with standard, probability, and reasoning
        """
        # If no ranked standards, return empty list
        if not ranked_standards:
            return []

        # Extract requirements from RAG results
        requirements = rag_results.get("detailed_context", {}).get("requirements", {})

        # Extract transaction elements
        transaction_text = parsed_transaction.get("raw_text", "")
        transaction_types = parsed_transaction.get("transaction_types", {})
        islamic_terms = parsed_transaction.get("islamic_terms", [])
        journal_entries = parsed_transaction.get("journal_entries", [])

        # Use LLM to generate reasoning for each standard
        reasoned_standards = []

        # Create a prompt template for reasoning generation
        prompt_template = ChatPromptTemplate.from_template(
            """
            Generate structured reasoning for why the following AAOIFI Financial Accounting Standard (FAS) 
            is applicable to this transaction.

            Transaction:
            {transaction}

            Standard: {standard}

            Standard Requirements:
            {requirements}

            Transaction Elements:
            - Transaction Types: {transaction_types}
            - Islamic Finance Terms: {islamic_terms}
            - Journal Entries: {journal_entries}

            Please provide a detailed reasoning that explains:
            1. Why this standard applies to the transaction
            2. Which specific elements of the transaction match the standard's requirements
            3. Any potential limitations or considerations

            Format your response as a concise paragraph that would be suitable for inclusion in a formal analysis.

            Reasoning:
            """
        )

        # Create the chain
        chain = LLMChain(llm=self.llm, prompt=prompt_template)

        # Generate reasoning for each standard
        for ranked_standard in ranked_standards:
            standard = ranked_standard["standard"]
            probability = ranked_standard["probability"]

            # Get requirements for this standard
            standard_requirements = requirements.get(standard, [])
            requirements_text = "\n".join([f"- {req}" for req in standard_requirements])
            if not requirements_text:
                requirements_text = "No specific requirements found in the retrieved documents."

            # Format transaction types
            transaction_types_text = ", ".join([f"{t_type} ({confidence:.2f})"
                                                for t_type, confidence in transaction_types.items()])

            # Format journal entries
            journal_entries_text = []
            for entry in journal_entries:
                debit = entry.get("debit_account", "")
                credit = entry.get("credit_account", "")
                debit_amount = entry.get("debit_amount", "")
                credit_amount = entry.get("credit_amount", "")

                if debit and credit:
                    entry_text = f"Dr. {debit}"
                    if debit_amount:
                        entry_text += f" {debit_amount}"
                    entry_text += f" / Cr. {credit}"
                    if credit_amount:
                        entry_text += f" {credit_amount}"
                    journal_entries_text.append(entry_text)

            journal_entries_formatted = "\n".join(
                journal_entries_text) if journal_entries_text else "No journal entries found"

            # Run the chain
            reasoning = chain.run(
                transaction=transaction_text,
                standard=standard,
                requirements=requirements_text,
                transaction_types=transaction_types_text,
                islamic_terms=", ".join(islamic_terms),
                journal_entries=journal_entries_formatted
            )

            # Add to reasoned standards
            reasoned_standards.append({
                "standard": standard,
                "probability": probability,
                "reasoning": reasoning.strip()
            })

        return reasoned_standards

    def _apply_edge_case_rules(self,
                               parsed_transaction: Dict[str, Any],
                               reasoned_standards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply edge case rules and scope limitations

        Returns:
            List of dictionaries with final standards, probabilities, and reasoning
        """
        # If no reasoned standards, return empty list
        if not reasoned_standards:
            # Check for construction/contract features and add FAS 10
            transaction_text = parsed_transaction.get("raw_text", "").lower()
            transaction_types = parsed_transaction.get("transaction_types", {})
            journal_entries = parsed_transaction.get("journal_entries", [])

            has_construction = "construction" in transaction_types or any(term in transaction_text for term
                                                                          in ["construction", "project", "development",
                                                                              "contract"])
            has_reversal = "reversal" in transaction_types or any(term in transaction_text for term
                                                                  in ["cancel", "revert", "reverse", "adjustment",
                                                                      "revised"])
            has_work_in_progress = any("work-in-progress" in entry.get("debit_account", "").lower() or
                                       "work-in-progress" in entry.get("credit_account", "").lower()
                                       for entry in journal_entries)

            if has_construction or has_reversal or has_work_in_progress or "istisna" in transaction_text:
                # Generate reasoning for FAS 10
                prompt_template = ChatPromptTemplate.from_template(
                    """
                    Generate reasoning for why FAS 10 (Istisna'a and Parallel Istisna'a) is applicable 
                    to this transaction which involves construction contract elements or modifications/reversals.

                    Transaction:
                    {transaction}

                    Reasoning:
                    """
                )
                chain = LLMChain(llm=self.llm, prompt=prompt_template)
                reasoning = chain.run(transaction=parsed_transaction.get("raw_text", ""))

                return [{
                    "standard": "FAS 10",
                    "probability": 1.0,
                    "probability_percentage": "100.0%",
                    "reasoning": reasoning.strip()
                }]
            return []

        # Extract transaction data
        transaction_text = parsed_transaction.get("raw_text", "").lower()
        transaction_types = parsed_transaction.get("transaction_types", {})
        journal_entries = parsed_transaction.get("journal_entries", [])

        # Detect key scenario indicators
        has_construction = "construction" in transaction_types or any(term in transaction_text for term
                                                                    in ["construction", "project", "development", "contract"])
        has_reversal = "reversal" in transaction_types or any(term in transaction_text for term
                                                           in ["cancel", "revert", "reverse", "adjustment", "revised"])
        has_work_in_progress = any("work-in-progress" in entry.get("debit_account", "").lower() or
                                 "work-in-progress" in entry.get("credit_account", "").lower()
                                 for entry in journal_entries)

        # Detect banking/equity buyout indicators
        has_bank = any(term in transaction_text for term in
                      ["bank", "financial", "finance", "banking"])
        has_equity_transaction = any(term in transaction_text for term in
                                   ["equity", "stake", "share", "ownership", "acquisition"])
        has_cash_payment = any("cash" in entry.get("credit_account", "").lower() for entry in journal_entries)

        # Check if there are equity-related journal entries
        has_equity_journal = False
        for entry in journal_entries:
            debit_account = entry.get("debit_account", "").lower()
            credit_account = entry.get("credit_account", "").lower()
            if "equity" in debit_account or "equity" in credit_account:
                has_equity_journal = True
                break

        # Special case: banking buyout with equity transactions - prioritize FAS 4 and FAS 20
        if "buyout" in transaction_types and (has_bank or has_equity_transaction) and has_equity_journal:
            # Check if FAS 4 is present
            fas4_present = any(std["standard"] == "FAS 4" for std in reasoned_standards)
            fas20_present = any(std["standard"] == "FAS 20" for std in reasoned_standards)

            # If not present, add them
            if not fas4_present:
                # Generate reasoning for FAS 4
                prompt_template = ChatPromptTemplate.from_template(
                    """
                    Generate reasoning for why FAS 4 (Murabaha and Other Deferred Payment Sales) 
                    is applicable to this banking/financial buyout transaction involving equity transfer.

                    Transaction:
                    {transaction}

                    Reasoning:
                    """
                )
                chain = LLMChain(llm=self.llm, prompt=prompt_template)
                reasoning = chain.run(transaction=parsed_transaction.get("raw_text", ""))

                # Add FAS 4 with high probability
                reasoned_standards.append({
                    "standard": "FAS 4",
                    "probability": 0.8,  # Assign a very high probability
                    "reasoning": reasoning.strip() + "\n\nNote: Added due to banking/financial buyout with equity transfer."
                })

            if not fas20_present:
                # Generate reasoning for FAS 20
                prompt_template = ChatPromptTemplate.from_template(
                    """
                    Generate reasoning for why FAS 20 (Sale and Leaseback)
                    might be applicable to this banking/financial buyout transaction.

                    Transaction:
                    {transaction}

                    Reasoning:
                    """
                )
                chain = LLMChain(llm=self.llm, prompt=prompt_template)
                reasoning = chain.run(transaction=parsed_transaction.get("raw_text", ""))

                # Add FAS 20 with high probability
                reasoned_standards.append({
                    "standard": "FAS 20",
                    "probability": 0.6,  # Assign a high probability but less than FAS 4
                    "reasoning": reasoning.strip() + "\n\nNote: Added as a potential alternative treatment for this banking/financial buyout."
                })

            # Boost existing FAS 4 and FAS 20 if present
            for standard in reasoned_standards:
                if standard["standard"] == "FAS 4":
                    standard["probability"] = max(standard["probability"] * 2.0, 0.8)
                    standard["reasoning"] += "\n\nNote: Probability significantly increased due to banking/financial buyout scenario which is particularly relevant to FAS 4."
                elif standard["standard"] == "FAS 20":
                    standard["probability"] = max(standard["probability"] * 1.5, 0.6)
                    standard["reasoning"] += "\n\nNote: Probability increased due to banking/financial buyout scenario."
                elif standard["standard"] == "FAS 32":
                    standard["probability"] = max(standard["probability"] * 1.2, 0.4)
                elif standard["standard"] == "FAS 10":
                    # Reduce probability of FAS 10 when it's a banking buyout, not construction
                    if not (has_construction or has_work_in_progress):
                        standard["probability"] *= 0.5
                        standard["reasoning"] += "\n\nNote: Probability decreased as this appears to be a banking/financial buyout rather than a construction contract."

        # Rule 1: For construction/istisna contracts, especially with work-in-progress accounts, prioritize FAS 10
        elif has_construction or has_reversal or has_work_in_progress or "istisna" in transaction_text:
            fas10_present = False
            for standard in reasoned_standards:
                if standard["standard"] == "FAS 10":
                    fas10_present = True
                    # Significantly increase probability for FAS 10
                    standard["probability"] = max(standard["probability"] * 2.0, 0.7)
                    standard["reasoning"] += "\n\nNote: Probability significantly increased due to construction/contract elements or reversal scenario which is particularly relevant to FAS 10."
                    break

            # If FAS 10 is not present but should be, add it with high probability
            if not fas10_present:
                prompt_template = ChatPromptTemplate.from_template(
                    """
                    Generate reasoning for why FAS 10 (Istisna'a and Parallel Istisna'a) is applicable 
                    to this transaction which involves construction contract elements or modifications/reversals.

                    Transaction:
                    {transaction}

                    Reasoning:
                    """
                )
                chain = LLMChain(llm=self.llm, prompt=prompt_template)
                reasoning = chain.run(transaction=parsed_transaction.get("raw_text", ""))

                # Add FAS 10 to the standards with high probability
                reasoned_standards.append({
                    "standard": "FAS 10",
                    "probability": 0.7,  # Assign a high probability
                    "reasoning": reasoning.strip() + "\n\nNote: Added due to construction contract elements or reversal scenario in the transaction."
                })

        # Rule 2: For Ijarah with transfer of ownership, prioritize FAS 32
        if "ijarah" in transaction_text and any(term in transaction_text for term in ["transfer", "ownership", "end"]):
            for standard in reasoned_standards:
                if standard["standard"] == "FAS 32":
                    # Increase probability for FAS 32
                    standard["probability"] = max(standard["probability"] * 1.3, 0.4)
                    standard["reasoning"] += "\n\nNote: Probability adjusted due to Ijarah with potential transfer of ownership."

        # Remove excluded standards for construction/reversal transactions
        if has_construction or has_reversal:
            excluded = ["FAS 8", "FAS 19", "FAS 23"]
            reasoned_standards = [std for std in reasoned_standards if std["standard"] not in excluded]

        # If we still have standards to rank
        if reasoned_standards:
            # Normalize probabilities again to sum to 1.0
            total_probability = sum(std["probability"] for std in reasoned_standards)
            if total_probability > 0:
                for standard in reasoned_standards:
                    standard["probability"] = standard["probability"] / total_probability

            # Sort by probability
            reasoned_standards.sort(key=lambda x: x["probability"], reverse=True)

            # Convert probabilities to percentages for display
            for standard in reasoned_standards:
                standard["probability_percentage"] = f"{standard['probability'] * 100:.1f}%"

        return reasoned_standards

    def _summarize_transaction_analysis(self, parsed_transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a summary of the transaction analysis

        Returns:
            Dictionary with transaction analysis summary
        """
        return {
            "transaction_types": parsed_transaction.get("transaction_types", {}),
            "islamic_terms": parsed_transaction.get("islamic_terms", []),
            "accounting_terms": parsed_transaction.get("accounting_terms", []),
            "journal_entries": parsed_transaction.get("journal_entries", []),
            "context": parsed_transaction.get("context", {})
        }
