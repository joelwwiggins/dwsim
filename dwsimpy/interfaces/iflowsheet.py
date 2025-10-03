"""
IFlowsheet Interface

Converted from VB.NET to Python.
This module defines the IFlowsheet interface.
"""

from abc import ABC, abstractmethod
from typing import Any


class IFlowsheet(ABC):
    """
    Interface for flowsheet objects.
    """

    @abstractmethod
    def add_unit_operation(self, unit_op: Any):
        """Add a unit operation to the flowsheet."""
        pass

    @abstractmethod
    def remove_unit_operation(self, unit_op: Any):
        """Remove a unit operation from the flowsheet."""
        pass

    @abstractmethod
    def get_unit_operations(self) -> list[Any]:
        """Get list of unit operations."""
        pass

    @abstractmethod
    def add_stream(self, stream: Any):
        """Add a stream to the flowsheet."""
        pass

    @abstractmethod
    def get_streams(self) -> list[Any]:
        """Get list of streams."""
        pass

    @abstractmethod
    def solve(self) -> bool:
        """Solve the flowsheet."""
        pass