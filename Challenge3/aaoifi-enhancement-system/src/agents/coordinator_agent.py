import logging
import datetime
import json
import os
from src.config.settings import OUTPUT_DIR

class CoordinatorAgent:
    def __init__(self, conversation_buffer=None, primary_llm=None, secondary_llm=None):
        self.name = "Coordinator Agent"
        self.conversation_buffer = conversation_buffer
        self.primary_llm = primary_llm
        self.secondary_llm = secondary_llm
        self.agents = []
        self.documents = []
        self.standards = []
        self.workflow_state = {}
        self.results_cache = {}
        self.started_at = None
        self.completed_at = None
        self.workflow_steps = []
        self.amendment_sources = {}  # Track sources for each amendment
        self.amendment_reasoning = {}  # Track reasoning for each amendment
        self.verification_steps = {}  # Track verification steps for amendments
        
        # Set up logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger("CoordinatorAgent")
        
        # Initialize workflow steps
        self._initialize_workflow_steps()
    
    def _initialize_workflow_steps(self):
        """Initialize the standard workflow sequence for AAOIFI standards enhancement."""
        self.workflow_steps = [
            {
                "step_name": "standards_review",
                "description": "Review existing standards to identify enhancement opportunities",
                "agent_type": "StandardsReviewerAgent",
                "required_inputs": ["documents", "standards"],
                "outputs": ["enhancement_opportunities"]
            },
            {
                "step_name": "shariah_evaluation",
                "description": "Evaluate enhancement opportunities from a Shariah perspective",
                "agent_type": "ShariahExpertAgent",
                "required_inputs": ["enhancement_opportunities", "standards"],
                "outputs": ["shariah_insights"]
            },
            {
                "step_name": "financial_assessment",
                "description": "Assess financial implications of proposed enhancements",
                "agent_type": "FinancialAnalystAgent",
                "required_inputs": ["enhancement_opportunities", "shariah_insights"],
                "outputs": ["financial_implications"]
            },
            {
                "step_name": "compliance_check",
                "description": "Check compliance of proposed amendments with regulatory requirements",
                "agent_type": "ComplianceCheckerAgent",
                "required_inputs": ["enhancement_opportunities", "shariah_insights", "financial_implications"],
                "outputs": ["compliance_reports"]
            },
            {
                "step_name": "final_proposal",
                "description": "Formulate final enhancement proposals",
                "agent_type": "CoordinatorAgent",
                "required_inputs": ["enhancement_opportunities", "shariah_insights", "financial_implications", "compliance_reports"],
                "outputs": ["final_proposals"]
            }
        ]
    
    def coordinate_workflow(self):
        """
        Orchestrates the workflow between different agents in a structured sequence.
        Ensures each agent has the required inputs before execution and stores outputs for later steps.
        """
        self.started_at = datetime.datetime.now()
        self._log_workflow_start()
        
        # Initialize workflow state
        self.workflow_state = {
            "documents": self.documents,
            "standards": self.standards,
            "enhancement_opportunities": None,
            "shariah_insights": None,
            "financial_implications": None,
            "compliance_reports": None,
            "final_proposals": None
        }
        
        # Execute each workflow step in sequence
        for step in self.workflow_steps:
            self.logger.info(f"Starting workflow step: {step['step_name']}")
            
            # Check if required inputs are available
            if not self._check_required_inputs(step):
                self.logger.error(f"Missing required inputs for step '{step['step_name']}'. Cannot proceed.")
                message = f"Workflow step '{step['step_name']}' skipped due to missing inputs"
                self._add_to_conversation(message)
                continue
                
            # Execute the step with the appropriate agent
            step_results = self._execute_workflow_step(step)
            
            # Store the results in workflow state and cache
            for output in step['outputs']:
                self.workflow_state[output] = step_results.get(output)
                self.results_cache[output] = step_results.get(output)
            
            # Log step completion
            self._add_to_conversation(f"Completed workflow step: {step['step_name']}")
            
        self.completed_at = datetime.datetime.now()
        self._log_workflow_completion()
        
        # Generate final workflow summary
        return self._generate_workflow_summary()
    
    def _check_required_inputs(self, step):
        """
        Check if all required inputs for a workflow step are available.
        
        Args:
            step (dict): The workflow step definition
            
        Returns:
            bool: True if all required inputs are available, False otherwise
        """
        for input_name in step['required_inputs']:
            if input_name not in self.workflow_state or self.workflow_state[input_name] is None:
                self.logger.warning(f"Required input '{input_name}' missing for step '{step['step_name']}'")
                return False
        return True
    
    def _execute_workflow_step(self, step):
        """
        Execute a workflow step using the appropriate agent.
        
        Args:
            step (dict): The workflow step definition
            
        Returns:
            dict: The results of the workflow step
        """
        agent_type = step['agent_type']
        step_name = step['step_name']
        
        # Log detailed step execution
        self.logger.info(f"Executing workflow step '{step_name}' with agent type '{agent_type}'")
        self._add_to_conversation(f"Starting {step_name} with {agent_type}")
        
        # Handle the case where the coordinator itself is the agent
        if agent_type == "CoordinatorAgent":
            results = self._execute_coordinator_step(step)
            
            # For final proposals, verify each amendment with a secondary model
            if step_name == 'final_proposal' and 'final_proposals' in results:
                self.logger.info(f"Verifying {len(results['final_proposals'])} amendments with secondary model")
                for amendment in results['final_proposals']:
                    amendment_id = amendment.get('id')
                    if amendment_id:
                        verification = self.verify_amendment_with_secondary_model(amendment_id, amendment)
                        amendment['verification_results'] = verification
            
            return results
        
        # Find the appropriate agent
        agent = self._get_agent_by_type(agent_type)
        if not agent:
            self.logger.error(f"Agent of type '{agent_type}' not found")
            return {}
        
        # Prepare inputs for the agent
        inputs = {input_name: self.workflow_state[input_name] for input_name in step['required_inputs']}
        
        # Execute the agent with the appropriate method based on the step
        return self.execute_agent(agent, step, inputs)
    
    def _execute_coordinator_step(self, step):
        """
        Execute a workflow step where the coordinator itself is the agent.
        
        Args:
            step (dict): The workflow step definition
            
        Returns:
            dict: The results of the workflow step
        """
        if step['step_name'] == 'final_proposal':
            # Generate final proposals based on all previous step outputs
            enhancements = self.workflow_state['enhancement_opportunities']
            shariah_insights = self.workflow_state['shariah_insights']
            financial = self.workflow_state['financial_implications']
            compliance = self.workflow_state['compliance_reports']
            
            proposals = self._formulate_final_proposals(
                enhancements, shariah_insights, financial, compliance
            )
            
            self._add_to_conversation("Final enhancement proposals formulated")
            
            return {"final_proposals": proposals}
            
        return {}
    
    def _get_agent_by_type(self, agent_type):
        """
        Find an agent by its class name.
        
        Args:
            agent_type (str): The class name of the agent
            
        Returns:
            object: The agent instance, or None if not found
        """
        for agent in self.agents:
            if agent.__class__.__name__ == agent_type:
                return agent
        return None
    
    def execute_agent(self, agent, step, inputs):
        """
        Execute an agent's task based on the workflow step.
        
        Args:
            agent (object): The agent instance
            step (dict): The workflow step definition
            inputs (dict): The inputs for the agent
            
        Returns:
            dict: The results from the agent's execution
        """
        self._add_to_conversation(f"Executing {agent.__class__.__name__} for step '{step['step_name']}'")
        
        results = {}
        try:
            if step['step_name'] == 'standards_review':
                if hasattr(agent, 'analyze_standards'):
                    enhancement_opportunities = agent.analyze_standards(inputs['standards'])
                    results['enhancement_opportunities'] = enhancement_opportunities
                    
            elif step['step_name'] == 'shariah_evaluation':
                if hasattr(agent, 'evaluate_standard'):
                    shariah_insights = []
                    for enhancement in inputs['enhancement_opportunities']:
                        insight = agent.evaluate_standard({
                            'title': enhancement.get('title', 'Untitled Enhancement'),
                            'content': enhancement.get('description', ''),
                            'standard_id': enhancement.get('standard_id', '')
                        })
                        shariah_insights.append(insight)
                    results['shariah_insights'] = shariah_insights
                    
            elif step['step_name'] == 'financial_assessment':
                if hasattr(agent, 'assess_financial_implications'):
                    financial_implications = agent.assess_financial_implications(inputs['enhancement_opportunities'])
                    results['financial_implications'] = financial_implications
                    
            elif step['step_name'] == 'compliance_check':
                if hasattr(agent, 'check_compliance'):
                    compliance_reports = []
                    for enhancement in inputs['enhancement_opportunities']:
                        # Create a proposed amendment from the enhancement
                        proposed_amendment = {
                            'id': enhancement.get('id', ''),
                            'title': enhancement.get('title', 'Untitled Enhancement'),
                            'content': enhancement.get('description', ''),
                            'standard_id': enhancement.get('standard_id', ''),
                            'financial_impact': 'medium'  # Placeholder, could be determined from financial_implications
                        }
                        compliance_result = agent.check_compliance(proposed_amendment)
                        compliance_reports.append(compliance_result)
                    results['compliance_reports'] = compliance_reports
                
        except Exception as e:
            self.logger.error(f"Error executing agent {agent.__class__.__name__}: {str(e)}")
            self._add_to_conversation(f"Error occurred while executing {agent.__class__.__name__}: {str(e)}")
        
        self._add_to_conversation(f"Completed execution of {agent.__class__.__name__} for step '{step['step_name']}'")
        return results
    
    def gather_results(self):
        """
        Gather all results from the workflow execution.
        
        Returns:
            dict: Aggregated results from all workflow steps
        """
        return self.results_cache
        
    def _generate_workflow_summary(self):
        """
        Generate a summary of the workflow execution with all results.
        
        Returns:
            dict: Workflow summary including results from all workflow steps
        """
        summary = {
            "workflow_start": self.started_at,
            "workflow_end": self.completed_at,
            "duration_seconds": (self.completed_at - self.started_at).total_seconds() if self.completed_at and self.started_at else 0,
            "completed_steps": [step.get('step_name') for step in self.workflow_steps],
            "results": self.gather_results()
        }
        return summary
    
    def communicate(self, message, target_agents=None):
        """
        Send a message to one or more agents through the conversation buffer.
        
        Args:
            message (str): The message to send
            target_agents (list): List of agent instances to receive the message. If None, send to all agents.
        """
        self._add_to_conversation(message)
        
        if target_agents is None:
            target_agents = self.agents
            
        for agent in target_agents:
            if hasattr(agent, 'receive_message'):
                agent.receive_message({
                    'sender': self.name,
                    'message': message,
                    'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
    
    def run(self):
        """
        Execute the full workflow and return the results.
        
        Returns:
            dict: The final results from the workflow
        """
        if not self.agents:
            self.logger.error("No agents registered. Cannot run workflow.")
            return {}
            
        self.coordinate_workflow()
        results = self.gather_results()
        
        # Generate and save workflow report
        workflow_report = {
            "workflow_id": f"workflow_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "started_at": self.started_at.strftime("%Y-%m-%d %H:%M:%S") if self.started_at else None,
            "completed_at": self.completed_at.strftime("%Y-%m-%d %H:%M:%S") if self.completed_at else None,
            "duration_seconds": (self.completed_at - self.started_at).total_seconds() if self.completed_at and self.started_at else None,
            "agents_used": [agent.__class__.__name__ for agent in self.agents],
            "documents_processed": len(self.documents),
            "standards_processed": len(self.standards),
            "final_proposals": results.get('final_proposals', [])
        }
        
        # Save report to file
        self._save_workflow_report(workflow_report)
        
        self._add_to_conversation("Workflow execution completed")
        return results
        
    def manage_workflow(self, documents, standards, agents):
        """
        Manage the workflow between different agents.
        
        Args:
            documents: The loaded documents for analysis
            standards: The retrieved standards
            agents: List of specialized agents for the workflow
            
        Returns:
            dict: The results of the workflow execution
        """
        self.documents = documents
        self.standards = standards
        self.agents = agents
        
        self._add_to_conversation(
            f"Starting workflow with {len(documents)} documents, {len(standards)} standards, " 
            f"and {len(agents)} specialized agents"
        )
        
        for agent in agents:
            agent_type = agent.__class__.__name__
            self._add_to_conversation(f"Registered {agent_type} for workflow")
            
        # Execute the workflow
        results = self.run()
        
        # Log workflow completion
        self._add_to_conversation("Workflow completed successfully")
        
        return results
    
    def _add_to_conversation(self, message):
        """
        Add a message to the conversation buffer.
        
        Args:
            message (str): The message to add
        """
        if self.conversation_buffer:
            self.conversation_buffer.add_message(self.name, message)
        self.logger.info(message)
    
    def _log_workflow_start(self):
        """Log the start of the workflow."""
        self._add_to_conversation(
            f"Workflow started at {self.started_at.strftime('%Y-%m-%d %H:%M:%S')}"
        )
    
    def _log_workflow_completion(self):
        """Log the completion of the workflow."""
        duration = (self.completed_at - self.started_at).total_seconds()
        self._add_to_conversation(
            f"Workflow completed at {self.completed_at.strftime('%Y-%m-%d %H:%M:%S')} "
            f"(duration: {duration:.2f} seconds)"
        )
    
    def _save_workflow_report(self, report):
        """
        Save the workflow report to a file.
        
        Args:
            report (dict): The workflow report
        """
        try:
            filename = f"workflow_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
                
            self.logger.info(f"Workflow report saved to {filepath}")
        except Exception as e:
            self.logger.error(f"Error saving workflow report: {str(e)}")
    
    def _formulate_final_proposals(self, enhancements, shariah_insights, financial_implications, compliance_reports):
        """
        Formulate final enhancement proposals based on all agent inputs.
        
        Args:
            enhancements (list): Enhancement opportunities from standards reviewer
            shariah_insights (list): Shariah compliance insights
            financial_implications (dict): Financial impact assessment
            compliance_reports (list): Compliance check results
            
        Returns:
            list: Final enhancement proposals
        """
        # In a real implementation, this would involve more sophisticated integration
        # and prioritization of the various agent inputs
        
        final_proposals = []
        
        for i, enhancement in enumerate(enhancements):
            # Find corresponding compliance report and shariah insight if available
            compliance_report = compliance_reports[i] if i < len(compliance_reports) else None
            shariah_insight = shariah_insights[i] if i < len(shariah_insights) else None
            
            is_compliant = True
            if compliance_report and 'overall_compliant' in compliance_report:
                is_compliant = compliance_report['overall_compliant']
            
            # Only include compliant enhancements in final proposals
            if is_compliant:
                proposal = {
                    "id": enhancement.get('id', f"proposal_{i+1}"),
                    "title": enhancement.get('title', 'Untitled Enhancement'),
                    "description": enhancement.get('description', ''),
                    "standard_id": enhancement.get('standard_id', ''),
                    "justification": enhancement.get('rationale', ''),
                    "shariah_compliance": self._extract_shariah_compliance(shariah_insight),
                    "financial_impact": self._extract_financial_impact(financial_implications, enhancement),
                    "recommendation": "Approved for implementation",
                    "priority": self._calculate_priority(enhancement, shariah_insight, financial_implications, compliance_report)
                }
                final_proposals.append(proposal)
            else:
                # Log that this enhancement was rejected
                self._add_to_conversation(
                    f"Enhancement '{enhancement.get('title', 'Untitled')}' rejected due to compliance issues"
                )
        
        # Sort proposals by priority (high to low)
        final_proposals.sort(key=lambda x: x['priority'], reverse=True)
        
        return final_proposals
    
    def _extract_shariah_compliance(self, shariah_insight):
        """Extract shariah compliance information from insight."""
        if not shariah_insight:
            return "Unknown"
            
        if 'compliance_status' in shariah_insight:
            return shariah_insight['compliance_status']
            
        return "Pending Shariah review"
    
    def _extract_financial_impact(self, financial_implications, enhancement):
        """Extract financial impact information."""
        if not financial_implications:
            return "Unknown"
            
        # In a real implementation, this would extract relevant financial data
        # specific to this enhancement
        return financial_implications.get('financial_impact', 'Unknown')
    
    def _calculate_priority(self, enhancement, shariah_insight, financial_implications, compliance_report):
        """
        Calculate priority score for an enhancement proposal.
        
        Returns:
            int: Priority score (1-10, higher is more important)
        """
        priority = 5  # Default medium priority
        
        # Increase priority for fully shariah compliant proposals
        if shariah_insight and shariah_insight.get('compliant', False):
            priority += 2
            
        # Adjust priority based on compliance score if available
        if compliance_report and 'overall_compliant' in compliance_report:
            if compliance_report['overall_compliant']:
                priority += 1
                
            # If there's a compliance score, use it to further adjust priority
            if 'shariah_compliance' in compliance_report and 'compliance_score' in compliance_report['shariah_compliance']:
                score = compliance_report['shariah_compliance']['compliance_score']
                if score > 90:
                    priority += 1
        
        # Cap priority between 1-10
        priority = max(1, min(10, priority))
        return priority
    
    def track_amendment_metadata(self, amendment_id, metadata):
        """
        Track metadata for amendments, including sources and reasoning.
        
        Args:
            amendment_id (str): The unique identifier for the amendment
            metadata (dict): Metadata about the amendment, including:
                - sources: List of source documents or references
                - reasoning: The reasoning behind the amendment
                - verification: Steps taken to verify the amendment
                - confidence: Confidence score (0-1) for the amendment
                - model_used: Which model made this recommendation
        """
        if amendment_id not in self.amendment_sources:
            self.amendment_sources[amendment_id] = []
            self.amendment_reasoning[amendment_id] = ""
            self.verification_steps[amendment_id] = []
            
        # Add sources
        if 'sources' in metadata:
            if isinstance(metadata['sources'], list):
                self.amendment_sources[amendment_id].extend(metadata['sources'])
            else:
                self.amendment_sources[amendment_id].append(metadata['sources'])
        
        # Update reasoning
        if 'reasoning' in metadata:
            current_reasoning = self.amendment_reasoning[amendment_id]
            if current_reasoning:
                self.amendment_reasoning[amendment_id] = f"{current_reasoning}\n\nAdditional reasoning:\n{metadata['reasoning']}"
            else:
                self.amendment_reasoning[amendment_id] = metadata['reasoning']
        
        # Add verification steps
        if 'verification' in metadata:
            if isinstance(metadata['verification'], list):
                self.verification_steps[amendment_id].extend(metadata['verification'])
            else:
                self.verification_steps[amendment_id].append(metadata['verification'])
        
        # Log metadata tracking
        self._add_to_conversation(f"Tracked metadata for amendment {amendment_id}: {len(self.amendment_sources[amendment_id])} sources, {len(self.verification_steps[amendment_id])} verification steps")

    def verify_amendment_with_secondary_model(self, amendment_id, amendment_data):
        """
        Verifies a proposed amendment using the secondary model as a different perspective.
        
        Args:
            amendment_id (str): The unique identifier for the amendment
            amendment_data (dict): The amendment data to verify
            
        Returns:
            dict: Verification results including:
                - verified (bool): Whether the amendment passed verification
                - confidence (float): Confidence score (0-1)
                - suggestions (list): Any modification suggestions
                - reasoning (str): Reasoning for the verification outcome
        """
        if not self.secondary_llm:
            self.logger.warning("Secondary model not available for verification")
            return {"verified": True, "confidence": 0.5, "suggestions": [], "reasoning": "No verification performed (secondary model unavailable)"}
            
        self.logger.info(f"Verifying amendment {amendment_id} with secondary model")
        
        # Extract relevant information from the amendment
        standard_id = amendment_data.get('standard_id', 'unknown')
        title = amendment_data.get('title', 'Untitled')
        description = amendment_data.get('description', '')
        original_text = amendment_data.get('original_text', '')
        proposed_text = amendment_data.get('proposed_text', '')
        
        # Create verification prompt
        verification_prompt = f"""
        Please verify the following proposed amendment to AAOIFI standard {standard_id}:
        
        AMENDMENT TITLE: {title}
        
        DESCRIPTION: {description}
        
        ORIGINAL TEXT: {original_text}
        
        PROPOSED AMENDMENT: {proposed_text}
        
        Please evaluate this amendment on the following criteria:
        1. Shariah compliance: Is the amendment fully compliant with Islamic principles?
        2. Technical accuracy: Is the amendment technically sound and accurate?
        3. Practical applicability: Can the amendment be applied in real-world scenarios?
        4. Clarity: Is the amendment clearly worded and unambiguous?
        
        Provide your verification results, including:
        - Whether the amendment should be approved (Yes/No/With modifications)
        - Your confidence score (0-1)
        - Any suggested modifications
        - Your reasoning for the verification outcome
        """
        
        # TODO: Call the secondary model with this prompt and process the response
        # This is a placeholder for actual model call implementation
        verification_result = {
            "verified": True,
            "confidence": 0.85,
            "suggestions": ["Consider adding explicit reference to relevant Quranic verses or Hadiths"],
            "reasoning": "The amendment is fundamentally sound and Shariah-compliant, but would benefit from explicit textual references."
        }
        
        # Track verification step
        self.track_amendment_metadata(amendment_id, {
            "verification": f"Secondary model verification (confidence: {verification_result['confidence']})",
            "reasoning": verification_result['reasoning']
        })
        
        return verification_result