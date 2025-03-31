"""
Main entry point for the Neo4j data loader application.

This module serves as the main entry point for the application, coordinating
the interaction between different components and handling the main execution flow.
"""

import sys
import logging

from .core.loader import Neo4jLoader
from .utils.file_utils import load_json_file
from .utils.logging_utils import setup_logging
from .config.arguments import parse_args, get_password

logger = logging.getLogger(__name__)


def main() -> None:
    """Main function to execute the script."""
    args = parse_args()
    
    # Set logging level
    setup_logging(args.log_level)
    
    # Get password from args or environment
    password = get_password(args)
    if not password:
        logger.error(
            "Neo4j password not provided. Use --password or set NEO4J_PASSWORD environment variable."
        )
        sys.exit(1)
    
    try:
        # Load JSON data
        json_data = load_json_file(args.file)
        
        # Initialize loader
        loader = Neo4jLoader(
            uri=args.uri,
            username=args.user,
            password=password,
            encrypted=args.secure,
        )
        
        # Load data into Neo4j
        nodes_count, rels_count = loader.load_data(json_data)
        logger.info(f"Data loading completed. Created {nodes_count} nodes and {rels_count} relationships.")
        
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        sys.exit(1)
    finally:
        # Ensure connection is closed
        if 'loader' in locals() and loader.driver:
            loader.close()


if __name__ == "__main__":
    main() 