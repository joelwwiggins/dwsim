"""
Reactor unit operation for DWSIM Python implementation.
"""

from typing import Dict, Any
from .base_unit import BaseUnitOperation


class Reactor(BaseUnitOperation):
    """Reactor unit operation - models chemical reactions"""

    def __init__(self, unit_id: str, config: Dict[str, Any]):
        super().__init__(unit_id, config)
        self.reactor_type = config.get('reactor_type', 'cstr')  # cstr, pfr, batch
        self.volume = config.get('volume', 1.0)  # m³
        self.temperature = config.get('temperature', 298.15)  # K
        self.pressure = config.get('pressure', 101325.0)  # Pa
        # Simple reaction: A -> B with first-order kinetics
        self.reaction_rate_constant = config.get('reaction_rate_constant', 0.1)  # 1/s
        self.conversion = config.get('conversion', 0.5)  # Target conversion

    def solve(self) -> float:
        """Solve the reactor equations"""
        if len(self.inlet_streams) != 1:
            raise ValueError("Reactor requires exactly 1 inlet stream")

        if len(self.outlet_streams) != 1:
            raise ValueError("Reactor requires exactly 1 outlet stream")

        inlet_stream = self.inlet_streams[0]
        outlet_stream = self.outlet_streams[0]

        # Simple reaction model: A -> B
        # Assume inlet contains 'A' and we produce 'B'

        if 'methane' not in inlet_stream.composition:
            # No reactant, just pass through
            outlet_stream.mass_flow_rate = inlet_stream.mass_flow_rate
            outlet_stream.temperature = self.temperature
            outlet_stream.pressure = self.pressure
            outlet_stream.composition = inlet_stream.composition.copy()
        else:
            # Simple CSTR model with first-order reaction
            reactant_conc = inlet_stream.composition.get('methane', 0.0)
            flow_rate = inlet_stream.mass_flow_rate  # kg/s

            # Residence time = volume / volumetric_flow_rate
            # Assume density = 1 kg/L for simplicity
            volumetric_flow = flow_rate  # L/s (approximate)
            residence_time = self.volume / volumetric_flow if volumetric_flow > 0 else 0

            # First-order reaction: C_out = C_in / (1 + k*τ)
            # where τ is residence time
            if residence_time > 0:
                outlet_conc = reactant_conc / (1 + self.reaction_rate_constant * residence_time)
                conversion = 1 - (outlet_conc / reactant_conc) if reactant_conc > 0 else 0
            else:
                outlet_conc = reactant_conc
                conversion = 0

            # Update composition
            outlet_composition = inlet_stream.composition.copy()
            outlet_composition['methane'] = outlet_conc

            # Assume product 'ethane' is produced
            product_produced = reactant_conc - outlet_conc
            outlet_composition['ethane'] = outlet_composition.get('ethane', 0.0) + product_produced

            # Normalize composition
            total = sum(outlet_composition.values())
            if total > 0:
                outlet_composition = {k: v/total for k, v in outlet_composition.items()}

            # Set outlet properties
            outlet_stream.mass_flow_rate = inlet_stream.mass_flow_rate
            outlet_stream.temperature = self.temperature
            outlet_stream.pressure = self.pressure
            outlet_stream.composition = outlet_composition

        # Store results
        self.results = {
            'reactor_type': self.reactor_type,
            'volume': self.volume,
            'temperature': self.temperature,
            'pressure': self.pressure,
            'reaction_rate_constant': self.reaction_rate_constant,
            'conversion': conversion if 'conversion' in locals() else 0
        }

        return 0.0  # Perfect convergence for simplified model