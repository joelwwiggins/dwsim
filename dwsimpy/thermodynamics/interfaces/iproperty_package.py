"""
Interface for property packages in DWSIM Python implementation.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional


class IPropertyPackage(ABC):
    """Interface for thermodynamic property packages"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Property package name"""
        pass

    @property
    @abstractmethod
    def components(self) -> List[Dict[str, Any]]:
        """List of components in the package"""
        pass

    @abstractmethod
    def add_component(self, component: Dict[str, Any]) -> None:
        """Add a component to the package"""
        pass

    @abstractmethod
    def calculate_properties(self, temperature: float, pressure: float,
                           composition: Dict[str, float]) -> Dict[str, float]:
        """Calculate thermodynamic properties"""
        pass

    @abstractmethod
    def calculate_flash(self, temperature: float, pressure: float,
                       composition: Dict[str, float], flash_type: str) -> Dict[str, Any]:
        """Perform flash calculation"""
        pass

    @abstractmethod
    def calculate_enthalpy(self, temperature: float, pressure: float,
                          composition: Dict[str, float]) -> float:
        """Calculate mixture enthalpy"""
        pass

    @abstractmethod
    def calculate_entropy(self, temperature: float, pressure: float,
                         composition: Dict[str, float]) -> float:
        """Calculate mixture entropy"""
        pass

    @abstractmethod
    def calculate_viscosity(self, temperature: float, pressure: float,
                           composition: Dict[str, float], phase: str = 'liquid') -> float:
        """Calculate mixture viscosity"""
        pass

    @abstractmethod
    def calculate_thermal_conductivity(self, temperature: float, pressure: float,
                                      composition: Dict[str, float], phase: str = 'liquid') -> float:
        """Calculate mixture thermal conductivity"""
        pass