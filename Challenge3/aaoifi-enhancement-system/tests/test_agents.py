import unittest
from src.agents.standards_reviewer import StandardsReviewerAgent
from src.agents.compliance_checker import ComplianceCheckerAgent
from src.agents.shariah_expert import ShariahExpertAgent
from src.agents.financial_analyst import FinancialAnalystAgent
from src.agents.coordinator_agent import CoordinatorAgent

class TestAgents(unittest.TestCase):

    def setUp(self):
        self.standards_reviewer = StandardsReviewerAgent()
        self.compliance_checker = ComplianceCheckerAgent()
        self.shariah_expert = ShariahExpertAgent()
        self.financial_analyst = FinancialAnalystAgent()
        self.coordinator_agent = CoordinatorAgent()

    def test_standards_reviewer(self):
        result = self.standards_reviewer.analyze_standards("sample_standard")
        self.assertIsNotNone(result)
        self.assertIn("enhancement", result)

    def test_compliance_checker(self):
        result = self.compliance_checker.check_compliance("proposed_amendment")
        self.assertTrue(result)

    def test_shariah_expert(self):
        ruling = self.shariah_expert.provide_ruling("contemporary_issue")
        self.assertIsNotNone(ruling)

    def test_financial_analyst(self):
        analysis = self.financial_analyst.analyze_market("market_data")
        self.assertIsNotNone(analysis)

    def test_coordinator_agent(self):
        workflow_status = self.coordinator_agent.manage_workflow()
        self.assertTrue(workflow_status)

if __name__ == '__main__':
    unittest.main()