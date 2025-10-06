"""
Heat Exchanger Unit Operation

Converted from VB.NET to Python.
This module implements the Heat Exchanger unit operation for heat transfer between streams.
"""

from ..unit_operations.base_unit import BaseUnitOperation
from typing import Dict, Any


class HeatExchanger(BaseUnitOperation):
    """
    Heat Exchanger unit operation.

    Exchanges heat between hot and cold streams.
    """

    def __init__(self, unit_id: str, config: Dict[str, Any]):
        super().__init__(unit_id, config)
        self.ua = config.get("ua", 1000.0)  # Overall heat transfer coefficient * area in W/K
        self.area = config.get("area", 10.0)  # Heat transfer area in m²
        self.overall_heat_transfer_coeff = config.get("overall_heat_transfer_coeff", 100.0)  # U in W/m².K

    def solve(self) -> float:
        """Solve the heat exchanger equations"""
        if len(self.inlet_streams) != 2:
            raise ValueError("Heat exchanger requires exactly 2 inlet streams")

        if len(self.outlet_streams) != 2:
            raise ValueError("Heat exchanger requires exactly 2 outlet streams")

        hot_inlet = self.inlet_streams[0]  # Assume first inlet is hot
        cold_inlet = self.inlet_streams[1]  # Assume second inlet is cold
        hot_outlet = self.outlet_streams[0]  # Assume first outlet is hot
        cold_outlet = self.outlet_streams[1]  # Assume second outlet is cold

        # Simplified heat transfer calculation
        # Assume counter-current heat exchanger with energy balance

        # Calculate heat transfer
        # Q = U * A * ΔT_lm (log mean temperature difference)
        # For simplicity, assume ΔT = (T_hot_in - T_cold_in) / 2
        delta_t = (hot_inlet.temperature - cold_inlet.temperature) / 2.0

        # Calculate heat transfer rate
        q_transfer = self.ua * delta_t  # W

        # Limit by available heat in hot stream
        cp_hot = 4186  # J/kg·K approximation
        max_q_hot = hot_inlet.mass_flow_rate * cp_hot * (hot_inlet.temperature - cold_inlet.temperature)

        if max_q_hot > 0:
            q_actual = min(q_transfer, max_q_hot)
        else:
            q_actual = 0.0

        # Calculate outlet temperatures
        if hot_inlet.mass_flow_rate > 0:
            delta_t_hot = -q_actual / (hot_inlet.mass_flow_rate * cp_hot)
            hot_outlet.temperature = hot_inlet.temperature + delta_t_hot
        else:
            hot_outlet.temperature = hot_inlet.temperature

        if cold_inlet.mass_flow_rate > 0:
            delta_t_cold = q_actual / (cold_inlet.mass_flow_rate * cp_hot)
            cold_outlet.temperature = cold_inlet.temperature + delta_t_cold
        else:
            cold_outlet.temperature = cold_inlet.temperature

        # Set outlet stream properties
        for outlet in [hot_outlet, cold_outlet]:
            inlet = hot_inlet if outlet == hot_outlet else cold_inlet
            outlet.mass_flow_rate = inlet.mass_flow_rate
            outlet.pressure = inlet.pressure
            outlet.composition = inlet.composition.copy()

        # Store results
        self.results = {
            'heat_transfer_rate': q_actual,
            'ua': self.ua,
            'area': self.area,
            'hot_inlet_temp': hot_inlet.temperature,
            'hot_outlet_temp': hot_outlet.temperature,
            'cold_inlet_temp': cold_inlet.temperature,
            'cold_outlet_temp': cold_outlet.temperature,
            'delta_t': delta_t
        }

        return 0.0  # Perfect convergence for simplified model

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