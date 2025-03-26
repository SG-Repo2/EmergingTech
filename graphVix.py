import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.offline as pyo

# Sample subset of the data (companies + relationships)
companies = [
    "Four Star Mushrooms",
    "Smallhold",
    "Tupu",
    "Nam Mushrooms",
    "Monterey Mushrooms",
    "Astanor Ventures",
    "City of Chicago Good Food Fund",
    "Jewel-Osco",
    "Local Breweries (Chicago)",
    "Sylvan Inc.",
    "Local Farms & Gardens",
    "University of Illinois at Urbana-Champaign",
    "Missouri Pellet Mill",
    "Chicago Michelin-Starred Restaurants",
    "Joe Weber",
    "Sean DiGioia",
    "Justin Hyunjae Chung"
]

relationships = [
    {
        "Start_Node": "Four Star Mushrooms",
        "End_Node": "Smallhold",
        "Relationship_Type": "Competitor"
    },
    {
        "Start_Node": "Four Star Mushrooms",
        "End_Node": "Tupu",
        "Relationship_Type": "Competitor"
    },
    {
        "Start_Node": "Four Star Mushrooms",
        "End_Node": "Monterey Mushrooms",
        "Relationship_Type": "Competitor"
    },
    {
        "Start_Node": "Four Star Mushrooms",
        "End_Node": "Local Breweries (Chicago)",
        "Relationship_Type": "Partner"
    },
    {
        "Start_Node": "Four Star Mushrooms",
        "End_Node": "Missouri Pellet Mill",
        "Relationship_Type": "Supplier"
    },
    {
        "Start_Node": "Four Star Mushrooms",
        "End_Node": "Sylvan Inc.",
        "Relationship_Type": "Supplier"
    },
    {
        "Start_Node": "City of Chicago Good Food Fund",
        "End_Node": "Four Star Mushrooms",
        "Relationship_Type": "Investor"
    },
    {
        "Start_Node": "Jewel-Osco",
        "End_Node": "Four Star Mushrooms",
        "Relationship_Type": "Customer"
    },
    {
        "Start_Node": "Chicago Michelin-Starred Restaurants",
        "End_Node": "Four Star Mushrooms",
        "Relationship_Type": "Customer"
    },
    {
        "Start_Node": "Local Farms & Gardens",
        "End_Node": "Four Star Mushrooms",
        "Relationship_Type": "Partner"
    },
    {
        "Start_Node": "University of Illinois at Urbana-Champaign",
        "End_Node": "Four Star Mushrooms",
        "Relationship_Type": "Research Collaboration"
    },
    {
        "Start_Node": "Four Star Mushrooms",
        "End_Node": "Joe Weber",
        "Relationship_Type": "Has_Founder"
    },
    {
        "Start_Node": "Four Star Mushrooms",
        "End_Node": "Sean DiGioia",
        "Relationship_Type": "Has_CoFounder"
    },
    {
        "Start_Node": "Four Star Mushrooms",
        "End_Node": "Justin Hyunjae Chung",
        "Relationship_Type": "Collaboration"
    },
    {
        "Start_Node": "Smallhold",
        "End_Node": "Astanor Ventures",
        "Relationship_Type": "Funded_By"
    }
]

# Create graph
G = nx.DiGraph()

# Add nodes (companies)
for c in companies:
    G.add_node(c)

# Add edges
for rel in relationships:
    G.add_edge(rel["Start_Node"], rel["End_Node"], label=rel["Relationship_Type"])

# Identify direct connections to Four Star Mushrooms
direct_connections = []
for u, v, d in G.edges(data=True):
    if u == "Four Star Mushrooms" or v == "Four Star Mushrooms":
        direct_connections.append((u, v))

# Identify second-level connections (connections of connections)
second_level_connections = []
for node in G.nodes():
    if node != "Four Star Mushrooms" and node not in [n for edge in direct_connections for n in edge]:
        paths = list(nx.all_simple_paths(G, source="Four Star Mushrooms", target=node, cutoff=2))
        paths.extend(list(nx.all_simple_paths(G, source=node, target="Four Star Mushrooms", cutoff=2)))
        if paths:
            for path in paths:
                if len(path) > 2:  # If path length > 2, it's a second-level connection
                    for i in range(len(path) - 1):
                        if (path[i], path[i+1]) not in direct_connections and (path[i], path[i+1]) not in second_level_connections:
                            second_level_connections.append((path[i], path[i+1]))

# Use a better layout for visualization with more spacing
pos = nx.spring_layout(G, k=1.5, iterations=50, seed=42)  # Increased `k` for more spacing

# Create separate edge traces for different connection types
edge_trace_direct = []  # For direct connections (green)
edge_trace_second = []  # For second-level connections (red)
edge_trace_other = []   # For other connections (gray)

# Create the edge traces
for u, v, data in G.edges(data=True):
    x0, y0 = pos[u]
    x1, y1 = pos[v]
    edge_text = f"{u} → {v}: {data['label']}"
    
    # Determine the edge type and add to appropriate trace
    if (u, v) in direct_connections or (v, u) in direct_connections:
        edge_color = 'green'
        edge_trace_direct.append(go.Scatter(
            x=[x0, x1, None], y=[y0, y1, None],
            line=dict(width=2, color=edge_color),
            hoverinfo='text',
            text=edge_text,
            mode='lines'
        ))
    elif (u, v) in second_level_connections or (v, u) in second_level_connections:
        edge_color = 'red'
        edge_trace_second.append(go.Scatter(
            x=[x0, x1, None], y=[y0, y1, None],
            line=dict(width=1.5, color=edge_color),
            hoverinfo='text',
            text=edge_text,
            mode='lines'
        ))
    else:
        edge_color = 'lightgray'
        edge_trace_other.append(go.Scatter(
            x=[x0, x1, None], y=[y0, y1, None],
            line=dict(width=1, color=edge_color),
            hoverinfo='text',
            text=edge_text,
            mode='lines'
        ))

# Update node trace for Plotly
node_x = []
node_y = []
node_sizes = []  # Add a list to control node sizes
for node in G.nodes():
    x, y = pos[node]
    node_x.append(x)
    node_y.append(y)
    if node == "Four Star Mushrooms":
        node_sizes.append(50)  # Much larger size for "Four Star Mushrooms"
    else:
        node_sizes.append(30)  # Larger size for other nodes

node_trace = go.Scatter(
    x=node_x, y=node_y,
    mode='markers+text',
    hoverinfo='text',
    text=[node for node in G.nodes()],
    textposition='top center',
    marker=dict(
        size=node_sizes,  # Use the updated node_sizes list
        color=['red' if node == "Four Star Mushrooms" 
               else 'green' if any((node, n) in direct_connections or (n, node) in direct_connections for n in G.nodes())
               else 'blue'],
        line=dict(width=2, color='black')
    )
)

# Update edge traces with new colors based on relationship type
edge_trace_direct = []  # For direct connections
edge_trace_second = []  # For second-level connections
edge_trace_other = []   # For other connections

for u, v, data in G.edges(data=True):
    x0, y0 = pos[u]
    x1, y1 = pos[v]
    edge_text = f"{u} → {v}: {data['label']}"
    
    # Determine edge color based on relationship type
    if data['label'] == "Competitor":
        edge_color = 'red'
    elif data['label'] in ["Supplier", "Collaboration"]:
        edge_color = 'purple'
    elif data['label'] in ["Customer", "Investor", "Partner"]:
        edge_color = 'green'
    else:
        edge_color = 'lightgray'  # Default for no affiliation

    edge_trace_direct.append(go.Scatter(
        x=[x0, x1, None], y=[y0, y1, None],
        line=dict(width=1.5, color=edge_color),  # Reduced line width for less emphasis
        hoverinfo='text',
        text=edge_text,
        mode='lines'
    ))

# Combine all edge traces and the node trace
all_traces = edge_trace_direct + [node_trace]

# Create the figure
fig = go.Figure(data=all_traces,
                layout=go.Layout(
                    title=dict(
                        text='Mushroom Ecosystem Visualization (Focus: Four Star Mushrooms)',
                        font=dict(size=16)
                    ),
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20, l=5, r=5, t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    plot_bgcolor='white',
                    annotations=[
                        dict(
                            text="Edge colors: Red = Competitor, Yellow = Supplier/Collaboration, Green = Customer, Gray = No affiliation",
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.5, y=-0.1,
                            font=dict(size=12)
                        )
                    ]
                ))

# Make the plot interactive
fig.update_layout(
    hoverlabel=dict(
        bgcolor="white",
        font_size=12,
        font_family="Arial"
    )
)

# Add custom hover information
hover_texts = []
for node in G.nodes():
    if node == "Four Star Mushrooms":
        hover_texts.append(f"<b>{node}</b><br>Urban indoor specialty mushroom farming<br>Founded: 2019<br>Location: Chicago, IL")
    else:
        rel_types = []
        for u, v, data in G.edges(data=True):
            if u == node and v == "Four Star Mushrooms":
                rel_types.append(f"{data['label']} to Four Star Mushrooms")
            elif v == node and u == "Four Star Mushrooms":
                rel_types.append(f"Four Star Mushrooms' {data['label']}")
        
        hover_texts.append(f"<b>{node}</b><br>" + (f"Relationship: {', '.join(rel_types)}" if rel_types else "No direct relationship with Four Star Mushrooms"))

# Apply hover texts to the node trace (last trace in the list)
fig.data[-1].hovertext = hover_texts
fig.data[-1].hoverinfo = 'text'

# Show the plot
fig.show()

# If you want to save the interactive HTML file
# pyo.plot(fig, filename='mushroom_ecosystem_visualization.html', auto_open=False)