import os
import json
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from src.config.settings import STANDARDS_DIR

def retrieve_standards():
    """
    Retrieve standards from the standards directory.
    If no standards are found, create a placeholder standard.
    
    Returns:
        list: A list of standards
    """
    # Check if there are standard files in the STANDARDS_DIR
    standard_files = [f for f in os.listdir(STANDARDS_DIR) if f.endswith('.json') or f.endswith('.txt')]
    
    standards = []
    if standard_files:
        # Load standards from files
        for file in standard_files:
            file_path = os.path.join(STANDARDS_DIR, file)
            try:
                if file.endswith('.json'):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        standard = json.load(f)
                else:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Create a simple standard object
                        standard = {
                            'id': file.replace('.txt', ''),
                            'name': file.replace('.txt', ''),
                            'content': content
                        }
                standards.append(standard)
            except Exception as e:
                print(f"Error loading standard from {file}: {e}")
    else:
        # Create a placeholder standard if no standards are found
        placeholder_standard = {
            'id': 'placeholder',
            'name': 'Placeholder Standard',
            'content': 'This is a placeholder for AAOIFI standards analysis.',
            'description': 'Use this placeholder to demonstrate the functionality of the system.'
        }
        standards.append(placeholder_standard)
        
        # Save the placeholder to the standards directory for future use
        placeholder_path = os.path.join(STANDARDS_DIR, 'placeholder_standard.json')
        with open(placeholder_path, 'w', encoding='utf-8') as f:
            json.dump(placeholder_standard, f, indent=4)
        
    return standards

class StandardsRetriever:
    def __init__(self, database_connection=None):
        self.database_connection = database_connection
        self.standards = retrieve_standards()

    def retrieve_standard(self, standard_id):
        """
        Retrieve a standard by ID.
        
        Args:
            standard_id (str): The ID of the standard to retrieve
            
        Returns:
            dict: The standard data
        """
        for standard in self.standards:
            if str(standard.get('id')) == str(standard_id):
                return standard
        return None

    def search_standards(self, keyword):
        """
        Search for standards based on a keyword.
        
        Args:
            keyword (str): Keyword to search for
            
        Returns:
            list: Matching standards
        """
        results = []
        for standard in self.standards:
            # Search in both name and content if they exist
            name = standard.get('name', '')
            content = standard.get('content', '')
            
            if keyword.lower() in name.lower() or keyword.lower() in content.lower():
                results.append(standard)
        return results

    def list_all_standards(self):
        """
        List all available standards.
        
        Returns:
            list: All standards
        """
        return self.standards