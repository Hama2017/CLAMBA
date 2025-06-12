"""
Logging utilities for CLAMBA
"""

import logging
import sys
from typing import Optional


def get_logger(name: str, debug: bool = False) -> logging.Logger:
    """
    Get a configured logger for CLAMBA modules
    
    Args:
        name: Logger name (usually __name__)
        debug: Enable debug logging
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    
    # Avoid adding multiple handlers
    if logger.handlers:
        return logger
    
    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    
    # Set format
    if debug:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
        )
        logger.setLevel(logging.DEBUG)
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )
        logger.setLevel(logging.INFO)
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


def setup_logging(debug: bool = False, log_file: Optional[str] = None) -> None:
    """
    Setup global logging configuration
    
    Args:
        debug: Enable debug logging
        log_file: Optional log file path
    """
    level = logging.DEBUG if debug else logging.INFO
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            *([logging.FileHandler(log_file)] if log_file else [])
        ]
    )
    
    # Set third-party loggers to WARNING
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.WARNING)