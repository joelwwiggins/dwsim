"""
Material stream class for DWSIM Python implementation.
"""

from typing import Dict, Any, Optional


class MaterialStream:
    """Represents a material stream in the flowsheet"""

    def __init__(self, stream_id: str, name: Optional[str] = None):
        self.id = stream_id
        self.name = name or stream_id

        # Thermodynamic properties
        self.temperature = 298.15  # K (25°C)
        self.pressure = 101325  # Pa (1 atm)
        self.mass_flow_rate = 0.0  # kg/s
        self.molar_flow_rate = 0.0  # mol/s

        # Composition (mole fractions)
        self.composition: Dict[str, float] = {}

        # Phase information
        self.phase = "liquid"  # liquid, vapor, or two-phase

    def set_temperature(self, temperature: float, unit: str = "K") -> None:
        """Set stream temperature"""
        if unit == "C":
            self.temperature = temperature + 273.15
        elif unit == "F":
            self.temperature = (temperature - 32) * 5/9 + 273.15
        else:  # K
            self.temperature = temperature

    def set_pressure(self, pressure: float, unit: str = "Pa") -> None:
        """Set stream pressure"""
        if unit == "bar":
            self.pressure = pressure * 1e5
        elif unit == "atm":
            self.pressure = pressure * 101325
        elif unit == "psi":
            self.pressure = pressure * 6894.76
        else:  # Pa
            self.pressure = pressure

    def set_flow_rate(self, flow_rate: float, unit: str = "kg/s",
                     basis: str = "mass") -> None:
        """Set flow rate"""
        if basis == "mass":
            if unit == "kg/h":
                self.mass_flow_rate = flow_rate / 3600
            elif unit == "kg/min":
                self.mass_flow_rate = flow_rate / 60
            else:  # kg/s
                self.mass_flow_rate = flow_rate
        else:  # molar
            if unit == "mol/h":
                self.molar_flow_rate = flow_rate / 3600
            elif unit == "mol/min":
                self.molar_flow_rate = flow_rate / 60
            else:  # mol/s
                self.molar_flow_rate = flow_rate

    def set_composition(self, composition: Dict[str, float]) -> None:
        """Set stream composition (mole fractions)"""
        total = sum(composition.values())
        if abs(total - 1.0) > 1e-6:
            # Normalize if not already normalized
            self.composition = {comp: frac/total for comp, frac in composition.items()}
        else:
            self.composition = composition.copy()

    def get_properties(self) -> Dict[str, Any]:
        """Get all stream properties"""
        return {
            'id': self.id,
            'name': self.name,
            'temperature': self.temperature,
            'pressure': self.pressure,
            'mass_flow_rate': self.mass_flow_rate,
            'molar_flow_rate': self.molar_flow_rate,
            'composition': self.composition.copy(),
            'phase': self.phase
        }

    def copy(self) -> 'MaterialStream':
        """Create a copy of this stream"""
        new_stream = MaterialStream(self.id, self.name)
        new_stream.temperature = self.temperature
        new_stream.pressure = self.pressure
        new_stream.mass_flow_rate = self.mass_flow_rate
        new_stream.molar_flow_rate = self.molar_flow_rate
        new_stream.composition = self.composition.copy()
        new_stream.phase = self.phase
        return new_stream