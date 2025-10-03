"""
Material Stream Implementation

Converted from VB.NET to Python.
This module implements the MaterialStream class for process streams.
"""

from typing import Dict, List, Any
from ..shared_classes.base_class import BaseClass


class Phase:
    """Represents a phase in the material stream."""

    def __init__(self):
        self.properties: Dict[str, float] = {}
        self.compounds: Dict[str, Any] = {}  # Will hold compound data


class MaterialStream(BaseClass):
    """
    Material Stream class for process simulation.

    Represents a stream of material with thermodynamic properties.
    """

    def __init__(self):
        super().__init__()
        self.phases: Dict[int, Phase] = {}  # Phase index to Phase object
        self.property_package = None
        self.property_package_id: str = ""
        self.defined_flow = "mass"  # mass, molar, volumetric
        self.force_phase = "global_def"
        self.override_single_compound_flash = False
        self.floating_table_basis = "default"
        self.total_energy_flow: float = 0.0
        self.maximum_dynamic_mass_flow: float = None
        self.last_solution_input_data = None

        # Initialize basic phases
        self._init_phases()

    def _init_phases(self):
        """Initialize standard phases."""
        self.phases[0] = Phase()  # Overall/Mixture
        self.phases[1] = Phase()  # Overall Liquid
        self.phases[2] = Phase()  # Vapor
        self.phases[3] = Phase()  # Liquid1
        self.phases[4] = Phase()  # Liquid2
        self.phases[7] = Phase()  # Solid

    @property
    def mixture(self):
        """Get the mixture/overall phase."""
        return self.phases.get(0)

    @property
    def vapor(self):
        """Get the vapor phase."""
        return self.phases.get(2)

    @property
    def overall_liquid(self):
        """Get the overall liquid phase."""
        return self.phases.get(1)

    @property
    def liquid1(self):
        """Get the first liquid phase."""
        return self.phases.get(3)

    @property
    def liquid2(self):
        """Get the second liquid phase."""
        return self.phases.get(4)

    @property
    def solid(self):
        """Get the solid phase."""
        return self.phases.get(7)

    def get_temperature(self) -> float:
        """Get stream temperature."""
        return self.mixture.properties.get("temperature", 298.15)

    def get_pressure(self) -> float:
        """Get stream pressure."""
        return self.mixture.properties.get("pressure", 101325.0)

    def get_mass_flow(self) -> float:
        """Get mass flow rate."""
        return self.mixture.properties.get("massflow", 0.0)

    def get_molar_flow(self) -> float:
        """Get molar flow rate."""
        return self.mixture.properties.get("molarflow", 0.0)

    def get_enthalpy(self) -> float:
        """Get specific enthalpy."""
        return self.mixture.properties.get("enthalpy", 0.0)

    def set_temperature(self, value: float):
        """Set stream temperature."""
        self.mixture.properties["temperature"] = value

    def set_pressure(self, value: float):
        """Set stream pressure."""
        self.mixture.properties["pressure"] = value

    def set_mass_flow(self, value: float):
        """Set mass flow rate."""
        self.mixture.properties["massflow"] = value

    def set_molar_flow(self, value: float):
        """Set molar flow rate."""
        self.mixture.properties["molarflow"] = value

    def set_enthalpy(self, value: float):
        """Set specific enthalpy."""
        self.mixture.properties["enthalpy"] = value

    def validate(self):
        """Validate the stream data."""
        # Basic validation
        if self.get_mass_flow() < 0:
            raise ValueError("Mass flow cannot be negative")
        if self.get_pressure() <= 0:
            raise ValueError("Pressure must be positive")
        if self.get_temperature() <= 0:
            raise ValueError("Temperature must be positive")

    def load_data(self, data: List[Any]) -> bool:
        """Load data from XML-like structure."""
        # Placeholder for deserialization
        return True

    def save_data(self) -> List[Any]:
        """Save data to XML-like structure."""
        # Placeholder for serialization
        return []

    def get_display_name(self) -> str:
        return "Material Stream"

    def get_display_description(self) -> str:
        return "Process material stream"

    def get_icon_bitmap(self):
        return None

    def display_edit_form(self):
        pass

    def update_edit_form(self):
        pass

    def close_edit_form(self):
        pass

    def clone_xml(self):
        return self.__class__()

    def clone_json(self):
        return self.__class__()