"""
Tank/Accumulator unit operation for DWSIM Python implementation.
"""

from typing import Dict, Any
from .base_unit import BaseUnitOperation


class Tank(BaseUnitOperation):
    """Tank unit operation - stores material with level control"""

    def __init__(self, unit_id: str, config: Dict[str, Any]):
        super().__init__(unit_id, config)
        self.volume = config.get('volume', 1.0)  # m³
        self.level = config.get('initial_level', 0.5)  # fraction

    def solve(self) -> float:
        """Solve the tank equations"""
        if len(self.inlet_streams) > 1:
            raise ValueError("Tank requires at most 1 inlet stream")

        if len(self.outlet_streams) != 1:
            raise ValueError("Tank requires exactly 1 outlet stream")

        inlet_flow = 0.0
        inlet_temp = 298.15
        inlet_pressure = 101325.0

        if self.inlet_streams:
            inlet_stream = self.inlet_streams[0]
            inlet_flow = inlet_stream.mass_flow_rate
            inlet_temp = inlet_stream.temperature
            inlet_pressure = inlet_stream.pressure

        outlet_stream = self.outlet_streams[0]

        # Simple tank model - outlet equals inlet (steady state)
        outlet_stream.mass_flow_rate = inlet_flow
        outlet_stream.temperature = inlet_temp
        outlet_stream.pressure = inlet_pressure

        # Update level based on flow (simplified)
        flow_balance = inlet_flow - inlet_flow  # Would be more complex in reality
        self.level = max(0.0, min(1.0, self.level + flow_balance * 0.001))  # Simplified level change

        # Store results
        self.results = {
            'volume': self.volume,
            'level': self.level,
            'level_percent': self.level * 100,
            'inlet_flow': inlet_flow,
            'outlet_flow': inlet_flow,
            'temperature': inlet_temp,
            'pressure': inlet_pressure
        }

        return 0.0