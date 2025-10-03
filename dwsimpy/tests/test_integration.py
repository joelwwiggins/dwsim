"""
Integration tests for DWSIM Python conversion.

Tests complete flowsheets with multiple unit operations.
"""

import pytest
from dwsimpy.unit_ops.mixer import Mixer
from dwsimpy.unit_ops.splitter import Splitter
from dwsimpy.unit_ops.heater import Heater
from dwsimpy.unit_ops.valve import Valve
from dwsimpy.unit_ops.pump import Pump
from dwsimpy.solvers.flowsheet_solver import FlowsheetSolver


class MockStream:
    def __init__(self, name, mass_flow=0, temperature=0, pressure=0, enthalpy=0, compositions=None):
        self.name = name
        self.mass_flow = mass_flow
        self.temperature = temperature
        self.pressure = pressure
        self.enthalpy = enthalpy
        self.compositions = compositions or {"H2O": 1.0}
        self.calculated = True


class TestIntegration:
    """Integration tests for flowsheet calculations."""

    def test_simple_flowsheet(self):
        """Test a simple flowsheet: inlet -> heater -> valve -> outlet"""
        # Create streams
        inlet = MockStream("inlet", mass_flow=100.0, temperature=300.0, pressure=101325.0, enthalpy=100.0)
        intermediate = MockStream("intermediate")
        outlet = MockStream("outlet")

        # Create unit operations
        heater = Heater()
        heater.delta_q = 500.0  # kW
        heater.input_stream = inlet
        heater.output_stream = intermediate
        heater.component_name = "Heater"

        valve = Valve()
        valve.delta_p = 50000.0  # Pressure drop (positive for drop)
        valve.input_stream = intermediate
        valve.output_stream = outlet
        valve.component_name = "Valve"

        # Create solver
        solver = FlowsheetSolver()
        solver.add_unit_operation(heater)
        solver.add_unit_operation(valve)
        solver.add_stream("inlet", inlet)
        solver.add_stream("intermediate", intermediate)
        solver.add_stream("outlet", outlet)

        # Solve
        result = solver.solve()

        assert result is True
        assert outlet.mass_flow == 100.0
        assert outlet.pressure < intermediate.pressure
        assert outlet.enthalpy > inlet.enthalpy  # Net effect depends on calculations

    def test_complex_flowsheet(self):
        """Test a more complex flowsheet with mixing and splitting."""
        # Create streams
        feed1 = MockStream("feed1", mass_flow=50.0, temperature=300.0, pressure=101325.0, enthalpy=100.0)
        feed2 = MockStream("feed2", mass_flow=30.0, temperature=320.0, pressure=101325.0, enthalpy=120.0)
        mixed = MockStream("mixed")
        product1 = MockStream("product1")
        product2 = MockStream("product2")

        # Create unit operations
        mixer = Mixer()
        mixer.input_streams = [feed1, feed2]
        mixer.output_stream = mixed
        mixer.component_name = "Mixer"

        splitter = Splitter()
        splitter.input_stream = mixed
        splitter.output_streams = [product1, product2]
        splitter.ratios = [0.7, 0.3, 0.0]
        splitter.component_name = "Splitter"

        # Create solver
        solver = FlowsheetSolver()
        solver.add_unit_operation(mixer)
        solver.add_unit_operation(splitter)
        solver.add_stream("feed1", feed1)
        solver.add_stream("feed2", feed2)
        solver.add_stream("mixed", mixed)
        solver.add_stream("product1", product1)
        solver.add_stream("product2", product2)

        # Solve
        result = solver.solve()

        assert result is True
        assert mixed.mass_flow == 80.0  # 50 + 30
        assert product1.mass_flow == pytest.approx(56.0, abs=1e-6)  # 80 * 0.7
        assert product2.mass_flow == pytest.approx(24.0, abs=1e-6)  # 80 * 0.3

    def test_pump_flowsheet(self):
        """Test flowsheet with pump."""
        inlet = MockStream("inlet", mass_flow=10.0, temperature=300.0, pressure=101325.0, enthalpy=100.0)
        outlet = MockStream("outlet")

        pump = Pump()
        pump.delta_p = 200000.0  # Pa
        pump.input_stream = inlet
        pump.output_stream = outlet
        pump.component_name = "Pump"

        solver = FlowsheetSolver()
        solver.add_unit_operation(pump)
        solver.add_stream("inlet", inlet)
        solver.add_stream("outlet", outlet)

        result = solver.solve()

        assert result is True
        assert outlet.pressure == 101325.0 + 200000.0
        assert outlet.mass_flow == 10.0