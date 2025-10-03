"""
Unit tests for Heater.

Generated using pytest.
"""

import pytest
from dwsimpy.unit_ops.heater import Heater


class MockStream:
    def __init__(self, mass_flow=0, temperature=0, pressure=0, enthalpy=0, compositions=None):
        self.mass_flow = mass_flow
        self.temperature = temperature
        self.pressure = pressure
        self.enthalpy = enthalpy
        self.compositions = compositions or {}
        self.calculated = True


class TestHeater:
    """Test cases for Heater class."""

    @pytest.fixture
    def heater(self):
        """Fixture to create Heater instance."""
        return Heater()

    def test_initialization(self, heater):
        """Test that heater initializes correctly."""
        assert heater.delta_q == 0.0
        assert heater.efficiency == 100.0
        assert heater.delta_p == 0.0
        assert heater.calc_mode == "heat_added"
        assert heater.input_stream is None
        assert heater.output_stream is None

    def test_calculate_heat_added(self, heater):
        """Test calculation with heat added."""
        heater.delta_q = 100.0  # kW
        heater.efficiency = 90.0  # %
        heater.delta_p = 10000.0  # Pa
        heater.input_stream = MockStream(
            mass_flow=10.0,  # kg/s
            temperature=300.0,  # K
            pressure=101325.0,  # Pa
            enthalpy=500.0,  # kJ/kg
            compositions={"A": 0.5, "B": 0.5}
        )
        heater.output_stream = MockStream()

        heater.calculate()

        assert heater.output_stream.mass_flow == 10.0
        assert heater.output_stream.pressure == 101325.0 - 10000.0
        assert heater.output_stream.enthalpy == 500.0 + (100.0 * 0.9) / 10.0  # 500 + 9
        assert heater.output_stream.compositions == {"A": 0.5, "B": 0.5}
        assert heater.output_stream.calculated

    def test_no_input_stream(self, heater):
        """Test error when no input stream."""
        heater.output_stream = MockStream()
        with pytest.raises(ValueError):
            heater.calculate()

    def test_no_output_stream(self, heater):
        """Test error when no output stream."""
        heater.input_stream = MockStream()
        with pytest.raises(ValueError):
            heater.calculate()

    def test_uncalculated_input(self, heater):
        """Test error when input stream not calculated."""
        heater.input_stream = MockStream()
        heater.input_stream.calculated = False
        heater.output_stream = MockStream()
        with pytest.raises(ValueError):
            heater.calculate()