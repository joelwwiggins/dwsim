"""
Unit tests for MaterialStream.

Generated using pytest.
"""

import pytest
from dwsimpy.streams.material_stream import MaterialStream


class TestMaterialStream:
    """Test cases for MaterialStream class."""

    @pytest.fixture
    def stream(self):
        """Fixture to create MaterialStream instance."""
        return MaterialStream()

    def test_initialization(self, stream):
        """Test that stream initializes correctly."""
        assert isinstance(stream.phases, dict)
        assert 0 in stream.phases  # Mixture phase
        assert 2 in stream.phases  # Vapor phase
        assert stream.property_package is None
        assert stream.defined_flow == "mass"

    def test_phase_properties(self, stream):
        """Test phase property access."""
        assert stream.mixture is not None
        assert stream.vapor is not None
        assert stream.overall_liquid is not None
        assert stream.liquid1 is not None
        assert stream.liquid2 is not None
        assert stream.solid is not None

    def test_getters_setters(self, stream):
        """Test property getters and setters."""
        stream.set_temperature(350.0)
        stream.set_pressure(200000.0)
        stream.set_mass_flow(100.0)
        stream.set_molar_flow(50.0)
        stream.set_enthalpy(50000.0)

        assert stream.get_temperature() == 350.0
        assert stream.get_pressure() == 200000.0
        assert stream.get_mass_flow() == 100.0
        assert stream.get_molar_flow() == 50.0
        assert stream.get_enthalpy() == 50000.0

    def test_validation(self, stream):
        """Test stream validation."""
        stream.set_mass_flow(100.0)
        stream.set_pressure(101325.0)
        stream.set_temperature(300.0)

        # Should not raise
        stream.validate()

        # Test negative mass flow
        stream.set_mass_flow(-10.0)
        with pytest.raises(ValueError):
            stream.validate()

        # Reset
        stream.set_mass_flow(100.0)

        # Test negative pressure
        stream.set_pressure(-101325.0)
        with pytest.raises(ValueError):
            stream.validate()

        # Reset
        stream.set_pressure(101325.0)

        # Test negative temperature
        stream.set_temperature(-300.0)
        with pytest.raises(ValueError):
            stream.validate()

    def test_default_values(self, stream):
        """Test default property values."""
        assert stream.get_temperature() == 298.15  # Default
        assert stream.get_pressure() == 101325.0   # Default
        assert stream.get_mass_flow() == 0.0       # Default
        assert stream.get_enthalpy() == 0.0        # Default