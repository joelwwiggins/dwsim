"""
Energy Stream implementation for DWSIM Python.
Represents energy/power flow between unit operations.
"""

from typing import Optional, Dict, Any
from .interfaces.imaterial_stream import IMaterialStream


class EnergyStream(IMaterialStream):
    """Energy stream for carrying power/heat between unit operations"""

    def __init__(self, stream_id: str, name: str = ""):
        self.id = stream_id
        self.name = name or stream_id
        self._energy_flow: Optional[float] = None  # Power in J/s (Watts)
        self._temperature_low: float = 0.0  # K
        self._temperature_high: float = 2000.0  # K

    @property
    def energy_flow(self) -> Optional[float]:
        """Power/energy flow in J/s (Watts)"""
        return self._energy_flow

    @energy_flow.setter
    def energy_flow(self, value: Optional[float]):
        self._energy_flow = value

    @property
    def temperature_low(self) -> float:
        """Lower temperature limit in K"""
        return self._temperature_low

    @temperature_low.setter
    def temperature_low(self, value: float):
        self._temperature_low = value

    @property
    def temperature_high(self) -> float:
        """Upper temperature limit in K"""
        return self._temperature_high

    @temperature_high.setter
    def temperature_high(self, value: float):
        self._temperature_high = value

    def set_energy_flow_kw(self, energy_flow_kw: float):
        """Set energy flow in kW"""
        self._energy_flow = energy_flow_kw * 1000  # Convert kW to W

    def get_energy_flow_kw(self) -> Optional[float]:
        """Get energy flow in kW"""
        return self._energy_flow / 1000 if self._energy_flow is not None else None

    def assign(self, source_stream: 'EnergyStream'):
        """Copy properties from another energy stream"""
        self.energy_flow = source_stream.energy_flow
        self.temperature_low = source_stream.temperature_low
        self.temperature_high = source_stream.temperature_high

    def get_properties(self) -> Dict[str, Any]:
        """Get stream properties for results display"""
        return {
            "energy_flow_watts": self.energy_flow,
            "energy_flow_kw": self.get_energy_flow_kw(),
            "temperature_low": self.temperature_low,
            "temperature_high": self.temperature_high,
            "stream_type": "energy"
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for saving"""
        return {
            "id": self.id,
            "name": self.name,
            "type": "energy_stream",
            "energy_flow": self.energy_flow,
            "temperature_low": self.temperature_low,
            "temperature_high": self.temperature_high
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnergyStream':
        """Deserialize from dictionary"""
        stream = cls(data["id"], data.get("name", ""))
        stream.energy_flow = data.get("energy_flow")
        stream.temperature_low = data.get("temperature_low", 0.0)
        stream.temperature_high = data.get("temperature_high", 2000.0)
        return stream

    # IMaterialStream interface methods (minimal implementation for energy streams)
    @property
    def temperature(self) -> Optional[float]:
        return None  # Energy streams don't have a single temperature

    @temperature.setter
    def temperature(self, value: Optional[float]):
        pass  # Not applicable for energy streams

    @property
    def pressure(self) -> Optional[float]:
        return None  # Energy streams don't have pressure

    @pressure.setter
    def pressure(self, value: Optional[float]):
        pass  # Not applicable for energy streams

    @property
    def mass_flow_rate(self) -> Optional[float]:
        return None  # Energy streams carry power, not mass

    @mass_flow_rate.setter
    def mass_flow_rate(self, value: Optional[float]):
        pass  # Not applicable for energy streams

    @property
    def composition(self) -> Optional[Dict[str, float]]:
        return None  # Energy streams don't have composition

    @composition.setter
    def composition(self, value: Optional[Dict[str, float]]):
        pass  # Not applicable for energy streams

    @property
    def property_package(self):
        return None  # Energy streams don't use property packages

    @property_package.setter
    def property_package(self, value):
        pass  # Not applicable for energy streams