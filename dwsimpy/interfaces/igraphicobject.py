"""
IGraphicObject Interface

Converted from VB.NET to Python.
This module defines the IGraphicObject interface.
"""

from abc import ABC, abstractmethod
from typing import Any


class IGraphicObject(ABC):
    """
    Interface for graphic objects in the UI.
    """

    @property
    @abstractmethod
    def tag(self) -> str:
        """Get the tag/name of the object."""
        pass

    @abstractmethod
    def draw(self):
        """Draw the graphic object."""
        pass

    @abstractmethod
    def update_position(self, x: float, y: float):
        """Update the position of the object."""
        pass

    @abstractmethod
    def get_bounds(self) -> tuple[float, float, float, float]:
        """Get the bounding box (x, y, width, height)."""
        pass