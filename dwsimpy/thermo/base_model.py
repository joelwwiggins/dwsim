"""
Base classes for thermodynamic models.

Converted from VB.NET to Python.
"""

from typing import List, Any


class IActivityCoefficientBase:
    """Interface for activity coefficient models."""

    def calc_activity_coefficients(self, T: float, Vx: List[float], otherargs: Any) -> List[float]:
        """Calculate activity coefficients."""
        raise NotImplementedError

    def calc_excess_enthalpy(self, T: float, Vx: List[float], otherargs: Any) -> float:
        """Calculate excess enthalpy."""
        raise NotImplementedError

    def calc_excess_heat_capacity(self, T: float, Vx: List[float], otherargs: Any) -> float:
        """Calculate excess heat capacity."""
        raise NotImplementedError