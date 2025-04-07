#!/usr/bin/env python3
"""
JSON Relation Extractor

This module handles extraction and processing of JSON-formatted financial relationship data
in a Neo4j-ready format. It processes raw text input containing node and relationship data
and creates a properly formatted JSON file.

The JSON format follows a graph-based structure with:
- nodes: Entities like companies, people, predictions, industries
- relationships: Connections between nodes like ownership, predictions, impacts
"""

import json
import re

def extract_json_data(json_content, output_path):
    """
    Extract and process JSON relation data from text content.
    
    Args:
        json_content (str): Raw JSON section content
        output_path (str): Path where the JSON file will be saved
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Find the JSON object in the content (between brackets)
        json_match = re.search(r'({[\s\S]*})', json_content, re.DOTALL)
        if json_match:
            json_text = json_match.group(1)
            
            # Try to clean up potentially broken JSON
            json_text = clean_json_text(json_text)
            
            # Parse and validate JSON
            json_data = json.loads(json_text)
            
            # Verify required components
            if not isinstance(json_data, dict):
                raise ValueError("JSON data must be an object")
                
            if "nodes" not in json_data or not isinstance(json_data["nodes"], list):
                raise ValueError("JSON must contain a 'nodes' array")
                
            if "relationships" not in json_data or not isinstance(json_data["relationships"], list):
                raise ValueError("JSON must contain a 'relationships' array")
            
            # Validate node structure
            for node in json_data["nodes"]:
                if "name" not in node or "node_type" not in node:
                    raise ValueError("Each node must have 'name' and 'node_type' properties")
            
            # Validate relationship structure
            for rel in json_data["relationships"]:
                if "start" not in rel or "end" not in rel or "relationship_type" not in rel:
                    raise ValueError("Each relationship must have 'start', 'end', and 'relationship_type' properties")
            
            # Write to JSON file
            with open(output_path, 'w', encoding='utf-8') as file:
                json.dump(json_data, file, indent=2)
            
            return True
        else:
            raise ValueError("No valid JSON object found in the content")
            
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        # Try to extract partial JSON if possible and save in a more lenient manner
        try:
            fixed_json = attempt_json_repair(json_content)
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(fixed_json)
            print("Warning: JSON had errors but was repaired and saved")
            return True
        except:
            print("Could not repair invalid JSON")
            return False
            
    except Exception as e:
        print(f"Error extracting JSON data: {e}")
        return False

def clean_json_text(json_text):
    """
    Clean and fix common JSON format issues.
    
    Args:
        json_text (str): The raw JSON text
        
    Returns:
        str: Cleaned JSON text
    """
    # Remove any non-JSON text (like comments or explanations)
    json_text = re.sub(r'//.*?\n', '\n', json_text)  # Remove single-line comments
    json_text = re.sub(r'/\*.*?\*/', '', json_text, flags=re.DOTALL)  # Remove multi-line comments
    
    # Fix trailing commas in arrays and objects
    json_text = re.sub(r',\s*}', '}', json_text)
    json_text = re.sub(r',\s*]', ']', json_text)
    
    return json_text

def attempt_json_repair(json_content):
    """
    Attempt to repair invalid JSON by extracting and rebuilding the structure.
    
    Args:
        json_content (str): The invalid JSON content
        
    Returns:
        str: Repaired JSON string
    """
    # Create a basic structure if nothing else works
    result = {"nodes": [], "relationships": []}
    
    # Try to find node definitions
    node_matches = re.finditer(r'{[^{}]*"name"\s*:\s*"([^"]+)"[^{}]*"node_type"\s*:\s*"([^"]+)"[^{}]*}', json_content)
    for match in node_matches:
        try:
            node_text = match.group(0)
            node_json = json.loads(node_text)
            result["nodes"].append(node_json)
        except:
            pass
    
    # Try to find relationship definitions
    rel_matches = re.finditer(r'{[^{}]*"start"\s*:\s*"([^"]+)"[^{}]*"end"\s*:\s*"([^"]+)"[^{}]*"relationship_type"\s*:\s*"([^"]+)"[^{}]*}', json_content)
    for match in rel_matches:
        try:
            rel_text = match.group(0)
            rel_json = json.loads(rel_text)
            result["relationships"].append(rel_json)
        except:
            pass
    
    return json.dumps(result, indent=2)

# System prompt for JSON extraction
JSON_SYSTEM_PROMPT = """
You are an expert in graph data modeling, specializing in extracting and structuring financial relationship data.
Your task is to identify entities and their relationships in financial texts and structure them in a Neo4j-ready JSON format.

The JSON structure has two main sections:
1. nodes - Representing entities like companies, people, predictions, and industries
2. relationships - Representing connections between these entities

NODE STRUCTURE:
{
  "name": "Entity Name",
  "node_type": "Company | Person | Prediction | Industry | ...",
  "properties": {
    "Property1": "Value1",
    "Property2": "Value2"
  }
}

RELATIONSHIP STRUCTURE:
{
  "start": "Name of Starting Node",
  "end": "Name of Ending Node",
  "relationship_type": "OWNS | MAKES_PREDICTION | AFFECTS | ...",
  "properties": {
    "Property1": "Value1"
  }
}

GUIDELINES:
- Identify all entities mentioned (companies, divisions, people, industries)
- Extract all predictions and model them as separate nodes
- Create relationships between companies and their subsidiaries
- Link predictions to their sources and affected entities
- Ensure all nodes have unique names
- Use consistent relationship types (uppercase with underscores)
- Include relevant properties for both nodes and relationships

OUTPUT FORMAT:
A valid JSON object with "nodes" and "relationships" arrays containing the structured data.
"""

# Action prompt for JSON extraction
JSON_ACTION_PROMPT = """
Analyze the provided financial text and extract all entities and relationships into a Neo4j-ready JSON structure.

The JSON must include:
1. A "nodes" array containing all entities (companies, people, predictions, industries)
2. A "relationships" array connecting these nodes

For each entity, create a node with:
- A unique "name" field
- A "node_type" field (Company, Person, Prediction, Industry, etc.)
- A "properties" object with relevant attributes

For each relationship, create a connection with:
- "start" field matching a source node's name
- "end" field matching a target node's name
- "relationship_type" in UPPERCASE_WITH_UNDERSCORES
- Optional "properties" object with additional details

Ensure all predictions are modeled as separate nodes linked to their sources and targets.
Make sure the output is valid JSON with proper nesting, quotes, and commas.

Return ONLY the valid JSON object with no additional commentary.
"""

if __name__ == "__main__":
    # For testing as standalone module
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            content = f.read()
        extract_json_data(content, "test_output.json")