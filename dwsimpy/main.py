"""
Main Entry Point for DWSIMPy

Console application for running chemical process simulations.
"""

import sys
from dwsimpy.streams.material_stream import MaterialStream
from dwsimpy.unit_ops.mixer import Mixer
from dwsimpy.unit_ops.heater import Heater
from dwsimpy.solvers.flowsheet_solver import FlowsheetSolver
from dwsimpy.property_packages.ideal_property_package import IdealPropertyPackage


def main():
    """Run a simple simulation example."""
    print("DWSIMPy - Chemical Process Simulator")
    print("====================================")

    # Create property package
    prop_pkg = IdealPropertyPackage()

    # Create streams
    stream1 = MaterialStream()
    stream1.component_name = "Feed 1"
    stream1.set_mass_flow(100.0)  # kg/h
    stream1.set_temperature(25.0)  # °C
    stream1.set_pressure(101325.0)  # Pa
    stream1.set_enthalpy(100.0)  # kJ/kg, placeholder
    stream1.property_package = prop_pkg
    stream1.calculated = True

    stream2 = MaterialStream()
    stream2.component_name = "Feed 2"
    stream2.set_mass_flow(50.0)  # kg/h
    stream2.set_temperature(30.0)  # °C
    stream2.set_pressure(101325.0)  # Pa
    stream2.set_enthalpy(110.0)  # kJ/kg, placeholder
    stream2.property_package = prop_pkg
    stream2.calculated = True

    outlet_stream = MaterialStream()
    outlet_stream.component_name = "Mixed Stream"
    outlet_stream.property_package = prop_pkg

    heated_stream = MaterialStream()
    heated_stream.component_name = "Heated Stream"
    heated_stream.property_package = prop_pkg

    # Create unit operations
    mixer = Mixer()
    mixer.component_name = "Mixer"
    mixer.input_streams = [stream1, stream2]
    mixer.output_stream = outlet_stream
    mixer.property_package = prop_pkg

    heater = Heater()
    heater.component_name = "Heater"
    heater.input_stream = outlet_stream
    heater.output_stream = heated_stream
    heater.delta_q = 10.0  # kW
    heater.property_package = prop_pkg

    # Create flowsheet solver
    solver = FlowsheetSolver()
    solver.add_stream("feed1", stream1)
    solver.add_stream("feed2", stream2)
    solver.add_stream("mixed", outlet_stream)
    solver.add_stream("heated", heated_stream)
    solver.add_unit_operation(mixer)
    solver.add_unit_operation(heater)

    # Solve
    print("Solving flowsheet...")
    success = solver.solve()
    if success:
        print("Solution converged!")
        print(f"Mixed stream mass flow: {outlet_stream.get_mass_flow()} kg/h")
        print(f"Heated stream temperature: {heated_stream.get_temperature()} °C")
    else:
        print("Solution did not converge.")
        sys.exit(1)


if __name__ == "__main__":
    main()