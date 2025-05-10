import datetime
import logging
import uuid
from src.config.settings import OPENAI_API_KEY

class StandardsReviewerAgent:
    def __init__(self, conversation_buffer=None, llm=None):
        self.name = "Standards Reviewer Agent"
        self.conversation_buffer = conversation_buffer
        self.openai_api_key = OPENAI_API_KEY
        self.llm = llm  # Store the LLM model
        self.evaluation_criteria = self._load_evaluation_criteria()
        self.industry_trends = self._load_industry_trends()
        self.recent_regulations = self._load_recent_regulations()
        self.reasoning_log = []  # Track reasoning and sources
        
        # Configure logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger("StandardsReviewerAgent")

    def analyze_standards(self, standards_data):
        """
        Analyze existing AAOIFI standards and identify areas for enhancement.
        
        Args:
            standards_data (list): List of standard dictionaries to analyze
            
        Returns:
            list: List of enhancement opportunities
        """
        if not standards_data:
            self._add_to_conversation("No standards provided for analysis")
            return []
            
        self._add_to_conversation(f"Beginning analysis of {len(standards_data)} standards")
        
        enhancements = []
        for standard in standards_data:
            # Check if the standard meets our criteria for needing improvement
            if self.needs_improvement(standard):
                # Get the specific enhancements suggested for this standard
                standard_enhancements = self.suggest_enhancement(standard)
                
                # Add each enhancement to the list with a unique ID
                for enhancement in standard_enhancements:
                    enhancement_id = str(uuid.uuid4())[:8]  # Generate a short unique ID
                    enhancement['id'] = enhancement_id
                    enhancement['standard_id'] = standard.get('id', 'unknown')
                    enhancement['standard_name'] = standard.get('name', 'Unnamed Standard')
                    enhancement['identified_at'] = datetime.datetime.now().strftime("%Y-%m-%d")
                    
                    enhancements.append(enhancement)
                    
                    # Log the enhancement
                    self._add_to_conversation(
                        f"Enhancement identified for standard '{standard.get('name', 'Unnamed')}': "
                        f"{enhancement.get('title', 'Untitled enhancement')}"
                    )
        
        self._add_to_conversation(f"Analysis complete. {len(enhancements)} enhancement opportunities identified")
        return enhancements

    def needs_improvement(self, standard):
        """
        Determine if a standard needs improvement based on various criteria.
        
        Args:
            standard (dict): The standard to evaluate
            
        Returns:
            bool: True if the standard needs improvement, False otherwise
        """
        # Extract standard content and metadata
        content = standard.get('content', '')
        standard_id = standard.get('id', '')
        
        # Skip standards that are explicitly marked as not needing review
        if standard.get('no_review_needed', False):
            self._add_to_conversation(f"Standard {standard_id} is marked as not needing review")
            return False
            
        # Always evaluate if it's a placeholder
        if standard_id == 'placeholder':
            return True
            
        # Check for criteria that indicate a need for improvement
        improvement_needed = False
        reasons = []
        
        # 1. Check for clarity issues
        clarity_score = self._evaluate_clarity(content)
        if clarity_score < 7:  # On a scale of 1-10
            improvement_needed = True
            reasons.append(f"Clarity issues detected (score: {clarity_score}/10)")
            
        # 2. Check for coverage gaps
        coverage_gaps = self._identify_coverage_gaps(standard)
        if coverage_gaps:
            improvement_needed = True
            reasons.append(f"Coverage gaps identified: {', '.join(coverage_gaps)}")
            
        # 3. Check for alignment with industry trends
        trend_alignment = self._check_trend_alignment(standard)
        if not trend_alignment.get('aligned', True):
            improvement_needed = True
            reasons.append(f"Not aligned with industry trends: {trend_alignment.get('details', '')}")
            
        # 4. Check for regulatory conflicts
        regulatory_conflicts = self._check_regulatory_alignment(standard)
        if regulatory_conflicts:
            improvement_needed = True
            reasons.append(f"Potential regulatory conflicts: {', '.join(regulatory_conflicts)}")
            
        # 5. Check for implementation challenges
        implementation_issues = self._identify_implementation_issues(standard)
        if implementation_issues:
            improvement_needed = True
            reasons.append(f"Implementation challenges: {', '.join(implementation_issues)}")
        
        # Log the evaluation outcome
        if improvement_needed:
            self._add_to_conversation(
                f"Standard '{standard.get('name', 'Unnamed')}' needs improvement. "
                f"Reasons: {'; '.join(reasons)}"
            )
        else:
            self._add_to_conversation(
                f"Standard '{standard.get('name', 'Unnamed')}' meets current evaluation criteria"
            )
            
        return improvement_needed

    def suggest_enhancement(self, standard):
        """
        Suggest specific enhancements for a standard that needs improvement.
        
        Args:
            standard (dict): The standard to enhance
            
        Returns:
            list: List of enhancement dictionaries
        """
        standard_id = standard.get('id', 'unknown')
        standard_name = standard.get('name', 'Unnamed Standard')
        content = standard.get('content', '')
        
        self._add_to_conversation(f"Generating enhancement suggestions for standard: {standard_name}")
        
        enhancements = []
        
        # 1. Check for clarity improvements
        clarity_score = self._evaluate_clarity(content)
        if clarity_score < 7:
            enhancement = {
                'title': f"Improve Clarity of {standard_name}",
                'type': 'clarity_improvement',
                'description': self._generate_clarity_enhancement(standard),
                'rationale': f"The current standard scores {clarity_score}/10 on clarity metrics. "
                            f"Improved wording and structure will reduce misinterpretation risks.",
                'priority': 'high' if clarity_score < 5 else 'medium'
            }
            enhancements.append(enhancement)
        
        # 2. Identify coverage gaps and suggest additions
        coverage_gaps = self._identify_coverage_gaps(standard)
        if coverage_gaps:
            for gap in coverage_gaps:
                enhancement = {
                    'title': f"Address {gap} in {standard_name}",
                    'type': 'coverage_expansion',
                    'description': self._generate_coverage_enhancement(standard, gap),
                    'rationale': f"The current standard lacks adequate coverage of {gap}, "
                                f"which is essential for comprehensive guidance.",
                    'priority': 'high'
                }
                enhancements.append(enhancement)
        
        # 3. Align with current industry trends
        trend_alignment = self._check_trend_alignment(standard)
        if not trend_alignment.get('aligned', True):
            enhancement = {
                'title': f"Align {standard_name} with Current Industry Trends",
                'type': 'trend_alignment',
                'description': self._generate_trend_alignment_enhancement(
                    standard, trend_alignment.get('misaligned_trends', [])
                ),
                'rationale': trend_alignment.get('details', 'Standard requires updating to reflect current market practices.'),
                'priority': 'medium'
            }
            enhancements.append(enhancement)
        
        # 4. Address regulatory conflicts
        regulatory_conflicts = self._check_regulatory_alignment(standard)
        if regulatory_conflicts:
            enhancement = {
                'title': f"Resolve Regulatory Conflicts in {standard_name}",
                'type': 'regulatory_alignment',
                'description': self._generate_regulatory_alignment_enhancement(standard, regulatory_conflicts),
                'rationale': f"The standard contains elements that may conflict with {len(regulatory_conflicts)} "
                            f"recent regulatory developments.",
                'priority': 'critical'
            }
            enhancements.append(enhancement)
        
        # 5. Address implementation challenges
        implementation_issues = self._identify_implementation_issues(standard)
        if implementation_issues:
            enhancement = {
                'title': f"Improve Implementability of {standard_name}",
                'type': 'implementation_improvement',
                'description': self._generate_implementation_enhancement(standard, implementation_issues),
                'rationale': f"Stakeholders face challenges implementing this standard due to "
                            f"{len(implementation_issues)} identified practical issues.",
                'priority': 'high'
            }
            enhancements.append(enhancement)
        
        # 6. For placeholder standards, suggest comprehensive development
        if standard_id == 'placeholder':
            enhancement = self._generate_placeholder_enhancement(standard)
            enhancements.append(enhancement)
        
        self._add_to_conversation(f"Generated {len(enhancements)} enhancement suggestions for {standard_name}")
        return enhancements

    def generate_report(self, enhancements):
        """
        Generate a comprehensive report of the suggested enhancements.
        
        Args:
            enhancements (list): List of enhancement dictionaries
            
        Returns:
            str: A formatted report of enhancement opportunities
        """
        if not enhancements:
            return "# AAOIFI Standards Enhancement Report\n\nNo enhancement opportunities identified at this time."
        
        # Count enhancements by type and priority
        enhancement_types = {}
        priority_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        standards_affected = set()
        
        for enhancement in enhancements:
            enhancement_type = enhancement.get('type', 'other')
            priority = enhancement.get('priority', 'medium')
            standard_id = enhancement.get('standard_id', 'unknown')
            
            if enhancement_type in enhancement_types:
                enhancement_types[enhancement_type] += 1
            else:
                enhancement_types[enhancement_type] = 1
                
            priority_counts[priority] += 1
            standards_affected.add(standard_id)
        
        # Generate the report
        report = [
            "# AAOIFI Standards Enhancement Report",
            f"## Date: {datetime.datetime.now().strftime('%Y-%m-%d')}",
            f"\n## Executive Summary",
            f"This analysis identified {len(enhancements)} enhancement opportunities across {len(standards_affected)} standards.",
            f"Critical priority items: {priority_counts['critical']}",
            f"High priority items: {priority_counts['high']}",
            f"Medium priority items: {priority_counts['medium']}",
            f"Low priority items: {priority_counts['low']}",
            
            f"\n## Enhancement Opportunities by Type",
        ]
        
        # List enhancement types
        for enhancement_type, count in enhancement_types.items():
            report.append(f"- {enhancement_type.replace('_', ' ').title()}: {count}")
        
        # Group enhancements by priority
        report.append("\n## Enhancement Details")
        
        # First list critical priority items
        if priority_counts['critical'] > 0:
            report.append("\n### Critical Priority")
            for enhancement in enhancements:
                if enhancement.get('priority') == 'critical':
                    report.append(self._format_enhancement_for_report(enhancement))
        
        # Then high priority items
        if priority_counts['high'] > 0:
            report.append("\n### High Priority")
            for enhancement in enhancements:
                if enhancement.get('priority') == 'high':
                    report.append(self._format_enhancement_for_report(enhancement))
        
        # Then medium priority items
        if priority_counts['medium'] > 0:
            report.append("\n### Medium Priority")
            for enhancement in enhancements:
                if enhancement.get('priority') == 'medium':
                    report.append(self._format_enhancement_for_report(enhancement))
        
        # Finally low priority items
        if priority_counts['low'] > 0:
            report.append("\n### Low Priority")
            for enhancement in enhancements:
                if enhancement.get('priority') == 'low':
                    report.append(self._format_enhancement_for_report(enhancement))
        
        # Add recommendations section
        report.append("\n## Recommendations")
        report.append(self._generate_overall_recommendations(enhancements))
        
        # Add implementation roadmap
        report.append("\n## Implementation Roadmap")
        report.append(self._generate_implementation_roadmap(enhancements))
        
        self._add_to_conversation("Generated comprehensive enhancement report")
        return "\n".join(report)
        
    def rate_enhancement_priority(self, enhancement, standard_impact_factors):
        """
        Rate the priority of an enhancement based on various factors.
        
        Args:
            enhancement (dict): The enhancement to rate
            standard_impact_factors (dict): Impact factors for the standard
            
        Returns:
            str: Priority level ('critical', 'high', 'medium', or 'low')
        """
        # Default to medium priority
        priority = 'medium'
        
        # Get enhancement type
        enhancement_type = enhancement.get('type', '')
        
        # Regulatory alignment issues are always critical
        if enhancement_type == 'regulatory_alignment':
            priority = 'critical'
            
        # Clarity improvements are high priority if the clarity score is very low
        elif enhancement_type == 'clarity_improvement':
            clarity_score = standard_impact_factors.get('clarity_score', 5)
            if clarity_score < 4:
                priority = 'high'
            elif clarity_score < 7:
                priority = 'medium'
            else:
                priority = 'low'
                
        # Coverage expansions are generally high priority
        elif enhancement_type == 'coverage_expansion':
            priority = 'high'
            
        # Implementation improvements depend on the severity of the issues
        elif enhancement_type == 'implementation_improvement':
            implementation_issues = standard_impact_factors.get('implementation_issues', [])
            if len(implementation_issues) > 3:
                priority = 'high'
            else:
                priority = 'medium'
                
        # Trend alignments are generally medium priority
        elif enhancement_type == 'trend_alignment':
            priority = 'medium'
            
        return priority

    def _load_evaluation_criteria(self):
        """
        Load the evaluation criteria for standards review.
        
        Returns:
            dict: Dictionary of evaluation criteria
        """
        # In a production environment, this would load from a database or file
        return {
            "clarity": {
                "description": "Standard language should be clear, concise, and unambiguous",
                "metrics": ["readability", "technical precision", "structural organization"]
            },
            "coverage": {
                "description": "Standard should address all relevant aspects of the topic",
                "areas": [
                    "definition of terms", 
                    "scope and applicability", 
                    "implementation guidance",
                    "edge cases and exceptions",
                    "compliance assessment",
                    "interaction with other standards"
                ]
            },
            "industry_alignment": {
                "description": "Standard should reflect current industry practices and trends",
                "considerations": [
                    "digital transformation", 
                    "sustainable finance", 
                    "cross-border transactions", 
                    "emerging market needs"
                ]
            },
            "regulatory_compliance": {
                "description": "Standard should align with relevant regulatory frameworks",
                "jurisdictions": ["global", "middle_east", "southeast_asia", "europe"]
            },
            "implementability": {
                "description": "Standard should be practical to implement",
                "factors": [
                    "technical feasibility", 
                    "resource requirements", 
                    "transition timeline", 
                    "verification mechanisms"
                ]
            }
        }
        
    def _load_industry_trends(self):
        """
        Load current industry trends for evaluating standard alignment.
        
        Returns:
            dict: Dictionary of relevant industry trends
        """
        # In a production environment, this would load from a database or API
        return {
            "digital_transformation": {
                "name": "Digital Transformation in Islamic Finance",
                "description": "Adoption of digital technologies in Islamic finance operations",
                "examples": [
                    "Smart contracts for Sukuk issuance",
                    "Blockchain-based Islamic banking services",
                    "Digital Zakat collection and distribution platforms",
                    "AI-powered Shariah compliance verification"
                ],
                "relevance": "High"
            },
            "sustainable_finance": {
                "name": "Sustainable and Ethical Finance Integration",
                "description": "Alignment of Islamic finance with sustainability principles",
                "examples": [
                    "Green Sukuk frameworks",
                    "ESG integration in Islamic investment screening",
                    "Sustainable development goals (SDG) alignment metrics",
                    "Climate risk assessment for Islamic financial institutions"
                ],
                "relevance": "High"
            },
            "financial_inclusion": {
                "name": "Financial Inclusion Initiatives",
                "description": "Expanding Islamic financial services to underserved populations",
                "examples": [
                    "Microfinance products compliant with Shariah principles",
                    "Mobile Islamic banking solutions for rural areas",
                    "Simplified KYC for basic Islamic financial products",
                    "Cooperative Islamic finance models for communities"
                ],
                "relevance": "Medium"
            },
            "cross_border_standardization": {
                "name": "Cross-Border Standardization",
                "description": "Harmonization of Islamic finance standards across jurisdictions",
                "examples": [
                    "Standardized Sukuk documentation",
                    "Common Shariah compliance frameworks",
                    "Mutual recognition of Islamic finance certifications",
                    "Global Islamic liquidity management standards"
                ],
                "relevance": "High"
            },
            "product_innovation": {
                "name": "Islamic Financial Product Innovation",
                "description": "Development of new Shariah-compliant financial products",
                "examples": [
                    "Islamic fintech products",
                    "Hybrid Sukuk structures",
                    "Shariah-compliant derivatives alternatives",
                    "Islamic wealth management solutions"
                ],
                "relevance": "Medium"
            }
        }
        
    def _load_recent_regulations(self):
        """
        Load recent regulatory developments relevant to Islamic finance standards.
        
        Returns:
            dict: Dictionary of recent regulatory developments
        """
        # In a production environment, this would load from a regulatory database
        return {
            "basel_iv": {
                "name": "Basel IV Implementation",
                "description": "Capital requirements and risk management standards",
                "issued_by": "Bank for International Settlements",
                "regions_affected": ["global"],
                "effective_date": "2023-01-01",
                "relevance": "High"
            },
            "ifrs_17": {
                "name": "IFRS 17 Insurance Contracts",
                "description": "Accounting standard for insurance contracts",
                "issued_by": "International Accounting Standards Board",
                "regions_affected": ["global"],
                "effective_date": "2023-01-01",
                "relevance": "Medium"
            },
            "eu_sfdr": {
                "name": "Sustainable Finance Disclosure Regulation",
                "description": "ESG disclosure requirements for financial products",
                "issued_by": "European Union",
                "regions_affected": ["europe"],
                "effective_date": "2021-03-10",
                "relevance": "Medium"
            },
            "malaysia_vbi": {
                "name": "Value-based Intermediation",
                "description": "Framework for Islamic financial institutions to deliver sustainable impact",
                "issued_by": "Bank Negara Malaysia",
                "regions_affected": ["southeast_asia"],
                "effective_date": "2021-01-01",
                "relevance": "High"
            },
            "gcc_digital_banking": {
                "name": "Digital Banking Regulations",
                "description": "Regulatory framework for digital banking operations",
                "issued_by": "Various GCC Central Banks",
                "regions_affected": ["middle_east"],
                "effective_date": "2022-06-01",
                "relevance": "High"
            }
        }

    def _evaluate_clarity(self, content):
        """
        Evaluate the clarity of a standard's content.
        
        Args:
            content (str): The content to evaluate
            
        Returns:
            int: Clarity score from 1-10 (10 being most clear)
        """
        # In a production environment, this would use NLP techniques
        # For this implementation, we'll use simple heuristics
        
        if not content:
            return 0
            
        # Simple clarity evaluation based on text length, sentence complexity, etc.
        score = 7  # Default score
        
        # Reduce score for very short or very long content
        if len(content) < 100:
            score -= 2
        elif len(content) > 10000:
            score -= 1
            
        # Check for potential clarity issues using keyword indicators
        clarity_issue_indicators = [
            "may", "might", "could", "should consider", "possibly", 
            "in certain cases", "under specific circumstances"
        ]
        
        # Count vague language instances
        vagueness_count = sum(content.lower().count(indicator) for indicator in clarity_issue_indicators)
        
        # Reduce score based on the number of vague terms
        if vagueness_count > 20:
            score -= 3
        elif vagueness_count > 10:
            score -= 2
        elif vagueness_count > 5:
            score -= 1
            
        # Ensure score is within bounds
        return max(1, min(10, score))

    def _identify_coverage_gaps(self, standard):
        """
        Identify coverage gaps in a standard.
        
        Args:
            standard (dict): The standard to analyze
            
        Returns:
            list: List of identified coverage gaps
        """
        # Extract standard information
        content = standard.get('content', '').lower()
        standard_name = standard.get('name', '').lower()
        
        # Common areas that should be covered in comprehensive standards
        required_coverage_areas = [
            "definitions",
            "scope",
            "implementation guidance",
            "compliance assessment",
            "effective date",
            "related standards"
        ]
        
        # Check for specific coverage based on the standard topic
        if "sukuk" in standard_name or "sukuk" in content:
            required_coverage_areas.extend([
                "sukuk types",
                "asset ownership",
                "risk transfer",
                "tradability conditions",
                "investor protection"
            ])
            
        elif "takaful" in standard_name or "takaful" in content:
            required_coverage_areas.extend([
                "risk sharing mechanism",
                "surplus distribution",
                "retakaful guidelines",
                "claim handling",
                "investment guidelines"
            ])
            
        elif "mudaraba" in standard_name or "mudaraba" in content:
            required_coverage_areas.extend([
                "capital protection",
                "profit distribution",
                "loss allocation",
                "termination conditions",
                "expense management"
            ])
            
        elif "murabaha" in standard_name or "murabaha" in content:
            required_coverage_areas.extend([
                "cost disclosure",
                "asset possession",
                "pricing methodology",
                "default management",
                "early settlement"
            ])
        
        # Check which required areas are missing
        gaps = []
        for area in required_coverage_areas:
            area_keywords = area.replace('_', ' ').split()
            
            # Consider the area covered if any keyword is present
            if not any(keyword in content for keyword in area_keywords):
                gaps.append(area.replace('_', ' '))
                
        return gaps

    def _check_trend_alignment(self, standard):
        """
        Check alignment of a standard with current industry trends.
        
        Args:
            standard (dict): The standard to analyze
            
        Returns:
            dict: Alignment assessment
        """
        content = standard.get('content', '').lower()
        standard_name = standard.get('name', '').lower()
        
        # Determine relevant trends for this standard
        relevant_trends = []
        misaligned_trends = []
        
        for trend_key, trend_info in self.industry_trends.items():
            # Check if the trend is potentially relevant to this standard
            trend_relevant = False
            
            # Check for topic relevance
            trend_name = trend_info['name'].lower()
            if any(word in standard_name for word in trend_name.split()):
                trend_relevant = True
                
            # Check examples for relevance
            for example in trend_info['examples']:
                example_keywords = [word.lower() for word in example.split() if len(word) > 4]
                if any(keyword in content for keyword in example_keywords):
                    trend_relevant = True
                    break
                    
            # If trend is relevant, check for alignment
            if trend_relevant:
                relevant_trends.append(trend_key)
                
                # Check if the standard addresses this trend
                trend_keywords = trend_info['name'].lower().split() + trend_info['description'].lower().split()
                trend_keywords = [word for word in trend_keywords if len(word) > 4 and word not in ['with', 'that', 'this', 'have', 'from']]
                
                # If few trend keywords are found, consider it misaligned
                keyword_matches = sum(content.count(keyword) for keyword in trend_keywords)
                if keyword_matches < 2:
                    misaligned_trends.append({
                        'trend': trend_info['name'],
                        'description': trend_info['description'],
                        'examples': trend_info['examples']
                    })
        
        # If no relevant trends, default to aligned
        if not relevant_trends:
            return {'aligned': True, 'relevant_trends': [], 'misaligned_trends': []}
            
        # Determine overall alignment
        is_aligned = len(misaligned_trends) < len(relevant_trends) / 2
        
        return {
            'aligned': is_aligned,
            'relevant_trends': [self.industry_trends[t]['name'] for t in relevant_trends],
            'misaligned_trends': misaligned_trends,
            'details': f"Standard is {'aligned' if is_aligned else 'not aligned'} with "
                      f"{len(relevant_trends) - len(misaligned_trends)} of {len(relevant_trends)} relevant trends."
        }

    def _check_regulatory_alignment(self, standard):
        """
        Check for potential conflicts with recent regulatory developments.
        
        Args:
            standard (dict): The standard to analyze
            
        Returns:
            list: List of potential regulatory conflicts
        """
        content = standard.get('content', '').lower()
        conflicts = []
        
        for reg_key, regulation in self.recent_regulations.items():
            reg_name = regulation['name'].lower()
            reg_description = regulation['description'].lower()
            
            # Check if the regulation is relevant to this standard
            reg_keywords = reg_name.split() + reg_description.split()
            reg_keywords = [word for word in reg_keywords if len(word) > 4 and word not in ['with', 'that', 'this', 'have', 'from']]
            
            # If keywords are found, check for potential conflicts
            if any(keyword in content for keyword in reg_keywords):
                # For a real implementation, this would involve more sophisticated analysis
                # Here we'll check if the standard mentions the regulation but doesn't fully address it
                
                if regulation['name'].lower() not in content and regulation['issued_by'].lower() not in content:
                    conflicts.append(
                        f"{regulation['name']} ({regulation['issued_by']})"
                    )
        
        return conflicts

    def _identify_implementation_issues(self, standard):
        """
        Identify potential implementation challenges in a standard.
        
        Args:
            standard (dict): The standard to analyze
            
        Returns:
            list: List of implementation issues
        """
        content = standard.get('content', '').lower()
        issues = []
        
        # Check for common implementation challenge indicators
        implementation_challenge_indicators = {
            "complex technical requirements": [
                "sophisticated", "advanced", "complex", "technical expertise"
            ],
            "resource intensive processes": [
                "substantial resources", "significant investment", "costly", "resource intensive"
            ],
            "lack of detailed guidance": [
                "general principles", "broad guidelines", "high-level"
            ],
            "challenging timelines": [
                "immediate implementation", "rapid adoption", "quick transition"
            ],
            "operational difficulties": [
                "operational challenges", "systems changes", "process reengineering"
            ],
            "market infrastructure gaps": [
                "market infrastructure", "ecosystem development", "supporting framework"
            ]
        }
        
        # Check for each implementation challenge
        for issue, indicators in implementation_challenge_indicators.items():
            if any(indicator in content for indicator in indicators):
                issues.append(issue)
        
        # If it's a placeholder or very short content, add specific issues
        if standard.get('id') == 'placeholder' or len(content) < 200:
            issues.append("insufficient implementation detail")
            issues.append("lack of practical examples")
            
        return issues

    def _generate_clarity_enhancement(self, standard):
        """
        Generate a description for a clarity enhancement.
        
        Args:
            standard (dict): The standard to enhance
            
        Returns:
            str: Enhancement description
        """
        standard_name = standard.get('name', 'Unnamed Standard')
        
        enhancement = (
            f"Revise the language and structure of the '{standard_name}' standard to improve clarity "
            f"and reduce ambiguity. Specifically:\n\n"
            f"1. Replace vague terms ('may', 'might', 'could') with definitive language\n"
            f"2. Add precise definitions for all technical terms\n"
            f"3. Restructure content with clear section hierarchies and numbering\n"
            f"4. Include flowcharts and decision trees for complex processes\n"
            f"5. Provide concrete examples demonstrating the application of principles\n"
            f"6. Add a glossary of terms with precise definitions\n"
            f"7. Standardize terminology throughout the document"
        )
        
        return enhancement

    def _generate_coverage_enhancement(self, standard, gap):
        """
        Generate a description for a coverage gap enhancement.
        
        Args:
            standard (dict): The standard to enhance
            gap (str): The identified coverage gap
            
        Returns:
            str: Enhancement description
        """
        standard_name = standard.get('name', 'Unnamed Standard')
        
        enhancement = (
            f"Expand the '{standard_name}' standard to address the current gap in guidance regarding '{gap}'. "
            f"The enhancement should:\n\n"
            f"1. Add a dedicated section covering '{gap}'\n"
            f"2. Provide clear principles and guidelines specific to '{gap}'\n"
            f"3. Include practical examples demonstrating application\n"
            f"4. Address common scenarios and edge cases related to '{gap}'\n"
            f"5. Align the new content with existing sections\n"
            f"6. Update the table of contents and index accordingly\n"
            f"7. Include cross-references to related standards or sections"
        )
        
        return enhancement

    def _generate_trend_alignment_enhancement(self, standard, misaligned_trends):
        """
        Generate a description for a trend alignment enhancement.
        
        Args:
            standard (dict): The standard to enhance
            misaligned_trends (list): List of trends the standard is not aligned with
            
        Returns:
            str: Enhancement description
        """
        standard_name = standard.get('name', 'Unnamed Standard')
        
        if not misaligned_trends:
            return f"Update the '{standard_name}' standard to align with current industry trends."
            
        enhancement = [f"Update the '{standard_name}' standard to align with the following current industry trends:"]
        
        for i, trend in enumerate(misaligned_trends, 1):
            trend_name = trend.get('trend', 'Unnamed trend')
            trend_examples = trend.get('examples', [])
            
            enhancement.append(f"\n{i}. {trend_name}")
            enhancement.append(f"   Description: {trend.get('description', '')}")
            
            if trend_examples:
                enhancement.append("   Examples to incorporate:")
                for example in trend_examples:
                    enhancement.append(f"   - {example}")
                    
        enhancement.append("\nRecommended approach:")
        enhancement.append("1. Review and update definitions to include new concepts")
        enhancement.append("2. Expand scope sections to address emerging practices")
        enhancement.append("3. Add implementation guidance specific to these trends")
        enhancement.append("4. Provide case studies demonstrating application")
        enhancement.append("5. Update references to include recent industry developments")
        
        return "\n".join(enhancement)

    def _generate_regulatory_alignment_enhancement(self, standard, conflicts):
        """
        Generate a description for a regulatory alignment enhancement.
        
        Args:
            standard (dict): The standard to enhance
            conflicts (list): List of regulatory conflicts
            
        Returns:
            str: Enhancement description
        """
        standard_name = standard.get('name', 'Unnamed Standard')
        
        enhancement = [f"Update the '{standard_name}' standard to align with the following regulatory developments:"]
        
        for i, conflict in enumerate(conflicts, 1):
            enhancement.append(f"\n{i}. {conflict}")
            
        enhancement.append("\nRecommended approach:")
        enhancement.append("1. Add explicit references to these regulatory frameworks")
        enhancement.append("2. Identify areas requiring harmonization between the standard and regulations")
        enhancement.append("3. Adjust requirements to ensure compliance with regulatory minimums")
        enhancement.append("4. Provide guidance on managing compliance with both the standard and regulations")
        enhancement.append("5. Include a regulatory compliance mapping appendix")
        enhancement.append("6. Consider jurisdiction-specific implementation notes where applicable")
        
        return "\n".join(enhancement)

    def _generate_implementation_enhancement(self, standard, issues):
        """
        Generate a description for an implementation improvement enhancement.
        
        Args:
            standard (dict): The standard to enhance
            issues (list): List of implementation issues
            
        Returns:
            str: Enhancement description
        """
        standard_name = standard.get('name', 'Unnamed Standard')
        
        enhancement = [f"Enhance the '{standard_name}' standard to address the following implementation challenges:"]
        
        for i, issue in enumerate(issues, 1):
            enhancement.append(f"\n{i}. {issue.title()}")
            
        enhancement.append("\nRecommended approach:")
        enhancement.append("1. Develop detailed implementation guidance with step-by-step procedures")
        enhancement.append("2. Create templates and tools to facilitate practical application")
        enhancement.append("3. Add phased implementation options for complex requirements")
        enhancement.append("4. Provide case studies of successful implementation")
        enhancement.append("5. Include resource requirement estimations and planning guidance")
        enhancement.append("6. Develop implementation FAQs addressing common challenges")
        enhancement.append("7. Create assessment tools for implementation readiness")
        
        return "\n".join(enhancement)

    def _generate_placeholder_enhancement(self, standard):
        """
        Generate an enhancement for a placeholder standard.
        
        Args:
            standard (dict): The placeholder standard
            
        Returns:
            dict: Enhancement dictionary
        """
        # For placeholder standards, suggest comprehensive development
        return {
            'title': "Develop Comprehensive Standard from Placeholder",
            'type': 'new_standard_development',
            'description': (
                "Transform the placeholder into a fully developed AAOIFI standard following best practices in "
                "standard design. The development should include:\n\n"
                "1. Comprehensive research of existing practices and benchmarks\n"
                "2. Stakeholder consultation with Islamic finance practitioners\n"
                "3. Development of clear principles and detailed guidelines\n"
                "4. Creation of implementation guidance and examples\n"
                "5. Alignment with relevant Shariah principles\n"
                "6. Consideration of cross-border application\n"
                "7. Incorporation of contemporary market practices\n"
                "8. Development of compliance assessment framework"
            ),
            'rationale': "The current placeholder needs to be developed into a comprehensive standard to provide proper guidance.",
            'priority': 'high'
        }

    def _format_enhancement_for_report(self, enhancement):
        """
        Format an enhancement for inclusion in the report.
        
        Args:
            enhancement (dict): The enhancement to format
            
        Returns:
            str: Formatted enhancement text
        """
        lines = []
        lines.append(f"\n#### {enhancement.get('title', 'Untitled Enhancement')}")
        lines.append(f"**ID**: {enhancement.get('id', 'Unknown')}")
        lines.append(f"**Standard**: {enhancement.get('standard_name', 'Unknown Standard')}")
        lines.append(f"**Type**: {enhancement.get('type', 'Unknown').replace('_', ' ').title()}")
        lines.append(f"**Priority**: {enhancement.get('priority', 'medium').title()}")
        
        lines.append("\n**Rationale**:")
        lines.append(enhancement.get('rationale', 'No rationale provided.'))
        
        lines.append("\n**Description**:")
        lines.append(enhancement.get('description', 'No description provided.'))
        
        return "\n".join(lines)

    def _generate_overall_recommendations(self, enhancements):
        """
        Generate overall recommendations based on the enhancements.
        
        Args:
            enhancements (list): List of enhancement dictionaries
            
        Returns:
            str: Recommendations text
        """
        # Count enhancements by type
        enhancement_types = {}
        priority_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        
        for enhancement in enhancements:
            enhancement_type = enhancement.get('type', 'other')
            priority = enhancement.get('priority', 'medium')
            
            if enhancement_type in enhancement_types:
                enhancement_types[enhancement_type] += 1
            else:
                enhancement_types[enhancement_type] = 1
                
            priority_counts[priority] += 1
        
        # Generate recommendations based on the types of enhancements needed
        recommendations = []
        
        if priority_counts['critical'] > 0:
            recommendations.append(
                "1. **Immediately Address Regulatory Conflicts**: "
                "Form a dedicated taskforce to resolve critical regulatory alignment issues "
                "to ensure AAOIFI standards remain compatible with global regulatory frameworks."
            )
            
        if enhancement_types.get('clarity_improvement', 0) > 0:
            recommendations.append(
                "2. **Standardize Documentation Format**: "
                "Implement a consistent documentation structure and terminology across all standards "
                "to improve clarity and reduce interpretation variations."
            )
            
        if enhancement_types.get('coverage_expansion', 0) > 0:
            recommendations.append(
                "3. **Fill Identified Coverage Gaps**: "
                "Prioritize the development of guidance for areas with identified coverage gaps "
                "to ensure comprehensive treatment of all relevant topics."
            )
            
        if enhancement_types.get('implementation_improvement', 0) > 0:
            recommendations.append(
                "4. **Enhance Implementation Support**: "
                "Create dedicated implementation guides, templates, and tools to support "
                "practical application of standards in various institutional contexts."
            )
            
        if enhancement_types.get('trend_alignment', 0) > 0:
            recommendations.append(
                "5. **Institute Regular Trend Reviews**: "
                "Establish a periodic industry trend monitoring process to ensure standards "
                "remain aligned with evolving market practices and innovations."
            )
            
        # Add general recommendations if needed
        if not recommendations:
            recommendations.append(
                "1. **Continuous Improvement**: "
                "Maintain ongoing review of standards to ensure they remain current, "
                "clear, and aligned with industry needs and regulatory requirements."
            )
        
        # Add a recommendation about stakeholder engagement
        recommendations.append(
            f"{len(recommendations) + 1}. **Enhance Stakeholder Engagement**: "
            "Implement a structured stakeholder feedback mechanism to continually gather "
            "insights from practitioners on standards implementation challenges and opportunities."
        )
        
        return "\n\n".join(recommendations)

    def _generate_implementation_roadmap(self, enhancements):
        """
        Generate an implementation roadmap for the enhancements.
        
        Args:
            enhancements (list): List of enhancement dictionaries
            
        Returns:
            str: Implementation roadmap text
        """
        # Group enhancements by priority
        critical = [e for e in enhancements if e.get('priority') == 'critical']
        high = [e for e in enhancements if e.get('priority') == 'high']
        medium = [e for e in enhancements if e.get('priority') == 'medium']
        low = [e for e in enhancements if e.get('priority') == 'low']
        
        roadmap = []
        
        # Immediate Phase (0-3 months)
        roadmap.append("### Immediate Phase (0-3 months)")
        if critical:
            roadmap.append("- Address all critical priority enhancements:")
            for enhancement in critical:
                roadmap.append(f"  - {enhancement.get('title')}")
                
        roadmap.append("- Establish enhancement working groups")
        roadmap.append("- Develop detailed project plans for high priority items")
        roadmap.append("- Initiate stakeholder consultations")
        
        # Short-term Phase (3-6 months)
        roadmap.append("\n### Short-term Phase (3-6 months)")
        if high:
            roadmap.append("- Address high priority enhancements:")
            for enhancement in high[:3]:  # Show up to 3 examples
                roadmap.append(f"  - {enhancement.get('title')}")
            if len(high) > 3:
                roadmap.append(f"  - Plus {len(high) - 3} additional high priority items")
                
        roadmap.append("- Begin development of implementation support materials")
        roadmap.append("- Conduct preliminary impact assessments")
        
        # Medium-term Phase (6-12 months)
        roadmap.append("\n### Medium-term Phase (6-12 months)")
        if medium:
            roadmap.append("- Address medium priority enhancements")
            roadmap.append(f"  - Focus on {len(medium)} identified items")
                
        roadmap.append("- Release updated standards documentation")
        roadmap.append("- Conduct training and awareness sessions")
        roadmap.append("- Gather implementation feedback")
        
        # Long-term Phase (12+ months)
        roadmap.append("\n### Long-term Phase (12+ months)")
        if low:
            roadmap.append("- Address remaining low priority enhancements")
            roadmap.append(f"  - Complete {len(low)} identified items")
                
        roadmap.append("- Conduct comprehensive review of standards ecosystem")
        roadmap.append("- Develop next-generation standards framework")
        roadmap.append("- Establish continuous improvement mechanism")
        
        return "\n".join(roadmap)

    def _add_to_conversation(self, message):
        """
        Add a message to the conversation buffer if available.
        
        Args:
            message (str): The message to add
        """
        if self.conversation_buffer:
            self.conversation_buffer.add_message(self.name, message)
        self.logger.info(message)