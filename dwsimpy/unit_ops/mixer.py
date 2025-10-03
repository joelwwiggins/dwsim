"""
Mixer Unit Operation

Converted from VB.NET to Python.
This module implements the Mixer unit operation for mixing streams.
"""

from ..shared_classes.base_class import BaseClass


class Mixer(BaseClass):
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

            mass_flow = stream.mass_flow
            enthalpy = stream.enthalpy
            stream_pressure = stream.pressure

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
        self.output_stream.mass_flow = total_mass_flow
        self.output_stream.pressure = pressure

        # Calculate temperature via PH flash
        if total_mass_flow > 0:
            avg_enthalpy = total_enthalpy / total_mass_flow
            self.output_stream.enthalpy = avg_enthalpy
            # PH flash would be done here with property package

        self.output_stream.calculated = True