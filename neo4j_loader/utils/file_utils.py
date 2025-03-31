"""
Utility module for file operations.

This module contains functions for handling JSON file operations and data validation.
"""

import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def load_json_file(file_path: str) -> Dict[str, Any]:
    """
    Load and parse a JSON file.

    Args:
        file_path: Path to the JSON file

    Returns:
        Parsed JSON data as a dictionary

    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file isn't valid JSON
    """
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
        logger.info(f"Successfully loaded JSON file: {file_path}")
        return data
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON file {file_path}: {e}")
        raise 