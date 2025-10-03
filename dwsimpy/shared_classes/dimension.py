"""
Dimension Class

Converted from VB.NET to Python.
This module implements the Dimension class for unit operations.
"""

import uuid
from typing import Any


class Dimension:
    """
    Dimension class for unit operations.

    Represents dimensions with name, value, and units.
    """

    def __init__(self):
        self.id: str = str(uuid.uuid4())
        self.name = None  # DimensionName
        self.value: float = 0.0
        self.is_user_defined: bool = False
        self.user_defined_value: float = 0.0

    def save_data(self) -> list:
        """Save to XML data."""
        # Placeholder for serialization
        return []

    def load_data(self, data: list) -> bool:
        """Load from XML data."""
        # Placeholder for deserialization
        return True

    def get_display_name(self) -> str:
        """Get display name."""
        name_map = {
            "Area": "Area",
            "Diameter": "Diameter",
            "Flow": "Flow",
            "Efficiency": "Efficiency",
            "Head": "Head",
            "HeatDuty": "Heat Duty",
            "Height": "Height",
            "Length": "Length",
            "NotDefined": "Not Defined",
            "NumberOfCells": "Number of Cells",
            "NumberofPackings": "Number of Packings",
            "NumberOfSections": "Number of Sections",
            "NumberOfTrays": "Number of Trays",
            "NumberOfTubes": "Number of Tubes",
            "Power": "Power",
            "Pressure": "Pressure",
            "PressureDifference": "Pressure Difference",
            "Volume": "Volume",
        }
        return name_map.get(str(self.name), "Not Defined")

    def get_units_type(self):
        """Get units type."""
        unit_map = {
            "Area": "area",
            "Diameter": "diameter",
            "Efficiency": "none",
            "Flow": "volumetricFlow",
            "Head": "distance",
            "HeatDuty": "heatflow",
            "Height": "distance",
            "Length": "distance",
            "NotDefined": "none",
            "NumberOfCells": "none",
            "NumberofPackings": "none",
            "NumberOfSections": "none",
            "NumberOfTrays": "none",
            "NumberOfTubes": "none",
            "Power": "heatflow",
            "Pressure": "pressure",
            "PressureDifference": "deltaP",
            "Volume": "volume",
        }
        return unit_map.get(str(self.name), "none")