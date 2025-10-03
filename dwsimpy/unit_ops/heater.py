"""
Heater Unit Operation

Converted from VB.NET to Python.
This module implements the Heater unit operation for energy addition.
"""

from ..shared_classes.base_class import BaseClass


class Heater(BaseClass):
    """
    Heater unit operation.

    Adds heat to a stream, calculating outlet temperature via energy balance.
    """

    def __init__(self):
        super().__init__()
        self.delta_q = 0.0  # Heat added in kW
        self.efficiency = 100.0  # Efficiency in %
        self.delta_p = 0.0  # Pressure drop in Pa
        self.calc_mode = "heat_added"  # heat_added, etc.
        self.input_stream = None
        self.output_stream = None
        self.property_package = None

    def calculate(self):
        """Perform the heater calculation."""
        if not self.input_stream:
            raise ValueError("No input stream attached")

        if not self.output_stream:
            raise ValueError("No output stream attached")

        if not self.input_stream.calculated:
            raise ValueError("Input stream not calculated")

        if self.calc_mode == "heat_added":
            # Calculate outlet enthalpy
            wi = self.input_stream.mass_flow
            hi = self.input_stream.enthalpy
            q_added = self.delta_q * (self.efficiency / 100.0)

            if wi > 0:
                h2 = hi + q_added / wi  # kJ/kg
            else:
                h2 = hi

            # Set outlet properties
            self.output_stream.mass_flow = wi
            self.output_stream.pressure = self.input_stream.pressure - self.delta_p
            self.output_stream.enthalpy = h2
            self.output_stream.compositions = self.input_stream.compositions.copy()

            # In reality, would do PH flash for temperature
            # For now, assume temperature change based on simple calculation
            cp_assumed = 4.18  # kJ/kg.K, water
            delta_t = q_added / (wi * cp_assumed) if wi > 0 else 0
            self.output_stream.temperature = self.input_stream.temperature + delta_t

        self.output_stream.calculated = True