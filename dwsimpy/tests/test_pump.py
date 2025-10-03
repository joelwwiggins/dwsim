"""
Unit tests for Pump.

Generated using pytest.
"""

import pytest
from dwsimpy.unit_ops.pump import Pump


class MockStream:
    def __init__(self, mass_flow=0, temperature=0, pressure=0, enthalpy=0, compositions=None):
        self.mass_flow = mass_flow
        self.temperature = temperature
        self.pressure = pressure
        self.enthalpy = enthalpy
        self.compositions = compositions or {}
        self.calculated = True


class TestPump:
    """Test cases for Pump class."""

    @pytest.fixture
    def pump(self):
        """Fixture to create Pump instance."""
        return Pump()

    def test_initialization(self, pump):
        """Test that pump initializes correctly."""
        assert pump.calc_mode == "delta_p"
        assert pump.delta_p == 0.0
        assert pump.efficiency == 0.75
        assert pump.power == 0.0
        assert pump.input_stream is None
        assert pump.output_stream is None

    def test_calculate_delta_p(self, pump):
        """Test calculation with delta_p mode."""
        pump.delta_p = 100000.0  # Pa
        pump.efficiency = 0.8
        pump.input_stream = MockStream(
            mass_flow=10.0,  # kg/s
            temperature=300.0,  # K
            pressure=101325.0,  # Pa
            enthalpy=500.0,  # kJ/kg
            compositions={"A": 0.5, "B": 0.5}
        )
        pump.output_stream = MockStream()

        pump.calculate()

        assert pump.output_stream.mass_flow == 10.0
        assert pump.output_stream.pressure == 101325.0 + 100000.0
        delta_h = 100000.0 / 1000.0  # 100 kJ/kg
        assert pump.output_stream.enthalpy == 500.0 + delta_h
        assert pump.output_stream.compositions == {"A": 0.5, "B": 0.5}
        assert pump.output_stream.calculated

    def test_calculate_outlet_pressure(self, pump):
        """Test calculation with outlet_pressure mode."""
        pump.calc_mode = "outlet_pressure"
        pump.outlet_pressure = 200000.0  # Pa
        pump.input_stream = MockStream(pressure=101325.0, enthalpy=500.0, mass_flow=10.0)
        pump.output_stream = MockStream()

        pump.calculate()

        assert pump.output_stream.pressure == 200000.0

    def test_no_input_stream(self, pump):
        """Test error when no input stream."""
        pump.output_stream = MockStream()
        with pytest.raises(ValueError):
            pump.calculate()

    def test_no_output_stream(self, pump):
        """Test error when no output stream."""
        pump.input_stream = MockStream()
        with pytest.raises(ValueError):
            pump.calculate()

    def test_uncalculated_input(self, pump):
        """Test error when input stream not calculated."""
        pump.input_stream = MockStream()
        pump.input_stream.calculated = False
        pump.output_stream = MockStream()
        with pytest.raises(ValueError):
            pump.calculate()