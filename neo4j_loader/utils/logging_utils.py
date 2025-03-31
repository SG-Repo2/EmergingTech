"""
Utility module for logging configuration.

This module contains functions for setting up and configuring logging for the application.
"""

import logging
from typing import Optional


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configure logging for the application.

    Args:
        log_level: The logging level to use (default: INFO)
    """
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    ) 