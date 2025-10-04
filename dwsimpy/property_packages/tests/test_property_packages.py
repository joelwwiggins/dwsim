import pytest
import numpy as np
from dwsimpy.property_packages.ideal_property_package import IdealPropertyPackage
from dwsimpy.property_packages.peng_robinson_property_package import PengRobinsonPropertyPackage
from dwsimpy.property_packages.soave_redlich_kwong_property_package import SoaveRedlichKwongPropertyPackage


class TestIdealPropertyPackage:
    """Test cases for Ideal Property Package."""

    def setup_method(self):
        self.pp = IdealPropertyPackage()

    def test_single_component_vapor(self):
        """Test single component vapor phase."""
        components = ['methane']
        mole_fractions = [1.0]
        temperature = 300.0  # K
        pressure = 1.0  # atm

        vapor, liquid, vapor_fraction = self.pp.pt_flash(components, mole_fractions, temperature, pressure)

        assert vapor_fraction == 1.0
        assert np.allclose(vapor, [1.0])
        assert np.allclose(liquid, [0.0])

    def test_single_component_liquid(self):
        """Test single component liquid phase."""
        components = ['water']
        mole_fractions = [1.0]
        temperature = 300.0  # K
        pressure = 10.0  # atm (above vapor pressure)

        vapor, liquid, vapor_fraction = self.pp.pt_flash(components, mole_fractions, temperature, pressure)

        assert vapor_fraction == 0.0
        assert np.allclose(vapor, [0.0])
        assert np.allclose(liquid, [1.0])

    def test_binary_mixture(self):
        """Test binary mixture flash."""
        components = ['methane', 'ethane']
        mole_fractions = [0.5, 0.5]
        temperature = 200.0  # K
        pressure = 20.0  # atm

        vapor, liquid, vapor_fraction = self.pp.pt_flash(components, mole_fractions, temperature, pressure)

        assert 0.0 <= vapor_fraction <= 1.0
        assert np.allclose(np.sum(vapor), 1.0 if vapor_fraction > 0 else 0.0)
        assert np.allclose(np.sum(liquid), 1.0 if vapor_fraction < 1 else 0.0)


class TestPengRobinsonPropertyPackage:
    """Test cases for Peng-Robinson Property Package."""

    def setup_method(self):
        self.pp = PengRobinsonPropertyPackage()

    def test_single_component_critical(self):
        """Test single component at critical point."""
        components = ['methane']
        mole_fractions = [1.0]
        tc = 190.56  # K (methane critical temperature)
        pc = 45.99   # atm (methane critical pressure)

        vapor, liquid, vapor_fraction = self.pp.pt_flash(components, mole_fractions, tc, pc)

        # At critical point, should be single phase
        assert vapor_fraction == 1.0 or vapor_fraction == 0.0

    def test_compressibility_factor_calculation(self):
        """Test compressibility factor calculation."""
        components = ['methane']
        mole_fractions = [1.0]
        temperature = 300.0
        pressure = 1.0

        a_mix, b_mix = self.pp._calculate_mixture_parameters(components, mole_fractions, temperature, pressure)
        z = self.pp._calculate_compressibility_factor(a_mix, b_mix, temperature, pressure)

        assert z > 0.0
        assert z < 2.0  # Reasonable range for gases

    def test_fugacity_coefficients(self):
        """Test fugacity coefficient calculation."""
        components = ['methane']
        mole_fractions = [1.0]
        temperature = 300.0
        pressure = 1.0

        a_mix, b_mix = self.pp._calculate_mixture_parameters(components, mole_fractions, temperature, pressure)
        z = self.pp._calculate_compressibility_factor(a_mix, b_mix, temperature, pressure)
        phi = self.pp._calculate_fugacity_coefficients(components, mole_fractions, temperature, pressure, z)

        assert len(phi) == len(components)
        assert all(phi > 0.0)

    def test_density_calculation(self):
        """Test density calculation."""
        components = ['methane']
        mole_fractions = [1.0]
        temperature = 300.0
        pressure = 1.0

        density = self.pp.calculate_density(components, mole_fractions, temperature, pressure)

        assert density > 0.0
        # Methane density at STP should be around 0.7 kg/m³
        assert 0.1 < density < 10.0


class TestSoaveRedlichKwongPropertyPackage:
    """Test cases for Soave-Redlich-Kwong Property Package."""

    def setup_method(self):
        self.pp = SoaveRedlichKwongPropertyPackage()

    def test_single_component_srk(self):
        """Test single component with SRK EOS."""
        components = ['methane']
        mole_fractions = [1.0]
        temperature = 300.0
        pressure = 1.0

        vapor, liquid, vapor_fraction = self.pp.pt_flash(components, mole_fractions, temperature, pressure)

        assert vapor_fraction == 1.0  # Should be vapor at these conditions

    def test_srk_compressibility_factor(self):
        """Test SRK compressibility factor calculation."""
        components = ['methane']
        mole_fractions = [1.0]
        temperature = 300.0
        pressure = 1.0

        a_mix, b_mix = self.pp._calculate_mixture_parameters(components, mole_fractions, temperature, pressure)
        z = self.pp._calculate_compressibility_factor(a_mix, b_mix, temperature, pressure)

        assert z > 0.0
        assert z < 2.0

    def test_srk_fugacity_coefficients(self):
        """Test SRK fugacity coefficient calculation."""
        components = ['methane']
        mole_fractions = [1.0]
        temperature = 300.0
        pressure = 1.0

        a_mix, b_mix = self.pp._calculate_mixture_parameters(components, mole_fractions, temperature, pressure)
        z = self.pp._calculate_compressibility_factor(a_mix, b_mix, temperature, pressure)
        phi = self.pp._calculate_fugacity_coefficients(components, mole_fractions, temperature, pressure, z)

        assert len(phi) == len(components)
        assert all(phi > 0.0)

    def test_srk_density(self):
        """Test SRK density calculation."""
        components = ['methane']
        mole_fractions = [1.0]
        temperature = 300.0
        pressure = 1.0

        density = self.pp.calculate_density(components, mole_fractions, temperature, pressure)

        assert density > 0.0
        assert 0.1 < density < 10.0


class TestPropertyPackageComparison:
    """Compare different property packages."""

    def setup_method(self):
        self.ideal = IdealPropertyPackage()
        self.pr = PengRobinsonPropertyPackage()
        self.srk = SoaveRedlichKwongPropertyPackage()

    def test_consistent_interface(self):
        """Test that all packages implement the same interface."""
        components = ['methane', 'ethane']
        mole_fractions = [0.6, 0.4]
        temperature = 250.0
        pressure = 10.0

        # All should return valid results
        for pp in [self.ideal, self.pr, self.srk]:
            vapor, liquid, vapor_fraction = pp.pt_flash(components, mole_fractions, temperature, pressure)
            assert 0.0 <= vapor_fraction <= 1.0
            assert len(vapor) == len(components)
            assert len(liquid) == len(components)

    def test_density_differences(self):
        """Test that EOS packages give different densities than ideal."""
        components = ['methane']
        mole_fractions = [1.0]
        temperature = 300.0
        pressure = 10.0  # Higher pressure to see EOS effects

        ideal_density = self.ideal.calculate_density(components, mole_fractions, temperature, pressure)
        pr_density = self.pr.calculate_density(components, mole_fractions, temperature, pressure)
        srk_density = self.srk.calculate_density(components, mole_fractions, temperature, pressure)

        # EOS should give different results than ideal gas
        assert abs(pr_density - ideal_density) > 0.01
        assert abs(srk_density - ideal_density) > 0.01


if __name__ == "__main__":
    pytest.main([__file__])