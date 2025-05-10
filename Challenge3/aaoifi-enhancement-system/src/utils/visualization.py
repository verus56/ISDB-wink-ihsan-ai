"""
Visualization utilities for AAOIFI Enhancement System.

This module provides visualization tools for displaying the amendment process,
reasoning trails, sources, and verification steps.
"""

import os
import json
import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import networkx as nx
from src.config.settings import OUTPUT_DIR

def generate_amendment_flowchart(amendment_data, output_path=None):
    """
    Generate a flowchart visualization of the amendment process.
    
    Args:
        amendment_data (dict): Amendment data including reasoning and sources
        output_path (str, optional): Path to save the visualization
        
    Returns:
        str: Path to the generated visualization
    """
    if output_path is None:
        current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(OUTPUT_DIR, f"amendment_flowchart_{current_time}.png")
    
    # Create a directed graph
    G = nx.DiGraph()
    
    # Add nodes for the standard and amendment
    G.add_node("Standard", type="standard", pos=(0, 0))
    G.add_node("Amendment", type="amendment", pos=(0, -4))
    
    # Add nodes for the different analysis steps
    G.add_node("Standards Review", type="step", pos=(-2, -1))
    G.add_node("Shariah Analysis", type="step", pos=(0, -1))
    G.add_node("Financial Impact", type="step", pos=(2, -1))
    
    # Add nodes for verification steps
    G.add_node("Verification", type="verify", pos=(0, -2))
    G.add_node("Sources", type="sources", pos=(0, -3))
    
    # Connect nodes
    G.add_edge("Standard", "Standards Review")
    G.add_edge("Standard", "Shariah Analysis")
    G.add_edge("Standard", "Financial Impact")
    G.add_edge("Standards Review", "Verification")
    G.add_edge("Shariah Analysis", "Verification")
    G.add_edge("Financial Impact", "Verification")
    G.add_edge("Verification", "Sources")
    G.add_edge("Sources", "Amendment")
    
    # Add labels based on the amendment data
    if isinstance(amendment_data, dict):
        if 'standard_name' in amendment_data:
            G.nodes["Standard"]["label"] = amendment_data['standard_name']
        if 'title' in amendment_data:
            G.nodes["Amendment"]["label"] = amendment_data['title']
        if 'description' in amendment_data:
            G.nodes["Amendment"]["description"] = amendment_data['description'][:100] + "..."
        
        # Add confidence scores if available
        if 'verification_results' in amendment_data and 'confidence' in amendment_data['verification_results']:
            G.nodes["Verification"]["confidence"] = f"{amendment_data['verification_results']['confidence'] * 100:.1f}%"
    
    # Create the plot
    plt.figure(figsize=(12, 8))
    pos = nx.get_node_attributes(G, 'pos')
    
    # Define colors for different node types
    node_colors = []
    for node in G.nodes():
        if G.nodes[node]['type'] == 'standard':
            node_colors.append('skyblue')
        elif G.nodes[node]['type'] == 'amendment':
            node_colors.append('lightgreen')
        elif G.nodes[node]['type'] == 'verify':
            node_colors.append('orange')
        elif G.nodes[node]['type'] == 'sources':
            node_colors.append('purple')
        else:
            node_colors.append('lightgrey')
    
    # Draw the network
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=2000, alpha=0.8)
    nx.draw_networkx_edges(G, pos, width=2, edge_color='grey', arrows=True, arrowsize=20)
    
    # Add labels for nodes
    custom_labels = {}
    for node in G.nodes():
        if 'label' in G.nodes[node]:
            custom_labels[node] = G.nodes[node]['label']
        else:
            custom_labels[node] = node
            
        # Add confidence to verification node
        if node == 'Verification' and 'confidence' in G.nodes[node]:
            custom_labels[node] = f"{node}\n({G.nodes[node]['confidence']})"
            
    nx.draw_networkx_labels(G, pos, custom_labels, font_size=10, font_family='sans-serif')
    
    # Add a title and legend
    plt.title('Amendment Process and Verification Flow', fontsize=15)
    
    # Add legend for node colors
    standard_patch = mpatches.Patch(color='skyblue', label='Standard')
    amendment_patch = mpatches.Patch(color='lightgreen', label='Amendment')
    verify_patch = mpatches.Patch(color='orange', label='Verification')
    sources_patch = mpatches.Patch(color='purple', label='Sources')
    step_patch = mpatches.Patch(color='lightgrey', label='Analysis Step')
    
    plt.legend(handles=[standard_patch, step_patch, verify_patch, sources_patch, amendment_patch],
               loc='upper right')
    
    plt.axis('off')
    plt.tight_layout()
    
    # Save the figure
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_path

def generate_confidence_heatmap(amendments, output_path=None):
    """
    Generate a heatmap of confidence scores for all amendments.
    
    Args:
        amendments (list): List of amendment dictionaries with confidence scores
        output_path (str, optional): Path to save the visualization
        
    Returns:
        str: Path to the generated visualization
    """
    if output_path is None:
        current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(OUTPUT_DIR, f"confidence_heatmap_{current_time}.png")
    
    # Extract amendment titles and confidence scores
    titles = []
    confidence_scores = []
    
    for amendment in amendments:
        title = amendment.get('title', 'Untitled')[:30]  # Truncate long titles
        titles.append(title)
        
        # Get confidence score
        if 'verification_results' in amendment and 'confidence' in amendment['verification_results']:
            confidence = amendment['verification_results']['confidence']
        else:
            confidence = 0.5  # Default confidence
            
        confidence_scores.append(confidence)
    
    # Create the plot
    plt.figure(figsize=(10, 6))
    
    # Create a colormap from red to green
    cmap = LinearSegmentedColormap.from_list('confidence', ['red', 'yellow', 'green'])
    
    # Create the heatmap
    plt.barh(titles, confidence_scores, color=[cmap(score) for score in confidence_scores])
    
    # Add labels and title
    plt.xlabel('Confidence Score')
    plt.ylabel('Amendment')
    plt.title('Amendment Confidence Scores')
    plt.xlim(0, 1)
      # Add a colorbar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(0, 1))
    sm.set_array([])
    
    # Get the current axes instance and use that for the colorbar
    ax = plt.gca()
    plt.colorbar(sm, ax=ax, label='Confidence')
    
    plt.tight_layout()
    
    # Save the figure
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_path

def visualize_amendment_process(coordinator_agent):
    """
    Generate visualizations for the amendment process based on coordinator agent data.
    
    Args:
        coordinator_agent: The coordinator agent with amendment data
        
    Returns:
        list: Paths to generated visualizations
    """
    outputs = []
    
    # Get final proposals from coordinator
    final_proposals = coordinator_agent.workflow_state.get('final_proposals', [])
    
    if not final_proposals:
        return outputs
    
    # Generate flowchart for each amendment
    for amendment in final_proposals:
        flowchart_path = generate_amendment_flowchart(amendment)
        outputs.append(flowchart_path)
    
    # Generate confidence heatmap for all amendments
    heatmap_path = generate_confidence_heatmap(final_proposals)
    outputs.append(heatmap_path)
    
    return outputs
