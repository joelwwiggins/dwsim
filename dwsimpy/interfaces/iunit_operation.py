"""
IUnitOperation Interface

Converted from VB.NET to Python.
This module defines the IUnitOperation interface.
"""

from abc import ABC, abstractmethod
from typing import Any, List


class IUnitOperation(ABC):
    """
    Interface for unit operation objects.
    """

    @property
    @abstractmethod
    def dimensions(self) -> List[Any]:
        """Get the dimensions of the unit operation."""
        pass

    @dimensions.setter
    @abstractmethod
    def dimensions(self, value: List[Any]):
        """Set the dimensions of the unit operation."""
        pass

    @property
    @abstractmethod
    def selected_equipment_type(self) -> str:
        """Get the selected equipment type."""
        pass

    @selected_equipment_type.setter
    @abstractmethod
    def selected_equipment_type(self, value: str):
        """Set the selected equipment type."""
        pass

    @property
    @abstractmethod
    def equipment_types(self) -> List[str]:
        """Get the list of available equipment types."""
        pass