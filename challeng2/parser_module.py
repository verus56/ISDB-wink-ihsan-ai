import re
from typing import Dict, List, Any
import json


class TransactionParser:
    """
    Parser Module for AAOIFI FAS Identification System

    Extracts structured data from transaction descriptions including:
    - Context
    - Adjustments
    - Accounting treatment
    - Journal entries
    - Transaction types
    """

    # Common financial and accounting terms
    ACCOUNTING_TERMS = [
        "debit", "credit", "journal", "entry", "recognition", "derecognition",
        "equity", "asset", "liability", "revenue", "expense", "capital",
        "profit", "loss", "dividend", "interest", "principal", "amortization",
        "contract", "reversal", "adjustment", "revised", "modification", "work-in-progress",
        "buyout", "acquisition", "ownership", "stake", "banking"
    ]

    # Islamic finance specific terms
    ISLAMIC_TERMS = [
        "murabaha", "ijarah", "istisna", "salam", "musharakah", "mudarabah",
        "sukuk", "takaful", "wadiah", "qard", "wakalah", "hibah", "bai", "ujrah"
    ]

    # Transaction type patterns
    TRANSACTION_TYPES = {
        "buyout": ["buyout", "acquisition", "purchase", "takeover", "buy out", "exits", "stake"],
        "equity_buyout": ["equity buyout", "stake purchase", "ownership transfer", "exits", "ownership"],
        "financial_buyout": ["financial buyout", "bank buyout", "institutional buyout", "bank purchase"],
        "banking_buyout": ["bank", "banking", "finance house", "financial institution", "buyout", "purchase"],
        "reversal": ["reversal", "reverse", "cancel", "void", "nullify", "adjustment", "restore", "revert"],
        "recognition": ["recognition", "recognize", "record", "book", "account for"],
        "lease": ["lease", "rental", "ijarah", "hire", "usufruct"],
        "sale": ["sale", "sell", "dispose", "transfer ownership", "convey"],
        "construction": ["construction", "build", "develop", "project", "istisna", "work-in-progress"],
        "investment": ["investment", "invest", "fund", "finance", "capital"],
        "partnership": ["partnership", "musharakah", "joint venture", "collaboration"],
        "contract": ["contract", "agreement", "arrangement", "commitment", "obligation"]
    }

    def __init__(self):
        """Initialize the parser with default patterns"""
        # Compile regex patterns for better performance
        self.amount_pattern = re.compile(
            r'\$\s*\d+(?:,\d+)*(?:\.\d+)?|\d+(?:,\d+)*(?:\.\d+)?\s*(?:USD|AED|SAR|EUR|GBP)')
        self.percentage_pattern = re.compile(r'\d+(?:\.\d+)?\s*%')
        self.date_pattern = re.compile(
            r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4}')
        self.account_pattern = re.compile(r'(?:account|acct)\.?\s*(?:#|no\.?|number)?\s*\d+', re.IGNORECASE)

    def parse(self, transaction_text: str) -> Dict[str, Any]:
        """
        Parse transaction text into structured data

        Args:
            transaction_text: Raw transaction description

        Returns:
            Dictionary containing structured transaction data
        """
        # Initialize result structure
        result = {
            "raw_text": transaction_text,
            "financial_values": self._extract_financial_values(transaction_text),
            "dates": self._extract_dates(transaction_text),
            "accounts": self._extract_accounts(transaction_text),
            "accounting_terms": self._extract_accounting_terms(transaction_text),
            "islamic_terms": self._extract_islamic_terms(transaction_text),
            "transaction_types": self._identify_transaction_types(transaction_text),
            "journal_entries": self._extract_journal_entries(transaction_text),
            "context": self._extract_context(transaction_text)
        }

        # Add normalized values
        result["normalized_values"] = self._normalize_values(result)

        return result

    def _extract_financial_values(self, text: str) -> List[str]:
        """Extract financial values from text"""
        return self.amount_pattern.findall(text)

    def _extract_dates(self, text: str) -> List[str]:
        """Extract dates from text"""
        return self.date_pattern.findall(text)

    def _extract_accounts(self, text: str) -> List[str]:
        """Extract account references from text"""
        accounts = self.account_pattern.findall(text)

        # Also look for common account names
        common_accounts = ["cash", "inventory", "receivable", "payable",
                           "revenue", "expense", "asset", "liability", "equity"]

        for account in common_accounts:
            pattern = re.compile(r'\b' + account + r'\b\s+(?:account|acct)?', re.IGNORECASE)
            matches = pattern.findall(text)
            if matches:
                accounts.extend(matches)

        return accounts

    def _extract_accounting_terms(self, text: str) -> List[str]:
        """Extract accounting terminology from text"""
        text_lower = text.lower()
        return [term for term in self.ACCOUNTING_TERMS if term in text_lower]

    def _extract_islamic_terms(self, text: str) -> List[str]:
        """Extract Islamic finance terminology from text"""
        text_lower = text.lower()
        islamic_terms = [term for term in self.ISLAMIC_TERMS if term in text_lower]

        # Infer terms from context if not explicitly mentioned
        if "bank" in text_lower and "equity" in text_lower and "purchase" in text_lower:
            if "murabaha" not in islamic_terms:
                islamic_terms.append("murabaha")

        return islamic_terms

    def _identify_transaction_types(self, text: str) -> Dict[str, float]:
        """
        Identify transaction types with confidence scores

        Returns:
            Dictionary mapping transaction types to confidence scores (0-1)
        """
        text_lower = text.lower()
        results = {}

        # First look for very specific transaction contexts

        # Check for construction contract indicators
        if "construction" in text_lower or "istisna" in text_lower or "work-in-progress" in text_lower:
            results["construction"] = 0.8

        # Check for reversal indicators
        if "cancel" in text_lower or "revert" in text_lower or "reverse" in text_lower or "adjustment" in text_lower or "revised" in text_lower:
            results["reversal"] = 0.7

        # Check for contract indicators
        if "contract" in text_lower and "value" in text_lower:
            results["contract"] = 0.7

        # Check for bank/financial buyout indicators
        if ("bank" in text_lower or "financial" in text_lower) and (
                "equity" in text_lower or "stake" in text_lower or "exits" in text_lower or "buyout" in text_lower):
            results["banking_buyout"] = 0.8
            results["financial_buyout"] = 0.7
            results["buyout"] = 0.6

        # Check for equity transfer indicators
        if ("equity" in text_lower or "stake" in text_lower or "ownership" in text_lower) and (
                "buy" in text_lower or "purchase" in text_lower or "acquire" in text_lower or "exit" in text_lower):
            results["equity_buyout"] = 0.8
            results["buyout"] = 0.7

        # Then do the standard keyword matching
        for t_type, keywords in self.TRANSACTION_TYPES.items():
            score = 0.0
            for keyword in keywords:
                if keyword in text_lower:
                    # Base score for keyword match
                    base_score = 0.3

                    # Increase score based on prominence (e.g., appears in first sentence)
                    first_sentence = text.split('.')[0].lower()
                    if keyword in first_sentence:
                        base_score += 0.2

                    # Increase score based on frequency
                    frequency = text_lower.count(keyword)
                    if frequency > 1:
                        base_score += min(0.1 * frequency, 0.3)  # Cap at 0.3

                    score = max(score, base_score)  # Take highest score among keywords

            if score > 0:
                # If there's already a score for this type, take the higher one
                if t_type in results:
                    results[t_type] = max(results[t_type], min(score, 1.0))
                else:
                    results[t_type] = min(score, 1.0)  # Cap at 1.0

        return results

    def _extract_journal_entries(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract journal entries from text

        Looks for patterns like:
        - Dr. Account X / Cr. Account Y
        - Debit Account X / Credit Account Y
        - Account X (Dr) / Account Y (Cr)
        """
        journal_entries = []

        # Look for common journal entry patterns
        dr_cr_pattern = re.compile(r'(?:Dr\.?|Debit)\s+([^/\n]+)(?:/|\n)?\s*(?:Cr\.?|Credit)\s+([^/\n]+)',
                                   re.IGNORECASE)
        matches = dr_cr_pattern.findall(text)

        for debit, credit in matches:
            # Extract amounts if present
            debit_amount = self._extract_amount_from_entry(debit)
            credit_amount = self._extract_amount_from_entry(credit)

            journal_entries.append({
                "debit_account": debit.strip().split('$')[0].strip() if '$' in debit else debit.strip(),
                "credit_account": credit.strip().split('$')[0].strip() if '$' in credit else credit.strip(),
                "debit_amount": debit_amount,
                "credit_amount": credit_amount
            })

        # If no structured entries found, look for mentions of debits and credits separately
        if not journal_entries:
            debit_pattern = re.compile(r'(?:Dr\.?|Debit)\s+([^.\n]+)', re.IGNORECASE)
            credit_pattern = re.compile(r'(?:Cr\.?|Credit)\s+([^.\n]+)', re.IGNORECASE)

            debits = debit_pattern.findall(text)
            credits = credit_pattern.findall(text)

            if debits and credits:
                for debit in debits:
                    debit_amount = self._extract_amount_from_entry(debit)
                    debit_account = debit.strip().split('$')[0].strip() if '$' in debit else debit.strip()

                    for credit in credits:
                        credit_amount = self._extract_amount_from_entry(credit)
                        credit_account = credit.strip().split('$')[0].strip() if '$' in credit else credit.strip()

                        journal_entries.append({
                            "debit_account": debit_account,
                            "credit_account": credit_account,
                            "debit_amount": debit_amount,
                            "credit_amount": credit_amount
                        })

        return journal_entries

    def _extract_amount_from_entry(self, entry_text: str) -> str:
        """Extract amount from journal entry text"""
        amounts = self.amount_pattern.findall(entry_text)
        return amounts[0] if amounts else ""

    def _extract_context(self, text: str) -> Dict[str, Any]:
        """
        Extract contextual information from the transaction

        Identifies:
        - Industry/sector
        - Parties involved
        - Purpose of transaction
        - Timeframe
        """
        # Initialize context
        context = {
            "industry": None,
            "parties": [],
            "purpose": None,
            "timeframe": None
        }

        # Extract potential parties (entities)
        party_pattern = re.compile(
            r'(?:[A-Z][a-z]+\s+){1,3}(?:Bank|Company|Corporation|LLC|Ltd|Inc|PLC|Group|Institution)', re.IGNORECASE)
        parties = party_pattern.findall(text)
        if parties:
            context["parties"] = [p.strip() for p in parties]

        # Look for industry keywords
        industries = {
            "banking": ["bank", "financial institution", "finance house"],
            "real_estate": ["real estate", "property", "construction", "development"],
            "manufacturing": ["manufacturing", "production", "factory"],
            "retail": ["retail", "store", "shop", "merchandise"],
            "agriculture": ["agriculture", "farming", "crop", "harvest"],
            "energy": ["energy", "oil", "gas", "power", "electricity"]
        }

        text_lower = text.lower()
        for industry, keywords in industries.items():
            if any(keyword in text_lower for keyword in keywords):
                context["industry"] = industry
                break

        # Extract purpose (often follows phrases like "for the purpose of", "in order to")
        purpose_patterns = [
            r'for\s+(?:the\s+)?purpose\s+of\s+([^.]+)',
            r'in\s+order\s+to\s+([^.]+)',
            r'with\s+the\s+aim\s+of\s+([^.]+)',
            r'intended\s+to\s+([^.]+)'
        ]

        for pattern in purpose_patterns:
            matches = re.search(pattern, text_lower)
            if matches:
                context["purpose"] = matches.group(1).strip()
                break

        # Extract timeframe
        timeframe_patterns = [
            r'(?:period|term)\s+of\s+(\d+)\s+(?:year|month|day)s?',
            r'(\d+)[-]year\s+(?:period|term)',
            r'over\s+(?:a|the)\s+(?:period|term)\s+of\s+(\d+)\s+(?:year|month|day)s?'
        ]

        for pattern in timeframe_patterns:
            matches = re.search(pattern, text_lower)
            if matches:
                duration = matches.group(1)
                unit = "years" if "year" in matches.group(0) else "months" if "month" in matches.group(0) else "days"
                context["timeframe"] = f"{duration} {unit}"
                break

        return context

    def _normalize_values(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize extracted values for consistency

        - Standardize financial amounts
        - Normalize account names
        - Standardize dates
        """
        normalized = {}

        # Normalize financial values
        if parsed_data["financial_values"]:
            normalized_amounts = []
            for amount in parsed_data["financial_values"]:
                # Remove currency symbols, commas and convert to float
                clean_amount = re.sub(r'[^\d.]', '', amount.split()[0].replace('$', '').replace(',', ''))
                try:
                    normalized_amounts.append(float(clean_amount))
                except ValueError:
                    # If conversion fails, keep original
                    normalized_amounts.append(amount)
            normalized["financial_values"] = normalized_amounts

        # Normalize account names
        if parsed_data["accounts"]:
            normalized_accounts = []
            for account in parsed_data["accounts"]:
                # Standardize account references
                norm_account = account.lower()
                norm_account = re.sub(r'account|acct\.?|#|no\.?|number', '', norm_account).strip()
                normalized_accounts.append(norm_account)
            normalized["accounts"] = normalized_accounts

        # Normalize transaction types - keep only the highest confidence types
        if parsed_data["transaction_types"]:
            # Sort by confidence score and keep top 2
            sorted_types = sorted(parsed_data["transaction_types"].items(),
                                  key=lambda x: x[1], reverse=True)
            normalized["transaction_types"] = dict(sorted_types[:2])

        return normalized

    def to_json(self, parsed_data: Dict[str, Any]) -> str:
        """Convert parsed data to JSON string"""
        return json.dumps(parsed_data, indent=2)


# Example usage
if __name__ == "__main__":
    parser = TransactionParser()
    sample_transaction = """
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
    """

    result = parser.parse(sample_transaction)
    print(parser.to_json(result))