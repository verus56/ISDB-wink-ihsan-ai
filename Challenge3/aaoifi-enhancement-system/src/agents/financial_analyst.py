import os
import datetime
import json
import logging
from src.config.settings import OPENAI_API_KEY, GOOGLE_API_KEY, DATA_DIR, FINANCIAL_DATA_SOURCE

class FinancialAnalystAgent:
    def __init__(self, conversation_buffer=None, llm=None):
        self.name = "Financial Analyst Agent"
        self.conversation_buffer = conversation_buffer
        self.openai_api_key = OPENAI_API_KEY
        self.google_api_key = GOOGLE_API_KEY
        self.llm = llm  # Store the LLM model
        self.financial_data_source = os.path.join(DATA_DIR, FINANCIAL_DATA_SOURCE)
        self.market_sectors = self._load_market_sectors()
        self.financial_indicators = self._load_financial_indicators()
        self.analysis_trail = []  # Track analysis methodology and data sources
        
        # Configure logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger("FinancialAnalystAgent")
    
    def conduct_market_analysis(self, proposed_changes):
        """
        Analyze the market implications of the proposed changes to Islamic finance standards.
        
        Args:
            proposed_changes (list/dict): The proposed changes to be evaluated
            
        Returns:
            dict: Analysis results including market trends, potential impacts and opportunities
        """
        # Log the analysis start
        if self.conversation_buffer:
            self.conversation_buffer.add_message(
                self.name, 
                f"Starting market analysis for proposed changes"
            )
        
        # Process proposed changes to identify relevant market sectors
        if isinstance(proposed_changes, list):
            # For multiple changes, analyze each one
            sectors_affected = set()
            for change in proposed_changes:
                sectors = self._identify_affected_sectors(change)
                sectors_affected.update(sectors)
        else:
            # For single change as dictionary
            sectors_affected = self._identify_affected_sectors(proposed_changes)
        
        # Analyze market trends for each affected sector
        sector_trends = {}
        for sector in sectors_affected:
            sector_trends[sector] = self._analyze_sector_trends(sector)
        
        # Generate projections based on proposed changes
        market_projections = self._generate_market_projections(proposed_changes, sector_trends)
        
        # Identify opportunities and risks
        opportunities = self._identify_opportunities(proposed_changes, sector_trends)
        risks = self._identify_risks(proposed_changes, sector_trends)
        
        # Compile the analysis results
        analysis_results = {
            "sectors_affected": list(sectors_affected),
            "sector_trends": sector_trends,
            "market_projections": market_projections,
            "opportunities": opportunities,
            "risks": risks,
            "analysis_date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "analysis_summary": self._generate_analysis_summary(
                sectors_affected, sector_trends, opportunities, risks
            )
        }
        
        # Log the completion of the analysis
        if self.conversation_buffer:
            self.conversation_buffer.add_message(
                self.name, 
                f"Market analysis completed with {len(sectors_affected)} sectors affected and {len(opportunities)} opportunities identified"
            )
        
        return analysis_results
    
    def assess_financial_implications(self, proposed_changes):
        """
        Assess the financial impact of the proposed changes to Islamic finance standards.
        
        Args:
            proposed_changes (list/dict): The proposed changes to be evaluated
            
        Returns:
            dict: Financial assessment including costs, benefits, and ROI analysis
        """
        # Log the assessment start
        if self.conversation_buffer:
            self.conversation_buffer.add_message(
                self.name, 
                f"Starting financial impact assessment for proposed changes"
            )
        
        # Process the proposed changes
        if isinstance(proposed_changes, list):
            # For multiple changes, assess each one
            individual_assessments = []
            for change in proposed_changes:
                assessment = self._assess_individual_change(change)
                individual_assessments.append(assessment)
            
            # Combine individual assessments into an aggregate assessment
            aggregate_assessment = self._aggregate_financial_assessments(individual_assessments)
            
        else:
            # For single change as dictionary
            aggregate_assessment = self._assess_individual_change(proposed_changes)
            individual_assessments = [aggregate_assessment]
        
        # Perform cost-benefit analysis
        cost_benefit = self._perform_cost_benefit_analysis(aggregate_assessment)
        
        # Calculate ROI and timeline
        roi_analysis = self._calculate_roi(aggregate_assessment)
        implementation_timeline = self._estimate_implementation_timeline(proposed_changes)
        
        # Compile the financial assessment
        financial_assessment = {
            "overall_impact": aggregate_assessment["overall_impact"],
            "impact_level": aggregate_assessment["impact_level"],
            "impact_timeframe": aggregate_assessment["impact_timeframe"],
            "implementation_costs": aggregate_assessment["implementation_costs"],
            "potential_benefits": aggregate_assessment["potential_benefits"],
            "cost_benefit_analysis": cost_benefit,
            "roi_analysis": roi_analysis,
            "implementation_timeline": implementation_timeline,
            "individual_assessments": individual_assessments,
            "assessment_date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "assessment_summary": self._generate_financial_summary(
                aggregate_assessment, cost_benefit, roi_analysis
            )
        }
        
        # Log the completion of the assessment
        if self.conversation_buffer:
            impact_level = aggregate_assessment["impact_level"]
            self.conversation_buffer.add_message(
                self.name, 
                f"Financial assessment completed. Overall impact level: {impact_level}"
            )
        
        return financial_assessment
    
    def generate_financial_report(self, market_analysis, financial_assessment):
        """
        Generate a comprehensive financial report combining market analysis and financial assessment.
        
        Args:
            market_analysis (dict): Results from conduct_market_analysis
            financial_assessment (dict): Results from assess_financial_implications
            
        Returns:
            str: A formatted financial report
        """
        # Log report generation
        if self.conversation_buffer:
            self.conversation_buffer.add_message(
                self.name, 
                "Generating comprehensive financial report"
            )
        
        # Build the report
        report = []
        report.append("# FINANCIAL ANALYSIS REPORT")
        report.append(f"## Date: {datetime.datetime.now().strftime('%Y-%m-%d')}")
        report.append("\n## 1. EXECUTIVE SUMMARY")
        report.append(market_analysis.get('analysis_summary', 'No market analysis summary available.'))
        report.append("\nFinancial Impact: " + financial_assessment.get('assessment_summary', 'No financial assessment summary available.'))
        
        # Market Analysis Section
        report.append("\n## 2. MARKET ANALYSIS")
        report.append("\n### 2.1 Sectors Affected")
        for sector in market_analysis.get('sectors_affected', []):
            report.append(f"- {sector}")
        
        report.append("\n### 2.2 Market Trends")
        for sector, trend in market_analysis.get('sector_trends', {}).items():
            report.append(f"\n#### {sector}")
            report.append(f"Current Trend: {trend.get('trend', 'Unknown')}")
            report.append(f"Growth Rate: {trend.get('growth_rate', 'Unknown')}")
        
        report.append("\n### 2.3 Opportunities")
        for opportunity in market_analysis.get('opportunities', []):
            report.append(f"- {opportunity}")
        
        report.append("\n### 2.4 Risks")
        for risk in market_analysis.get('risks', []):
            report.append(f"- {risk}")
        
        # Financial Assessment Section
        report.append("\n## 3. FINANCIAL ASSESSMENT")
        report.append(f"\n### 3.1 Overall Impact: {financial_assessment.get('impact_level', 'Unknown')}")
        report.append(f"Timeframe: {financial_assessment.get('impact_timeframe', 'Unknown')}")
        
        report.append("\n### 3.2 Implementation Costs")
        for cost_type, amount in financial_assessment.get('implementation_costs', {}).items():
            report.append(f"- {cost_type}: ${amount:,}")
        
        report.append("\n### 3.3 Potential Benefits")
        for benefit_type, amount in financial_assessment.get('potential_benefits', {}).items():
            report.append(f"- {benefit_type}: ${amount:,}")
        
        report.append("\n### 3.4 Cost-Benefit Analysis")
        cb_analysis = financial_assessment.get('cost_benefit_analysis', {})
        report.append(f"Total Costs: ${cb_analysis.get('total_costs', 0):,}")
        report.append(f"Total Benefits: ${cb_analysis.get('total_benefits', 0):,}")
        report.append(f"Net Benefit: ${cb_analysis.get('net_benefit', 0):,}")
        report.append(f"Benefit-Cost Ratio: {cb_analysis.get('benefit_cost_ratio', 0):.2f}")
        
        report.append("\n### 3.5 ROI Analysis")
        roi = financial_assessment.get('roi_analysis', {})
        report.append(f"Expected ROI: {roi.get('expected_roi', 0):.2f}%")
        report.append(f"Payback Period: {roi.get('payback_period', 'Unknown')}")
        
        # Implementation Timeline
        report.append("\n## 4. IMPLEMENTATION TIMELINE")
        timeline = financial_assessment.get('implementation_timeline', {})
        for phase, details in timeline.items():
            report.append(f"\n### Phase: {phase}")
            report.append(f"Duration: {details.get('duration', 'Unknown')}")
            report.append(f"Key Activities: {', '.join(details.get('activities', []))}")
        
        # Recommendations
        report.append("\n## 5. RECOMMENDATIONS")
        recommendations = self._generate_recommendations(market_analysis, financial_assessment)
        for recommendation in recommendations:
            report.append(f"- {recommendation}")
        
        # Log report completion
        if self.conversation_buffer:
            self.conversation_buffer.add_message(
                self.name, 
                "Financial report generation completed"
            )
        
        return "\n".join(report)
    
    def _load_market_sectors(self):
        """
        Load market sectors relevant to Islamic finance.
        
        Returns:
            dict: Dictionary of market sectors with their descriptions
        """
        # In a production environment, this would load from a database or file
        # Here we're creating a simple dictionary of sectors
        return {
            "islamic_banking": {
                "name": "Islamic Banking",
                "description": "Traditional banking activities that comply with Shariah law",
                "growth_rate": 14.0  # Annual growth rate in percentage
            },
            "sukuk": {
                "name": "Sukuk (Islamic Bonds)",
                "description": "Shariah-compliant bonds that represent ownership in assets",
                "growth_rate": 10.5
            },
            "takaful": {
                "name": "Takaful (Islamic Insurance)",
                "description": "Cooperative insurance that complies with Shariah principles",
                "growth_rate": 12.0
            },
            "islamic_funds": {
                "name": "Islamic Investment Funds",
                "description": "Investment vehicles that comply with Shariah principles",
                "growth_rate": 15.5
            },
            "islamic_fintech": {
                "name": "Islamic Fintech",
                "description": "Financial technology solutions that comply with Shariah principles",
                "growth_rate": 22.0
            },
            "islamic_microfinance": {
                "name": "Islamic Microfinance",
                "description": "Small-scale financial services that comply with Shariah principles",
                "growth_rate": 18.0
            },
            "islamic_real_estate": {
                "name": "Islamic Real Estate Investment",
                "description": "Real estate investments structured according to Shariah principles",
                "growth_rate": 9.0
            }
        }
    
    def _load_financial_indicators(self):
        """
        Load key financial indicators for Islamic finance industry.
        
        Returns:
            dict: Dictionary of financial indicators
        """
        # In a production environment, this would load from a database or API
        # Here we're creating a simple dictionary of indicators
        return {
            "global_islamic_finance_assets": {
                "name": "Global Islamic Finance Assets",
                "value": 3.08,  # In trillion USD
                "growth_rate": 10.2,  # Annual growth rate in percentage
                "year": 2024
            },
            "sukuk_outstanding": {
                "name": "Outstanding Sukuk",
                "value": 756.2,  # In billion USD
                "growth_rate": 8.7,
                "year": 2024
            },
            "islamic_banking_assets": {
                "name": "Islamic Banking Assets",
                "value": 2.1,  # In trillion USD
                "growth_rate": 12.1,
                "year": 2024
            },
            "takaful_contributions": {
                "name": "Takaful Contributions",
                "value": 56.8,  # In billion USD
                "growth_rate": 9.4,
                "year": 2024
            },
            "islamic_funds_aum": {
                "name": "Islamic Funds Assets Under Management",
                "value": 178.6,  # In billion USD
                "growth_rate": 13.2,
                "year": 2024
            }
        }
    
    def _analyze_market_trends(self, proposed_changes):
        """
        Analyze market trends based on proposed changes.
        This is a higher-level method that coordinates the market analysis.
        
        Args:
            proposed_changes: The proposed changes to analyze
            
        Returns:
            dict: Market trend analysis results
        """
        # This method now delegates to more specific analysis methods
        affected_sectors = []
        
        if isinstance(proposed_changes, list):
            for change in proposed_changes:
                sectors = self._identify_affected_sectors(change)
                affected_sectors.extend(sectors)
        else:
            affected_sectors = self._identify_affected_sectors(proposed_changes)
        
        # Remove duplicates
        affected_sectors = list(set(affected_sectors))
        
        # Build comprehensive market trend analysis
        trend_analysis = {
            "affected_sectors": affected_sectors,
            "sector_analyses": {}
        }
        
        for sector in affected_sectors:
            trend_analysis["sector_analyses"][sector] = self._analyze_sector_trends(sector)
        
        return trend_analysis
    
    def _evaluate_financial_impact(self, proposed_changes):
        """
        Evaluate the financial impact of proposed changes.
        This is a higher-level method that coordinates the financial impact evaluation.
        
        Args:
            proposed_changes: The proposed changes to evaluate
            
        Returns:
            dict: Financial impact evaluation results
        """
        # This method now delegates to more specific evaluation methods
        assessments = []
        
        if isinstance(proposed_changes, list):
            for change in proposed_changes:
                assessment = self._assess_individual_change(change)
                assessments.append(assessment)
        else:
            assessment = self._assess_individual_change(proposed_changes)
            assessments = [assessment]
        
        # Aggregate the assessments
        aggregate = self._aggregate_financial_assessments(assessments)
        
        # Add cost-benefit and ROI analysis
        aggregate["cost_benefit_analysis"] = self._perform_cost_benefit_analysis(aggregate)
        aggregate["roi_analysis"] = self._calculate_roi(aggregate)
        
        return aggregate
    
    def _identify_affected_sectors(self, change):
        """
        Identify the market sectors affected by a proposed change.
        
        Args:
            change (dict): The proposed change
            
        Returns:
            list: Names of affected sectors
        """
        # In a production environment, this would use NLP to analyze the change
        # Here we're using simple keyword matching
        affected_sectors = []
        
        # Extract text from the change
        change_text = ""
        if isinstance(change, dict):
            change_text = (
                change.get('title', '') + ' ' + 
                change.get('description', '') + ' ' + 
                change.get('rationale', '') + ' ' +
                change.get('content', '')
            ).lower()
        elif isinstance(change, str):
            change_text = change.lower()
            
        # Check each sector for relevant keywords
        if 'bank' in change_text or 'deposit' in change_text or 'loan' in change_text:
            affected_sectors.append('islamic_banking')
            
        if 'sukuk' in change_text or 'bond' in change_text or 'certificate' in change_text:
            affected_sectors.append('sukuk')
            
        if 'takaful' in change_text or 'insurance' in change_text or 'risk' in change_text:
            affected_sectors.append('takaful')
            
        if 'fund' in change_text or 'invest' in change_text or 'portfolio' in change_text:
            affected_sectors.append('islamic_funds')
            
        if 'tech' in change_text or 'digital' in change_text or 'online' in change_text:
            affected_sectors.append('islamic_fintech')
            
        if 'micro' in change_text or 'small' in change_text or 'entrepreneur' in change_text:
            affected_sectors.append('islamic_microfinance')
            
        if 'real estate' in change_text or 'property' in change_text or 'land' in change_text:
            affected_sectors.append('islamic_real_estate')
        
        # If no specific sectors identified, assume impact on all sectors
        if not affected_sectors:
            affected_sectors = list(self.market_sectors.keys())
        
        return affected_sectors
    
    def _analyze_sector_trends(self, sector):
        """
        Analyze current trends for a specific market sector.
        
        Args:
            sector (str): The market sector to analyze
            
        Returns:
            dict: Analysis of sector trends
        """
        # Get sector information
        sector_info = self.market_sectors.get(sector, {})
        sector_name = sector_info.get('name', sector)
        growth_rate = sector_info.get('growth_rate', 0.0)
        
        # Determine trend direction
        trend = "Neutral"
        if growth_rate > 15.0:
            trend = "Strong Growth"
        elif growth_rate > 10.0:
            trend = "Moderate Growth"
        elif growth_rate > 5.0:
            trend = "Slight Growth"
        elif growth_rate < 0.0:
            trend = "Decline"
        
        # Analyze market sentiment (simulated)
        sentiment = "Neutral"
        if growth_rate > 12.0:
            sentiment = "Optimistic"
        elif growth_rate < 0.0:
            sentiment = "Pessimistic"
            
        # Generate 5-year projection
        five_year_projection = growth_rate * 5
        
        # Return analysis
        return {
            "sector": sector_name,
            "trend": trend,
            "growth_rate": f"{growth_rate}%",
            "market_sentiment": sentiment,
            "five_year_growth_projection": f"{five_year_projection}%",
            "analysis": f"The {sector_name} sector is showing {trend.lower()} with an annual growth rate of {growth_rate}%."
        }
    
    def _generate_market_projections(self, proposed_changes, sector_trends):
        """
        Generate market projections based on proposed changes and sector trends.
        
        Args:
            proposed_changes: The proposed changes
            sector_trends: Current sector trends
            
        Returns:
            dict: Market projections
        """
        # In a production environment, this would use more sophisticated modeling
        # Here we're generating simple projections
        projections = {}
        
        # Calculate a change impact factor (0.0 to 0.2) based on the number and type of changes
        impact_factor = 0.05
        if isinstance(proposed_changes, list) and len(proposed_changes) > 3:
            impact_factor = 0.1
        
        for sector, trends in sector_trends.items():
            sector_info = self.market_sectors.get(sector, {})
            base_growth = sector_info.get('growth_rate', 0.0)
            
            # Estimate impact on growth rate
            growth_impact = base_growth * impact_factor
            adjusted_growth = base_growth + growth_impact
            
            projections[sector] = {
                "base_growth_rate": f"{base_growth}%",
                "projected_growth_rate": f"{adjusted_growth}%",
                "growth_impact": f"+{growth_impact}%",
                "projection_period": "12 months",
                "projected_change": "Increase"
            }
        
        return projections
    
    def _identify_opportunities(self, proposed_changes, sector_trends):
        """
        Identify market opportunities based on proposed changes and sector trends.
        
        Args:
            proposed_changes: The proposed changes
            sector_trends: Current sector trends
            
        Returns:
            list: Identified opportunities
        """
        opportunities = []
        
        # Generate generic opportunities based on sector trends
        for sector, trend in sector_trends.items():
            sector_info = self.market_sectors.get(sector, {})
            sector_name = sector_info.get('name', sector)
            
            if sector == 'islamic_banking':
                opportunities.append(f"Increased adoption of standardized Islamic banking products compliant with new standards")
                opportunities.append(f"Potential for more cross-border Islamic banking activities due to harmonized standards")
                
            elif sector == 'sukuk':
                opportunities.append(f"Growth in Sukuk issuances due to clearer standards and structures")
                opportunities.append(f"Enhanced investor confidence in Sukuk markets")
                
            elif sector == 'takaful':
                opportunities.append(f"Expansion of Takaful offerings to new markets with clearer regulatory frameworks")
                opportunities.append(f"Development of innovative Takaful products aligned with standardized principles")
                
            elif sector == 'islamic_funds':
                opportunities.append(f"Increased investor participation in Islamic funds due to enhanced transparency")
                opportunities.append(f"Development of specialized Islamic investment products")
                
            elif sector == 'islamic_fintech':
                opportunities.append(f"Acceleration of Islamic fintech innovation within a clearer regulatory framework")
                opportunities.append(f"Integration of conventional fintech solutions with Islamic finance principles")
                
            elif sector == 'islamic_microfinance':
                opportunities.append(f"Greater financial inclusion through standardized Islamic microfinance products")
                opportunities.append(f"Expansion of Islamic microfinance in underserved markets")
                
            elif sector == 'islamic_real_estate':
                opportunities.append(f"Increased cross-border Islamic real estate investment with standardized structures")
                opportunities.append(f"Development of innovative Islamic REITs with clear compliance frameworks")
        
        return opportunities
    
    def _identify_risks(self, proposed_changes, sector_trends):
        """
        Identify market risks based on proposed changes and sector trends.
        
        Args:
            proposed_changes: The proposed changes
            sector_trends: Current sector trends
            
        Returns:
            list: Identified risks
        """
        risks = []
        
        # Generate generic risks based on sector trends
        for sector, trend in sector_trends.items():
            sector_info = self.market_sectors.get(sector, {})
            sector_name = sector_info.get('name', sector)
            
            if sector == 'islamic_banking':
                risks.append(f"Implementation costs may create competitive disadvantages for smaller Islamic banks")
                risks.append(f"Potential resistance to changes from established market participants")
                
            elif sector == 'sukuk':
                risks.append(f"Existing Sukuk structures may require restructuring, creating market uncertainty")
                risks.append(f"Transition period could temporarily reduce new Sukuk issuances")
                
            elif sector == 'takaful':
                risks.append(f"Compliance costs may increase Takaful premiums in the short term")
                risks.append(f"Possible market fragmentation if standards adoption varies by region")
                
            elif sector == 'islamic_funds':
                risks.append(f"Portfolio restructuring costs to comply with new standards")
                risks.append(f"Potential short-term performance impact during adjustment period")
                
            elif sector == 'islamic_fintech':
                risks.append(f"Innovation may be temporarily slowed by adaptation to new standards")
                risks.append(f"Compliance costs may impact fintech startups disproportionately")
                
            elif sector == 'islamic_microfinance':
                risks.append(f"Increased operational costs may affect financial inclusion objectives")
                risks.append(f"Small providers may struggle with compliance resources")
                
            elif sector == 'islamic_real_estate':
                risks.append(f"Existing real estate investment structures may require costly restructuring")
                risks.append(f"Potential delays in transactions during adaptation period")
        
        return risks
    
    def _generate_analysis_summary(self, sectors_affected, sector_trends, opportunities, risks):
        """
        Generate a summary of the market analysis.
        
        Args:
            sectors_affected: The affected sectors
            sector_trends: Current sector trends
            opportunities: Identified opportunities
            risks: Identified risks
            
        Returns:
            str: Analysis summary
        """
        # Generate a concise summary of the market analysis
        num_sectors = len(sectors_affected)
        num_opportunities = len(opportunities)
        num_risks = len(risks)
        
        sector_names = [self.market_sectors.get(s, {}).get('name', s) for s in sectors_affected]
        
        summary = (
            f"The proposed changes will primarily impact {num_sectors} Islamic finance sectors: "
            f"{', '.join(sector_names)}. "
            f"Analysis reveals {num_opportunities} market opportunities and {num_risks} potential risks. "
            f"Overall market sentiment is cautiously optimistic, with projected growth increases "
            f"across affected sectors. Key opportunities include increased standardization, "
            f"enhanced investor confidence, and potential for innovation. Primary risks involve "
            f"implementation costs, adaptation challenges, and potential short-term market uncertainty."
        )
        
        return summary
    
    def _assess_individual_change(self, change):
        """
        Assess the financial implications of an individual proposed change.
        
        Args:
            change (dict): The proposed change
            
        Returns:
            dict: Financial assessment of the individual change
        """
        # Extract change information
        change_title = change.get('title', 'Untitled Change')
        change_description = change.get('description', '')
        change_content = change.get('content', '')
        
        # Analyze complexity (simulated)
        complexity = "Medium"
        if len(change_description + change_content) > 1000:
            complexity = "High"
        elif len(change_description + change_content) < 200:
            complexity = "Low"
        
        # Determine impact level based on complexity and affected sectors
        affected_sectors = self._identify_affected_sectors(change)
        impact_level = "Medium"
        if len(affected_sectors) > 3 or complexity == "High":
            impact_level = "High"
        elif len(affected_sectors) <= 1 and complexity == "Low":
            impact_level = "Low"
        
        # Estimate implementation costs (simulated)
        base_cost = 0
        if impact_level == "High":
            base_cost = 5000000  # $5 million
        elif impact_level == "Medium":
            base_cost = 1000000  # $1 million
        else:
            base_cost = 200000   # $200,000
        
        implementation_costs = {
            "technology_updates": int(base_cost * 0.4),
            "training_education": int(base_cost * 0.2),
            "documentation_updates": int(base_cost * 0.15),
            "compliance_verification": int(base_cost * 0.15),
            "administrative_costs": int(base_cost * 0.1)
        }
        
        # Estimate potential benefits (simulated)
        benefit_multiplier = 0
        if impact_level == "High":
            benefit_multiplier = 3.2
        elif impact_level == "Medium":
            benefit_multiplier = 2.8
        else:
            benefit_multiplier = 2.5
        
        total_costs = sum(implementation_costs.values())
        potential_benefits = {
            "increased_market_efficiency": int(total_costs * 0.5 * benefit_multiplier),
            "reduced_compliance_issues": int(total_costs * 0.3 * benefit_multiplier),
            "enhanced_investor_confidence": int(total_costs * 0.4 * benefit_multiplier),
            "expanded_market_access": int(total_costs * 0.3 * benefit_multiplier)
        }
        
        # Determine impact timeframe
        impact_timeframe = "Medium-term (1-3 years)"
        if complexity == "Low":
            impact_timeframe = "Short-term (< 1 year)"
        elif complexity == "High":
            impact_timeframe = "Long-term (3+ years)"
        
        # Generate assessment
        assessment = {
            "change_title": change_title,
            "complexity": complexity,
            "affected_sectors": affected_sectors,
            "impact_level": impact_level,
            "impact_timeframe": impact_timeframe,
            "implementation_costs": implementation_costs,
            "potential_benefits": potential_benefits,
            "overall_impact": "The proposed change is expected to have a " + impact_level.lower() + " financial impact."
        }
        
        return assessment
    
    def _aggregate_financial_assessments(self, assessments):
        """
        Aggregate multiple financial assessments into a single assessment.
        
        Args:
            assessments (list): List of individual financial assessments
            
        Returns:
            dict: Aggregated financial assessment
        """
        if not assessments:
            return {
                "impact_level": "Unknown",
                "impact_timeframe": "Unknown",
                "implementation_costs": {},
                "potential_benefits": {},
                "overall_impact": "No changes to assess"
            }
        
        # Determine overall impact level
        impact_levels = [a["impact_level"] for a in assessments]
        if "High" in impact_levels:
            overall_impact_level = "High"
        elif "Medium" in impact_levels:
            overall_impact_level = "Medium"
        else:
            overall_impact_level = "Low"
        
        # Determine overall impact timeframe
        timeframes = [a["impact_timeframe"] for a in assessments]
        if "Long-term (3+ years)" in timeframes:
            overall_timeframe = "Long-term (3+ years)"
        elif "Medium-term (1-3 years)" in timeframes:
            overall_timeframe = "Medium-term (1-3 years)"
        else:
            overall_timeframe = "Short-term (< 1 year)"
        
        # Aggregate implementation costs
        aggregated_costs = {}
        for assessment in assessments:
            costs = assessment.get("implementation_costs", {})
            for cost_type, amount in costs.items():
                if cost_type in aggregated_costs:
                    aggregated_costs[cost_type] += amount
                else:
                    aggregated_costs[cost_type] = amount
        
        # Aggregate potential benefits
        aggregated_benefits = {}
        for assessment in assessments:
            benefits = assessment.get("potential_benefits", {})
            for benefit_type, amount in benefits.items():
                if benefit_type in aggregated_benefits:
                    aggregated_benefits[benefit_type] += amount
                else:
                    aggregated_benefits[benefit_type] = amount
        
        # Generate overall impact statement
        overall_impact = (
            f"The proposed changes are expected to have a {overall_impact_level.lower()} financial impact "
            f"with effects primarily realized in the {overall_timeframe.lower()}."
        )
        
        return {
            "impact_level": overall_impact_level,
            "impact_timeframe": overall_timeframe,
            "implementation_costs": aggregated_costs,
            "potential_benefits": aggregated_benefits,
            "overall_impact": overall_impact
        }
    
    def _perform_cost_benefit_analysis(self, financial_assessment):
        """
        Perform a cost-benefit analysis based on the financial assessment.
        
        Args:
            financial_assessment (dict): Financial assessment results
            
        Returns:
            dict: Cost-benefit analysis results
        """
        # Extract costs and benefits
        costs = financial_assessment.get("implementation_costs", {})
        benefits = financial_assessment.get("potential_benefits", {})
        
        # Calculate totals
        total_costs = sum(costs.values())
        total_benefits = sum(benefits.values())
        net_benefit = total_benefits - total_costs
        
        # Calculate benefit-cost ratio
        benefit_cost_ratio = total_benefits / total_costs if total_costs > 0 else 0
        
        # Determine if economically viable
        is_viable = benefit_cost_ratio > 1.5
        
        # Return analysis
        return {
            "total_costs": total_costs,
            "total_benefits": total_benefits,
            "net_benefit": net_benefit,
            "benefit_cost_ratio": benefit_cost_ratio,
            "is_economically_viable": is_viable,
            "analysis": (
                f"The proposed changes have a benefit-cost ratio of {benefit_cost_ratio:.2f}, "
                f"with a net benefit of ${net_benefit:,}. "
                f"This indicates the changes are {'economically viable' if is_viable else 'economically challenging'}."
            )
        }
    
    def _calculate_roi(self, financial_assessment):
        """
        Calculate Return on Investment for the proposed changes.
        
        Args:
            financial_assessment (dict): Financial assessment results
            
        Returns:
            dict: ROI analysis results
        """
        # Extract costs and benefits
        costs = financial_assessment.get("implementation_costs", {})
        benefits = financial_assessment.get("potential_benefits", {})
        
        # Calculate totals
        total_costs = sum(costs.values())
        total_benefits = sum(benefits.values())
        net_benefit = total_benefits - total_costs
        
        # Calculate ROI percentage
        roi_percentage = (net_benefit / total_costs) * 100 if total_costs > 0 else 0
        
        # Estimate payback period (in years)
        annual_benefit = total_benefits / 3  # Assuming benefits are realized over 3 years
        payback_years = total_costs / annual_benefit if annual_benefit > 0 else float('inf')
        
        if payback_years == float('inf'):
            payback_period = "Indefinite"
        elif payback_years < 1:
            payback_period = f"{payback_years * 12:.1f} months"
        else:
            payback_period = f"{payback_years:.1f} years"
        
        # Return ROI analysis
        return {
            "expected_roi": roi_percentage,
            "payback_period": payback_period,
            "analysis": (
                f"The proposed changes are expected to yield an ROI of {roi_percentage:.2f}% "
                f"with a payback period of {payback_period}."
            )
        }
    
    def _estimate_implementation_timeline(self, proposed_changes):
        """
        Estimate the implementation timeline for the proposed changes.
        
        Args:
            proposed_changes: The proposed changes
            
        Returns:
            dict: Implementation timeline
        """
        # Count the number of changes
        num_changes = 1
        if isinstance(proposed_changes, list):
            num_changes = len(proposed_changes)
        
        # Base timeline on the number and complexity of changes
        timeline = {}
        
        # Phase 1: Planning and Assessment
        timeline["1_planning"] = {
            "name": "Planning and Assessment",
            "duration": f"{max(1, int(num_changes / 3))} months",
            "activities": [
                "Detailed impact analysis",
                "Resource planning",
                "Stakeholder communication"
            ]
        }
        
        # Phase 2: Development and Documentation
        timeline["2_development"] = {
            "name": "Development and Documentation",
            "duration": f"{max(2, int(num_changes / 2))} months",
            "activities": [
                "Policy updates",
                "Process revisions",
                "Documentation development",
                "System modifications"
            ]
        }
        
        # Phase 3: Testing and Validation
        timeline["3_testing"] = {
            "name": "Testing and Validation",
            "duration": f"{max(1, int(num_changes / 3))} months",
            "activities": [
                "Compliance testing",
                "Process validation",
                "Stakeholder review"
            ]
        }
        
        # Phase 4: Training and Rollout
        timeline["4_rollout"] = {
            "name": "Training and Rollout",
            "duration": f"{max(2, int(num_changes / 2))} months",
            "activities": [
                "Staff training",
                "Client education",
                "Phased implementation",
                "Compliance verification"
            ]
        }
        
        # Phase 5: Monitoring and Evaluation
        timeline["5_monitoring"] = {
            "name": "Monitoring and Evaluation",
            "duration": "Ongoing",
            "activities": [
                "Performance monitoring",
                "Compliance auditing",
                "Feedback collection",
                "Continuous improvement"
            ]
        }
        
        return timeline
    
    def _generate_recommendations(self, market_analysis, financial_assessment):
        """
        Generate recommendations based on market analysis and financial assessment.
        
        Args:
            market_analysis (dict): Market analysis results
            financial_assessment (dict): Financial assessment results
            
        Returns:
            list: Recommendations
        """
        recommendations = []
        
        # Generate recommendations based on financial viability
        cb_analysis = financial_assessment.get('cost_benefit_analysis', {})
        is_viable = cb_analysis.get('is_economically_viable', False)
        benefit_cost_ratio = cb_analysis.get('benefit_cost_ratio', 0)
        
        if is_viable:
            recommendations.append(
                "Proceed with the implementation of the proposed changes as they demonstrate strong economic viability."
            )
        elif benefit_cost_ratio > 1.0:
            recommendations.append(
                "Proceed with caution and consider phasing implementation to manage costs and monitor benefits."
            )
        else:
            recommendations.append(
                "Reconsider or modify the proposed changes to improve economic viability."
            )
        
        # Recommendations based on implementation timeline
        timeline = financial_assessment.get('implementation_timeline', {})
        planning_duration = timeline.get('1_planning', {}).get('duration', '')
        
        recommendations.append(
            f"Allocate at least {planning_duration} for planning and assessment to ensure thorough preparation."
        )
        
        # Recommendations based on market opportunities
        opportunities = market_analysis.get('opportunities', [])
        if opportunities:
            recommendations.append(
                "Develop a strategic communication plan to highlight the benefits and opportunities "
                "created by these changes to stakeholders."
            )
        
        # Recommendations based on identified risks
        risks = market_analysis.get('risks', [])
        if risks:
            recommendations.append(
                "Establish a risk management framework to monitor and mitigate identified risks during implementation."
            )
        
        # General recommendations
        recommendations.append(
            "Engage with industry stakeholders early in the implementation process to address concerns and gather feedback."
        )
        
        recommendations.append(
            "Develop comprehensive training materials to facilitate adoption and ensure proper implementation."
        )
        
        return recommendations
    
    def _generate_financial_summary(self, assessment, cost_benefit, roi):
        """
        Generate a financial summary based on the assessment results.
        
        Args:
            assessment (dict): Financial assessment
            cost_benefit (dict): Cost-benefit analysis
            roi (dict): ROI analysis
            
        Returns:
            str: Financial summary
        """
        impact_level = assessment.get('impact_level', 'Unknown')
        timeframe = assessment.get('impact_timeframe', 'Unknown')
        total_costs = cost_benefit.get('total_costs', 0)
        total_benefits = cost_benefit.get('total_benefits', 0)
        bcr = cost_benefit.get('benefit_cost_ratio', 0)
        roi_value = roi.get('expected_roi', 0)
        payback = roi.get('payback_period', 'Unknown')
        
        summary = (
            f"Financial analysis indicates a {impact_level.lower()} impact with effects realized in the {timeframe.lower()}. "
            f"Estimated implementation costs of ${total_costs:,} are projected to yield ${total_benefits:,} in benefits, "
            f"resulting in a benefit-cost ratio of {bcr:.2f} and an ROI of {roi_value:.2f}% with a payback period of {payback}. "
            f"The financial assessment {'supports' if bcr > 1.5 else 'suggests caution for'} proceeding with implementation."
        )
        
        return summary