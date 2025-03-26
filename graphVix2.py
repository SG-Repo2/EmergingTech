import networkx as nx
import matplotlib.pyplot as plt

# 1. Create a directed graph
G = nx.DiGraph()

# 2. Define color mappings for each node type (Company, HVACProvider, etc.)
color_map = {
    "Company": "lightblue",
    "TechnologyProvider": "lightgreen",
    "HVACProvider": "orange",
    "SubstrateEquipmentProvider": "pink",
    "Investor": "yellow",
    "ResearchOrg": "violet",
    "Customer": "turquoise",
    "Partner": "brown"
}

# 3. Define an expanded list of nodes (company, providers, etc.), each with a node_type
expanded_nodes = [
    ("Four Star Mushrooms", "Company"),
    ("Smallhold", "Company"),
    ("Tupu", "Company"),
    ("Monterey Mushrooms", "Company"),
    ("Nam Mushrooms", "Company"),
    # Example HVAC / substrate / tech providers
    ("Air Control Industries (ACI)", "HVACProvider"),
    ("Fancom", "HVACProvider"),
    ("Dalsem", "HVACProvider"),
    ("Christiaens Group", "SubstrateEquipmentProvider"),
    ("MeeFog", "TechnologyProvider"),
    ("Humidiflex", "TechnologyProvider"),
    ("Ecovative", "TechnologyProvider"),  # mycelium-based insulation
    ("Engie", "TechnologyProvider"),      # energy management
    ("Schneider Electric", "TechnologyProvider"),
    ("Shandong Zibo Taigu", "SubstrateEquipmentProvider"),
    ("Kingspan Panels", "TechnologyProvider"),
    ("Philips Grow Lights", "TechnologyProvider"),
    ("Illumitex", "TechnologyProvider"),
]

# 4. Add these nodes to the graph with the node_type as an attribute
for node, node_type in expanded_nodes:
    G.add_node(node, node_type=node_type)

# 5. Example existing relationships (simplified) plus new ones referencing the text
prior_relationships = [
    {
       "Start_Node": "Four Star Mushrooms",
       "End_Node": "Smallhold",
       "Relationship_Type": "COMPETITOR"
    },
    {
       "Start_Node": "Four Star Mushrooms",
       "End_Node": "Tupu",
       "Relationship_Type": "COMPETITOR"
    },
    {
       "Start_Node": "Four Star Mushrooms",
       "End_Node": "Monterey Mushrooms",
       "Relationship_Type": "COMPETITOR"
    },
]

# New “expanded” relationships from the user’s analysis: for example, “uses technology” or “partners”
expanded_relationships = [
    {
        "start": "Four Star Mushrooms",
        "end": "Air Control Industries (ACI)",
        "type": "USES_TECHNOLOGY",
        "details": "Specialized HVAC fans",
        "strength": "Low"
    },
    {
        "start": "Monterey Mushrooms",
        "end": "Fancom",
        "type": "USES_TECHNOLOGY",
        "details": "Climate control integration",
        "strength": "High"
    },
    {
        "start": "Smallhold",
        "end": "MeeFog",
        "type": "USES_TECHNOLOGY",
        "details": "High-pressure fogging systems",
        "strength": "Medium"
    },
    {
        "start": "Tupu",
        "end": "Christiaens Group",
        "type": "USES_TECHNOLOGY",
        "details": "Substrate prep solutions",
        "strength": "Medium"
    },
    {
        "start": "Nam Mushrooms",
        "end": "Humidiflex",
        "type": "USES_TECHNOLOGY",
        "details": "Indoor humidification modules",
        "strength": "Low"
    },
    {
        "start": "Tupu",
        "end": "Shandong Zibo Taigu",
        "type": "USES_TECHNOLOGY",
        "details": "Bottle lines for gourmet mushrooms",
        "strength": "Low"
    },
    {
        "start": "Four Star Mushrooms",
        "end": "Ecovative",
        "type": "PARTNER",
        "details": "Mycelium-based insulation pilot",
        "strength": "Low"
    },
    {
        "start": "Monterey Mushrooms",
        "end": "Engie",
        "type": "USES_TECHNOLOGY",
        "details": "Energy management software",
        "strength": "High"
    },
    {
        "start": "Smallhold",
        "end": "Schneider Electric",
        "type": "USES_TECHNOLOGY",
        "details": "Power/monitoring for micro-farms",
        "strength": "Medium"
    },
    {
        "start": "Four Star Mushrooms",
        "end": "Philips Grow Lights",
        "type": "USES_TECHNOLOGY",
        "details": "Low-intensity LED for fruiting cues",
        "strength": "Medium"
    },
    {
        "start": "Four Star Mushrooms",
        "end": "Kingspan Panels",
        "type": "USES_TECHNOLOGY",
        "details": "Insulated panels for grow rooms",
        "strength": "High"
    },
]

# 6. Add relationships to the graph
for pr in prior_relationships:
    G.add_edge(pr["Start_Node"], pr["End_Node"],
               relationship_type=pr["Relationship_Type"])

for er in expanded_relationships:
    G.add_edge(er["start"], er["end"],
               relationship_type=er["type"],
               details=er["details"],
               strength=er["strength"])

# 7. Color each node by its node_type
node_colors = []
for node, attrs in G.nodes(data=True):
    ntype = attrs.get("node_type", "Company")  # fallback if not assigned
    node_colors.append(color_map.get(ntype, "lightgray"))

# 8. Create a layout and plot
pos = nx.spring_layout(G, k=1.0, seed=42)
plt.figure(figsize=(12, 8))
nx.draw_networkx_nodes(G, pos, node_size=2000, node_color=node_colors)
nx.draw_networkx_labels(G, pos, font_size=8)
nx.draw_networkx_edges(G, pos, arrowstyle="->", arrowsize=15)

# Label edges with their relationship_type
edge_labels = {
    (u, v): d["relationship_type"]
    for u, v, d in G.edges(data=True)
}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7)

plt.title("Expanded Ecosystem Graph (Companies, Technology Providers, Partnerships)")
plt.axis("off")
plt.tight_layout()
plt.show()