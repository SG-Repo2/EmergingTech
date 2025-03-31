"""
Core module for Neo4j data loading operations.

This module contains the main Neo4jLoader class that handles all database operations
including connection management, node creation, and relationship creation.
"""

import logging
from typing import Dict, List, Any, Tuple

from neo4j import GraphDatabase, Session, Transaction
from neo4j.exceptions import ServiceUnavailable

logger = logging.getLogger(__name__)


class Neo4jLoader:
    """Handles loading data into Neo4j from a structured JSON file."""

    def __init__(
        self, uri: str, username: str, password: str, encrypted: bool = True
    ) -> None:
        """
        Initialize the Neo4jLoader with connection parameters.

        Args:
            uri: The URI for the Neo4j database
            username: Neo4j username
            password: Neo4j password
            encrypted: Whether to use encryption for the connection
        """
        self.uri = uri
        self.username = username
        self.password = password
        self.encrypted = encrypted
        self.driver = None
        self.connect()

    def connect(self) -> None:
        """
        Establish a connection to the Neo4j database.

        Raises:
            ServiceUnavailable: If connection to Neo4j fails
        """
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password),
                encrypted=self.encrypted,
            )
            # Verify connection is working
            self.driver.verify_connectivity()
            logger.info(f"Successfully connected to Neo4j database at {self.uri}")
        except ServiceUnavailable as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise

    def close(self) -> None:
        """Close the Neo4j database connection."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")

    def load_data(self, json_data: Dict[str, List[Dict[str, Any]]]) -> Tuple[int, int]:
        """
        Load data from parsed JSON into Neo4j.

        Args:
            json_data: Dictionary containing nodes and relationships

        Returns:
            Tuple containing count of created nodes and relationships
        """
        nodes_count = 0
        rels_count = 0

        try:
            # Process nodes
            if "nodes" in json_data:
                nodes_count = self._create_nodes(json_data["nodes"])
                logger.info(f"Successfully created {nodes_count} nodes")

            # Process relationships
            if "relationships" in json_data:
                rels_count = self._create_relationships(json_data["relationships"])
                logger.info(f"Successfully created {rels_count} relationships")

            return nodes_count, rels_count

        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise

    def _create_nodes(self, nodes: List[Dict[str, Any]]) -> int:
        """
        Create nodes in Neo4j from the provided list.

        Args:
            nodes: List of node dictionaries with properties

        Returns:
            Number of nodes created
        """
        created_count = 0

        with self.driver.session() as session:
            for node in nodes:
                try:
                    # Extract node type and name (required fields)
                    if "name" not in node or "node_type" not in node:
                        logger.warning("Skipping node missing required fields: name or node_type")
                        continue

                    node_name = node.pop("name")
                    node_type = node.pop("node_type")
                    
                    # Create the node with a MERGE operation to avoid duplicates
                    result = session.execute_write(
                        self._create_node_tx, node_name, node_type, node
                    )
                    created_count += result
                    logger.debug(f"Created node: {node_name} ({node_type})")
                except Exception as e:
                    logger.error(f"Error creating node {node.get('name', 'unknown')}: {e}")

        return created_count

    @staticmethod
    def _create_node_tx(tx: Transaction, name: str, label: str, properties: Dict[str, Any]) -> int:
        """
        Create a node in Neo4j within a transaction.

        Args:
            tx: Neo4j transaction
            name: Name of the node
            label: Label (type) of the node
            properties: Node properties

        Returns:
            Number of nodes created (0 or 1)
        """
        # Sanitize the label to remove any special characters
        label = label.replace("/", "_").replace(" ", "_")
        
        query = (
            f"MERGE (n:{label} {{name: $name}}) "
            "SET n += $properties "
            "RETURN count(n) as count"
        )
        
        # Include name in properties for consistency
        all_properties = {"name": name, **properties}
        
        result = tx.run(query, name=name, properties=all_properties)
        record = result.single()
        return record["count"] if record else 0

    def _create_relationships(self, relationships: List[Dict[str, Any]]) -> int:
        """
        Create relationships in Neo4j from the provided list.

        Args:
            relationships: List of relationship dictionaries

        Returns:
            Number of relationships created
        """
        created_count = 0

        with self.driver.session() as session:
            for rel in relationships:
                try:
                    # Check for required fields
                    if not all(k in rel for k in ["start", "end", "relationship_type"]):
                        logger.warning("Skipping relationship missing required fields")
                        continue

                    # Extract relationship details
                    start_node = rel["start"]
                    end_node = rel["end"]
                    rel_type = rel["relationship_type"]
                    
                    # Extract additional properties if any
                    properties = {k: v for k, v in rel.items() 
                                  if k not in ["start", "end", "relationship_type"]}

                    # Create the relationship
                    result = session.execute_write(
                        self._create_relationship_tx,
                        start_node,
                        end_node,
                        rel_type,
                        properties,
                    )
                    created_count += result
                    logger.debug(
                        f"Created relationship: ({start_node})-[:{rel_type}]->({end_node})"
                    )
                except Exception as e:
                    logger.error(f"Error creating relationship: {e}")

        return created_count

    @staticmethod
    def _create_relationship_tx(
        tx: Transaction, start_node: str, end_node: str, rel_type: str, properties: Dict[str, Any]
    ) -> int:
        """
        Create a relationship in Neo4j within a transaction.

        Args:
            tx: Neo4j transaction
            start_node: Name of the start node
            end_node: Name of the end node
            rel_type: Type of relationship
            properties: Relationship properties

        Returns:
            Number of relationships created (0 or 1)
        """
        # Sanitize the relationship type to remove any special characters
        rel_type = rel_type.replace("/", "_").replace(" ", "_")
        
        # Use MATCH to find the nodes and MERGE to create the relationship
        query = (
            "MATCH (a {name: $start_node}), (b {name: $end_node}) "
            f"MERGE (a)-[r:{rel_type}]->(b) "
            "SET r += $properties "
            "RETURN count(r) as count"
        )
        
        result = tx.run(
            query,
            start_node=start_node,
            end_node=end_node,
            properties=properties,
        )
        record = result.single()
        return record["count"] if record else 0 