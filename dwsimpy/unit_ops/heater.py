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
            wi = self.input_stream.get_mass_flow()
            hi = self.input_stream.get_enthalpy()
            q_added = self.delta_q * (self.efficiency / 100.0)

            if wi > 0:
                h2 = hi + q_added / wi  # kJ/kg
            else:
                h2 = hi

            # Set outlet properties
            self.output_stream.set_mass_flow(wi)
            self.output_stream.set_pressure(self.input_stream.get_pressure() - self.delta_p)
            self.output_stream.set_enthalpy(h2)
            self.output_stream.compositions = self.input_stream.compositions.copy()  # Assuming compositions exist

            # In reality, would do PH flash for temperature
            # For now, assume temperature change based on simple calculation
            cp_assumed = 4.18  # kJ/kg.K, water
            delta_t = q_added / (wi * cp_assumed) if wi > 0 else 0
            self.output_stream.set_temperature(self.input_stream.get_temperature() + delta_t)

        self.output_stream.calculated = True

    def get_display_name(self) -> str:
        return "Heater"

    def get_display_description(self) -> str:
        return "Energy addition unit operation"

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