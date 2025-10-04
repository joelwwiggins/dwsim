"""
Mixer unit operation for DWSIM Python implementation.
"""

from typing import Dict, Any
import numpy as np
from .base_unit import BaseUnitOperation


class Mixer(BaseUnitOperation):
    """Mixer unit operation - combines multiple inlet streams"""

    def __init__(self, unit_id: str, config: Dict[str, Any]):
        super().__init__(unit_id, config)
        self.pressure_drop = config.get('pressure_drop', 0.0)  # Pa

    def solve(self) -> float:
        """Solve the mixer equations"""
        if len(self.inlet_streams) < 2:
            raise ValueError("Mixer requires at least 2 inlet streams")

        if len(self.outlet_streams) != 1:
            raise ValueError("Mixer requires exactly 1 outlet stream")

        # Get inlet stream properties
        inlet_flows = []
        inlet_temps = []
        inlet_pressures = []

        for stream in self.inlet_streams:
            inlet_flows.append(stream.mass_flow_rate)
            inlet_temps.append(stream.temperature)
            inlet_pressures.append(stream.pressure)

        # Calculate outlet conditions
        total_flow = sum(inlet_flows)

        if total_flow == 0:
            # No flow case
            outlet_temp = np.mean(inlet_temps)
            outlet_pressure = min(inlet_pressures) - self.pressure_drop
        else:
            # Energy balance for temperature
            outlet_temp = sum(f * t for f, t in zip(inlet_flows, inlet_temps)) / total_flow
            # Pressure is minimum inlet pressure minus pressure drop
            outlet_pressure = min(inlet_pressures) - self.pressure_drop

        # Set outlet stream properties
        outlet_stream = self.outlet_streams[0]
        outlet_stream.mass_flow_rate = total_flow
        outlet_stream.temperature = outlet_temp
        outlet_stream.pressure = outlet_pressure

        # Store results
        self.results = {
            'total_flow': total_flow,
            'outlet_temperature': outlet_temp,
            'outlet_pressure': outlet_pressure,
            'inlet_streams': len(self.inlet_streams)
        }

        return 0.0  # Perfect convergence for mixer