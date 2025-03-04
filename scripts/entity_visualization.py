# scripts/entity_visualization.py
import spacy
from pyvis.network import Network
import os
from collections import Counter
import itertools

def create_entity_graph(text, min_occurrences=2, output_path="outputs/entity_graph.html"):
    """Create an interactive graph of entity relationships."""
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    
    # Count entity occurrences
    entity_counts = Counter([ent.text.lower() for ent in doc.ents])
    
    # Filter entities by minimum occurrences
    significant_entities = {ent.text for ent in doc.ents 
                           if entity_counts[ent.text.lower()] >= min_occurrences}
    
    # Create a network graph
    net = Network(height="800px", width="100%", bgcolor="#ffffff", font_color="black")
    
    # Add entity nodes by type (colored differently)
    entity_types = {}
    for ent in doc.ents:
        if ent.text in significant_entities:
            entity_types[ent.text] = ent.label_
            
            # Skip adding if already in the graph
            if ent.text not in [node['id'] for node in net.nodes]:
                # Choose color based on entity type
                if ent.label_ == "ORG":
                    color = "#4169E1"  # Royal Blue for organizations
                elif ent.label_ == "PERSON":
                    color = "#32CD32"  # Lime Green for people
                elif ent.label_ == "PRODUCT":
                    color = "#FF8C00"  # Dark Orange for products
                elif ent.label_ == "GPE":
                    color = "#9370DB"  # Medium Purple for geo/political entities
                else:
                    color = "#A9A9A9"  # Dark Gray for other entities
                
                # Add the node
                net.add_node(ent.text, label=ent.text, title=f"{ent.label_}: {ent.text}", 
                            color=color, size=10 + (entity_counts[ent.text.lower()] * 2))
    
    # Track relationships to avoid duplicates
    relationships = set()
    
    # Add edges for entities that appear in the same sentence
    for sent in doc.sents:
        # Get significant entities in this sentence
        sent_entities = [ent.text for ent in sent.ents if ent.text in significant_entities]
        
        # Create edges between all pairs
        for entity_pair in itertools.combinations(sent_entities, 2):
            # Skip self-relationships and already added relationships
            if entity_pair[0] != entity_pair[1] and entity_pair not in relationships:
                # Add edge with tooltip showing the sentence
                net.add_edge(entity_pair[0], entity_pair[1], 
                            title=sent.text[:100] + "..." if len(sent.text) > 100 else sent.text)
                relationships.add(entity_pair)
    
    # Set physics layout
    net.barnes_hut(gravity=-80000, central_gravity=0.3, spring_length=200)
    
    # Save the network
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    net.save_graph(output_path)
    
    print(f"Entity relationship graph created with {len(net.nodes)} nodes and {len(relationships)} edges")
    print(f"Saved to {output_path}")
    
    return output_path

# Example usage
if __name__ == "__main__":
    # Load cached text
    with open("cache/sample.pdf.txt", "r", encoding="utf-8") as f:
        text = f.read()
    
    # Create the graph
    graph_path = create_entity_graph(text, min_occurrences=3)