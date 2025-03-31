import json
from neo4j import GraphDatabase
import os

def sanitize_label(label):
    """Sanitize label by replacing spaces with underscores and removing special characters"""
    return label.replace(' ', '_').replace('/', '_').replace('-', '_')

def load_data(json_file_path):
    # Neo4j connection details
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "8aPaBe8X3mGEsYcXzvUhHwjrC9rV64LmrSVXIE_X-Wk"
    
    # Read JSON data
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    # Connect to Neo4j
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    try:
        with driver.session() as session:
            # Create nodes
            for node in data['nodes']:
                # Create labels from node_type
                labels = [sanitize_label(node['node_type'])]
                if 'Entity_Type' in node:
                    labels.append(sanitize_label(node['Entity_Type']))
                
                # Create properties
                properties = {k: v for k, v in node.items() if k not in ['node_type', 'Entity_Type']}
                
                # Create Cypher query
                labels_str = ':'.join(labels)
                properties_str = ', '.join(f"{k}: ${k}" for k in properties.keys())
                query = f"MERGE (n:{labels_str} {{name: $name}}) SET n += {{{properties_str}}}"
                
                # Execute query
                session.run(query, **properties)
            
            # Create relationships
            for rel in data['relationships']:
                # Create relationship properties
                rel_properties = {k: v for k, v in rel.items() if k not in ['start', 'end', 'relationship_type']}
                
                # Create Cypher query
                rel_type = sanitize_label(rel['relationship_type'])
                properties_str = ', '.join(f"{k}: ${k}" for k in rel_properties.keys())
                query = f"""
                MATCH (start {{name: $start}})
                MATCH (end {{name: $end}})
                MERGE (start)-[r:{rel_type}]->(end)
                SET r += {{{properties_str}}}
                """
                
                # Execute query
                session.run(query, start=rel['start'], end=rel['end'], **rel_properties)
            
            print(f"Successfully loaded data from {json_file_path}")
            
    finally:
        driver.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python load_data.py <json_file_path>")
        sys.exit(1)
    
    json_file_path = sys.argv[1]
    if not os.path.exists(json_file_path):
        print(f"Error: File {json_file_path} does not exist")
        sys.exit(1)
    
    load_data(json_file_path) 