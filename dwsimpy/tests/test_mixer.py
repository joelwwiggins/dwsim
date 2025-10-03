"""
Unit tests for Mixer.

Generated using pytest.
"""

import pytest
from dwsimpy.unit_ops.mixer import Mixer


class MockStream:
    def __init__(self, mass_flow, pressure, enthalpy):
        self.mass_flow = mass_flow
        self.pressure = pressure
        self.enthalpy = enthalpy
        self.calculated = True


class TestMixer:
    """Test cases for Mixer class."""

    @pytest.fixture
    def mixer(self):
        """Fixture to create Mixer instance."""
        return Mixer()

    def test_initialization(self, mixer):
        """Test that mixer initializes correctly."""
        assert mixer.pressure_behavior == "minimum"
        assert mixer.input_streams == []
        assert mixer.output_stream is None

    def test_calculate_minimum_pressure(self, mixer):
        """Test mixing with minimum pressure."""
        mixer.pressure_behavior = "minimum"
        mixer.input_streams = [
            MockStream(10.0, 101325.0, 100.0),
            MockStream(5.0, 100000.0, 150.0)
        ]
        mixer.output_stream = MockStream(0, 0, 0)
        mixer.output_stream.calculated = False

        mixer.calculate()

        assert mixer.output_stream.mass_flow == 15.0
        assert mixer.output_stream.pressure == 100000.0  # minimum
        assert mixer.output_stream.enthalpy == (10*100 + 5*150) / 15
        assert mixer.output_stream.calculated

    def test_calculate_maximum_pressure(self, mixer):
        """Test mixing with maximum pressure."""
        mixer.pressure_behavior = "maximum"
        mixer.input_streams = [
            MockStream(10.0, 101325.0, 100.0),
            MockStream(5.0, 100000.0, 150.0)
        ]
        mixer.output_stream = MockStream(0, 0, 0)
        mixer.output_stream.calculated = False

        mixer.calculate()

        assert mixer.output_stream.pressure == 101325.0  # maximum

    def test_no_output_stream(self, mixer):
        """Test error when no output stream."""
        mixer.input_streams = [MockStream(10.0, 101325.0, 100.0)]
        with pytest.raises(ValueError):
            mixer.calculate()

    def test_uncalculated_input(self, mixer):
        """Test error when input stream not calculated."""
        mixer.input_streams = [MockStream(10.0, 101325.0, 100.0)]
        mixer.input_streams[0].calculated = False
        mixer.output_stream = MockStream(0, 0, 0)
        with pytest.raises(ValueError):
            mixer.calculate()