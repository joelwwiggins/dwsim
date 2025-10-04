"""
Factory classes for DWSIM Python implementation.
"""

from typing import Dict, Any, Type
from .interfaces.iunit_operation import IUnitOperation


class UnitOperationFactory:
    """Factory for creating unit operation instances"""

    _registry: Dict[str, Type[IUnitOperation]] = {}

    @classmethod
    def register(cls, unit_type: str, unit_class: Type[IUnitOperation]) -> None:
        """Register a unit operation class"""
        cls._registry[unit_type] = unit_class

    @classmethod
    def create_unit_operation(cls, unit_type: str, unit_id: str,
                            config: Dict[str, Any]) -> IUnitOperation:
        """Create a unit operation instance"""
        if unit_type not in cls._registry:
            raise ValueError(f"Unknown unit operation type: {unit_type}")

        unit_class = cls._registry[unit_type]
        return unit_class(unit_id, config)

    @classmethod
    def get_available_types(cls) -> Dict[str, str]:
        """Get available unit operation types"""
        return {
            "mixer": "Mixer unit operation",
            "heater": "Heater unit operation",
            "cooler": "Cooler unit operation",
            "valve": "Valve unit operation",
            "pump": "Pump unit operation",
            "splitter": "Splitter unit operation",
            "tank": "Tank unit operation",
            "compressor": "Compressor unit operation",
            "expander": "Expander unit operation",
            "heat_exchanger": "Heat exchanger unit operation",
            "pipe": "Pipe unit operation",
            "vessel": "Vessel unit operation",
            "component_separator": "Component separator unit operation",
            "filter": "Filter unit operation",
            "orifice_plate": "Orifice plate unit operation",
            "relief_valve": "Relief valve unit operation"
        }