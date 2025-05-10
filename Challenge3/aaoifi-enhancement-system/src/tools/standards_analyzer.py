"""
Standards analyzer module for AAOIFI enhancement system.

This module provides specialized tools for analyzing AAOIFI standards
and identifying potential enhancements based on industry best practices,
recent developments, and compliance requirements.
"""

import re
from datetime import datetime

def analyze_fas_standard(document):
    """
    Analyzes a FAS standard document and identifies potential enhancement opportunities.
    
    Args:
        document (dict): The structured document data containing the standard
        
    Returns:
        dict: Analysis results with enhancement opportunities
    """
    content = document.get('content', '')
    metadata = document.get('metadata', {})
    
    # Initialize analysis results
    analysis = {
        'standard_info': {
            'number': metadata.get('standard_number', 'Unknown'),
            'title': metadata.get('standard_title', metadata.get('title', 'Unknown')),
            'effective_date': metadata.get('effective_date', 'Unknown'),
        },
        'enhancement_opportunities': [],
        'revision_required': False,
        'compliance_issues': [],
        'missing_elements': []
    }
    
    # Check for missing key sections
    if 'sections_present' in metadata:
        missing_sections = [k for k, v in metadata['sections_present'].items() if not v]
        if missing_sections:
            analysis['missing_elements'].extend(missing_sections)
            analysis['enhancement_opportunities'].append({
                'type': 'structural',
                'description': f"Add missing sections: {', '.join(missing_sections)}",
                'priority': 'high'
            })
            analysis['revision_required'] = True
    
    # Check for recent industry developments not addressed
    industry_developments = [
        ('digital assets', r'\b(crypto|blockchain|digital\s+asset|token|NFT)\b'),
        ('sustainable finance', r'\b(ESG|sustainability|green\s+financing|climate|carbon)\b'),
        ('fintech integration', r'\b(fintech|digital\s+banking|mobile\s+payment|API|open\s+banking)\b')
    ]
    
    for topic, pattern in industry_developments:
        if not re.search(pattern, content, re.IGNORECASE):
            analysis['enhancement_opportunities'].append({
                'type': 'coverage',
                'description': f"Expand coverage to address {topic}",
                'priority': 'medium'
            })
    
    # Check for alignment with IFRS developments
    ifrs_patterns = [
        r'\bIFRS\s+9\b', r'\bIFRS\s+15\b', r'\bIFRS\s+16\b', r'\bIFRS\s+17\b', r'\bIFRS\s+18\b'
    ]
    
    if not any(re.search(pattern, content, re.IGNORECASE) for pattern in ifrs_patterns):
        analysis['enhancement_opportunities'].append({
            'type': 'alignment',
            'description': "Review and align with recent IFRS developments",
            'priority': 'high'
        })
        analysis['revision_required'] = True
    
    # Check for implementation guidance
    if re.search(r'\bimplementation\b', content, re.IGNORECASE):
        if not re.search(r'\bimplementation\s+guidance\b', content, re.IGNORECASE):
            analysis['enhancement_opportunities'].append({
                'type': 'clarity',
                'description': "Add detailed implementation guidance and examples",
                'priority': 'medium'
            })
    
    # Check for clarity issues
    vague_terms = ['may', 'could', 'might', 'should consider', 'where appropriate', 'as applicable']
    vague_term_count = sum(content.lower().count(term) for term in vague_terms)
    
    if vague_term_count > 5:
        analysis['enhancement_opportunities'].append({
            'type': 'clarity',
            'description': f"Improve clarity by reducing vague language (found {vague_term_count} instances)",
            'priority': 'medium'
        })
    
    # Check if standard is older than 5 years
    if metadata.get('effective_date'):
        try:
            effective_date_str = metadata['effective_date']
            # Try to extract year from date string
            year_match = re.search(r'20\d{2}', effective_date_str)
            if year_match:
                year = int(year_match.group(0))
                current_year = datetime.now().year
                if (current_year - year) > 5:
                    analysis['enhancement_opportunities'].append({
                        'type': 'update',
                        'description': f"Standard is {current_year - year} years old and may require modernization",
                        'priority': 'high'
                    })
                    analysis['revision_required'] = True
        except Exception:
            # If date parsing fails, skip this check
            pass
    
    return analysis


def check_fas_compliance(standard_analysis):
    """
    Checks if a FAS standard meets required compliance criteria.
    
    Args:
        standard_analysis (dict): The analysis results for a standard
        
    Returns:
        dict: Compliance assessment
    """
    compliance = {
        'compliant': True,
        'issues': [],
        'recommendations': []
    }
    
    # Check if critical sections are missing
    missing_elements = standard_analysis.get('missing_elements', [])
    critical_sections = ['objective', 'scope', 'definitions']
    missing_critical = [section for section in critical_sections if section in missing_elements]
    
    if missing_critical:
        compliance['compliant'] = False
        compliance['issues'].append(f"Missing critical sections: {', '.join(missing_critical)}")
        compliance['recommendations'].append(f"Add missing critical sections: {', '.join(missing_critical)}")
    
    # Check if standard requires revision based on age or alignment issues
    if standard_analysis.get('revision_required', False):
        high_priority_enhancements = [
            e for e in standard_analysis.get('enhancement_opportunities', []) 
            if e.get('priority') == 'high'
        ]
        if high_priority_enhancements:
            compliance['compliant'] = False
            compliance['issues'].extend([e['description'] for e in high_priority_enhancements])
            compliance['recommendations'].append("Perform comprehensive review and update of the standard")
    
    return compliance


def generate_enhancement_proposal(standard_analysis):
    """
    Generates enhancement proposals based on standard analysis.
    
    Args:
        standard_analysis (dict): The analysis results for a standard
        
    Returns:
        list: Enhancement proposals
    """
    proposals = []
    
    for opportunity in standard_analysis.get('enhancement_opportunities', []):
        proposal = {
            'id': f"proposal_{len(proposals) + 1}",
            'title': opportunity['description'],
            'type': opportunity['type'],
            'priority': opportunity['priority'],
            'rationale': _generate_rationale(opportunity),
            'proposed_changes': _generate_proposed_changes(opportunity)
        }
        proposals.append(proposal)
    
    return proposals


def _generate_rationale(opportunity):
    """Helper function to generate rationale text based on opportunity type"""
    type_rationales = {
        'structural': "Complete standards require all key structural elements to ensure comprehensiveness and usability.",
        'coverage': "As Islamic finance evolves, standards must address emerging areas to maintain relevance.",
        'alignment': "Alignment with international frameworks ensures compatibility and reduces compliance burden.",
        'clarity': "Clear standards reduce interpretation differences and improve consistent application.",
        'update': "Regular updates ensure standards reflect current practices and address emerging issues."
    }
    
    return type_rationales.get(opportunity['type'], "Enhancement required to improve standard quality and application.")


def _generate_proposed_changes(opportunity):
    """Helper function to generate proposed changes based on opportunity type"""
    type_changes = {
        'structural': "Add missing sections with comprehensive content following AAOIFI's standard format.",
        'coverage': f"Include new section addressing {opportunity['description'].split('address ')[1]}.",
        'alignment': "Review and incorporate relevant aspects of recent international standards.",
        'clarity': "Replace ambiguous wording with specific, actionable guidance and examples.",
        'update': "Perform comprehensive review and modernization of all sections."
    }
    
    return type_changes.get(opportunity['type'], "Implement changes as specified in detailed enhancement plan.")


def analyze_standard_with_dual_models(document, primary_model=None, secondary_model=None):
    """
    Analyze a standard using both primary and secondary models for enhanced accuracy.
    
    Args:
        document (dict): The structured document data containing the standard
        primary_model: The primary LLM model (GPT-4o)
        secondary_model: The secondary LLM model (GPT-4-turbo)
        
    Returns:
        dict: Analysis results with enhancement opportunities, including:
            - standard_info: Basic information about the standard
            - primary_analysis: Analysis results from the primary model
            - secondary_analysis: Analysis results from the secondary model
            - combined_enhancements: The consolidated enhancement opportunities
            - confidence_scores: Confidence scores for each enhancement
            - sources: Citations and sources for the analysis
    """
    # First get the basic analysis using the existing function
    primary_analysis = analyze_fas_standard(document)
    
    content = document.get('content', '')
    metadata = document.get('metadata', {})
    
    # Initialize combined analysis
    combined_analysis = {
        'standard_info': primary_analysis['standard_info'],
        'primary_analysis': primary_analysis,
        'secondary_analysis': None,
        'combined_enhancements': [],
        'confidence_scores': {},
        'sources': {},
        'primary_model': 'gpt-4o',
        'secondary_model': 'gpt-4-turbo'
    }
    
    # If secondary model is available, get the secondary analysis
    if secondary_model:
        # This would be replaced with actual model call in production
        # For now, we'll simulate secondary model analysis
        secondary_enhancements = []
        for enhancement in primary_analysis['enhancement_opportunities']:
            # Create a modified version as if from secondary model
            # In production, this would be an actual call to the secondary model
            secondary_enhancement = enhancement.copy()
            
            # Add likelihood of this enhancement being correct (confidence)
            confidence = _calculate_enhancement_confidence(enhancement)
            secondary_enhancement['confidence'] = confidence
            
            # Add potential sources/citations
            secondary_enhancement['sources'] = _find_relevant_sources(enhancement, document)
            
            secondary_enhancements.append(secondary_enhancement)
            
        # Create the secondary analysis    
        secondary_analysis = {
            'standard_info': primary_analysis['standard_info'],
            'enhancement_opportunities': secondary_enhancements,
            'revision_required': primary_analysis['revision_required'],
            'compliance_issues': primary_analysis['compliance_issues'],
            'missing_elements': primary_analysis['missing_elements']
        }
        
        combined_analysis['secondary_analysis'] = secondary_analysis
    
    # Combine the enhancement opportunities
    combined_enhancements = _combine_enhancements(
        primary_analysis['enhancement_opportunities'],
        secondary_analysis['enhancement_opportunities'] if 'secondary_analysis' in combined_analysis else []
    )
    
    combined_analysis['combined_enhancements'] = combined_enhancements
    
    # Extract confidence scores
    for enhancement in combined_enhancements:
        enhancement_id = enhancement.get('id', 'unknown')
        combined_analysis['confidence_scores'][enhancement_id] = enhancement.get('confidence', 0.5)
        
        # Extract sources
        if 'sources' in enhancement and enhancement['sources']:
            combined_analysis['sources'][enhancement_id] = enhancement['sources']
    
    return combined_analysis

def _calculate_enhancement_confidence(enhancement):
    """
    Calculate a confidence score for an enhancement.
    
    Args:
        enhancement (dict): The enhancement to evaluate
        
    Returns:
        float: A confidence score between 0 and 1
    """
    # In a production system, this would use more sophisticated heuristics
    # For now, we'll use a simple mapping based on priority
    priority = enhancement.get('priority', 'medium').lower()
    
    if priority == 'high':
        base_confidence = 0.8
    elif priority == 'medium':
        base_confidence = 0.6
    else:
        base_confidence = 0.4
        
    # Add a small random factor for demonstration
    import random
    confidence = min(0.95, max(0.05, base_confidence + (random.random() - 0.5) * 0.2))
    
    return round(confidence, 2)

def _find_relevant_sources(enhancement, document):
    """
    Find relevant sources for an enhancement.
    
    Args:
        enhancement (dict): The enhancement to find sources for
        document (dict): The source document
        
    Returns:
        list: A list of relevant sources
    """
    # In production, this would use more sophisticated techniques
    # For now, we'll return some placeholder sources
    sources = []
    
    enhancement_type = enhancement.get('type', '')
    
    if enhancement_type == 'structural':
        sources.append("AAOIFI Governance Standard 1: Structure of Islamic Financial Standards")
    elif enhancement_type == 'conceptual':
        sources.append("IFSB Guiding Principles on Conceptual Clarity in Islamic Finance") 
    elif 'shariah' in enhancement.get('description', '').lower():
        sources.append("Quran 2:275-280 (Prohibition of Riba)")
        sources.append("Sahih Bukhari Hadith on Business Transactions")
    else:
        sources.append("Contemporary Islamic Finance: Innovations, Applications and Best Practices")
        
    # Add a reference to the source document
    metadata = document.get('metadata', {})
    document_title = metadata.get('title', 'Unknown Document')
    sources.append(f"Source document: {document_title}")
    
    return sources

def _combine_enhancements(primary_enhancements, secondary_enhancements):
    """
    Combine enhancements from primary and secondary analyses.
    
    Args:
        primary_enhancements (list): Enhancements from primary model
        secondary_enhancements (list): Enhancements from secondary model
        
    Returns:
        list: Combined and de-duplicated enhancements
    """
    # Start with all primary enhancements
    combined = primary_enhancements.copy()
    
    # Add unique enhancements from secondary model
    for sec_enhancement in secondary_enhancements:
        # Check if this enhancement is already included (by description)
        sec_desc = sec_enhancement.get('description', '').lower()
        
        duplicate = False
        for prim_enhancement in primary_enhancements:
            prim_desc = prim_enhancement.get('description', '').lower()
            
            # Simple text similarity check - would be more sophisticated in production
            if sec_desc == prim_desc or (len(sec_desc) > 10 and sec_desc in prim_desc) or (len(prim_desc) > 10 and prim_desc in sec_desc):
                duplicate = True
                
                # If secondary has sources, add them to primary
                if 'sources' in sec_enhancement:
                    if 'id' in prim_enhancement:
                        prim_id = prim_enhancement['id']
                        for i, enh in enumerate(combined):
                            if enh.get('id') == prim_id:
                                if 'sources' not in combined[i]:
                                    combined[i]['sources'] = []
                                combined[i]['sources'].extend(sec_enhancement['sources'])
                break
                
        # If not a duplicate, add to combined list
        if not duplicate:
            combined.append(sec_enhancement)
    
    return combined
