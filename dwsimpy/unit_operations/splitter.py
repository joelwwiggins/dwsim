"""
Splitter unit operation for DWSIM Python implementation.
"""

from typing import Dict, Any
from .base_unit import BaseUnitOperation


class Splitter(BaseUnitOperation):
    """Splitter unit operation - divides flow into multiple streams"""

    def __init__(self, unit_id: str, config: Dict[str, Any]):
        super().__init__(unit_id, config)
        self.split_ratios = config.get('split_ratios', [0.5, 0.5])  # Default 50/50 split

    def solve(self) -> float:
        """Solve the splitter equations"""
        if len(self.inlet_streams) != 1:
            raise ValueError("Splitter requires exactly 1 inlet stream")

        if len(self.outlet_streams) != len(self.split_ratios):
            raise ValueError("Number of outlet streams must match split ratios")

        inlet_stream = self.inlet_streams[0]
        inlet_flow = inlet_stream.mass_flow_rate

        # Split the flow according to ratios
        for i, (stream, ratio) in enumerate(zip(self.outlet_streams, self.split_ratios)):
            stream.mass_flow_rate = inlet_flow * ratio
            stream.temperature = inlet_stream.temperature
            stream.pressure = inlet_stream.pressure

        # Store results
        self.results = {
            'split_ratios': self.split_ratios,
            'inlet_flow': inlet_flow,
            'outlet_flows': [s.mass_flow_rate for s in self.outlet_streams]
        }

        return 0.0