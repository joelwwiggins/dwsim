"""
Unit tests for Peng-Robinson Property Package.

Generated using pytest.
"""

import pytest
from dwsimpy.property_packages.peng_robinson_property_package import PengRobinsonPropertyPackage
from dwsimpy.interfaces.enums import FlashCalculationType


class TestPengRobinsonPropertyPackage:
    """Test cases for PengRobinsonPropertyPackage class."""

    @pytest.fixture
    def pp(self):
        """Fixture to create PengRobinsonPropertyPackage instance."""
        pp = PengRobinsonPropertyPackage()
        # Add components from database
        pp.add_component({'id': 'methane'})
        pp.add_component({'id': 'ethane'})
        return pp

    def test_initialization(self, pp):
        """Test that property package initializes correctly."""
        assert pp.name == "Peng-Robinson EOS"
        assert len(pp.components) >= 0

    def test_add_component(self, pp):
        """Test adding components to property package."""
        initial_count = len(pp.components)
        pp.add_component({'id': 'water'})
        assert len(pp.components) == initial_count + 1

    def test_calculate_properties(self, pp):
        """Test calculation of thermodynamic properties."""
        composition = {'methane': 0.8, 'ethane': 0.2}
        result = pp.calculate_properties(300, 50e5, composition)
        assert 'temperature' in result
        assert 'pressure' in result
        assert 'density' in result
        assert 'enthalpy' in result
        assert 'entropy' in result

    def test_calculate_flash(self, pp):
        """Test PT flash calculation."""
        composition = {'methane': 0.8, 'ethane': 0.2}
        result = pp.calculate_flash(300, 50e5, composition, "PT")
        assert 'vapor_fraction' in result
        assert 'liquid_composition' in result
        assert 'vapor_composition' in result

    def test_calculate_viscosity_gas(self, pp):
        """Test gas viscosity calculation."""
        composition = {'methane': 0.8, 'ethane': 0.2}
        viscosity = pp.calculate_viscosity(300, 50e5, composition, 'gas')
        assert viscosity > 0
        assert viscosity < 1e-3  # Gas viscosity should be small

    def test_calculate_viscosity_liquid(self, pp):
        """Test liquid viscosity calculation."""
        composition = {'water': 1.0}
        viscosity = pp.calculate_viscosity(300, 50e5, composition, 'liquid')
        assert viscosity > 0
        assert viscosity < 1.0  # Liquid viscosity should be reasonable

    def test_calculate_thermal_conductivity_gas(self, pp):
        """Test gas thermal conductivity calculation."""
        composition = {'methane': 0.8, 'ethane': 0.2}
        conductivity = pp.calculate_thermal_conductivity(300, 50e5, composition, 'gas')
        assert conductivity > 0
        assert conductivity < 1.0  # Gas conductivity should be reasonable

    def test_calculate_thermal_conductivity_liquid(self, pp):
        """Test liquid thermal conductivity calculation."""
        composition = {'water': 1.0}
        conductivity = pp.calculate_thermal_conductivity(300, 50e5, composition, 'liquid')
        assert conductivity > 0
        assert conductivity < 10.0  # Liquid conductivity should be reasonable