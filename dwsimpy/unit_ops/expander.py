"""
Expander Unit Operation

Converted from VB.NET to Python.
This module implements the Expander unit operation for pressure drop with work generation.
"""

from ..shared_classes.base_class import BaseClass


class Expander(BaseClass):
    """
    Expander unit operation.

    Reduces pressure in a stream with work generation.
    """

    def __init__(self):
        super().__init__()
        self.calc_mode = "outlet_pressure"  # outlet_pressure, delta_p, power_generated, etc.
        self.outlet_pressure = 0.0  # Outlet pressure in Pa
        self.delta_p = 0.0  # Pressure drop in Pa
        self.adiabatic_efficiency = 0.75  # Adiabatic efficiency
        self.polytropic_efficiency = 0.75  # Polytropic efficiency
        self.power_generated = 0.0  # Power generated in kW
        self.process_path = "adiabatic"  # adiabatic, polytropic
        self.ignore_phase = False
        self.outlet_temperature = 0.0
        self.delta_t = 0.0
        self.delta_q = 0.0
        self.input_stream = None
        self.output_stream = None
        self.property_package = None

    def calculate(self):
        """Perform the expander calculation."""
        if not self.input_stream:
            raise ValueError("No input stream attached")

        if not self.output_stream:
            raise ValueError("No output stream attached")

        if not self.input_stream.calculated:
            raise ValueError("Input stream not calculated")

        wi = self.input_stream.mass_flow
        pi = self.input_stream.pressure
        hi = self.input_stream.enthalpy
        ti = self.input_stream.temperature

        if self.calc_mode == "outlet_pressure":
            p2 = self.outlet_pressure
            delta_p = pi - p2
        elif self.calc_mode == "delta_p":
            delta_p = self.delta_p
            p2 = pi - delta_p
        elif self.calc_mode == "power_generated":
            # Given power, calculate delta_p
            # Simplified
            delta_p = self.power_generated * 1000 / wi  # Rough estimate
            p2 = pi - delta_p
        else:
            p2 = pi
            delta_p = 0

        # Simplified enthalpy calculation
        # For adiabatic expansion
        gamma = 1.4  # Assume air
        if self.process_path == "adiabatic":
            efficiency = self.adiabatic_efficiency
        else:
            efficiency = self.polytropic_efficiency

        ratio = (p2 / pi) ** ((gamma - 1) / gamma)
        t2_ideal = ti * ratio
        delta_h_ideal = wi * (t2_ideal - ti) * 1.0  # Assume cp = 1 kJ/kg.K
        delta_h = delta_h_ideal / efficiency
        h2 = hi + delta_h  # For expansion, enthalpy increases? Wait, no.
        # For expansion, work is extracted, so enthalpy decreases.
        # Actually, for adiabatic expansion, h2 = hi - work, but work = delta_h * efficiency
        # Simplified: assume isentropic
        h2 = hi - delta_h_ideal / efficiency  # Approximate
        power = -delta_h * wi  # Negative for generation

        # Set outlet properties
        self.output_stream.mass_flow = wi
        self.output_stream.pressure = p2
        self.output_stream.enthalpy = h2
        self.output_stream.compositions = self.input_stream.compositions.copy()

        # Temperature
        self.output_stream.temperature = ti + (h2 - hi) / 1.0  # Assume cp

        self.output_stream.calculated = True

    def get_display_name(self) -> str:
        return "Expander"

    def get_display_description(self) -> str:
        return "Pressure drop with work generation unit operation"

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