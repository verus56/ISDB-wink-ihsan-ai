from src.config.settings import OPENAI_API_KEY
import datetime
import json

class ComplianceCheckerAgent:
    def __init__(self, conversation_buffer=None, llm=None):
        self.name = "Compliance Checker Agent"
        self.conversation_buffer = conversation_buffer
        self.openai_api_key = OPENAI_API_KEY
        self.llm = llm  # Store the LLM model
        self.compliance_frameworks = self._load_compliance_frameworks()
        self.regulatory_requirements = self._load_regulatory_requirements()
        self.compliance_reasoning = []  # Track reasoning and citations
    
    def check_compliance(self, proposed_amendment):
        """
        Check if the proposed amendment aligns with Shariah principles and regulatory requirements.
        
        Args:
            proposed_amendment (dict): The proposed changes to be evaluated.
        
        Returns:
            dict: Comprehensive compliance evaluation results.
        """
        # Log the start of compliance checking
        if self.conversation_buffer:
            self.conversation_buffer.add_message(
                self.name, 
                f"Starting compliance evaluation for amendment: {proposed_amendment.get('id', 'Unnamed')}"
            )
        
        # Perform comprehensive compliance checks
        shariah_compliance = self._check_shariah_compliance(proposed_amendment)
        regulatory_compliance = self._check_regulatory_compliance(proposed_amendment)
        ethical_compliance = self._check_ethical_compliance(proposed_amendment)
        
        # Aggregate compliance results
        all_issues = []
        all_issues.extend(shariah_compliance.get('issues', []))
        all_issues.extend(regulatory_compliance.get('issues', []))
        all_issues.extend(ethical_compliance.get('issues', []))
        
        # Determine overall compliance status
        overall_compliance = True
        if (not shariah_compliance.get('compliant', False) or 
            not regulatory_compliance.get('compliant', False) or 
            not ethical_compliance.get('compliant', False)):
            overall_compliance = False
        
        # Generate comprehensive compliance results
        compliance_results = {
            'overall_compliant': overall_compliance,
            'shariah_compliance': shariah_compliance,
            'regulatory_compliance': regulatory_compliance,
            'ethical_compliance': ethical_compliance,
            'issues_count': len(all_issues),
            'issues': all_issues,
            'recommendations': self._generate_compliance_recommendations(all_issues),
            'evaluated_at': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Log the completion of compliance checking
        if self.conversation_buffer:
            status = "compliant" if overall_compliance else "non-compliant"
            self.conversation_buffer.add_message(
                self.name, 
                f"Compliance evaluation completed. Amendment is {status} with {len(all_issues)} issues identified."
            )
        
        return compliance_results
    
    def generate_compliance_report(self, proposed_amendment):
        """
        Generate a detailed report on the compliance status of the proposed amendment.
        
        Args:
            proposed_amendment (dict): The proposed changes to be evaluated.
        
        Returns:
            str: A comprehensive report summarizing the compliance evaluation.
        """
        # Get compliance evaluation results
        compliance_results = self.check_compliance(proposed_amendment)
        
        # Generate a detailed compliance report
        report = []
        report.append(f"# COMPLIANCE EVALUATION REPORT")
        report.append(f"## Amendment: {proposed_amendment.get('title', proposed_amendment.get('id', 'Unnamed'))}")
        report.append(f"## Date: {compliance_results['evaluated_at']}")
        report.append(f"\n### OVERALL COMPLIANCE STATUS: {'COMPLIANT' if compliance_results['overall_compliant'] else 'NON-COMPLIANT'}")
        
        # Shariah Compliance Section
        shariah = compliance_results['shariah_compliance']
        report.append(f"\n## 1. SHARIAH COMPLIANCE")
        report.append(f"Status: {'Compliant' if shariah['compliant'] else 'Non-Compliant'}")
        report.append(f"Score: {shariah['compliance_score']}/100")
        if shariah['issues']:
            report.append("\nIssues:")
            for issue in shariah['issues']:
                report.append(f"- {issue['description']} (Severity: {issue['severity']})")
        
        # Regulatory Compliance Section
        regulatory = compliance_results['regulatory_compliance']
        report.append(f"\n## 2. REGULATORY COMPLIANCE")
        report.append(f"Status: {'Compliant' if regulatory['compliant'] else 'Non-Compliant'}")
        report.append(f"Score: {regulatory['compliance_score']}/100")
        if regulatory['issues']:
            report.append("\nIssues:")
            for issue in regulatory['issues']:
                report.append(f"- {issue['description']} (Severity: {issue['severity']})")
        
        # Ethical Compliance Section
        ethical = compliance_results['ethical_compliance']
        report.append(f"\n## 3. ETHICAL COMPLIANCE")
        report.append(f"Status: {'Compliant' if ethical['compliant'] else 'Non-Compliant'}")
        report.append(f"Score: {ethical['compliance_score']}/100")
        if ethical['issues']:
            report.append("\nIssues:")
            for issue in ethical['issues']:
                report.append(f"- {issue['description']} (Severity: {issue['severity']})")
        
        # Recommendations Section
        report.append(f"\n## 4. RECOMMENDATIONS")
        if compliance_results['recommendations']:
            for i, recommendation in enumerate(compliance_results['recommendations'], 1):
                report.append(f"{i}. {recommendation}")
        else:
            report.append("No recommendations necessary.")
        
        # Final Summary
        report.append(f"\n## 5. CONCLUSION")
        if compliance_results['overall_compliant']:
            report.append("The proposed amendment is in compliance with Shariah principles, regulatory requirements, and ethical standards.")
        else:
            report.append("The proposed amendment requires modifications to fully comply with all standards. Please address the identified issues.")
        
        # Log report generation
        if self.conversation_buffer:
            self.conversation_buffer.add_message(
                self.name, 
                f"Generated compliance report for amendment: {proposed_amendment.get('id', 'Unnamed')}"
            )
        
        return "\n".join(report)
    
    def evaluate_risk_level(self, proposed_amendment):
        """
        Evaluate the risk level of implementing the proposed amendment.
        
        Args:
            proposed_amendment (dict): The proposed changes to be evaluated.
        
        Returns:
            dict: Risk assessment results.
        """
        # Perform risk assessment
        risk_areas = [
            self._assess_implementation_risk(proposed_amendment),
            self._assess_reputation_risk(proposed_amendment),
            self._assess_financial_risk(proposed_amendment),
            self._assess_legal_risk(proposed_amendment)
        ]
        
        # Calculate overall risk level (1-10)
        total_risk = sum(area['risk_level'] for area in risk_areas)
        average_risk = total_risk / len(risk_areas)
        
        # Determine risk category
        risk_category = "Low"
        if average_risk > 7:
            risk_category = "High"
        elif average_risk > 4:
            risk_category = "Medium"
        
        # Generate risk assessment results
        risk_assessment = {
            'overall_risk_level': round(average_risk, 1),
            'risk_category': risk_category,
            'risk_areas': risk_areas,
            'mitigating_actions': self._generate_risk_mitigations(risk_areas),
            'evaluated_at': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Log risk assessment
        if self.conversation_buffer:
            self.conversation_buffer.add_message(
                self.name, 
                f"Risk assessment completed for amendment: {proposed_amendment.get('id', 'Unnamed')}. Risk level: {risk_category}"
            )
        
        return risk_assessment
    
    def _load_compliance_frameworks(self):
        """
        Load compliance frameworks used for evaluating amendments.
        
        Returns:
            dict: Dictionary of compliance frameworks.
        """
        # In a production system, this would load from a database or file
        # Here we're creating a simple dictionary of frameworks
        return {
            "shariah": {
                "name": "AAOIFI Shariah Standards",
                "version": "2023",
                "principles": [
                    "Prohibition of riba (interest)",
                    "Avoidance of gharar (uncertainty)",
                    "Prohibition of maysir (gambling)",
                    "Profit and loss sharing",
                    "Asset-backing requirement",
                    "Ethical investment criteria"
                ]
            },
            "regulatory": {
                "name": "Islamic Financial Services Board (IFSB) Standards",
                "version": "2024",
                "principles": [
                    "Capital adequacy",
                    "Risk management",
                    "Corporate governance",
                    "Transparency and market discipline",
                    "Supervisory review process"
                ]
            },
            "ethical": {
                "name": "Islamic Finance Ethical Framework",
                "version": "2023",
                "principles": [
                    "Social responsibility",
                    "Environmental sustainability",
                    "Fair treatment of stakeholders",
                    "Transparency in operations",
                    "Avoidance of harmful activities"
                ]
            }
        }
    
    def _load_regulatory_requirements(self):
        """
        Load regulatory requirements for different jurisdictions.
        
        Returns:
            dict: Dictionary of regulatory requirements by jurisdiction.
        """
        # In a production system, this would load from a database or file
        # Here we're creating a simple dictionary of requirements
        return {
            "global": {
                "name": "Global Islamic Finance Standards",
                "requirements": [
                    "Shariah governance framework",
                    "Risk management framework",
                    "Transparency in financial reporting"
                ]
            },
            "middle_east": {
                "name": "Middle East Islamic Finance Regulations",
                "requirements": [
                    "Shariah supervisory board",
                    "Compliance with AAOIFI standards",
                    "Regular Shariah audits"
                ]
            },
            "southeast_asia": {
                "name": "Southeast Asian Islamic Finance Regulations",
                "requirements": [
                    "Compliance with local Shariah resolutions",
                    "Islamic financial product approval process",
                    "Separate funds for Islamic and conventional operations"
                ]
            },
            "europe": {
                "name": "European Islamic Finance Regulations",
                "requirements": [
                    "Compliance with EU banking regulations",
                    "Transparency in Shariah compliance",
                    "Customer protection measures"
                ]
            }
        }
    
    def _check_shariah_compliance(self, proposed_amendment):
        """
        Check if the amendment complies with Shariah principles.
        
        Args:
            proposed_amendment (dict): The proposed amendment to check.
            
        Returns:
            dict: Shariah compliance assessment results.
        """
        # In a production system, this would use NLP and other techniques
        # Here we're simulating a basic check
        
        # Extract key information from amendment
        title = proposed_amendment.get('title', '')
        content = proposed_amendment.get('content', '')
        rationale = proposed_amendment.get('rationale', '')
        
        # Simple keyword-based checks (for demonstration)
        issues = []
        
        # Check for riba-related issues
        if "interest" in content.lower() and not "prohibit interest" in content.lower():
            issues.append({
                "type": "shariah",
                "principle": "riba",
                "description": "Potential riba (interest) issue detected",
                "severity": "High"
            })
        
        # Check for gharar-related issues
        if "uncertain" in content.lower() and not "avoid uncertainty" in content.lower():
            issues.append({
                "type": "shariah",
                "principle": "gharar",
                "description": "Potential gharar (excessive uncertainty) issue detected",
                "severity": "Medium"
            })
        
        # Check for maysir-related issues
        if "speculation" in content.lower() and not "prohibit speculation" in content.lower():
            issues.append({
                "type": "shariah",
                "principle": "maysir",
                "description": "Potential maysir (gambling/speculation) issue detected",
                "severity": "High"
            })
        
        # Calculate compliance score (100 is perfect)
        compliance_score = 100
        for issue in issues:
            if issue['severity'] == "High":
                compliance_score -= 25
            elif issue['severity'] == "Medium":
                compliance_score -= 15
            else:
                compliance_score -= 5
        
        compliance_score = max(0, compliance_score)
        
        # Determine overall shariah compliance
        is_compliant = compliance_score >= 70 and not any(i['severity'] == "High" for i in issues)
        
        return {
            "compliant": is_compliant,
            "compliance_score": compliance_score,
            "issues": issues,
            "framework": self.compliance_frameworks["shariah"]["name"]
        }
    
    def _check_regulatory_compliance(self, proposed_amendment):
        """
        Check if the amendment complies with regulatory requirements.
        
        Args:
            proposed_amendment (dict): The proposed amendment to check.
            
        Returns:
            dict: Regulatory compliance assessment results.
        """
        # Extract key information from amendment
        jurisdiction = proposed_amendment.get('jurisdiction', 'global')
        content = proposed_amendment.get('content', '')
        
        # Get relevant regulatory requirements
        requirements = self.regulatory_requirements.get(
            jurisdiction, 
            self.regulatory_requirements['global']
        )['requirements']
        
        # Simple compliance check (for demonstration)
        issues = []
        
        # Check for capital adequacy issues
        if "capital" in content.lower() and not "adequate capital" in content.lower():
            issues.append({
                "type": "regulatory",
                "requirement": "capital adequacy",
                "description": "Potential capital adequacy compliance issue",
                "severity": "Medium"
            })
        
        # Check for risk management issues
        if "risk" in content.lower() and not "manage risk" in content.lower():
            issues.append({
                "type": "regulatory",
                "requirement": "risk management",
                "description": "Potential risk management compliance issue",
                "severity": "Low"
            })
        
        # Check for governance issues
        if "governance" in content.lower() and not "proper governance" in content.lower():
            issues.append({
                "type": "regulatory",
                "requirement": "corporate governance",
                "description": "Potential corporate governance compliance issue",
                "severity": "Medium"
            })
        
        # Calculate compliance score (100 is perfect)
        compliance_score = 100
        for issue in issues:
            if issue['severity'] == "High":
                compliance_score -= 25
            elif issue['severity'] == "Medium":
                compliance_score -= 15
            else:
                compliance_score -= 5
        
        compliance_score = max(0, compliance_score)
        
        # Determine overall regulatory compliance
        is_compliant = compliance_score >= 80 and not any(i['severity'] == "High" for i in issues)
        
        return {
            "compliant": is_compliant,
            "compliance_score": compliance_score,
            "issues": issues,
            "framework": f"Regulatory Framework: {self.regulatory_requirements.get(jurisdiction, self.regulatory_requirements['global'])['name']}"
        }
    
    def _check_ethical_compliance(self, proposed_amendment):
        """
        Check if the amendment complies with ethical standards.
        
        Args:
            proposed_amendment (dict): The proposed amendment to check.
            
        Returns:
            dict: Ethical compliance assessment results.
        """
        # Extract content from amendment
        content = proposed_amendment.get('content', '')
        rationale = proposed_amendment.get('rationale', '')
        
        # Simple ethical check (for demonstration)
        issues = []
        
        # Check for social responsibility issues
        if "community" in content.lower() and not "benefit community" in content.lower():
            issues.append({
                "type": "ethical",
                "principle": "social responsibility",
                "description": "Potential issue with social responsibility considerations",
                "severity": "Medium"
            })
        
        # Check for environmental issues
        if "environment" in content.lower() and not "protect environment" in content.lower():
            issues.append({
                "type": "ethical",
                "principle": "environmental sustainability",
                "description": "Potential issue with environmental sustainability considerations",
                "severity": "Low"
            })
        
        # Calculate compliance score (100 is perfect)
        compliance_score = 100
        for issue in issues:
            if issue['severity'] == "High":
                compliance_score -= 25
            elif issue['severity'] == "Medium":
                compliance_score -= 10
            else:
                compliance_score -= 5
        
        compliance_score = max(0, compliance_score)
        
        # Determine overall ethical compliance
        is_compliant = compliance_score >= 75
        
        return {
            "compliant": is_compliant,
            "compliance_score": compliance_score,
            "issues": issues,
            "framework": self.compliance_frameworks["ethical"]["name"]
        }
    
    def _generate_compliance_recommendations(self, issues):
        """
        Generate recommendations to address compliance issues.
        
        Args:
            issues (list): List of identified compliance issues.
            
        Returns:
            list: Recommendations to address issues.
        """
        recommendations = []
        
        # Generate recommendations based on issue types
        shariah_issues = [i for i in issues if i.get('type') == 'shariah']
        regulatory_issues = [i for i in issues if i.get('type') == 'regulatory']
        ethical_issues = [i for i in issues if i.get('type') == 'ethical']
        
        # Recommendations for shariah issues
        if any(i for i in shariah_issues if i.get('principle') == 'riba'):
            recommendations.append(
                "Remove all interest-based elements and replace with profit-sharing mechanisms."
            )
        
        if any(i for i in shariah_issues if i.get('principle') == 'gharar'):
            recommendations.append(
                "Increase clarity and specificity in contractual terms to eliminate uncertainty."
            )
        
        if any(i for i in shariah_issues if i.get('principle') == 'maysir'):
            recommendations.append(
                "Remove speculative elements and ensure all transactions are asset-backed."
            )
        
        # Recommendations for regulatory issues
        if regulatory_issues:
            recommendations.append(
                "Review the amendment with a regulatory compliance officer to ensure alignment with current regulations."
            )
        
        # Recommendations for ethical issues
        if ethical_issues:
            recommendations.append(
                "Enhance social and environmental responsibility aspects of the amendment."
            )
        
        # General recommendation if there are any issues
        if issues:
            recommendations.append(
                "Conduct a formal Shariah board review of the amendment before implementation."
            )
        
        return recommendations
    
    def _assess_implementation_risk(self, proposed_amendment):
        """
        Assess implementation risk of the amendment.
        
        Args:
            proposed_amendment (dict): The proposed amendment.
            
        Returns:
            dict: Risk assessment results.
        """
        # Simple implementation risk assessment (for demonstration)
        risk_level = 3  # Default medium-low risk
        
        # Increase risk level based on amendment complexity
        complexity = proposed_amendment.get('complexity', 'low')
        if complexity == 'high':
            risk_level += 3
        elif complexity == 'medium':
            risk_level += 1
        
        # Cap risk level at 10
        risk_level = min(10, risk_level)
        
        return {
            "risk_area": "Implementation",
            "risk_level": risk_level,
            "factors": ["Complexity", "System integration", "Staff training needs"]
        }
    
    def _assess_reputation_risk(self, proposed_amendment):
        """
        Assess reputation risk of the amendment.
        
        Args:
            proposed_amendment (dict): The proposed amendment.
            
        Returns:
            dict: Risk assessment results.
        """
        # Simple reputation risk assessment (for demonstration)
        risk_level = 2  # Default low risk
        
        # Increase risk for controversial amendments
        content = proposed_amendment.get('content', '').lower()
        if 'controversial' in content:
            risk_level += 4
        
        # Cap risk level at 10
        risk_level = min(10, risk_level)
        
        return {
            "risk_area": "Reputation",
            "risk_level": risk_level,
            "factors": ["Public perception", "Stakeholder acceptance", "Media coverage"]
        }
    
    def _assess_financial_risk(self, proposed_amendment):
        """
        Assess financial risk of the amendment.
        
        Args:
            proposed_amendment (dict): The proposed amendment.
            
        Returns:
            dict: Risk assessment results.
        """
        # Simple financial risk assessment (for demonstration)
        risk_level = 4  # Default medium risk
        
        # Adjust based on financial impact
        financial_impact = proposed_amendment.get('financial_impact', 'low')
        if financial_impact == 'high':
            risk_level += 3
        elif financial_impact == 'medium':
            risk_level += 1
        
        # Cap risk level at 10
        risk_level = min(10, risk_level)
        
        return {
            "risk_area": "Financial",
            "risk_level": risk_level,
            "factors": ["Implementation costs", "Revenue impact", "Asset valuation changes"]
        }
    
    def _assess_legal_risk(self, proposed_amendment):
        """
        Assess legal risk of the amendment.
        
        Args:
            proposed_amendment (dict): The proposed amendment.
            
        Returns:
            dict: Risk assessment results.
        """
        # Simple legal risk assessment (for demonstration)
        risk_level = 3  # Default medium-low risk
        
        # Adjust based on regulatory changes
        content = proposed_amendment.get('content', '').lower()
        if 'regulation' in content or 'legal' in content:
            risk_level += 2
        
        # Cap risk level at 10
        risk_level = min(10, risk_level)
        
        return {
            "risk_area": "Legal",
            "risk_level": risk_level,
            "factors": ["Regulatory compliance", "Contract enforceability", "Dispute resolution"]
        }
    
    def _generate_risk_mitigations(self, risk_areas):
        """
        Generate risk mitigation strategies based on identified risks.
        
        Args:
            risk_areas (list): List of risk areas with assessments.
            
        Returns:
            list: Risk mitigation strategies.
        """
        mitigations = []
        
        for area in risk_areas:
            if area['risk_level'] >= 7:
                if area['risk_area'] == 'Implementation':
                    mitigations.append("Develop a detailed implementation plan with phased rollout approach.")
                elif area['risk_area'] == 'Reputation':
                    mitigations.append("Engage stakeholders early and develop a communication strategy.")
                elif area['risk_area'] == 'Financial':
                    mitigations.append("Conduct detailed financial impact analysis and prepare contingency funds.")
                elif area['risk_area'] == 'Legal':
                    mitigations.append("Obtain legal opinions from multiple jurisdictions and prepare for regulatory changes.")
        
        # Add general mitigation if high risks exist
        if any(area['risk_level'] >= 7 for area in risk_areas):
            mitigations.append("Establish a cross-functional risk management committee to monitor implementation.")
        
        return mitigations