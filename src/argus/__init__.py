"""
Argus AI Gateway - A Cognitive Immune System for AI Security

Main package exports for easy imports.
"""

from .core.gateway import ArgusGateway
from .core.exceptions import ArgusException, SecurityViolationError, ConfigurationError
from .core.types import SecurityDecision, ViolationReason

__version__ = "1.0.0"
__author__ = "Thales ACADX AI Challenge 2025"

__all__ = [
    "ArgusGateway",
    "ArgusException", 
    "SecurityViolationError",
    "ConfigurationError",
    "SecurityDecision",
    "ViolationReason",
]
