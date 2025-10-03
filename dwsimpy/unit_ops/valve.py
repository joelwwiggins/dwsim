"""
Valve Unit Operation

Converted from VB.NET to Python.
This module implements the Valve unit operation for pressure drop.
"""

from ..shared_classes.base_class import BaseClass


class Valve(BaseClass):
    """
    Valve unit operation.

    Simulates pressure drop with isenthalpic expansion.
    """

    def __init__(self):
        super().__init__()
        self.delta_p = 0.0  # Pressure drop in Pa
        self.outlet_pressure = 0.0
        self.input_stream = None
        self.output_stream = None
        self.property_package = None

    def calculate(self):
        """Perform the valve calculation."""
        if not self.input_stream:
            raise ValueError("No input stream attached")

        if not self.output_stream:
            raise ValueError("No output stream attached")

        if not self.input_stream.calculated:
            raise ValueError("Input stream not calculated")

        # Copy properties from inlet
        self.output_stream.temperature = self.input_stream.temperature
        self.output_stream.enthalpy = self.input_stream.enthalpy  # Isenthalpic
        self.output_stream.mass_flow = self.input_stream.mass_flow
        self.output_stream.compositions = self.input_stream.compositions.copy()

        # Calculate outlet pressure
        if self.outlet_pressure > 0:
            self.output_stream.pressure = self.outlet_pressure
        else:
            self.output_stream.pressure = self.input_stream.pressure - self.delta_p

        # In reality, would do PH flash here to get correct temperature
        # For now, assume isothermal or use property package

        self.output_stream.calculated = True

    def get_display_name(self) -> str:
        return "Valve"

    def get_display_description(self) -> str:
        return "Pressure drop unit operation"

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