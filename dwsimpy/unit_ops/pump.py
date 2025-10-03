"""
Pump Unit Operation

Converted from VB.NET to Python.
This module implements the Pump unit operation for pressure increase.
"""

from ..shared_classes.base_class import BaseClass


class Pump(BaseClass):
    """
    Pump unit operation.

    Increases pressure in a stream, calculating required power.
    """

    def __init__(self):
        super().__init__()
        self.calc_mode = "delta_p"  # delta_p, outlet_pressure, power
        self.delta_p = 0.0  # Pressure increase in Pa
        self.efficiency = 0.75  # Pump efficiency
        self.power = 0.0  # Required power in kW
        self.outlet_pressure = 0.0
        self.input_stream = None
        self.output_stream = None
        self.property_package = None

    def calculate(self):
        """Perform the pump calculation."""
        if not self.input_stream:
            raise ValueError("No input stream attached")

        if not self.output_stream:
            raise ValueError("No output stream attached")

        if not self.input_stream.calculated:
            raise ValueError("Input stream not calculated")

        wi = self.input_stream.mass_flow
        pi = self.input_stream.pressure
        hi = self.input_stream.enthalpy

        if self.calc_mode == "delta_p":
            # Calculate outlet pressure and enthalpy
            p2 = pi + self.delta_p
            # Assume incompressible: H2 = H1 + DeltaP / rho
            # For simplicity, use density approximation
            rho = 1000.0  # kg/m³, water
            delta_h = self.delta_p / rho  # kJ/kg
            h2 = hi + delta_h
            power = wi * delta_h / self.efficiency  # kW

        elif self.calc_mode == "outlet_pressure":
            p2 = self.outlet_pressure
            delta_p = p2 - pi
            rho = 1000.0
            delta_h = delta_p / rho
            h2 = hi + delta_h
            power = wi * delta_h / self.efficiency

        elif self.calc_mode == "power":
            # Given power, calculate delta_p
            delta_h = self.power * self.efficiency / wi
            rho = 1000.0
            delta_p = delta_h * rho
            p2 = pi + delta_p
            h2 = hi + delta_h

        # Set outlet properties
        self.output_stream.mass_flow = wi
        self.output_stream.pressure = p2
        self.output_stream.enthalpy = h2
        self.output_stream.compositions = self.input_stream.compositions.copy()

        # Simple temperature calculation (isentropic approximation)
        # In reality, would do PH flash
        gamma = 1.4  # For air, but approximate
        t_ratio = (p2 / pi) ** ((gamma - 1) / gamma)
        self.output_stream.temperature = self.input_stream.temperature * t_ratio

        self.output_stream.calculated = True

    def get_display_name(self) -> str:
        return "Pump"

    def get_display_description(self) -> str:
        return "Pressure increase unit operation"

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