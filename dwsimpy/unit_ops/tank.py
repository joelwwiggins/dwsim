"""
Tank Unit Operation

Converted from VB.NET to Python.
This module implements the Tank unit operation for liquid storage and mixing.
"""

from ..shared_classes.base_class import BaseClass


class Tank(BaseClass):
    """
    Tank unit operation.

    Stores liquid, performs mixing, calculates residence time.
    """

    def __init__(self):
        super().__init__()
        self.volume = 1.0  # Volume in m³
        self.residence_time = 0.0  # Residence time in seconds
        self.ignore_phase = True
        self.input_stream = None
        self.output_stream = None
        self.property_package = None

    def calculate(self):
        """Perform the tank calculation."""
        if not self.input_stream:
            raise ValueError("No input stream attached")

        if not self.output_stream:
            raise ValueError("No output stream attached")

        if not self.input_stream.calculated:
            raise ValueError("Input stream not calculated")

        # For tank, assume perfect mixing, outlet = inlet
        self.output_stream.mass_flow = self.input_stream.mass_flow
        self.output_stream.temperature = self.input_stream.temperature
        self.output_stream.pressure = self.input_stream.pressure
        self.output_stream.enthalpy = self.input_stream.enthalpy
        self.output_stream.compositions = self.input_stream.compositions.copy()

        # Calculate residence time
        if self.output_stream.mass_flow > 0:
            density = 1000.0  # Assume kg/m³
            volumetric_flow = self.output_stream.mass_flow / density  # m³/s
            self.residence_time = self.volume / volumetric_flow

        self.output_stream.calculated = True

    def get_display_name(self) -> str:
        return "Tank"

    def get_display_description(self) -> str:
        return "Liquid storage and mixing unit operation"

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