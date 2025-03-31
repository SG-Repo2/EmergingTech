# Neo4j Data Loader

A Python package for loading structured JSON data into Neo4j databases.

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd neo4j_loader
```

2. Install the required dependencies:
```bash
pip install neo4j
```

## Usage

The package can be used in two ways:

### 1. Command Line Interface

Run the script directly with your JSON file:

```bash
python -m neo4j_loader --file your_data.json --uri neo4j://localhost:7687 --user neo4j --password your_password
```

Or use environment variable for password:
```bash
export NEO4J_PASSWORD=your_password
python -m neo4j_loader --file your_data.json
```

### 2. Python API

Import and use the package in your Python code:

```python
from neo4j_loader import Neo4jLoader, load_json_file

# Load your JSON data
json_data = load_json_file("your_data.json")

# Initialize the loader
loader = Neo4jLoader(
    uri="neo4j://localhost:7687",
    username="neo4j",
    password="your_password",
    encrypted=True
)

# Load data into Neo4j
nodes_count, rels_count = loader.load_data(json_data)
print(f"Created {nodes_count} nodes and {rels_count} relationships")
```

## JSON Data Format

The JSON file should follow this structure:

```json
{
    "nodes": [
        {
            "name": "Node1",
            "node_type": "Person",
            "age": 30,
            "city": "New York"
        },
        {
            "name": "Node2",
            "node_type": "Company",
            "industry": "Technology"
        }
    ],
    "relationships": [
        {
            "start": "Node1",
            "end": "Node2",
            "relationship_type": "WORKS_FOR",
            "since": 2020
        }
    ]
}
```

## Command Line Arguments

- `--file`, `-f`: Path to the JSON data file (required)
- `--uri`, `-u`: Neo4j URI (default: neo4j://localhost:7687)
- `--user`: Neo4j username (default: neo4j)
- `--password`: Neo4j password (or use NEO4J_PASSWORD environment variable)
- `--secure`: Use encrypted connection (default: True)
- `--log-level`: Set the logging level (default: INFO)

## Features

- Secure connection handling
- Transaction-based operations
- Duplicate prevention using MERGE
- Comprehensive error handling
- Detailed logging
- Support for custom node types and relationship types
- Property preservation for both nodes and relationships

## License

MIT License 