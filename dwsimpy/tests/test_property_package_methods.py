"""
Unit tests for PropertyPackageMethods.

Generated using pytest.
"""

import pytest
from dwsimpy.core.property_package_methods import PropertyPackageMethods


class TestPropertyPackageMethods:
    """Test cases for PropertyPackageMethods class."""

    @pytest.fixture
    def methods(self):
        """Fixture to create PropertyPackageMethods instance."""
        return PropertyPackageMethods()

    def test_initialization(self, methods):
        """Test that methods initialize with default values."""
        assert isinstance(methods.vapor_fugacity, str)
        assert methods.vapor_thermal_conductivity == "Experimental / Ely-Hanley"
        assert methods.liquid_density == "Experimental / Rackett / COSTALD"

    def test_property_getters(self, methods):
        """Test property getters match attributes."""
        assert methods.vapor_fugacity_prop == methods.vapor_fugacity
        assert methods.liquid_viscosity_prop == methods.liquid_viscosity

    def test_modification(self, methods):
        """Test that properties can be modified."""
        methods.vapor_fugacity = "Custom Method"
        assert methods.vapor_fugacity == "Custom Method"
        assert methods.vapor_fugacity_prop == "Custom Method"