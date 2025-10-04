"""
Vessel Unit Operation

Converted from VB.NET to Python.
This module implements the Vessel unit operation for phase separation.
"""

from ..unit_operations.base_unit import BaseUnitOperation
from typing import Dict, Any


class Vessel(BaseUnitOperation):
    """
    Vessel unit operation.

    Separates phases via flash calculation.
    """

    def __init__(self, unit_id: str, config: Dict[str, Any]):
        super().__init__(unit_id, config)
        self.pressure_behavior = config.get("pressure_behavior", "minimum")  # average, maximum, minimum
        self.calculation_mode = config.get("calculation_mode", "adiabatic")  # adiabatic, legacy
        self.input_stream = None
        self.vapor_outlet = None
        self.liquid_outlet = None
        self.energy_stream = None
        self.property_package = None

    def calculate(self):
        """Perform the vessel calculation."""
        if not self.input_stream:
            raise ValueError("No input stream attached")

        if not self.vapor_outlet or not self.liquid_outlet:
            raise ValueError("Outlet streams not attached")

        if not self.input_stream.calculated:
            raise ValueError("Input stream not calculated")

        # Simplified flash: assume some vapor fraction
        vapor_fraction = 0.1  # Placeholder

        # Split flow
        total_flow = self.input_stream.mass_flow
        vapor_flow = total_flow * vapor_fraction
        liquid_flow = total_flow * (1 - vapor_fraction)

        # Assume same temperature and pressure
        temp = self.input_stream.temperature
        press = self.input_stream.pressure
        enthalpy = self.input_stream.enthalpy
        comps = self.input_stream.compositions

        # Vapor outlet
        self.vapor_outlet.mass_flow = vapor_flow
        self.vapor_outlet.temperature = temp
        self.vapor_outlet.pressure = press
        self.vapor_outlet.enthalpy = enthalpy  # Approximate
        self.vapor_outlet.compositions = comps.copy()
        self.vapor_outlet.calculated = True

        # Liquid outlet
        self.liquid_outlet.mass_flow = liquid_flow
        self.liquid_outlet.temperature = temp
        self.liquid_outlet.pressure = press
        self.liquid_outlet.enthalpy = enthalpy  # Approximate
        self.liquid_outlet.compositions = comps.copy()
        self.liquid_outlet.calculated = True

    def get_display_name(self) -> str:
        return "Vessel"

    def get_display_description(self) -> str:
        return "Phase separation unit operation"

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