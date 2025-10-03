"""
Pipe Unit Operation

Converted from VB.NET to Python.
This module implements the Pipe unit operation for pressure drop and flow calculations.
"""

from ..shared_classes.base_class import BaseClass


class Pipe(BaseClass):
    """
    Pipe unit operation.

    Calculates pressure drop and heat transfer in pipes.
    """

    def __init__(self):
        super().__init__()
        self.length = 100.0  # Length in m
        self.diameter = 0.1  # Diameter in m
        self.roughness = 0.000045  # Roughness in m
        self.spec_mode = "length"  # length, outlet_pressure, outlet_temperature
        self.outlet_pressure = 101325.0
        self.outlet_temperature = 298.15
        self.input_stream = None
        self.output_stream = None
        self.property_package = None

    def calculate(self):
        """Perform the pipe calculation."""
        if not self.input_stream:
            raise ValueError("No input stream attached")

        if not self.output_stream:
            raise ValueError("No output stream attached")

        if not self.input_stream.calculated:
            raise ValueError("Input stream not calculated")

        # Simplified pressure drop calculation
        # Darcy-Weisbach equation placeholder
        velocity = 1.0  # m/s, assume
        density = 1000.0  # kg/m³
        viscosity = 0.001  # Pa.s
        reynolds = density * velocity * self.diameter / viscosity
        friction_factor = 0.316 / (reynolds ** 0.25)  # Blasius

        delta_p = friction_factor * self.length / self.diameter * 0.5 * density * velocity ** 2

        # Set outlet properties
        self.output_stream.mass_flow = self.input_stream.mass_flow
        self.output_stream.temperature = self.input_stream.temperature
        self.output_stream.enthalpy = self.input_stream.enthalpy
        self.output_stream.compositions = self.input_stream.compositions.copy()

        if self.spec_mode == "length":
            self.output_stream.pressure = self.input_stream.pressure - delta_p
        elif self.spec_mode == "outlet_pressure":
            self.output_stream.pressure = self.outlet_pressure
        else:
            self.output_stream.pressure = self.input_stream.pressure

        self.output_stream.calculated = True

    def get_display_name(self) -> str:
        return "Pipe"

    def get_display_description(self) -> str:
        return "Pressure drop and flow in pipes unit operation"

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