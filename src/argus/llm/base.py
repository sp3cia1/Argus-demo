"""
Abstract base LLM interface for extensibility.
"""

from abc import ABC, abstractmethod

class BaseLLM(ABC):
    """Abstract base class for all LLM implementations."""
    
    @abstractmethod
    def get_response(self, prompt: str) -> str:
        """Get a response from the LLM."""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Get the name/identifier of this LLM."""
        pass
