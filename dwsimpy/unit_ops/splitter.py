"""
Splitter Unit Operation

Converted from VB.NET to Python.
This module implements the Splitter unit operation for dividing streams.
"""

from ..shared_classes.base_class import BaseClass


class Splitter(BaseClass):
    """
    Splitter unit operation.

    Divides an inlet stream into multiple outlet streams based on ratios.
    """

    def __init__(self):
        super().__init__()
        self.operation_mode = "split_ratios"  # split_ratios, stream_mass_flow_spec, stream_mole_flow_spec
        self.ratios = [1.0, 0.0, 0.0]  # Split ratios for up to 3 outlets
        self.stream_flow_spec = 0.0
        self.stream2_flow_spec = 0.0
        self.input_stream = None
        self.output_streams = []

    def calculate(self):
        """Perform the splitting calculation."""
        if not self.input_stream:
            raise ValueError("No input stream attached")

        if not self.input_stream.calculated:
            raise ValueError("Input stream not calculated")

        if not self.output_streams:
            raise ValueError("No output streams attached")

        out_count = len(self.output_streams)

        # Adjust ratios based on operation mode and outlet count
        if self.operation_mode == "split_ratios":
            if out_count == 1:
                self.ratios = [1.0, 0.0, 0.0]
            elif out_count == 2:
                self.ratios[1] = 1.0 - self.ratios[0]
                self.ratios[2] = 0.0
            elif out_count == 3:
                self.ratios[2] = 1.0 - self.ratios[0] - self.ratios[1]

        # Copy properties from inlet to outlets
        inlet_mass_flow = self.input_stream.mass_flow
        inlet_temp = self.input_stream.temperature
        inlet_press = self.input_stream.pressure
        inlet_enthalpy = self.input_stream.enthalpy
        inlet_compositions = self.input_stream.compositions  # Assume dict of mole fractions

        for i, outlet in enumerate(self.output_streams):
            ratio = self.ratios[i] if i < len(self.ratios) else 0.0

            outlet.temperature = inlet_temp
            outlet.pressure = inlet_press
            outlet.enthalpy = inlet_enthalpy
            outlet.mass_flow = inlet_mass_flow * ratio
            outlet.compositions = inlet_compositions.copy()  # Same composition
            outlet.calculated = True

    @property
    def ratios(self):
        return self._ratios

    @ratios.setter
    def ratios(self, value):
        if len(value) != 3:
            raise ValueError("Ratios must be a list of 3 values")
        self._ratios = value

    def get_display_name(self) -> str:
        return "Splitter"

    def get_display_description(self) -> str:
        return "Stream splitting unit operation"

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