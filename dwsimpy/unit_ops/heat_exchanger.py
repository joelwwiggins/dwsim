"""
Heat Exchanger Unit Operation

Converted from VB.NET to Python.
This module implements the Heat Exchanger unit operation for heat transfer between streams.
"""

from ..shared_classes.base_class import BaseClass


class HeatExchanger(BaseClass):
    """
    Heat Exchanger unit operation.

    Exchanges heat between hot and cold streams.
    """

    def __init__(self):
        super().__init__()
        self.calc_mode = "calc_both_temp"  # calc_temp_hot_out, calc_temp_cold_out, calc_both_temp, etc.
        self.ua = 1000.0  # Overall heat transfer coefficient * area in W/K
        self.area = 10.0  # Heat transfer area in m²
        self.overall_heat_transfer_coeff = 100.0  # U in W/m².K
        self.hot_stream_in = None
        self.hot_stream_out = None
        self.cold_stream_in = None
        self.cold_stream_out = None
        self.property_package = None

    def calculate(self):
        """Perform the heat exchanger calculation."""
        if not self.hot_stream_in or not self.hot_stream_out or not self.cold_stream_in or not self.cold_stream_out:
            raise ValueError("All streams must be attached")

        if not all(s.calculated for s in [self.hot_stream_in, self.cold_stream_in]):
            raise ValueError("Input streams not calculated")

        # Simplified heat balance
        # Assume counter-current, etc.

        # For simplicity, assume energy balance
        # Q = m_hot * cp_hot * (T_hot_in - T_hot_out) = m_cold * cp_cold * (T_cold_out - T_cold_in)

        # But for now, placeholder
        # Copy properties and adjust temperatures

        # Hot stream out
        self.hot_stream_out.mass_flow = self.hot_stream_in.mass_flow
        self.hot_stream_out.pressure = self.hot_stream_in.pressure
        self.hot_stream_out.compositions = self.hot_stream_in.compositions.copy()
        # Assume temperature drop
        self.hot_stream_out.temperature = self.hot_stream_in.temperature - 10  # Placeholder
        # Enthalpy adjustment
        cp_assumed = 4.18  # kJ/kg.K
        delta_h = -cp_assumed * 10
        self.hot_stream_out.enthalpy = self.hot_stream_in.enthalpy + delta_h

        # Cold stream out
        self.cold_stream_out.mass_flow = self.cold_stream_in.mass_flow
        self.cold_stream_out.pressure = self.cold_stream_in.pressure
        self.cold_stream_out.compositions = self.cold_stream_in.compositions.copy()
        # Assume temperature rise
        self.cold_stream_out.temperature = self.cold_stream_in.temperature + 10  # Placeholder
        delta_h_cold = cp_assumed * 10
        self.cold_stream_out.enthalpy = self.cold_stream_in.enthalpy + delta_h_cold

        self.hot_stream_out.calculated = True
        self.cold_stream_out.calculated = True

    def get_display_name(self) -> str:
        return "Heat Exchanger"

    def get_display_description(self) -> str:
        return "Heat transfer between streams unit operation"

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