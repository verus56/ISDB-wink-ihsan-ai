# AAOIFI Standards Enhancement System

## Overview
The AAOIFI Standards Enhancement System is a multi-agent system designed to analyze and enhance the standards set by the Accounting and Auditing Organization for Islamic Financial Institutions (AAOIFI). The system leverages various specialized agents powered by GPT-4o and GPT-4-turbo models to ensure comprehensive evaluation and compliance with Shariah principles.

### Key Features

- **Dual-Model Architecture**: Uses both GPT-4o (primary) and GPT-4-turbo (secondary) for enhanced accuracy and reliability
- **Multi-Agent Collaboration**: Specialized agents for standards review, compliance checking, Shariah expertise, and financial analysis
- **Transparent Amendment Process**: All amendments include reasoning and sources
- **Enhanced Reporting**: Detailed reports with verification steps and confidence scores 
- **Visualization**: Process flowcharts and confidence heatmaps (requires matplotlib)

## How the System Works

### 1. Document Loading and Processing
The system begins by loading AAOIFI standard documents (such as the provided FAS4.PDF) from the data directory. It uses PyPDF2 to extract text from the PDFs and then applies advanced pattern matching to identify key components like standard numbers, titles, effective dates, and content sections.

### 2. Dual-Model Analysis
Each standard is analyzed using a dual-model approach:
- **Primary Model (GPT-4o)**: Performs the initial analysis with focus on technical accuracy
- **Secondary Model (GPT-4-turbo)**: Conducts a secondary analysis to verify findings
- The system compares both analyses and identifies high-confidence enhancements where both models agree

### 3. Multi-Agent Workflow
The system orchestrates a workflow involving four specialized agents:

1. **Standards Reviewer Agent**: Analyzes existing standards to identify enhancement opportunities based on clarity, comprehensiveness, and modern financial practices
2. **Compliance Checker Agent**: Verifies that proposed amendments align with Shariah principles and regulatory requirements
3. **Shariah Expert Agent**: Provides specialized Islamic jurisprudence insights on proposed changes
4. **Financial Analyst Agent**: Assesses the financial and market implications of potential amendments

These agents communicate through a conversation buffer managed by the Coordinator Agent.

### 4. Amendment Generation and Verification
For each identified enhancement opportunity:
1. The amendment is formulated with proposed changes
2. Verification is performed using the secondary model
3. Reasoning and sources are documented
4. Confidence scores are calculated

### 5. Visualization and Reporting
The system generates:
- Detailed text reports in the data/output directory
- Visual flowcharts of the amendment process
- Verification step visualization

## System Architecture

```
                  ┌─────────────────┐
                  │ Coordinator     │
                  │ Agent           │
                  └─────────────────┘
                          │
            ┌─────────────┼─────────────┐
            │             │             │
  ┌─────────▼─────┐ ┌─────▼─────┐ ┌─────▼─────┐
  │ Standards     │ │ Shariah   │ │ Financial │
  │ Reviewer      │ │ Expert    │ │ Analyst   │
  └───────────────┘ └───────────┘ └───────────┘
            │             │             │
            └─────────────┼─────────────┘
                          │
                  ┌───────▼───────┐
                  │ Compliance    │
                  │ Checker       │
                  └───────────────┘
                          │
                  ┌───────▼───────┐
                  │ Report        │
                  │ Generator     │
                  └───────────────┘
```

## Project Structure
```
aaoifi-enhancement-system
├── src
│   ├── main.py                     # Entry point for the application
│   ├── agents                       # Contains agent implementations
│   │   ├── standards_reviewer.py    # Analyzes existing standards
│   │   ├── compliance_checker.py     # Checks compliance with Shariah
│   │   ├── shariah_expert.py        # Provides Shariah insights
│   │   ├── financial_analyst.py      # Conducts market analysis
│   │   └── coordinator_agent.py      # Manages agent interactions
│   ├── tools                        # Contains utility tools
│   │   ├── document_loader.py        # Loads and parses documents
│   │   ├── standards_retriever.py    # Retrieves relevant standards
│   │   ├── standards_analyzer.py     # Analyzes standards with dual models
│   │   └── report_generator.py       # Generates reports
│   ├── memory                       # Manages conversation history
│   │   └── conversation_buffer.py    # Stores agent interactions
│   ├── config                       # Configuration settings
│   │   └── settings.py              # Application settings
│   └── utils                        # Utility functions
│       ├── helper_functions.py       # Assists in operations
│       └── visualization.py          # Generates visualizations
├── data
│   ├── standards                    # Directory for standard documents
│   │   └── placeholder_standard.json # Example standard
│   ├── FAS4.PDF                     # Sample AAOIFI standard document
│   └── output                       # Directory for generated outputs
│       ├── aaoifi_report_*.txt      # Generated text reports
│       └── amendment_flowchart_*.png # Visual flowcharts
├── tests                            # Unit tests for the application
│   ├── test_agents.py               # Tests for agent functionality
│   └── test_tools.py                # Tests for tool functions
├── requirements.txt                 # Project dependencies
├── run_agent.py                     # Script to run the system
└── README.md                        # Project documentation
```

## Setup Instructions
1. Clone the repository:
   ```
   git clone <repository-url>
   cd aaoifi-enhancement-system
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. For visualization capabilities, ensure matplotlib and networkx are installed:
   ```
   pip install matplotlib networkx
   ```

4. Set up environment variables:
   - Create a `.env` file with:
     ```
     OPENAI_API_KEY=your_openai_api_key
     GOOGLE_API_KEY=your_google_api_key
     FINANCIAL_DATA_SOURCE=FAS4.PDF
     ```

5. Run the system:
   ```
   python run_agent.py
   ```

## Model Configuration

The system uses:
- Primary model: GPT-4o (temperature 0.3)
- Secondary model: GPT-4-turbo (temperature 0.3)
- Max tokens: 4000

These settings can be customized in `src/config/settings.py`.

## Usage Examples

### Example 1: Standard Review and Enhancement

Input: Place an AAOIFI standard PDF in the data directory and run the system:
```
python run_agent.py
```

Output:
- Detailed analysis of the standard in the terminal
- Amendment proposals with reasoning and sources
- Visualization flowcharts in the data/output directory
- Full report in data/output/aaoifi_report_[timestamp].txt

### Example 2: Custom Standard Analysis

To analyze a custom standard document:
1. Place your PDF file in the data directory
2. Update the FINANCIAL_DATA_SOURCE environment variable:
   ```
   FINANCIAL_DATA_SOURCE=YourDocument.pdf
   ```
3. Run the system

## Sample Results

The system produces detailed reports including:

1. **Amendment Proposals:**
   - Clear descriptions of proposed changes
   - Original and proposed text
   - Reasoning for changes
   - Sources and references
   - Verification steps and confidence scores

2. **Visualizations:**
   - Amendment process flowcharts
   - Verification step diagrams

## Agent Roles and Responsibilities
- **StandardsReviewerAgent**: Analyzes existing standards and identifies areas for enhancement.
- **ComplianceCheckerAgent**: Ensures proposed amendments align with Shariah principles and regulatory requirements.
- **ShariahExpertAgent**: Provides insights and rulings based on contemporary Shariah scholarship.
- **FinancialAnalystAgent**: Conducts market analysis and assesses the financial implications of proposed changes.
- **CoordinatorAgent**: Manages the workflow between different agents and ensures effective communication.

## Contributors

This system was developed for the Islamic Finance Hackathon Challenge 3.

## License
Contributions are welcome! Please submit a pull request or open an issue for discussion.
