from langchain.agents import initialize_agent, AgentType
from langchain_community.llms import OpenAI  # Updated to use langchain_community
import openai
import os
import sys
import json
import datetime
from src.agents.standards_reviewer import StandardsReviewerAgent
from src.agents.compliance_checker import ComplianceCheckerAgent
from src.agents.shariah_expert import ShariahExpertAgent
from src.agents.financial_analyst import FinancialAnalystAgent
from src.agents.coordinator_agent import CoordinatorAgent
from src.tools.document_loader import load_documents
from src.tools.standards_retriever import retrieve_standards
from src.tools.report_generator import generate_report
from src.memory.conversation_buffer import ConversationBuffer
from src.config.settings import OPENAI_API_KEY, GOOGLE_API_KEY, FINANCIAL_DATA_SOURCE, OUTPUT_DIR

def main():
    # Set API keys
    if not OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY is not set in the environment.")
        sys.exit(1)
    
    if not GOOGLE_API_KEY:
        print("Warning: GOOGLE_API_KEY is not set, some functionality may be limited.")
    
    print(f"Using financial data source: {FINANCIAL_DATA_SOURCE}")
    
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
    openai.api_key = OPENAI_API_KEY
    
    # Initialize the conversation buffer
    conversation_buffer = ConversationBuffer()
    
    print("Initializing agents with API keys and GPT models...")
    # Initialize the OpenAI clients with configured models
    from src.config.settings import MODEL_CONFIG
    
    # Primary model (GPT-4o)
    primary_llm = OpenAI(
        model_name=MODEL_CONFIG["primary_model"],
        temperature=MODEL_CONFIG["temperature"],
        max_tokens=MODEL_CONFIG["max_tokens"]
    )
    
    # Secondary model (GPT-4-turbo)
    secondary_llm = OpenAI(
        model_name=MODEL_CONFIG["secondary_model"],
        temperature=MODEL_CONFIG["temperature"],
        max_tokens=MODEL_CONFIG["max_tokens"]
    )
    
    print(f"Using primary model: {MODEL_CONFIG['primary_model']}")
    print(f"Using secondary model: {MODEL_CONFIG['secondary_model']}")
    print(f"Model temperature: {MODEL_CONFIG['temperature']}")

    # Initialize agents with appropriate models
    standards_reviewer = StandardsReviewerAgent(conversation_buffer, llm=primary_llm)
    compliance_checker = ComplianceCheckerAgent(conversation_buffer, llm=primary_llm)
    shariah_expert = ShariahExpertAgent(conversation_buffer, llm=secondary_llm)
    financial_analyst = FinancialAnalystAgent(conversation_buffer, llm=secondary_llm)
    coordinator = CoordinatorAgent(conversation_buffer, primary_llm=primary_llm, secondary_llm=secondary_llm)

    print("Loading documents...")
    # Load documents and retrieve standards with enhanced processing
    documents = load_documents()
    print(f"Loaded {len(documents)} documents")
    
    # Process documents with dual-model standards analyzer for enhanced accuracy
    from src.tools.standards_analyzer import analyze_standard_with_dual_models, check_fas_compliance
    
    print("Using dual-model analysis for maximum accuracy and reliability...")
    
    for i, doc in enumerate(documents):
        content = doc.get('content', '')
        metadata = doc.get('metadata', {})
        
        if metadata.get('document_type') == 'AAOIFI_Standard' or 'FAS' in content:
            print(f"\nAnalyzing document {i+1} as potential AAOIFI standard...")
            print(f"Primary model: {MODEL_CONFIG['primary_model']}, Secondary model: {MODEL_CONFIG['secondary_model']}")
            
            # Use both models for analysis
            analysis = analyze_standard_with_dual_models(
                doc, 
                primary_model=primary_llm,
                secondary_model=secondary_llm
            )
            
            # Print analysis results
            standard_info = analysis['standard_info']
            print(f"Standard: FAS {standard_info['number']} - {standard_info['title']}")
            
            combined_enhancements = analysis.get('combined_enhancements', [])
            if combined_enhancements:
                print(f"Found {len(combined_enhancements)} enhancement opportunities (dual-model consensus):")
                for j, opportunity in enumerate(combined_enhancements):
                    confidence = opportunity.get('confidence', 0.5) * 100
                    print(f"  {j+1}. [{opportunity['priority'].upper()}] {opportunity['description']} (Confidence: {confidence:.1f}%)")
                    
                    # Show sources if available
                    if 'sources' in opportunity and opportunity['sources']:
                        print("     Sources:")
                        for source in opportunity['sources'][:2]:  # Just show first 2 sources
                            print(f"      - {source}")
            
            # Check compliance
            compliance = check_fas_compliance(analysis.get('primary_analysis', analysis))
            if not compliance['compliant']:
                print("\nCompliance issues detected:")
                for issue in compliance['issues']:
                    print(f"  - {issue}")
                print("\nRecommendations:")
                for rec in compliance['recommendations']:
                    print(f"  - {rec}")
                    
            # Save the detailed analysis for review
            analysis_file = os.path.join(OUTPUT_DIR, f"standard_analysis_{standard_info['number']}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(analysis_file, 'w') as f:
                # Convert any complex objects to serializable form
                import json
                analysis_copy = {k: v for k, v in analysis.items() if k != 'primary_model' and k != 'secondary_model'}
                json.dump(analysis_copy, f, indent=2)
    
    # Retrieve standards
    standards = retrieve_standards()

    # Orchestrate the interaction between agents
    print("Starting agent workflow...")
    coordinator.manage_workflow(documents, standards, [
        standards_reviewer,
        compliance_checker,
        shariah_expert,
        financial_analyst
    ])

    # Generate final report with detailed reasoning and sources
    print("Generating final report with reasoning trails and sources...")
    report = generate_report(conversation_buffer, coordinator)
    print(report)
    
    # Save all amendments with their detailed reasoning and sources
    current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    amendments_file = os.path.join(OUTPUT_DIR, f"amendments_detailed_{current_time}.json")
    
    print(f"Saving detailed amendment data to {amendments_file}")
    with open(amendments_file, 'w') as f:
        json.dump({
            'amendments': coordinator.workflow_state.get('final_proposals', []),
            'reasoning': coordinator.amendment_reasoning,
            'sources': coordinator.amendment_sources,
            'verification': coordinator.verification_steps
        }, f, indent=2)
    
    # Generate visualizations for the amendment process
    try:
        print("Generating visualizations for amendment process...")
        from src.utils.visualization import visualize_amendment_process
        visualization_paths = visualize_amendment_process(coordinator)
        
        print(f"Generated {len(visualization_paths)} visualizations:")
        for path in visualization_paths:
            print(f"  - {path}")
            
    except Exception as e:
        print(f"Warning: Could not generate visualizations. Make sure matplotlib and networkx are installed. Error: {str(e)}")

if __name__ == "__main__":
    main()