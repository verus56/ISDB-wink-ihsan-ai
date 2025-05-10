from src.config.settings import OPENAI_API_KEY

class ShariahExpertAgent:
    def __init__(self, conversation_buffer=None, llm=None):
        self.name = "Shariah Expert Agent"
        self.conversation_buffer = conversation_buffer
        self.openai_api_key = OPENAI_API_KEY
        self.llm = llm  # Store the LLM model
        self.shariah_principles = self._load_shariah_principles()
        self.scholarly_sources = []  # Track sources of Shariah interpretations
    
    def provide_insight(self, query):
        """
        Provides insights on Islamic finance queries based on contemporary Shariah scholarship.
        
        Args:
            query (str): The query or question related to Islamic finance
            
        Returns:
            dict: A dictionary containing the insight and references to Shariah sources
        """
        # Analyze the query against Shariah principles
        insight = self._analyze_query(query)
        
        # Log the insight to the conversation buffer
        if self.conversation_buffer:
            self.conversation_buffer.add_message(
                self.name, 
                f"Insight on '{query}': {insight['summary']}"
            )
            
        return insight
    
    def evaluate_standard(self, standard):
        """
        Evaluates an AAOIFI standard against Shariah principles.
        
        Args:
            standard (dict): The standard to evaluate containing title, content, and other metadata
            
        Returns:
            dict: Evaluation results with compliance level and recommendations
        """
        # Evaluate the standard against Shariah principles
        evaluation = self._conduct_shariah_evaluation(standard)
        
        # Log the evaluation to the conversation buffer
        if self.conversation_buffer:
            compliance_status = evaluation['compliance_status']
            self.conversation_buffer.add_message(
                self.name, 
                f"Standard '{standard.get('title', 'Untitled')}' evaluated: {compliance_status}"
            )
            
        return evaluation
    
    def generate_ruling(self, context):
        """
        Generates a Shariah ruling based on the provided context.
        
        Args:
            context (dict): The context for the ruling including the question, relevant facts, and circumstances
            
        Returns:
            dict: Shariah ruling with justification and references
        """
        # Generate a ruling based on the context
        ruling = self._formulate_ruling(context)
        
        # Log the ruling to the conversation buffer
        if self.conversation_buffer:
            self.conversation_buffer.add_message(
                self.name, 
                f"Ruling generated for '{context.get('question', 'inquiry')}': {ruling['summary']}"
            )
            
        return ruling
    
    def _load_shariah_principles(self):
        """
        Loads the fundamental Shariah principles for Islamic finance.
        
        Returns:
            dict: Dictionary containing Shariah principles
        """
        # In a production environment, this would load from a database or file
        # This is a simplified version with basic principles
        return {
            "riba": {
                "name": "Prohibition of Riba (Interest)",
                "description": "The prohibition of lending with interest or usury",
                "references": ["Quran 2:275-280", "Quran 3:130", "Quran 4:161"]
            },
            "gharar": {
                "name": "Avoidance of Gharar (Uncertainty)",
                "description": "The prohibition of excessive uncertainty in contracts",
                "references": ["Hadith collections of Bukhari and Muslim"]
            },
            "maysir": {
                "name": "Prohibition of Maysir (Gambling)",
                "description": "The prohibition of gambling and games of chance",
                "references": ["Quran 2:219", "Quran 5:90-91"]
            },
            "zakat": {
                "name": "Obligation of Zakat",
                "description": "The obligation to pay zakat (almsgiving)",
                "references": ["Quran 2:43", "Quran 9:60"]
            },
            "halal_investments": {
                "name": "Halal Investments",
                "description": "The obligation to invest only in permissible activities",
                "references": ["Various scholarly consensus (ijma)"]
            }
        }
    
    def _analyze_query(self, query):
        """
        Analyzes a query against Shariah principles.
        
        Args:
            query (str): The query to analyze
            
        Returns:
            dict: Analysis results
        """
        # In a production environment, this would use NLP and ML models
        # to analyze the query against Shariah principles
        
        # Simulated analysis
        relevant_principles = self._identify_relevant_principles(query)
        
        return {
            "summary": "The query has been analyzed against Shariah principles",
            "relevant_principles": relevant_principles,
            "recommendation": "Based on the principles of Islamic finance, this would require further analysis by a qualified Shariah board.",
            "confidence_level": 0.85  # Simulated confidence level
        }
    
    def _identify_relevant_principles(self, query):
        """
        Identifies Shariah principles relevant to the query.
        
        Args:
            query (str): The query to analyze
            
        Returns:
            list: List of relevant principles
        """
        # Simple keyword matching for demonstration
        # In production, this would use more sophisticated NLP techniques
        query_lower = query.lower()
        relevant_principles = []
        
        if "interest" in query_lower or "riba" in query_lower:
            relevant_principles.append(self.shariah_principles["riba"])
        
        if "uncertainty" in query_lower or "gharar" in query_lower:
            relevant_principles.append(self.shariah_principles["gharar"])
        
        if "gambling" in query_lower or "maysir" in query_lower:
            relevant_principles.append(self.shariah_principles["maysir"])
        
        if "zakat" in query_lower or "alms" in query_lower:
            relevant_principles.append(self.shariah_principles["zakat"])
        
        if "investment" in query_lower or "halal" in query_lower:
            relevant_principles.append(self.shariah_principles["halal_investments"])
        
        # If no specific principles are identified, return all principles as potentially relevant
        if not relevant_principles:
            relevant_principles = list(self.shariah_principles.values())
        
        return relevant_principles
    
    def _conduct_shariah_evaluation(self, standard):
        """
        Conducts a Shariah evaluation of a standard.
        
        Args:
            standard (dict): The standard to evaluate
            
        Returns:
            dict: Evaluation results
        """
        # In a production environment, this would use more sophisticated analysis
        # Here we're simulating a basic evaluation
        
        # Extract key information from the standard
        title = standard.get('title', '')
        content = standard.get('content', '')
        
        # Simulate compliance checking
        compliance_issues = self._check_compliance_issues(content)
        
        if not compliance_issues:
            compliance_status = "Fully compliant with Shariah principles"
            recommendations = []
        else:
            compliance_status = "Partially compliant with Shariah principles"
            recommendations = [f"Address issue with {issue}" for issue in compliance_issues]
        
        return {
            "standard_title": title,
            "compliance_status": compliance_status,
            "issues_identified": compliance_issues,
            "recommendations": recommendations,
            "evaluation_date": "2025-05-10"  # Using current date
        }
    
    def _check_compliance_issues(self, content):
        """
        Checks for compliance issues in the content.
        
        Args:
            content (str): The content to check
            
        Returns:
            list: List of identified compliance issues
        """
        # In production, this would use NLP and other advanced techniques
        # Here we're simulating with simple keyword matching
        content_lower = content.lower()
        issues = []
        
        # Simple checks for demonstration
        if "interest" in content_lower and "prohibited" not in content_lower:
            issues.append("interest (riba) considerations")
        
        if "speculation" in content_lower and "avoided" not in content_lower:
            issues.append("excessive uncertainty (gharar)")
        
        if "gambling" in content_lower and "prohibited" not in content_lower:
            issues.append("gambling (maysir) elements")
        
        return issues
    
    def _formulate_ruling(self, context):
        """
        Formulates a Shariah ruling based on the provided context.
        
        Args:
            context (dict): The context for the ruling
            
        Returns:
            dict: Shariah ruling
        """
        # Extract key information from the context
        question = context.get('question', '')
        facts = context.get('facts', {})
        circumstances = context.get('circumstances', [])
        
        # In production, this would use more sophisticated reasoning
        # Here we're simulating a basic ruling
        
        # Determine relevant principles
        relevant_principles = self._identify_relevant_principles(question)
        
        # Simulate reasoning process
        reasoning = f"Based on the provided facts and circumstances, and considering the principles of {', '.join([p['name'] for p in relevant_principles])}"
        
        return {
            "question": question,
            "summary": "This matter requires careful consideration of Shariah principles.",
            "ruling": "Conditionally permissible subject to specified conditions.",
            "reasoning": reasoning,
            "recommendations": [
                "Consult with a qualified Shariah board for final approval.",
                "Ensure all contractual elements are clearly defined to avoid gharar.",
                "Verify that the transaction does not indirectly involve prohibited elements."
            ],
            "references": [p["references"] for p in relevant_principles],
            "confidence_level": 0.80  # Simulated confidence level
        }