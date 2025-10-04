"""
DWSIMpy Web UI

Basic web interface using Streamlit for flowsheet simulation.
Converted from VB.NET to Python.
"""

import streamlit as st
from dwsimpy.solvers.flowsheet_solver import FlowsheetSolver
from dwsimpy.streams.material_stream import MaterialStream
from dwsimpy.unit_ops.mixer import Mixer
from dwsimpy.unit_ops.heater import Heater
from dwsimpy.property_packages.ideal_property_package import IdealPropertyPackage


def main():
    st.title("DWSIMpy - Chemical Process Simulator")

    st.sidebar.header("Flowsheet Builder")

    # Initialize flowsheet
    if 'flowsheet' not in st.session_state:
        st.session_state.flowsheet = FlowsheetSolver()
        st.session_state.streams = {}
        st.session_state.units = {}

    # Add components
    st.sidebar.subheader("Add Components")

    if st.sidebar.button("Add Material Stream"):
        stream_id = f"Stream_{len(st.session_state.streams) + 1}"
        stream = MaterialStream()
        stream.component_name = stream_id
        st.session_state.streams[stream_id] = stream
        st.session_state.flowsheet.add_stream(stream_id, stream)

    if st.sidebar.button("Add Mixer"):
        unit_id = f"Mixer_{len(st.session_state.units) + 1}"
        unit = Mixer()
        unit.component_name = unit_id
        st.session_state.units[unit_id] = unit
        st.session_state.flowsheet.add_unit_operation(unit)

    if st.sidebar.button("Add Heater"):
        unit_id = f"Heater_{len(st.session_state.units) + 1}"
        unit = Heater()
        unit.component_name = unit_id
        st.session_state.units[unit_id] = unit
        st.session_state.flowsheet.add_unit_operation(unit)

    # Display flowsheet
    st.header("Current Flowsheet")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Streams")
        for name, stream in st.session_state.streams.items():
            st.write(f"- {name}")

    with col2:
        st.subheader("Unit Operations")
        for name, unit in st.session_state.units.items():
            st.write(f"- {name}")

    # Solve button
    if st.button("Solve Flowsheet"):
        try:
            success = st.session_state.flowsheet.solve()
            if success:
                st.success("Flowsheet solved successfully!")
            else:
                st.error("Flowsheet did not converge.")
        except Exception as e:
            st.error(f"Error solving flowsheet: {e}")

    # Results
    if st.session_state.streams:
        st.header("Stream Results")
        for name, stream in st.session_state.streams.items():
            st.subheader(name)
            # Placeholder for results
            st.write("Mass Flow:", getattr(stream, 'mass_flow', 'N/A'))
            st.write("Temperature:", getattr(stream, 'temperature', 'N/A'))

    # Stream properties editor
    st.header("Stream Properties")
    selected_stream = st.selectbox("Select Stream", list(st.session_state.streams.keys()) if st.session_state.streams else [])
    if selected_stream:
        stream = st.session_state.streams[selected_stream]
        col1, col2, col3 = st.columns(3)
        with col1:
            mass_flow = st.number_input("Mass Flow (kg/s)", value=getattr(stream, 'mass_flow', 0.0), key=f"mf_{selected_stream}")
            stream.mass_flow = mass_flow
        with col2:
            temp = st.number_input("Temperature (K)", value=getattr(stream, 'temperature', 298.15), key=f"t_{selected_stream}")
            stream.temperature = temp
        with col3:
            press = st.number_input("Pressure (Pa)", value=getattr(stream, 'pressure', 101325.0), key=f"p_{selected_stream}")
            stream.pressure = press
        stream.calculated = True

    # Unit properties editor
    st.header("Unit Operation Properties")
    selected_unit = st.selectbox("Select Unit", list(st.session_state.units.keys()) if st.session_state.units else [])
    if selected_unit:
        unit = st.session_state.units[selected_unit]
        if isinstance(unit, Heater):
            delta_q = st.number_input("Heat Added (kW)", value=unit.delta_q, key=f"dq_{selected_unit}")
            unit.delta_q = delta_q
            efficiency = st.slider("Efficiency (%)", 0, 100, int(unit.efficiency * 100), key=f"eff_{selected_unit}")
            unit.efficiency = efficiency / 100.0
        elif isinstance(unit, Mixer):
            # Add mixer properties if needed
            pass

    # Property Grid
    st.header("Property Grid")
    if selected_stream:
        st.subheader(f"Properties for {selected_stream}")
        props = stream.get_properties(None)
        for prop in props:
            value = stream.get_property_value(prop)
            st.write(f"{prop}: {value}")

    # Reports
    st.header("Reports")
    if st.button("Generate Report"):
        report = ""
        for name, stream in st.session_state.streams.items():
            report += f"Stream {name}:\n"
            report += f"  Mass Flow: {getattr(stream, 'mass_flow', 'N/A')} kg/s\n"
            report += f"  Temperature: {getattr(stream, 'temperature', 'N/A')} K\n"
            report += f"  Pressure: {getattr(stream, 'pressure', 'N/A')} Pa\n\n"
        st.text_area("Flowsheet Report", report, height=200)


if __name__ == "__main__":
    main()