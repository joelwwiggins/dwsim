#!/usr/bin/env python3
"""
Simple test script for property packages without pytest dependencies.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
from property_packages.ideal_property_package import IdealPropertyPackage
from property_packages.peng_robinson_property_package import PengRobinsonPropertyPackage
from property_packages.soave_redlich_kwong_property_package import SoaveRedlichKwongPropertyPackage


def test_ideal_property_package():
    """Test Ideal Property Package."""
    print("Testing Ideal Property Package...")
    pp = IdealPropertyPackage()

    # Add methane component
    pp.add_component({
        'id': 'methane',
        'name': 'Methane',
        'molecular_weight': 16.04,
        'formula': 'CH4'
    })

    # Test single component - just check that method exists and returns dict
    components = ['methane']
    temperature = 300.0
    pressure = 1.0

    result = pp.calculate_flash(temperature, pressure, {'methane': 1.0}, 'PT')
    assert isinstance(result, dict), "calculate_flash should return a dictionary"
    assert 'vapor_fraction' in result, "Result should contain vapor_fraction"
    print("✓ Single component flash test passed")

    # Test density
    props = pp.calculate_properties(temperature, pressure, {'methane': 1.0})
    density = props.get('density', 0.0)
    assert density > 0.0, f"Density should be positive, got {density}"
    print("✓ Density calculation test passed")


def test_peng_robinson_property_package():
    """Test Peng-Robinson Property Package."""
    print("Testing Peng-Robinson Property Package...")
    pp = PengRobinsonPropertyPackage()

    # Test compressibility factor
    temperature = 300.0
    pressure = 1.0
    composition = {'methane': 1.0}

    a_mix, b_mix = pp._calculate_mixture_parameters(temperature, composition)
    z = pp._calculate_compressibility_factor(a_mix, b_mix, temperature, pressure)
    assert 0.0 < z < 2.0, f"Compressibility factor should be between 0 and 2, got {z}"
    print("✓ Compressibility factor test passed")

    # Test fugacity coefficients
    phi = pp._calculate_fugacity_coefficients(temperature, pressure, z, a_mix, b_mix, composition)
    assert len(phi) == len(composition), f"Expected {len(composition)} fugacity coefficients, got {len(phi)}"
    assert all(phi[comp] > 0.0 for comp in phi), f"All fugacity coefficients should be positive, got {phi}"
    print("✓ Fugacity coefficients test passed")

    # Test density via interface
    props = pp.calculate_properties(temperature, pressure, composition)
    density = props.get('density', 0.0)
    assert density > 0.0, f"Density should be positive, got {density}"
    print("✓ Density calculation test passed")


def test_soave_redlich_kwong_property_package():
    """Test Soave-Redlich-Kwong Property Package."""
    print("Testing Soave-Redlich-Kwong Property Package...")
    pp = SoaveRedlichKwongPropertyPackage()

    # Test compressibility factor
    components = ['methane']
    mole_fractions = [1.0]
    temperature = 300.0
    pressure = 1.0

    a_mix, b_mix = pp._calculate_mixture_parameters(components, mole_fractions, temperature, pressure)
    z = pp._calculate_compressibility_factor(a_mix, b_mix, temperature, pressure)
    assert 0.0 < z < 2.0, f"Compressibility factor should be between 0 and 2, got {z}"
    print("✓ Compressibility factor test passed")

    # Test fugacity coefficients
    phi = pp._calculate_fugacity_coefficients(components, mole_fractions, temperature, pressure, z)
    assert len(phi) == len(components), f"Expected {len(components)} fugacity coefficients, got {len(phi)}"
    assert all(phi > 0.0), f"All fugacity coefficients should be positive, got {phi}"
    print("✓ Fugacity coefficients test passed")

    # Test density via interface
    props = pp.calculate_properties(temperature, pressure, {'methane': 1.0})
    density = props.get('density', 0.0)
    assert density > 0.0, f"Density should be positive, got {density}"
    print("✓ Density calculation test passed")


def test_property_package_comparison():
    """Compare different property packages."""
    print("Testing property package comparison...")
    ideal = IdealPropertyPackage()
    pr = PengRobinsonPropertyPackage()
    srk = SoaveRedlichKwongPropertyPackage()

    components = ['methane', 'ethane']
    mole_fractions = [0.6, 0.4]
    temperature = 250.0
    pressure = 10.0

    # Test that all packages return valid results
    for name, pp in [("Ideal", ideal), ("PR", pr), ("SRK", srk)]:
        result = pp.calculate_flash(temperature, pressure, {'methane': 0.6, 'ethane': 0.4}, 'PT')
        vapor_fraction = result.get('vapor_fraction', 0.0)
        vapor = result.get('vapor_composition', [])
        liquid = result.get('liquid_composition', [])
        assert 0.0 <= vapor_fraction <= 1.0, f"{name}: Invalid vapor fraction {vapor_fraction}"
        assert len(vapor) == len(mole_fractions), f"{name}: Invalid vapor composition length"
        assert len(liquid) == len(mole_fractions), f"{name}: Invalid liquid composition length"
        print(f"✓ {name} package interface test passed")

    # Test density differences
    ideal_props = ideal.calculate_properties(temperature, pressure, {'methane': 0.6, 'ethane': 0.4})
    pr_props = pr.calculate_properties(temperature, pressure, {'methane': 0.6, 'ethane': 0.4})
    srk_props = srk.calculate_properties(temperature, pressure, {'methane': 0.6, 'ethane': 0.4})

    ideal_density = ideal_props.get('density', 0.0)
    pr_density = pr_props.get('density', 0.0)
    srk_density = srk_props.get('density', 0.0)

    # EOS should give different results than ideal gas
    assert abs(pr_density - ideal_density) > 0.01, "PR density should differ from ideal"
    assert abs(srk_density - ideal_density) > 0.01, "SRK density should differ from ideal"
    print("✓ Density differences test passed")


def main():
    """Run all tests."""
    print("Running Property Package Tests...")
    print("=" * 50)

    try:
        test_ideal_property_package()
        print()
        test_peng_robinson_property_package()
        print()
        test_soave_redlich_kwong_property_package()
        print()
        test_property_package_comparison()
        print()
        print("=" * 50)
        print("✅ All tests passed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())