"""
Interface for phases in DWSIM Python implementation.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class IPhase(ABC):
    """Interface for thermodynamic phases"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Phase name"""
        pass

    @property
    @abstractmethod
    def properties(self) -> Dict[str, Any]:
        """Phase properties"""
        pass

    @abstractmethod
    def calculate_properties(self, temperature: float, pressure: float,
                           composition: Dict[str, float]) -> Dict[str, Any]:
        """Calculate phase properties"""
        pass