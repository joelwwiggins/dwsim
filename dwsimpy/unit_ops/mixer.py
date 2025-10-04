"""
Mixer Unit Operation

Converted from VB.NET to Python.
This module implements the Mixer unit operation for mixing streams.
"""

from ..shared_classes.base_class import BaseClass
from ..interfaces.iunit_operation import IUnitOperation
from typing import List, Any


class Mixer(BaseClass, IUnitOperation):
    """
    Mixer unit operation.

    Mixes multiple inlet streams into one outlet stream.
    """

    def __init__(self):
        super().__init__()
        self.pressure_behavior = "minimum"  # average, maximum, minimum
        self.input_streams = []
        self.output_stream = None
        self.property_package = None
        self._dimensions: List[Any] = []
        self._selected_equipment_type = "Mixer"
        self._equipment_types = ["Mixer"]

    @property
    def dimensions(self) -> List[Any]:
        """Get the dimensions of the unit operation."""
        return self._dimensions

    @dimensions.setter
    def dimensions(self, value: List[Any]):
        """Set the dimensions of the unit operation."""
        self._dimensions = value

    @property
    def selected_equipment_type(self) -> str:
        """Get the selected equipment type."""
        return self._selected_equipment_type

    @selected_equipment_type.setter
    def selected_equipment_type(self, value: str):
        """Set the selected equipment type."""
        self._selected_equipment_type = value

    @property
    def equipment_types(self) -> List[str]:
        """Get the list of available equipment types."""
        return self._equipment_types

    def calculate(self):
        """Perform the mixing calculation."""
        if not self.output_stream:
            raise ValueError("No output stream attached")

        total_mass_flow = 0.0
        total_enthalpy = 0.0
        pressure = 0.0

        for stream in self.input_streams:
            if not stream.calculated:
                raise ValueError("Inlet stream not calculated")

            mass_flow = stream.get_mass_flow()
            enthalpy = stream.get_enthalpy()
            stream_pressure = stream.get_pressure()

            total_mass_flow += mass_flow
            if enthalpy is not None:
                total_enthalpy += mass_flow * enthalpy

            # Pressure calculation
            if self.pressure_behavior == "minimum":
                if pressure == 0 or stream_pressure < pressure:
                    pressure = stream_pressure
            elif self.pressure_behavior == "maximum":
                if stream_pressure > pressure:
                    pressure = stream_pressure
            else:  # average
                pressure += stream_pressure

        if self.pressure_behavior == "average":
            pressure /= len(self.input_streams)

        # Set outlet stream properties
        self.output_stream.set_mass_flow(total_mass_flow)
        self.output_stream.set_pressure(pressure)

        # Calculate temperature via PH flash
        if total_mass_flow > 0:
            avg_enthalpy = total_enthalpy / total_mass_flow
            self.output_stream.set_enthalpy(avg_enthalpy)
            # For simplicity, assume temperature is average
            total_temp = 0.0
            for stream in self.input_streams:
                total_temp += stream.get_mass_flow() * stream.get_temperature()
            avg_temp = total_temp / total_mass_flow
            self.output_stream.set_temperature(avg_temp)

        self.output_stream.calculated = True

    def get_display_name(self) -> str:
        return "Mixer"

    def get_display_description(self) -> str:
        return "Stream mixing unit operation"

    def get_icon_bitmap(self):
        return None

    def display_edit_form(self):
        pass

    def update_edit_form(self):
        pass

    def close_edit_form(self):
        pass

    def clone_xml(self):
        return self.__class__()

    def clone_json(self):
        return self.__class__()