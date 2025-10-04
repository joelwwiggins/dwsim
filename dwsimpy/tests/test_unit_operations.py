#!/usr/bin/env python3
"""
Unit tests for unit operations in DWSIM Python implementation.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from dwsimpy.material_stream import MaterialStream
from dwsimpy.unit_operations.mixer import Mixer
from dwsimpy.unit_operations.heater import Heater
from dwsimpy.unit_operations.cooler import Cooler
from dwsimpy.unit_operations.valve import Valve
from dwsimpy.unit_operations.pump import Pump
from dwsimpy.unit_operations.splitter import Splitter
from dwsimpy.property_packages.ideal_property_package import IdealPropertyPackage
from dwsimpy.property_packages.peng_robinson_property_package import PengRobinsonPropertyPackage


class TestMaterialStream:
    """Test MaterialStream functionality."""

    def setup_method(self):
        self.pp = IdealPropertyPackage()
        self.stream = MaterialStream("test_stream")
        self.stream.property_package = self.pp

    def test_stream_creation(self):
        """Test stream creation and basic properties."""
        assert self.stream.name == "test_stream"
        assert self.stream.temperature == 298.15  # Default
        assert self.stream.pressure == 101325  # Default (1 atm in Pa)
        assert self.stream.mass_flow_rate == 0.0

    def test_stream_properties(self):
        """Test setting and getting stream properties."""
        self.stream.temperature = 373.15  # 100°C
        self.stream.pressure = 2e5  # 2 bar
        self.stream.mass_flow_rate = 1.0  # kg/s

        assert self.stream.temperature == 373.15
        assert self.stream.pressure == 2e5
        assert self.stream.mass_flow_rate == 1.0

    def test_composition_setting(self):
        """Test composition setting and validation."""
        composition = {'methane': 0.8, 'ethane': 0.2}
        self.stream.set_composition(composition)

        # Should be stored in composition attribute
        assert self.stream.composition == composition


class TestMixer:
    """Test Mixer unit operation."""

    def setup_method(self):
        self.pp = IdealPropertyPackage()
        self.mixer = Mixer("test_mixer", {})

        # Create inlet streams
        self.inlet1 = MaterialStream("inlet1")
        self.inlet1.property_package = self.pp
        self.inlet1.temperature = 300.0
        self.inlet1.pressure = 101325
        self.inlet1.mass_flow_rate = 1.0
        self.inlet1.set_composition({'methane': 1.0})

        self.inlet2 = MaterialStream("inlet2")
        self.inlet2.property_package = self.pp
        self.inlet2.temperature = 320.0
        self.inlet2.pressure = 101325
        self.inlet2.mass_flow_rate = 1.0
        self.inlet2.set_composition({'methane': 1.0})

        self.outlet = MaterialStream("outlet")
        self.outlet.property_package = self.pp

    def test_mixer_creation(self):
        """Test mixer creation."""
        assert self.mixer.name == "test_mixer"
        assert len(self.mixer.inlet_streams) == 0
        assert len(self.mixer.outlet_streams) == 0

    def test_mixer_connectivity(self):
        """Test connecting streams to mixer."""
        self.mixer.add_inlet_stream(self.inlet1)
        self.mixer.add_inlet_stream(self.inlet2)
        self.mixer.add_outlet_stream(self.outlet)

        assert len(self.mixer.inlet_streams) == 2
        assert len(self.mixer.outlet_streams) == 1

    def test_mixer_calculation(self):
        """Test mixer calculation."""
        self.mixer.add_inlet_stream(self.inlet1)
        self.mixer.add_inlet_stream(self.inlet2)
        self.mixer.add_outlet_stream(self.outlet)

        self.mixer.solve()

        # Check mass balance
        expected_flow = self.inlet1.mass_flow_rate + self.inlet2.mass_flow_rate
        assert abs(self.outlet.mass_flow_rate - expected_flow) < 1e-6

        # Check pressure (should be minimum inlet pressure)
        assert self.outlet.pressure == 101325

        # Check temperature (energy balance - simplified)
        expected_temp = (self.inlet1.temperature * self.inlet1.mass_flow_rate +
                        self.inlet2.temperature * self.inlet2.mass_flow_rate) / expected_flow
        assert abs(self.outlet.temperature - expected_temp) < 1e-6


class TestHeater:
    """Test Heater unit operation."""

    def setup_method(self):
        self.pp = PengRobinsonPropertyPackage()  # Use PR for enthalpy calculations
        self.heater = Heater("test_heater", {'outlet_temperature': 400.0})

        # Create inlet stream
        self.inlet = MaterialStream("inlet")
        self.inlet.property_package = self.pp
        self.inlet.temperature = 300.0
        self.inlet.pressure = 101325
        self.inlet.mass_flow_rate = 1.0
        self.inlet.set_composition({'methane': 1.0})

        self.outlet = MaterialStream("outlet")
        self.outlet.property_package = self.pp

    def test_heater_creation(self):
        """Test heater creation."""
        assert self.heater.name == "test_heater"
        assert self.heater.outlet_temperature == 400.0

    def test_heater_connectivity(self):
        """Test connecting streams to heater."""
        self.heater.add_inlet_stream(self.inlet)
        self.heater.add_outlet_stream(self.outlet)

        assert len(self.heater.inlet_streams) == 1
        assert len(self.heater.outlet_streams) == 1

    def test_heater_calculation(self):
        """Test heater calculation."""
        self.heater.add_inlet_stream(self.inlet)
        self.heater.add_outlet_stream(self.outlet)

        self.heater.solve()

        # Check temperature
        assert abs(self.outlet.temperature - 400.0) < 1e-6

        # Check pressure (should be same)
        assert abs(self.outlet.pressure - self.inlet.pressure) < 1e-6

        # Check mass flow (should be same)
        assert abs(self.outlet.mass_flow_rate - self.inlet.mass_flow_rate) < 1e-6

        # Check composition (should be same)
        inlet_comp = self.inlet.composition
        outlet_comp = self.outlet.composition
        for comp in inlet_comp:
            assert abs(inlet_comp[comp] - outlet_comp[comp]) < 1e-6


class TestValve:
    """Test Valve unit operation."""

    def setup_method(self):
        self.pp = IdealPropertyPackage()
        self.valve = Valve("test_valve", {'outlet_pressure': 101325})

        # Create inlet stream
        self.inlet = MaterialStream("inlet")
        self.inlet.property_package = self.pp
        self.inlet.temperature = 300.0
        self.inlet.pressure = 5e5  # 5 bar
        self.inlet.mass_flow_rate = 1.0
        self.inlet.set_composition({'methane': 1.0})

        self.outlet = MaterialStream("outlet")
        self.outlet.property_package = self.pp

    def test_valve_creation(self):
        """Test valve creation."""
        assert self.valve.name == "test_valve"
        assert self.valve.outlet_pressure == 101325

    def test_valve_calculation(self):
        """Test valve calculation (isenthalpic expansion)."""
        self.valve.add_inlet_stream(self.inlet)
        self.valve.add_outlet_stream(self.outlet)

        self.valve.solve()

        # Check pressure
        assert abs(self.outlet.pressure - 101325) < 1e-6

        # Check mass flow (should be same)
        assert abs(self.outlet.mass_flow_rate - self.inlet.mass_flow_rate) < 1e-6

        # Check composition (should be same)
        inlet_comp = self.inlet.composition
        outlet_comp = self.outlet.composition
        for comp in inlet_comp:
            assert abs(inlet_comp[comp] - outlet_comp[comp]) < 1e-6

        # Temperature should be same (Joule-Thomson effect not implemented)
        assert abs(self.outlet.temperature - self.inlet.temperature) < 1e-6


class TestPump:
    """Test Pump unit operation."""

    def setup_method(self):
        self.pp = IdealPropertyPackage()
        self.pump = Pump("test_pump", {'outlet_pressure': 5e5})

        # Create inlet stream
        self.inlet = MaterialStream("inlet")
        self.inlet.property_package = self.pp
        self.inlet.temperature = 300.0
        self.inlet.pressure = 101325  # 1 atm
        self.inlet.mass_flow_rate = 1.0
        self.inlet.set_composition({'water': 1.0})

        self.outlet = MaterialStream("outlet")
        self.outlet.property_package = self.pp

    def test_pump_creation(self):
        """Test pump creation."""
        assert self.pump.name == "test_pump"
        assert self.pump.outlet_pressure == 5e5

    def test_pump_calculation(self):
        """Test pump calculation."""
        self.pump.add_inlet_stream(self.inlet)
        self.pump.add_outlet_stream(self.outlet)

        self.pump.solve()

        # Check pressure
        assert abs(self.outlet.pressure - 5e5) < 1e-6

        # Check mass flow (should be same)
        assert abs(self.outlet.mass_flow_rate - self.inlet.mass_flow_rate) < 1e-6

        # Check composition (should be same)
        inlet_comp = self.inlet.composition
        outlet_comp = self.outlet.composition
        for comp in inlet_comp:
            assert abs(inlet_comp[comp] - outlet_comp[comp]) < 1e-6

        # Temperature should be same (compression heating not implemented)
        assert abs(self.outlet.temperature - self.inlet.temperature) < 1e-6


class TestSplitter:
    """Test Splitter unit operation."""

    def setup_method(self):
        self.pp = IdealPropertyPackage()
        self.splitter = Splitter("test_splitter", {'split_ratios': [0.3, 0.7]})

        # Create inlet stream
        self.inlet = MaterialStream("inlet")
        self.inlet.property_package = self.pp
        self.inlet.temperature = 300.0
        self.inlet.pressure = 101325
        self.inlet.mass_flow_rate = 2.0
        self.inlet.set_composition({'methane': 1.0})

        self.outlet1 = MaterialStream("outlet1")
        self.outlet1.property_package = self.pp

        self.outlet2 = MaterialStream("outlet2")
        self.outlet2.property_package = self.pp

    def test_splitter_creation(self):
        """Test splitter creation."""
        assert self.splitter.name == "test_splitter"
        assert self.splitter.split_ratios == [0.3, 0.7]

    def test_splitter_calculation(self):
        """Test splitter calculation."""
        self.splitter.add_inlet_stream(self.inlet)
        self.splitter.add_outlet_stream(self.outlet1)
        self.splitter.add_outlet_stream(self.outlet2)

        self.splitter.solve()

        # Check mass balance
        total_outlet_flow = self.outlet1.mass_flow_rate + self.outlet2.mass_flow_rate
        assert abs(total_outlet_flow - self.inlet.mass_flow_rate) < 1e-6

        # Check split ratios
        expected_flow1 = self.inlet.mass_flow_rate * 0.3
        expected_flow2 = self.inlet.mass_flow_rate * 0.7
        assert abs(self.outlet1.mass_flow_rate - expected_flow1) < 1e-6
        assert abs(self.outlet2.mass_flow_rate - expected_flow2) < 1e-6

        # Check pressure and temperature (should be same)
        assert abs(self.outlet1.pressure - self.inlet.pressure) < 1e-6
        assert abs(self.outlet2.pressure - self.inlet.pressure) < 1e-6
        assert abs(self.outlet1.temperature - self.inlet.temperature) < 1e-6
        assert abs(self.outlet2.temperature - self.inlet.temperature) < 1e-6

        # Check composition (should be same)
        inlet_comp = self.inlet.composition
        outlet1_comp = self.outlet1.composition
        outlet2_comp = self.outlet2.composition
        for comp in inlet_comp:
            assert abs(inlet_comp[comp] - outlet1_comp[comp]) < 1e-6
            assert abs(inlet_comp[comp] - outlet2_comp[comp]) < 1e-6


def run_tests():
    """Run all unit operation tests."""
    print("Running Unit Operation Tests...")
    print("=" * 50)

    test_classes = [
        TestMaterialStream,
        TestMixer,
        TestHeater,
        TestValve,
        TestPump,
        TestSplitter
    ]

    passed = 0
    failed = 0

    for test_class in test_classes:
        print(f"\nTesting {test_class.__name__}...")
        instance = test_class()

        for method_name in dir(instance):
            if method_name.startswith('test_'):
                try:
                    setup_method = getattr(instance, 'setup_method', None)
                    if setup_method:
                        setup_method()

                    test_method = getattr(instance, method_name)
                    test_method()
                    print(f"✓ {method_name}")
                    passed += 1

                except Exception as e:
                    print(f"❌ {method_name}: {e}")
                    failed += 1

    print("\n" + "=" * 50)
    print(f"Tests completed: {passed} passed, {failed} failed")

    if failed == 0:
        print("✅ All unit operation tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(run_tests())