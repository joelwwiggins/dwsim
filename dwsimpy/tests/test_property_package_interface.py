"""
Test Property Package Interface
"""

import pytest
from dwsimpy.interfaces import (
    FlashCalculationType, FlashMethod, PhaseLabel, PhaseName,
    FlashCalculationResult, IFlashAlgorithm
)
from dwsimpy.property_packages import WilsonPropertyPackage


class TestFlashCalculationResult:
    """Test FlashCalculationResult class."""

    def test_initialization(self):
        """Test basic initialization."""
        result = FlashCalculationResult(
            base_mole_amount=1.0,
            kvalues=[1.0, 2.0],
            mixture_mole_amounts=[0.5, 0.5],
            vapor_phase_mole_amounts=[0.3, 0.2],
            liquid_phase1_mole_amounts=[0.2, 0.3],
            liquid_phase2_mole_amounts=[0.0, 0.0],
            solid_phase_mole_amounts=[0.0, 0.0]
        )

        assert result.base_mole_amount == 1.0
        assert result.kvalues == [1.0, 2.0]
        assert result.get_vapor_phase_mole_fraction() == 0.5
        assert result.get_liquid_phase1_mole_fraction() == 0.5

    def test_mole_fractions(self):
        """Test mole fraction calculations."""
        result = FlashCalculationResult(
            base_mole_amount=2.0,
            kvalues=[1.0, 1.0],
            mixture_mole_amounts=[1.0, 1.0],
            vapor_phase_mole_amounts=[0.6, 0.4],
            liquid_phase1_mole_amounts=[0.4, 0.6],
            liquid_phase2_mole_amounts=[0.0, 0.0],
            solid_phase_mole_amounts=[0.0, 0.0]
        )

        vapor_frac = result.get_vapor_phase_mole_fractions()
        liquid_frac = result.get_liquid_phase1_mole_fractions()

        assert vapor_frac == [0.6, 0.4]
        assert liquid_frac == [0.4, 0.6]


class TestWilsonPropertyPackage:
    """Test Wilson Property Package."""

    def test_initialization(self):
        """Test basic initialization."""
        pp = WilsonPropertyPackage()

        assert pp.name == "Wilson"
        assert pp.display_name == "Wilson Property Package"
        assert pp.is_functional is True
        assert pp.mobile_compatible is True

    def test_flash_algorithm(self):
        """Test flash algorithm property."""
        pp = WilsonPropertyPackage()
        alg = pp.flash_algorithm

        assert isinstance(alg, IFlashAlgorithm)
        assert alg.name == "Basic Nested Loops VLE"
        assert alg.algo_type == FlashMethod.NESTED_LOOPS_VLE

    def test_calculate_equilibrium(self):
        """Test equilibrium calculation."""
        pp = WilsonPropertyPackage()

        result = pp.calculate_equilibrium(
            calctype=FlashCalculationType.PRESSURE_TEMPERATURE,
            val1=298.15,  # T
            val2=101325.0,  # P
            mixmolefrac=[0.5, 0.5],
            initial_kval=[1.0, 1.0],
            initial_estimate=0.5
        )

        assert isinstance(result, FlashCalculationResult)
        assert result.calculated_temperature == 298.15
        assert result.calculated_pressure == 101325.0
        assert result.flash_algorithm_type == "Basic Nested Loops VLE"

    def test_clone(self):
        """Test cloning."""
        pp = WilsonPropertyPackage()
        pp.tag = "TestPP"

        cloned = pp.clone()

        assert cloned.name == "Wilson"
        assert cloned.tag == "TestPP_clone"
        assert cloned.unique_id != pp.unique_id

    def test_property_methods(self):
        """Test property package methods."""
        pp = WilsonPropertyPackage()

        assert pp.vapor_fugacity == "Wilson"
        assert pp.liquid_fugacity == "Wilson"
        assert pp.vapor_enthalpy_entropy_cp_cv == "Ideal Gas"
        assert pp.liquid_enthalpy_entropy_cp_cv == "Wilson"

    def test_aux_methods(self):
        """Test auxiliary methods."""
        pp = WilsonPropertyPackage()

        # Test heat capacity
        cp = pp.aux_cpm(PhaseLabel.LIQUID_MIXTURE, 298.15)
        assert cp == 36.0

        # Test molar mass
        mw = pp.aux_mmm(PhaseLabel.LIQUID_MIXTURE)
        assert mw == 18.0

        # Test compressibility
        z = pp.aux_z([0.5, 0.5], 298.15, 101325.0, PhaseName.LIQUID)
        assert z == 0.1

        z_vapor = pp.aux_z([0.5, 0.5], 298.15, 101325.0, PhaseName.VAPOR)
        assert z_vapor == 1.0