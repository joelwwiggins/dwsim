"""
IMaterialStream Interface

Converted from VB.NET to Python.
This module defines the IMaterialStream interface.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class IMaterialStream(ABC):
    """
    Interface for material stream objects.
    """

    @property
    @abstractmethod
    def temperature(self) -> float:
        """Get the temperature of the stream."""
        pass

    @temperature.setter
    @abstractmethod
    def temperature(self, value: float):
        """Set the temperature of the stream."""
        pass

    @property
    @abstractmethod
    def pressure(self) -> float:
        """Get the pressure of the stream."""
        pass

    @pressure.setter
    @abstractmethod
    def pressure(self, value: float):
        """Set the pressure of the stream."""
        pass

    @property
    @abstractmethod
    def mass_flow(self) -> float:
        """Get the mass flow rate."""
        pass

    @mass_flow.setter
    @abstractmethod
    def mass_flow(self, value: float):
        """Set the mass flow rate."""
        pass

    @property
    @abstractmethod
    def molar_flow(self) -> float:
        """Get the molar flow rate."""
        pass

    @molar_flow.setter
    @abstractmethod
    def molar_flow(self, value: float):
        """Set the molar flow rate."""
        pass

    @property
    @abstractmethod
    def composition(self) -> Dict[str, float]:
        """Get the composition (mole fractions)."""
        pass

    @composition.setter
    @abstractmethod
    def composition(self, value: Dict[str, float]):
        """Set the composition (mole fractions)."""
        pass

    @abstractmethod
    def calculate_properties(self):
        """Calculate thermodynamic properties."""
        pass