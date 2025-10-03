"""
Component Separator Unit Operation

Converted from VB.NET to Python.
This module implements the Component Separator unit operation for component-based separation.
"""

from ..shared_classes.base_class import BaseClass


class ComponentSeparationSpec:
    """Specification for component separation."""

    def __init__(self, component_id="", sep_spec="percent_inlet_mass", spec_value=0.0, spec_unit=""):
        self.component_id = component_id
        self.sep_spec = sep_spec  # mass_flow, molar_flow, percent_inlet_mass, percent_inlet_molar
        self.spec_value = spec_value
        self.spec_unit = spec_unit


class ComponentSeparator(BaseClass):
    """
    Component Separator unit operation.

    Separates components based on specified fractions.
    """

    def __init__(self):
        super().__init__()
        self.separation_specs = []  # List of ComponentSeparationSpec
        self.input_stream = None
        self.output_stream1 = None  # Product 1
        self.output_stream2 = None  # Product 2
        self.property_package = None

    def calculate(self):
        """Perform the component separator calculation."""
        if not self.input_stream:
            raise ValueError("No input stream attached")

        if not self.output_stream1 or not self.output_stream2:
            raise ValueError("Output streams not attached")

        if not self.input_stream.calculated:
            raise ValueError("Input stream not calculated")

        # Simplified: assume equal split for now
        total_flow = self.input_stream.mass_flow
        flow1 = total_flow / 2
        flow2 = total_flow / 2

        # Copy properties
        for stream in [self.output_stream1, self.output_stream2]:
            stream.temperature = self.input_stream.temperature
            stream.pressure = self.input_stream.pressure
            stream.enthalpy = self.input_stream.enthalpy
            stream.compositions = self.input_stream.compositions.copy()

        self.output_stream1.mass_flow = flow1
        self.output_stream2.mass_flow = flow2

        self.output_stream1.calculated = True
        self.output_stream2.calculated = True

    def get_display_name(self) -> str:
        return "Component Separator"

    def get_display_description(self) -> str:
        return "Component-based separation unit operation"

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