"""
Custom exception classes for Argus AI Gateway.
"""

class ArgusException(Exception):
    """Base exception class for all Argus-related errors."""
    pass

class SecurityViolationError(ArgusException):
    """Raised when a security violation is detected."""
    
    def __init__(self, message: str, violation_type: str = None, details: str = None):
        super().__init__(message)
        self.violation_type = violation_type
        self.details = details

class ConfigurationError(ArgusException):
    """Raised when there's a configuration error."""
    pass

class FilterError(ArgusException):
    """Raised when there's an error in filter processing."""
    pass

class LLMError(ArgusException):
    """Raised when there's an error with LLM processing."""
    pass
