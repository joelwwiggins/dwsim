"""
Base Class for Simulation Objects

Converted from VB.NET to Python.
This module defines the base class for all simulation objects.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseClass(ABC):
    """
    Abstract base class for simulation objects.

    All unit operations inherit from this class.
    """

    def __init__(self):
        self.class_id: str = ""
        self.flowsheet = None  # IFlowsheet
        self._is_dirty: bool = True
        self._can_use_previous_results: bool = False
        self.dynamics_spec = None  # DynamicsSpecType
        self.dynamics_only: bool = False
        self.extra_properties = {}
        self.extra_properties_unit_types = {}
        self.extra_properties_descriptions = {}
        self.extra_properties_types = {}
        self.visible: bool = True
        self.override_calculation_routine: bool = False
        self.store_detailed_debug_report: bool = False
        self.detailed_debug_report: str = ""
        self.is_functional: bool = True
        self.component_description: str = ""
        self.component_name: str = ""
        self.graphic_object = None  # IGraphicObject

    @property
    def is_dirty(self) -> bool:
        return self._is_dirty

    @property
    def can_use_previous_results(self) -> bool:
        return self._can_use_previous_results

    def clone(self) -> 'BaseClass':
        """Clone the object."""
        # Placeholder
        return self.__class__()

    def dispose(self):
        """Dispose resources."""
        pass

    def load_data(self, data: list) -> bool:
        """Load from XML data."""
        return True

    def save_data(self) -> list:
        """Save to XML data."""
        return []

    def __str__(self):
        if self.graphic_object:
            return self.graphic_object.tag
        return super().__str__()