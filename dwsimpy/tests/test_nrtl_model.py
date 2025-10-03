"""
Unit tests for NRTLModel.

Generated using pytest.
"""

import pytest
from dwsimpy.thermo.nrtl_model import NRTLModel


class TestNRTLModel:
    """Test cases for NRTLModel class."""

    @pytest.fixture
    def model(self):
        """Fixture to create NRTLModel instance."""
        return NRTLModel()

    def test_initialization(self, model):
        """Test that model initializes with IPs."""
        assert isinstance(model.ips, dict)

    def test_get_ips(self, model):
        """Test IP retrieval."""
        # Assuming some data is loaded
        ip = model.get_ips("50-00-0", "64-19-7")
        assert hasattr(ip, 'a12')

    def test_calc_activity_coefficients(self, model):
        """Test activity coefficient calculation."""
        T = 298.15  # K
        Vx = [0.5, 0.5]  # Molar fractions
        cas_ids = ["50-00-0", "64-19-7"]
        otherargs = (cas_ids,)

        result = model.calc_activity_coefficients(T, Vx, otherargs)
        assert len(result) == len(Vx)
        assert all(isinstance(coeff, float) for coeff in result)
        assert all(coeff > 0 for coeff in result)

    def test_calc_excess_enthalpy(self, model):
        """Test excess enthalpy calculation."""
        T = 298.15
        Vx = [0.5, 0.5]
        cas_ids = ["50-00-0", "64-19-7"]
        otherargs = (cas_ids,)

        result = model.calc_excess_enthalpy(T, Vx, otherargs)
        assert isinstance(result, float)

    def test_calc_excess_heat_capacity(self, model):
        """Test excess heat capacity calculation."""
        T = 298.15
        Vx = [0.5, 0.5]
        cas_ids = ["50-00-0", "64-19-7"]
        otherargs = (cas_ids,)

        result = model.calc_excess_heat_capacity(T, Vx, otherargs)
        assert isinstance(result, float)

    def test_error_handling(self, model):
        """Test error handling for invalid inputs."""
        # NRTL handles invalid inputs by returning default values
        result = model.calc_activity_coefficients(298.15, [0.5, 0.5], ("invalid",))
        assert len(result) == 2  # Should still return results