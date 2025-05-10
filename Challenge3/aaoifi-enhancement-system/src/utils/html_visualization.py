"""
HTML-based visualization utilities for AAOIFI Enhancement System.

This module provides visualization tools for displaying the amendment process,
reasoning trails, sources, and verification steps using simple HTML instead of matplotlib.
"""

import os
import json
import datetime
from src.config.settings import OUTPUT_DIR

def generate_html_visualization(amendment_data, output_path=None):
    """
    Generate an HTML visualization of amendments and their verification process.
    
    Args:
        amendment_data (dict): Amendment data including reasoning and sources
        output_path (str, optional): Path to save the visualization
        
    Returns:
        str: Path to the generated HTML file
    """
    if output_path is None:
        current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(OUTPUT_DIR, f"amendment_visualization_{current_time}.html")
    
    # Start creating the HTML content
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AAOIFI Amendment Visualization</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                color: #333;
                max-width: 1200px;
                margin: 0 auto;
            }
            header {
                background-color: #1e4d75;
                color: white;
                padding: 20px;
                text-align: center;
                margin-bottom: 30px;
                border-radius: 5px;
            }
            .amendment {
                background-color: #f8f8f8;
                border-left: 5px solid #1e4d75;
                margin-bottom: 30px;
                padding: 20px;
                border-radius: 0 5px 5px 0;
            }
            .amendment-header {
                border-bottom: 2px solid #ddd;
                padding-bottom: 10px;
                margin-bottom: 15px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .amendment-title {
                font-size: 1.5em;
                color: #1e4d75;
                margin: 0;
            }
            .amendment-priority {
                font-weight: bold;
                padding: 5px 10px;
                border-radius: 3px;
                color: white;
                background-color: #f39c12;
            }
            .priority-high {
                background-color: #e74c3c;
            }
            .priority-medium {
                background-color: #f39c12;
            }
            .priority-low {
                background-color: #3498db;
            }
            .section {
                margin-bottom: 20px;
            }
            .section-title {
                font-weight: bold;
                margin-bottom: 10px;
                color: #1e4d75;
            }
            .verification {
                display: flex;
                align-items: center;
                margin: 15px 0;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            .verification-icon {
                margin-right: 15px;
                font-size: 24px;
                color: #2ecc71;
            }
            .not-verified {
                color: #e74c3c;
            }
            .verification-details {
                flex-grow: 1;
            }
            .confidence-bar-container {
                width: 100%;
                background-color: #e0e0e0;
                height: 20px;
                border-radius: 10px;
                margin-top: 10px;
            }
            .confidence-bar {
                height: 20px;
                border-radius: 10px;
                background-color: #2ecc71;
            }
            .sources-list {
                list-style-type: none;
                padding-left: 0;
            }
            .sources-list li {
                margin-bottom: 5px;
                padding-left: 20px;
                position: relative;
            }
            .sources-list li:before {
                content: "•";
                position: absolute;
                left: 0;
                color: #1e4d75;
            }
            .reasoning {
                background-color: #f5f5f5;
                padding: 15px;
                border-radius: 5px;
                margin-top: 10px;
                white-space: pre-line;
            }
            .workflow-container {
                display: flex;
                justify-content: center;
                margin: 30px 0;
            }
            .workflow {
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            .workflow-step {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                margin: 5px 0;
                border-radius: 5px;
                min-width: 150px;
                text-align: center;
            }
            .workflow-arrow {
                height: 30px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #7f8c8d;
            }
            footer {
                margin-top: 40px;
                text-align: center;
                color: #7f8c8d;
                font-size: 0.9em;
                border-top: 1px solid #ddd;
                padding-top: 20px;
            }
        </style>
    </head>
    <body>
        <header>
            <h1>AAOIFI Amendment Visualization</h1>
            <p>Generated on """ + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
        </header>
        
        <div class="workflow-container">
            <div class="workflow">
                <div class="workflow-step">Standard Analysis</div>
                <div class="workflow-arrow">↓</div>
                <div class="workflow-step">Enhancement Identification</div>
                <div class="workflow-arrow">↓</div>
                <div class="workflow-step">Shariah Evaluation</div>
                <div class="workflow-arrow">↓</div>
                <div class="workflow-step">Financial Assessment</div>
                <div class="workflow-arrow">↓</div>
                <div class="workflow-step">Compliance Check</div>
                <div class="workflow-arrow">↓</div>
                <div class="workflow-step">Dual-Model Verification</div>
                <div class="workflow-arrow">↓</div>
                <div class="workflow-step">Final Amendment</div>
            </div>
        </div>
    """
    
    amendments = []
    
    # If amendment_data is a dict with a list of amendments
    if isinstance(amendment_data, dict) and 'amendments' in amendment_data:
        amendments = amendment_data['amendments']
    # If amendment_data is already a list of amendments
    elif isinstance(amendment_data, list):
        amendments = amendment_data
    # If amendment_data is a single amendment
    elif isinstance(amendment_data, dict):
        amendments = [amendment_data]
        
    # Add each amendment to the HTML
    for i, amendment in enumerate(amendments):
        amendment_id = amendment.get('id', f'unknown-{i}')
        title = amendment.get('title', 'Untitled Amendment')
        priority = amendment.get('priority', 'medium')
        if isinstance(priority, int):
            priority = 'high' if priority > 7 else ('medium' if priority > 3 else 'low')
        else:
            priority = str(priority).lower()
            
        standard_name = amendment.get('standard_name', 'Unknown Standard')
        description = amendment.get('description', 'No description provided')
        
        # Get verification results
        verification_results = amendment.get('verification_results', {})
        verified = verification_results.get('verified', False)
        confidence = verification_results.get('confidence', 0.5) * 100
        reasoning = verification_results.get('reasoning', '')
        suggestions = verification_results.get('suggestions', [])
        
        # Get additional metadata
        amendment_reasoning = amendment_data.get('reasoning', {}).get(amendment_id, '')
        amendment_sources = amendment_data.get('sources', {}).get(amendment_id, [])
        verification_steps = amendment_data.get('verification', {}).get(amendment_id, [])
        
        # Add the amendment to the HTML
        html_content += f"""
        <div class="amendment">
            <div class="amendment-header">
                <h2 class="amendment-title">{title}</h2>
                <span class="amendment-priority priority-{priority}">{priority.upper()}</span>
            </div>
            
            <div class="section">
                <div class="section-title">Standard:</div>
                {standard_name}
            </div>
            
            <div class="section">
                <div class="section-title">Description:</div>
                {description}
            </div>
        """
        
        # Add verification information
        html_content += f"""
            <div class="section">
                <div class="section-title">Verification:</div>
                <div class="verification">
                    <div class="verification-icon">{"✓" if verified else "✗"}</div>
                    <div class="verification-details">
                        <div>Status: {"Verified" if verified else "Not Verified"}</div>
                        <div>Confidence: {confidence:.1f}%</div>
                        <div class="confidence-bar-container">
                            <div class="confidence-bar" style="width: {confidence}%;"></div>
                        </div>
                    </div>
                </div>
            </div>
        """
        
        # Add reasoning if available
        if amendment_reasoning or reasoning:
            html_content += f"""
            <div class="section">
                <div class="section-title">Reasoning:</div>
                <div class="reasoning">
                    {amendment_reasoning or reasoning}
                </div>
            </div>
            """
            
        # Add suggestions if available
        if suggestions:
            html_content += f"""
            <div class="section">
                <div class="section-title">Suggestions:</div>
                <ul class="sources-list">
            """
            for suggestion in suggestions:
                html_content += f"<li>{suggestion}</li>"
            html_content += "</ul></div>"
            
        # Add sources if available
        if amendment_sources:
            html_content += f"""
            <div class="section">
                <div class="section-title">Sources:</div>
                <ul class="sources-list">
            """
            for source in amendment_sources:
                html_content += f"<li>{source}</li>"
            html_content += "</ul></div>"
            
        # Add verification steps if available
        if verification_steps:
            html_content += f"""
            <div class="section">
                <div class="section-title">Verification Steps:</div>
                <ul class="sources-list">
            """
            for step in verification_steps:
                html_content += f"<li>{step}</li>"
            html_content += "</ul></div>"
            
        # Close the amendment div
        html_content += "</div>"
        
    # Add a footer and close the HTML
    html_content += """
        <footer>
            <p>Generated by AAOIFI Standards Enhancement System</p>
            <p>Models used: GPT-4o (primary) and GPT-4-turbo (secondary) with temperature 0.3</p>
        </footer>
    </body>
    </html>
    """
    
    # Write the HTML to a file
    with open(output_path, 'w') as f:
        f.write(html_content)
        
    return output_path

def visualize_amendments_html(coordinator_agent=None, amendments_file=None):
    """
    Generate HTML visualizations for amendments.
    
    Args:
        coordinator_agent: Coordinator agent with amendment data
        amendments_file: Path to a JSON file with amendment data
        
    Returns:
        str: Path to the generated HTML visualization
    """
    # Get amendment data from coordinator agent or file
    amendment_data = {}
    
    if coordinator_agent:
        amendment_data = {
            'amendments': coordinator_agent.workflow_state.get('final_proposals', []),
            'reasoning': coordinator_agent.amendment_reasoning,
            'sources': coordinator_agent.amendment_sources,
            'verification': coordinator_agent.verification_steps
        }
    elif amendments_file:
        try:
            with open(amendments_file, 'r') as f:
                amendment_data = json.load(f)
        except Exception as e:
            print(f"Error reading amendments file: {str(e)}")
            return None
    else:
        # Look for the most recent amendments file in the output directory
        files = os.listdir(OUTPUT_DIR)
        amendment_files = [f for f in files if f.startswith('amendments_detailed_') and f.endswith('.json')]
        
        if amendment_files:
            # Sort by modification time (most recent first)
            amendment_files.sort(key=lambda x: os.path.getmtime(os.path.join(OUTPUT_DIR, x)), reverse=True)
            
            # Load the most recent file
            try:
                with open(os.path.join(OUTPUT_DIR, amendment_files[0]), 'r') as f:
                    amendment_data = json.load(f)
                print(f"Loaded amendments from {amendment_files[0]}")
            except Exception as e:
                print(f"Error reading amendments file: {str(e)}")
                return None
                
    if not amendment_data:
        print("No amendment data found")
        return None
        
    # Generate HTML visualization
    html_path = generate_html_visualization(amendment_data)
    return html_path
