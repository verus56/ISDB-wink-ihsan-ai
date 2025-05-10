import os
from datetime import datetime
from src.config.settings import OUTPUT_DIR

def generate_report(conversation_buffer, coordinator_agent=None):
    """
    Generate a structured report based on the conversation buffer and coordinator agent data.
    
    Args:
        conversation_buffer: The buffer containing messages from all agents
        coordinator_agent: The coordinator agent with amendment metadata
        
    Returns:
        str: The formatted report as text
    """
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append(f"AAOIFI STANDARDS ENHANCEMENT REPORT")
    report_lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"Models used: GPT-4o (primary) and GPT-4-turbo (secondary)")
    report_lines.append("=" * 80 + "\n")
    
    # Add executive summary
    report_lines.append("## EXECUTIVE SUMMARY")
    report_lines.append("-" * 80)
    report_lines.append("This report presents proposed enhancements to AAOIFI standards,")
    report_lines.append("evaluated by AI agents specialized in Shariah compliance, financial analysis,")
    report_lines.append("and regulatory requirements. Each amendment is verified through a multi-stage")
    report_lines.append("process involving multiple AI models to ensure accuracy and relevance.")
    report_lines.append("\n")
    
    # Get all messages from the conversation buffer
    messages = conversation_buffer.get_messages()
    
    # Organize messages by sender
    messages_by_sender = {}
    for message in messages:
        sender = message.get("sender", "unknown")
        if sender not in messages_by_sender:
            messages_by_sender[sender] = []
        messages_by_sender[sender].append(message.get("message", ""))
        
    # Add detailed metadata from coordinator if available
    if coordinator_agent:
        report_lines.append("## PROPOSED AMENDMENTS")
        report_lines.append("-" * 80)
        
        # Get final proposals from workflow state if available
        final_proposals = coordinator_agent.workflow_state.get('final_proposals', [])
        
        if final_proposals:
            for i, amendment in enumerate(final_proposals):
                amendment_id = amendment.get('id', f'unknown-{i}')
                report_lines.append(f"### AMENDMENT {i+1}: {amendment.get('title', 'Untitled')}")
                report_lines.append(f"ID: {amendment_id}")
                
                # Use standard_name if available, otherwise use standard_id or fallback to default
                standard_name = amendment.get('standard_name')
                if standard_name is None:
                    standard_name = amendment.get('standard_id', 'Unknown Standard')
                    # If the standard_id is 'placeholder', format it as 'Placeholder Standard'
                    if standard_name == 'placeholder':
                        standard_name = 'Placeholder Standard'
                report_lines.append(f"Standard: {standard_name}")
                
                # Handle priority that could be either string or integer
                priority = amendment.get('priority', 'medium')
                if isinstance(priority, str):
                    priority = priority.upper()
                report_lines.append(f"Priority: {priority}")
                report_lines.append("\n**Description:**")
                report_lines.append(amendment.get('description', 'No description provided'))
                
                # Add original and proposed text if available
                if 'original_text' in amendment:
                    report_lines.append("\n**Original Text:**")
                    report_lines.append(f"```\n{amendment['original_text']}\n```")
                if 'proposed_text' in amendment:
                    report_lines.append("\n**Proposed Amendment:**")
                    report_lines.append(f"```\n{amendment['proposed_text']}\n```")
                
                # Add reasoning from coordinator tracking
                if amendment_id in coordinator_agent.amendment_reasoning:
                    report_lines.append("\n**Reasoning:**")
                    report_lines.append(coordinator_agent.amendment_reasoning[amendment_id])
                
                # Add sources
                if amendment_id in coordinator_agent.amendment_sources and coordinator_agent.amendment_sources[amendment_id]:
                    report_lines.append("\n**Sources:**")
                    for source in coordinator_agent.amendment_sources[amendment_id]:
                        report_lines.append(f"- {source}")
                
                # Add verification steps
                if amendment_id in coordinator_agent.verification_steps and coordinator_agent.verification_steps[amendment_id]:
                    report_lines.append("\n**Verification Steps:**")
                    for step in coordinator_agent.verification_steps[amendment_id]:
                        report_lines.append(f"- {step}")
                
                # Add verification results if available
                if 'verification_results' in amendment:
                    verification = amendment['verification_results']
                    report_lines.append("\n**Secondary Model Verification:**")
                    report_lines.append(f"- Verification Status: {'Approved' if verification.get('verified', False) else 'Not Approved'}")
                    report_lines.append(f"- Confidence Score: {verification.get('confidence', 0) * 100:.1f}%")
                    
                    if 'suggestions' in verification and verification['suggestions']:
                        report_lines.append("\n**Suggested Modifications:**")
                        for suggestion in verification['suggestions']:
                            report_lines.append(f"- {suggestion}")
                
                report_lines.append("\n" + "-" * 40 + "\n")
    
    # Add sections for each agent
    for sender, msgs in messages_by_sender.items():
        report_lines.append(f"## FINDINGS FROM {sender.upper()}")
        report_lines.append("-" * 80)
        for i, msg in enumerate(msgs):
            report_lines.append(f"{i+1}. {msg}")
        report_lines.append("\n")
    
    # Add summary section
    report_lines.append("## SUMMARY AND RECOMMENDATIONS")
    report_lines.append("-" * 80)
    report_lines.append("Based on the analysis of the provided documents, the following recommendations are made:")
    report_lines.append("1. Further analysis may be required for specific areas.")
    report_lines.append("2. Consult with additional experts for comprehensive assessment.")
    report_lines.append("\n")
    
    # Generate the full report text
    report_text = "\n".join(report_lines)
    
    # Save the report to a file
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    report_filename = f"aaoifi_report_{timestamp}.md"
    report_path = os.path.join(OUTPUT_DIR, report_filename)
    
    with open(report_path, 'w', encoding='utf-8') as file:
        file.write(report_text)
    
    print(f"Report generated and saved to: {report_path}")
    
    return report_text