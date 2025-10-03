"""
Unit tests for Splitter.

Generated using pytest.
"""

import pytest
from dwsimpy.unit_ops.splitter import Splitter


class MockStream:
    def __init__(self, mass_flow=0, temperature=0, pressure=0, enthalpy=0, compositions=None):
        self.mass_flow = mass_flow
        self.temperature = temperature
        self.pressure = pressure
        self.enthalpy = enthalpy
        self.compositions = compositions or {}
        self.calculated = True


class TestSplitter:
    """Test cases for Splitter class."""

    @pytest.fixture
    def splitter(self):
        """Fixture to create Splitter instance."""
        return Splitter()

    def test_initialization(self, splitter):
        """Test that splitter initializes correctly."""
        assert splitter.operation_mode == "split_ratios"
        assert splitter.ratios == [1.0, 0.0, 0.0]
        assert splitter.input_stream is None
        assert splitter.output_streams == []

    def test_calculate_two_outlets(self, splitter):
        """Test splitting into two outlets."""
        splitter.ratios = [0.6, 0.0, 0.0]  # Will be adjusted to [0.6, 0.4, 0.0]
        splitter.input_stream = MockStream(
            mass_flow=100.0,
            temperature=300.0,
            pressure=101325.0,
            enthalpy=50000.0,
            compositions={"A": 0.5, "B": 0.5}
        )
        splitter.output_streams = [MockStream(), MockStream()]

        splitter.calculate()

        assert splitter.output_streams[0].mass_flow == 60.0
        assert splitter.output_streams[1].mass_flow == 40.0
        assert splitter.output_streams[0].temperature == 300.0
        assert splitter.output_streams[1].temperature == 300.0
        assert splitter.output_streams[0].compositions == {"A": 0.5, "B": 0.5}
        assert splitter.output_streams[1].compositions == {"A": 0.5, "B": 0.5}

    def test_calculate_three_outlets(self, splitter):
        """Test splitting into three outlets."""
        splitter.ratios = [0.5, 0.3, 0.0]  # Will be adjusted to [0.5, 0.3, 0.2]
        splitter.input_stream = MockStream(mass_flow=100.0)
        splitter.output_streams = [MockStream(), MockStream(), MockStream()]

        splitter.calculate()

        assert splitter.output_streams[0].mass_flow == 50.0
        assert splitter.output_streams[1].mass_flow == 30.0
        assert splitter.output_streams[2].mass_flow == 20.0

    def test_no_input_stream(self, splitter):
        """Test error when no input stream."""
        splitter.output_streams = [MockStream()]
        with pytest.raises(ValueError):
            splitter.calculate()

    def test_uncalculated_input(self, splitter):
        """Test error when input stream not calculated."""
        splitter.input_stream = MockStream()
        splitter.input_stream.calculated = False
        splitter.output_streams = [MockStream()]
        with pytest.raises(ValueError):
            splitter.calculate()

    def test_no_output_streams(self, splitter):
        """Test error when no output streams."""
        splitter.input_stream = MockStream()
        with pytest.raises(ValueError):
            splitter.calculate()

    def test_ratios_setter(self, splitter):
        """Test ratios property setter."""
        splitter.ratios = [0.3, 0.4, 0.3]
        assert splitter.ratios == [0.3, 0.4, 0.3]

        with pytest.raises(ValueError):
            splitter.ratios = [0.5, 0.5]  # Wrong length