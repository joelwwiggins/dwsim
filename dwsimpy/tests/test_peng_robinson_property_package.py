"""
Unit tests for Peng-Robinson Property Package.

Generated using pytest.
"""

import pytest
from dwsimpy.property_packages.peng_robinson_property_package import PengRobinsonPropertyPackage
from dwsimpy.interfaces.enums import FlashCalculationType


class MockCompound:
    def __init__(self, name, tc, pc, omega):
        self.name = name
        self.critical_temperature = tc
        self.critical_pressure = pc
        self.acentric_factor = omega


class TestPengRobinsonPropertyPackage:
    """Test cases for PengRobinsonPropertyPackage class."""

    @pytest.fixture
    def pp(self):
        """Fixture to create PengRobinsonPropertyPackage instance."""
        pp = PengRobinsonPropertyPackage()
        pp.selected_compounds = {
            'methane': MockCompound('methane', 190.6, 46e5, 0.008),
            'ethane': MockCompound('ethane', 305.3, 48.8e5, 0.098)
        }
        return pp

    def test_initialization(self, pp):
        """Test that property package initializes correctly."""
        assert pp.name == "Peng-Robinson"
        assert pp.selected_compounds is not None

    def test_calculate_a(self, pp):
        """Test calculation of a parameter."""
        comp = pp.selected_compounds['methane']
        a = pp.calculate_a(comp, 300)
        assert a > 0

    def test_calculate_b(self, pp):
        """Test calculation of b parameter."""
        comp = pp.selected_compounds['methane']
        b = pp.calculate_b(comp)
        assert b > 0

    def test_calculate_equilibrium_pt_flash(self, pp):
        """Test PT flash calculation."""
        composition = {'methane': 0.8, 'ethane': 0.2}
        result = pp.calculate_equilibrium(FlashCalculationType.PRESSURE_TEMPERATURE, 300, 50e5, list(composition.values()), [], None)
        assert result is not None
        assert result.calculated_temperature == 300
        assert result.calculated_pressure == 50e5