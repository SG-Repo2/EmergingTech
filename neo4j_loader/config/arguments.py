"""
Configuration module for command-line argument parsing.

This module contains functions for parsing and validating command-line arguments.
"""

import argparse
import os
from typing import Optional


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Load structured JSON data into Neo4j database"
    )
    parser.add_argument(
        "--file", "-f", required=True, help="Path to the JSON data file"
    )
    parser.add_argument(
        "--uri",
        "-u",
        default="neo4j://localhost:7687",
        help="Neo4j URI (default: neo4j://localhost:7687)",
    )
    parser.add_argument(
        "--user", default="neo4j", help="Neo4j username (default: neo4j)"
    )
    parser.add_argument(
        "--password", help="Neo4j password (if not provided, will look for NEO4J_PASSWORD env var)"
    )
    parser.add_argument(
        "--secure",
        action="store_true",
        help="Use encrypted connection (default: True)",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level (default: INFO)",
    )
    return parser.parse_args()


def get_password(args: argparse.Namespace) -> Optional[str]:
    """
    Get the Neo4j password from arguments or environment.

    Args:
        args: Parsed command line arguments

    Returns:
        The Neo4j password or None if not found
    """
    return args.password or os.environ.get("NEO4J_PASSWORD") 