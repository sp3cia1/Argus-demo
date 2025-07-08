"""
Abstract base filter class for extensibility.
"""

from abc import ABC, abstractmethod
from typing import Optional
from ..core.types import FilterResult

class BaseFilter(ABC):
    """Abstract base class for all filters."""
    
    @abstractmethod
    def check(self, text: str) -> FilterResult:
        """Check text for violations."""
        pass
    
    @abstractmethod
    def get_filter_name(self) -> str:
        """Get the name of this filter."""
        pass
