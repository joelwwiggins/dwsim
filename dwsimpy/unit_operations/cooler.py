"""
Cooler unit operation for DWSIM Python implementation.
"""

from typing import Dict, Any
from .base_unit import BaseUnitOperation


class Cooler(BaseUnitOperation):
    """Cooler unit operation - removes heat from a stream"""

    def __init__(self, unit_id: str, config: Dict[str, Any]):
        super().__init__(unit_id, config)
        self.heat_duty = config.get('heat_duty', 0.0)  # W (negative for cooling)
        self.pressure_drop = config.get('pressure_drop', 0.0)  # Pa
        self.efficiency = config.get('efficiency', 1.0)  # dimensionless

    def solve(self) -> float:
        """Solve the cooler equations"""
        if len(self.inlet_streams) != 1:
            raise ValueError("Cooler requires exactly 1 inlet stream")

        if len(self.outlet_streams) != 1:
            raise ValueError("Cooler requires exactly 1 outlet stream")

        inlet_stream = self.inlet_streams[0]
        outlet_stream = self.outlet_streams[0]

        # Simple energy balance
        # Assuming constant specific heat capacity for now
        cp = 4186  # J/kg·K (water)
        mass_flow = inlet_stream.mass_flow_rate

        if mass_flow > 0:
            delta_t = (self.heat_duty * self.efficiency) / (mass_flow * cp)
            outlet_temp = inlet_stream.temperature + delta_t
        else:
            outlet_temp = inlet_stream.temperature

        outlet_pressure = inlet_stream.pressure - self.pressure_drop

        # Set outlet stream properties
        outlet_stream.mass_flow_rate = mass_flow
        outlet_stream.temperature = outlet_temp
        outlet_stream.pressure = outlet_pressure

        # Store results
        self.results = {
            'heat_duty': self.heat_duty,
            'efficiency': self.efficiency,
            'inlet_temperature': inlet_stream.temperature,
            'outlet_temperature': outlet_temp,
            'temperature_drop': inlet_stream.temperature - outlet_temp,
            'pressure_drop': self.pressure_drop
        }

        return 0.0  # Perfect convergence for simple cooler