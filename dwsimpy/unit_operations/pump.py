"""
Pump unit operation for DWSIM Python implementation.
"""

from typing import Dict, Any
from .base_unit import BaseUnitOperation


class Pump(BaseUnitOperation):
    """Pump unit operation - increases pressure"""

    def __init__(self, unit_id: str, config: Dict[str, Any]):
        super().__init__(unit_id, config)
        self.pressure_rise = config.get('pressure_rise', 0.0)  # Pa
        self.efficiency = config.get('efficiency', 1.0)

    def solve(self) -> float:
        """Solve the pump equations"""
        if len(self.inlet_streams) != 1:
            raise ValueError("Pump requires exactly 1 inlet stream")

        if len(self.outlet_streams) != 1:
            raise ValueError("Pump requires exactly 1 outlet stream")

        inlet_stream = self.inlet_streams[0]
        outlet_stream = self.outlet_streams[0]

        # Pump increases pressure
        outlet_stream.mass_flow_rate = inlet_stream.mass_flow_rate
        outlet_stream.temperature = inlet_stream.temperature
        outlet_stream.pressure = inlet_stream.pressure + self.pressure_rise

        # Store results
        self.results = {
            'pressure_rise': self.pressure_rise,
            'efficiency': self.efficiency,
            'inlet_pressure': inlet_stream.pressure,
            'outlet_pressure': outlet_stream.pressure
        }

        return 0.0