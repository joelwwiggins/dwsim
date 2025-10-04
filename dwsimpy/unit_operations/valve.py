"""
Valve unit operation for DWSIM Python implementation.
"""

from typing import Dict, Any
from .base_unit import BaseUnitOperation


class Valve(BaseUnitOperation):
    """Valve unit operation - controls flow with pressure drop"""

    def __init__(self, unit_id: str, config: Dict[str, Any]):
        super().__init__(unit_id, config)
        self.pressure_drop = config.get('pressure_drop', 0.0)  # Pa

    def solve(self) -> float:
        """Solve the valve equations"""
        if len(self.inlet_streams) != 1:
            raise ValueError("Valve requires exactly 1 inlet stream")

        if len(self.outlet_streams) != 1:
            raise ValueError("Valve requires exactly 1 outlet stream")

        inlet_stream = self.inlet_streams[0]
        outlet_stream = self.outlet_streams[0]

        # Valve simply applies pressure drop
        outlet_stream.mass_flow_rate = inlet_stream.mass_flow_rate
        outlet_stream.temperature = inlet_stream.temperature
        outlet_stream.pressure = inlet_stream.pressure - self.pressure_drop

        # Store results
        self.results = {
            'pressure_drop': self.pressure_drop,
            'inlet_pressure': inlet_stream.pressure,
            'outlet_pressure': outlet_stream.pressure
        }

        return 0.0