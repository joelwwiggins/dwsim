"""
Base unit operation class for DWSIM Python implementation.
"""

from typing import Dict, Any, List, Optional
from ..interfaces.iunit_operation import IUnitOperation
from ..material_stream import MaterialStream


class BaseUnitOperation(IUnitOperation):
    """Base class for all unit operations"""

    def __init__(self, unit_id: str, config: Dict[str, Any]):
        self.id = unit_id
        self.name = config.get('label', unit_id)
        self.inlet_streams: List[MaterialStream] = []
        self.outlet_streams: List[MaterialStream] = []
        self.parameters: Dict[str, Any] = config.get('parameters', {})
        self.results: Dict[str, Any] = {}

    def add_inlet_stream(self, stream: MaterialStream) -> None:
        """Add an inlet stream"""
        self.inlet_streams.append(stream)

    def add_outlet_stream(self, stream: MaterialStream) -> None:
        """Add an outlet stream"""
        self.outlet_streams.append(stream)

    def initialize(self) -> None:
        """Initialize the unit operation"""
        self.results = {}

    def solve(self) -> float:
        """Solve the unit operation. Returns convergence error."""
        # Base implementation - override in subclasses
        return 0.0

    def get_results(self) -> Dict[str, Any]:
        """Get calculation results"""
        return self.results.copy()

    def set_parameter(self, name: str, value: Any) -> None:
        """Set a parameter value"""
        self.parameters[name] = value

    def get_parameter(self, name: str) -> Any:
        """Get a parameter value"""
        return self.parameters.get(name)

    def validate(self) -> bool:
        """Validate unit operation configuration"""
        return True

    @property
    def dimensions(self) -> List[Any]:
        """Get the dimensions of the unit operation."""
        return []

    @dimensions.setter
    def dimensions(self, value: List[Any]):
        """Set the dimensions of the unit operation."""
        pass

    @property
    def selected_equipment_type(self) -> str:
        """Get the selected equipment type."""
        return "default"

    @selected_equipment_type.setter
    def selected_equipment_type(self, value: str):
        """Set the selected equipment type."""
        pass

    @property
    def equipment_types(self) -> List[str]:
        """Get the list of available equipment types."""
        return ["default"]