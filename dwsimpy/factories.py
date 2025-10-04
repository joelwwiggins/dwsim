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


# Import and register unit operations
try:
    from .unit_operations.mixer import Mixer
    UnitOperationFactory.register("mixer", Mixer)
except ImportError:
    pass

try:
    from .unit_operations.heater import Heater
    UnitOperationFactory.register("heater", Heater)
except ImportError:
    pass

try:
    from .unit_operations.cooler import Cooler
    UnitOperationFactory.register("cooler", Cooler)
except ImportError:
    pass

try:
    from .unit_operations.valve import Valve
    UnitOperationFactory.register("valve", Valve)
except ImportError:
    pass

try:
    from .unit_operations.pump import Pump
    UnitOperationFactory.register("pump", Pump)
except ImportError:
    pass

try:
    from .unit_operations.splitter import Splitter
    UnitOperationFactory.register("splitter", Splitter)
except ImportError:
    pass

try:
    from .unit_operations.tank import Tank
    UnitOperationFactory.register("tank", Tank)
except ImportError:
    pass

try:
    from .unit_ops.compressor import Compressor
    UnitOperationFactory.register("compressor", Compressor)
except ImportError:
    pass

try:
    from .unit_ops.expander import Expander
    UnitOperationFactory.register("expander", Expander)
except ImportError:
    pass

try:
    from .unit_ops.heat_exchanger import HeatExchanger
    UnitOperationFactory.register("heat_exchanger", HeatExchanger)
except ImportError:
    pass

try:
    from .unit_ops.pipe import Pipe
    UnitOperationFactory.register("pipe", Pipe)
except ImportError:
    pass

try:
    from .unit_ops.vessel import Vessel
    UnitOperationFactory.register("vessel", Vessel)
except ImportError:
    pass

try:
    from .unit_ops.component_separator import ComponentSeparator
    UnitOperationFactory.register("component_separator", ComponentSeparator)
except ImportError:
    pass

try:
    from .unit_ops.filter import Filter
    UnitOperationFactory.register("filter", Filter)
except ImportError:
    pass

try:
    from .unit_ops.orifice_plate import OrificePlate
    UnitOperationFactory.register("orifice_plate", OrificePlate)
except ImportError:
    pass

try:
    from .unit_ops.relief_valve import ReliefValve
    UnitOperationFactory.register("relief_valve", ReliefValve)
except ImportError:
    pass