"""
Unit tests for Valve.

Generated using pytest.
"""

import pytest
from dwsimpy.unit_ops.valve import Valve


class MockStream:
    def __init__(self, mass_flow=0, temperature=0, pressure=0, enthalpy=0, compositions=None):
        self.mass_flow = mass_flow
        self.temperature = temperature
        self.pressure = pressure
        self.enthalpy = enthalpy
        self.compositions = compositions or {}
        self.calculated = True


class TestValve:
    """Test cases for Valve class."""

    @pytest.fixture
    def valve(self):
        """Fixture to create Valve instance."""
        return Valve()

    def test_initialization(self, valve):
        """Test that valve initializes correctly."""
        assert valve.delta_p == 0.0
        assert valve.outlet_pressure == 0.0
        assert valve.input_stream is None
        assert valve.output_stream is None

    def test_calculate_delta_p(self, valve):
        """Test calculation with pressure drop."""
        valve.delta_p = 100000.0  # 1 bar
        valve.input_stream = MockStream(
            mass_flow=10.0,
            temperature=300.0,
            pressure=200000.0,
            enthalpy=50000.0,
            compositions={"A": 0.5, "B": 0.5}
        )
        valve.output_stream = MockStream()

        valve.calculate()

        assert valve.output_stream.mass_flow == 10.0
        assert valve.output_stream.temperature == 300.0
        assert valve.output_stream.pressure == 100000.0  # 200000 - 100000
        assert valve.output_stream.enthalpy == 50000.0
        assert valve.output_stream.compositions == {"A": 0.5, "B": 0.5}
        assert valve.output_stream.calculated

    def test_calculate_outlet_pressure(self, valve):
        """Test calculation with specified outlet pressure."""
        valve.outlet_pressure = 150000.0
        valve.input_stream = MockStream(pressure=200000.0)
        valve.output_stream = MockStream()

        valve.calculate()

        assert valve.output_stream.pressure == 150000.0

    def test_no_input_stream(self, valve):
        """Test error when no input stream."""
        valve.output_stream = MockStream()
        with pytest.raises(ValueError):
            valve.calculate()

    def test_no_output_stream(self, valve):
        """Test error when no output stream."""
        valve.input_stream = MockStream()
        with pytest.raises(ValueError):
            valve.calculate()

    def test_uncalculated_input(self, valve):
        """Test error when input stream not calculated."""
        valve.input_stream = MockStream()
        valve.input_stream.calculated = False
        valve.output_stream = MockStream()
        with pytest.raises(ValueError):
            valve.calculate()