"""
Structured logging utilities.
"""

import logging
import sys
from typing import Optional
from ..config.settings import settings

def setup_logging(
    level: Optional[str] = None,
    format_string: Optional[str] = None,
    log_file: Optional[str] = None
) -> None:
    """Setup structured logging configuration."""
    
    log_level = level or settings.log_level
    log_format = format_string or settings.log_format
    
    # Configure basic logging
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=handlers
    )
    
    # Set specific loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    return logging.getLogger(name)
