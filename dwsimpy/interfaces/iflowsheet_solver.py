"""
IFlowsheetSolver Interface

Converted from VB.NET to Python.
This module defines the IFlowsheetSolver interface.
"""

from abc import ABC, abstractmethod
from typing import Any, List


class IFlowsheetSolver(ABC):
    """
    Interface for flowsheet solver objects.
    """

    @abstractmethod
    def solve_flowsheet(self, flowsheet: Any) -> List[Exception]:
        """Solve the flowsheet and return any exceptions."""
        pass