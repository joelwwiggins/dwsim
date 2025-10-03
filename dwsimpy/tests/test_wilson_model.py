"""
Unit tests for WilsonModel.

Generated using pytest.
"""

import pytest
from dwsimpy.thermo.wilson_model import WilsonModel


class TestWilsonModel:
    """Test cases for WilsonModel class."""

    @pytest.fixture
    def model(self):
        """Fixture to create WilsonModel instance."""
        return WilsonModel()

    def test_initialization(self, model):
        """Test that model initializes with BIPs."""
        assert isinstance(model.bips, dict)
        # Add more assertions based on expected data

    def test_get_bips(self, model):
        """Test BIP retrieval."""
        # Assuming some data is loaded
        result = model.get_bips("50-00-0", "64-19-7")
        assert isinstance(result, float)

    def test_calc_activity_coefficients(self, model):
        """Test activity coefficient calculation."""
        T = 298.15  # K
        Vx = [0.5, 0.5]  # Molar fractions
        cas_ids = ["50-00-0", "64-19-7"]
        molar_volumes = [50.0, 60.0]  # cm³/mol
        otherargs = (cas_ids, molar_volumes)

        result = model.calc_activity_coefficients(T, Vx, otherargs)
        assert len(result) == len(Vx)
        assert all(isinstance(coeff, float) for coeff in result)
        assert all(coeff > 0 for coeff in result)

    def test_calc_excess_enthalpy(self, model):
        """Test excess enthalpy calculation."""
        T = 298.15
        Vx = [0.5, 0.5]
        cas_ids = ["50-00-0", "64-19-7"]
        molar_volumes = [50.0, 60.0]
        otherargs = (cas_ids, molar_volumes)

        result = model.calc_excess_enthalpy(T, Vx, otherargs)
        assert isinstance(result, float)

    def test_calc_excess_heat_capacity(self, model):
        """Test excess heat capacity calculation."""
        T = 298.15
        Vx = [0.5, 0.5]
        cas_ids = ["50-00-0", "64-19-7"]
        molar_volumes = [50.0, 60.0]
        otherargs = (cas_ids, molar_volumes)

        result = model.calc_excess_heat_capacity(T, Vx, otherargs)
        assert isinstance(result, float)

    def test_error_handling(self, model):
        """Test error handling for invalid inputs."""
        with pytest.raises(ValueError):
            model.calc_activity_coefficients(298.15, [0.5, 0.5],
                                             ("invalid", [50.0]))