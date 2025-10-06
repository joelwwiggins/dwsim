"""
DWSIMpy Web UI

Enhanced web interface using Streamlit for flowsheet simulation.
Features visual flowsheet designer, comprehensive property editors, and save/load functionality.
"""

import streamlit as st
import json
import os
from typing import Dict, Any, List
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dwsimpy.flowsheet_solver import FlowsheetSolver
from dwsimpy.material_stream import MaterialStream
from dwsimpy.unit_operations.mixer import Mixer
from dwsimpy.unit_operations.heater import Heater
from dwsimpy.unit_operations.valve import Valve
from dwsimpy.unit_operations.pump import Pump
from dwsimpy.unit_operations.splitter import Splitter
from dwsimpy.unit_operations.reactor import Reactor
from dwsimpy.unit_ops.heat_exchanger import HeatExchanger
from dwsimpy.property_packages.ideal_property_package import IdealPropertyPackage
from dwsimpy.property_packages.peng_robinson_property_package import PengRobinsonPropertyPackage
from dwsimpy.ui.optimization_ui import render_optimization_tab


# Unit operation icons and colors
UNIT_ICONS = {
    'Mixer': '🔄',
    'Heater': '🔥',
    'Valve': '⚙️',
    'Pump': '💧',
    'Splitter': '📤',
    'Reactor': '⚗️',
    'HeatExchanger': '🔄🔥'
}

UNIT_COLORS = {
    'Mixer': '#FF6B6B',
    'Heater': '#4ECDC4',
    'Valve': '#45B7D1',
    'Pump': '#96CEB4',
    'Splitter': '#FFEAA7',
    'Reactor': '#DDA0DD',
    'HeatExchanger': '#F39C12'
}


def create_visual_flowsheet(flowsheet_data: Dict[str, Any]) -> str:
    """Create HTML for visual flowsheet representation"""
    html = """
    <div style="border: 2px solid #ddd; border-radius: 10px; padding: 20px; background-color: #f9f9f9; min-height: 400px; position: relative;">
        <h3 style="margin-top: 0;">Flowsheet Diagram</h3>
    """

    # Add streams
    for stream_id, stream in flowsheet_data.get('streams', {}).items():
        x, y = 100 + hash(stream_id) % 400, 100 + hash(stream_id) % 200
        html += f"""
        <div style="position: absolute; left: {x}px; top: {y}px; background-color: #3498db; color: white; padding: 8px; border-radius: 5px; font-size: 12px;">
            📊 {stream_id}<br>
            T: {stream.get('temperature', 'N/A')} K<br>
            P: {stream.get('pressure', 'N/A')/1000:.1f} kPa
        </div>
        """

    # Add unit operations
    for unit_data in flowsheet_data.get('unit_operations', []):
        unit_id = unit_data['id']
        unit_type = unit_data['type']
        x, y = 200 + hash(unit_id) % 300, 150 + hash(unit_id) % 150
        icon = UNIT_ICONS.get(unit_type, '⚙️')
        color = UNIT_COLORS.get(unit_type, '#95a5a6')

        html += f"""
        <div style="position: absolute; left: {x}px; top: {y}px; background-color: {color}; color: white; padding: 10px; border-radius: 8px; font-size: 14px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);">
            {icon} {unit_type}<br>
            <small>{unit_id}</small>
        </div>
        """

    html += "</div>"
    return html


def main():
    st.set_page_config(page_title="DWSIMpy - Chemical Process Simulator", page_icon="🧪", layout="wide")

    st.title("🧪 DWSIMpy - Chemical Process Simulator")
    st.markdown("---")

    # Initialize session state
    if 'flowsheet' not in st.session_state:
        st.session_state.flowsheet = FlowsheetSolver()
        st.session_state.flowsheet_data = {'unit_operations': [], 'streams': {}, 'edges': []}
        st.session_state.calculation_results = None
        st.session_state.selected_stream = None
        st.session_state.selected_unit = None

    # Sidebar for flowsheet building
    with st.sidebar:
        st.header("🏗️ Flowsheet Builder")

        # Property package selection
        st.subheader("Property Package")
        pp_options = ["Ideal", "Peng-Robinson"]
        selected_pp = st.selectbox("Select Property Package", pp_options, index=0)
        if selected_pp == "Ideal":
            st.session_state.property_package = IdealPropertyPackage()
        else:
            st.session_state.property_package = PengRobinsonPropertyPackage()

        st.markdown("---")

        # Add components
        st.subheader("Add Components")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("➕ Material Stream", use_container_width=True):
                stream_id = f"Stream_{len(st.session_state.flowsheet_data['streams']) + 1}"
                stream = MaterialStream(stream_id)
                stream.property_package = st.session_state.property_package
                st.session_state.flowsheet_data['streams'][stream_id] = stream.to_dict()
                st.session_state.flowsheet.streams[stream_id] = stream
                st.success(f"Added {stream_id}")

        with col2:
            if st.button("🔄 Mixer", use_container_width=True):
                unit_id = f"Mixer_{len(st.session_state.flowsheet_data['unit_operations']) + 1}"
                unit = Mixer(unit_id, {})
                st.session_state.flowsheet_data['unit_operations'].append({
                    'id': unit_id,
                    'type': 'Mixer',
                    'config': {},
                    'name': unit_id
                })
                st.session_state.flowsheet.unit_operations[unit_id] = unit
                st.success(f"Added {unit_id}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔥 Heater", use_container_width=True):
                unit_id = f"Heater_{len(st.session_state.flowsheet_data['unit_operations']) + 1}"
                unit = Heater(unit_id, {'outlet_temperature': 400.0})
                st.session_state.flowsheet_data['unit_operations'].append({
                    'id': unit_id,
                    'type': 'Heater',
                    'config': {'outlet_temperature': 400.0},
                    'name': unit_id
                })
                st.session_state.flowsheet.unit_operations[unit_id] = unit
                st.success(f"Added {unit_id}")

        with col2:
            if st.button("⚙️ Valve", use_container_width=True):
                unit_id = f"Valve_{len(st.session_state.flowsheet_data['unit_operations']) + 1}"
                unit = Valve(unit_id, {'outlet_pressure': 101325.0})
                st.session_state.flowsheet_data['unit_operations'].append({
                    'id': unit_id,
                    'type': 'Valve',
                    'config': {'outlet_pressure': 101325.0},
                    'name': unit_id
                })
                st.session_state.flowsheet.unit_operations[unit_id] = unit
                st.success(f"Added {unit_id}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("💧 Pump", use_container_width=True):
                unit_id = f"Pump_{len(st.session_state.flowsheet_data['unit_operations']) + 1}"
                unit = Pump(unit_id, {'outlet_pressure': 2e5})
                st.session_state.flowsheet_data['unit_operations'].append({
                    'id': unit_id,
                    'type': 'Pump',
                    'config': {'outlet_pressure': 2e5},
                    'name': unit_id
                })
                st.session_state.flowsheet.unit_operations[unit_id] = unit
                st.success(f"Added {unit_id}")

        with col2:
            if st.button("📤 Splitter", use_container_width=True):
                unit_id = f"Splitter_{len(st.session_state.flowsheet_data['unit_operations']) + 1}"
                unit = Splitter(unit_id, {'split_ratios': [0.5, 0.5]})
                st.session_state.flowsheet_data['unit_operations'].append({
                    'id': unit_id,
                    'type': 'Splitter',
                    'config': {'split_ratios': [0.5, 0.5]},
                    'name': unit_id
                })
                st.session_state.flowsheet.unit_operations[unit_id] = unit
                st.success(f"Added {unit_id}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⚗️ Reactor", use_container_width=True):
                unit_id = f"Reactor_{len(st.session_state.flowsheet_data['unit_operations']) + 1}"
                unit = Reactor(unit_id, {'volume': 1.0, 'temperature': 400.0})
                st.session_state.flowsheet_data['unit_operations'].append({
                    'id': unit_id,
                    'type': 'Reactor',
                    'config': {'volume': 1.0, 'temperature': 400.0},
                    'name': unit_id
                })
                st.session_state.flowsheet.unit_operations[unit_id] = unit
                st.success(f"Added {unit_id}")

        with col2:
            if st.button("🔄🔥 Heat Exchanger", use_container_width=True):
                unit_id = f"HeatExchanger_{len(st.session_state.flowsheet_data['unit_operations']) + 1}"
                unit = HeatExchanger(unit_id, {'ua': 1000.0, 'area': 10.0})
                st.session_state.flowsheet_data['unit_operations'].append({
                    'id': unit_id,
                    'type': 'HeatExchanger',
                    'config': {'ua': 1000.0, 'area': 10.0},
                    'name': unit_id
                })
                st.session_state.flowsheet.unit_operations[unit_id] = unit
                st.success(f"Added {unit_id}")

        st.markdown("---")

        # Save/Load flowsheet
        st.subheader("💾 Save/Load")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save Flowsheet", use_container_width=True):
                filename = st.text_input("Filename", "flowsheet.json", key="save_filename")
                if filename:
                    try:
                        with open(filename, 'w') as f:
                            json.dump(st.session_state.flowsheet_data, f, indent=2)
                        st.success(f"Saved to {filename}")
                    except Exception as e:
                        st.error(f"Error saving: {e}")

        with col2:
            uploaded_file = st.file_uploader("📁 Load Flowsheet", type=['json'])
            if uploaded_file is not None and st.button("Load", use_container_width=True):
                try:
                    data = json.load(uploaded_file)
                    st.session_state.flowsheet_data = data
                    # Recreate flowsheet objects
                    st.session_state.flowsheet = FlowsheetSolver.from_dict(data, {type(st.session_state.property_package).__name__: st.session_state.property_package})
                    st.success("Flowsheet loaded!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error loading: {e}")

    # Main content area with tabs
    tab1, tab2, tab3 = st.tabs(["🔍 Flowsheet", "📝 Properties", "🔬 Optimization"])

    with tab1:
        render_flowsheet_tab()

    with tab2:
        render_properties_tab()

    with tab3:
        render_optimization_tab(st.session_state.flowsheet, st.session_state.flowsheet_data)

    # Footer
    st.markdown("---")
    st.markdown("Built with ❤️ using DWSIMpy - Chemical Process Simulation in Python")


def render_flowsheet_tab():
    """Render the flowsheet view tab"""
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("🔍 Flowsheet View")

        # Visual flowsheet
        if st.session_state.flowsheet_data['unit_operations'] or st.session_state.flowsheet_data['streams']:
            st.components.v1.html(create_visual_flowsheet(st.session_state.flowsheet_data), height=400)
        else:
            st.info("Add components to your flowsheet using the sidebar")

        # Solve button
        if st.button("🚀 Solve Flowsheet", type="primary", use_container_width=True):
            try:
                with st.spinner("Solving flowsheet..."):
                    # Load flowsheet into solver
                    units = list(st.session_state.flowsheet.unit_operations.values())
                    streams = list(st.session_state.flowsheet.streams.values())
                    st.session_state.flowsheet.load_flowsheet(units, streams, st.session_state.flowsheet_data.get('edges', []))

                    # Solve
                    errors = st.session_state.flowsheet.solve_flowsheet(None)
                    if not errors:
                        st.success("✅ Flowsheet solved successfully!")
                        st.session_state.calculation_results = st.session_state.flowsheet._collect_results()
                    else:
                        st.error(f"❌ Solution failed: {errors[0]}")
            except Exception as e:
                st.error(f"❌ Error: {e}")

    with col2:
        st.header("📊 Results")

        if st.session_state.calculation_results:
            # Stream results
            st.subheader("Streams")
            for stream_id, stream_data in st.session_state.calculation_results.get('streams', {}).items():
                with st.expander(f"📊 {stream_id}"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Temperature", f"{stream_data.get('temperature', 0):.1f} K")
                        st.metric("Pressure", f"{stream_data.get('pressure', 0)/1000:.1f} kPa")
                    with col_b:
                        st.metric("Mass Flow", f"{stream_data.get('mass_flow_rate', 0):.3f} kg/s")
                        if stream_data.get('composition'):
                            comp_str = ", ".join([f"{k}: {v:.3f}" for k, v in stream_data['composition'].items()])
                            st.write(f"**Composition:** {comp_str}")

            # Unit operation results
            st.subheader("Unit Operations")
            for unit_id, unit_data in st.session_state.calculation_results.get('unit_operations', {}).items():
                with st.expander(f"⚙️ {unit_id}"):
                    for key, value in unit_data.items():
                        st.write(f"**{key}:** {value}")

        else:
            st.info("Run calculation to see results")


def render_properties_tab():
    """Render the properties editor tab"""
    col1, col2 = st.columns(2)

    with col1:
        st.header("📝 Stream Properties")

        if st.session_state.flowsheet_data['streams']:
            stream_options = list(st.session_state.flowsheet_data['streams'].keys())
            selected_stream = st.selectbox("Select Stream", stream_options, key="stream_select")

            if selected_stream:
                stream_data = st.session_state.flowsheet_data['streams'][selected_stream]
                stream_obj = st.session_state.flowsheet.streams[selected_stream]

                st.subheader(f"Properties for {selected_stream}")

                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    temp = st.number_input("Temperature (K)", value=stream_data.get('temperature', 298.15),
                                         min_value=1.0, max_value=2000.0, step=1.0, key=f"temp_{selected_stream}")
                    stream_obj.temperature = temp
                    stream_data['temperature'] = temp

                with col_b:
                    press = st.number_input("Pressure (Pa)", value=stream_data.get('pressure', 101325.0),
                                          min_value=1000.0, max_value=1e7, step=1000.0, key=f"press_{selected_stream}")
                    stream_obj.pressure = press
                    stream_data['pressure'] = press

                with col_c:
                    flow = st.number_input("Mass Flow (kg/s)", value=stream_data.get('mass_flow_rate', 0.0),
                                         min_value=0.0, max_value=1000.0, step=0.1, key=f"flow_{selected_stream}")
                    stream_obj.mass_flow_rate = flow
                    stream_data['mass_flow_rate'] = flow

                # Composition
                st.subheader("Composition (mole fractions)")
                if stream_data.get('composition'):
                    for comp, frac in stream_data['composition'].items():
                        new_frac = st.slider(f"{comp}", 0.0, 1.0, float(frac), 0.01, key=f"comp_{selected_stream}_{comp}")
                        stream_data['composition'][comp] = new_frac
                        stream_obj.composition = stream_data['composition']
                else:
                    st.info("Set composition in the stream object")
        else:
            st.info("Add streams to edit their properties")

    with col2:
        st.header("⚙️ Unit Operation Properties")

        if st.session_state.flowsheet_data['unit_operations']:
            unit_options = [unit['id'] for unit in st.session_state.flowsheet_data['unit_operations']]
            selected_unit = st.selectbox("Select Unit Operation", unit_options, key="unit_select")

            if selected_unit:
                unit_data = next(u for u in st.session_state.flowsheet_data['unit_operations'] if u['id'] == selected_unit)
                unit_obj = st.session_state.flowsheet.unit_operations[selected_unit]

                st.subheader(f"Properties for {selected_unit}")

                if unit_data['type'] == 'Heater':
                    temp = st.number_input("Outlet Temperature (K)", value=unit_data['config'].get('outlet_temperature', 400.0),
                                         min_value=273.0, max_value=1000.0, step=10.0, key=f"heater_temp_{selected_unit}")
                    unit_data['config']['outlet_temperature'] = temp
                    unit_obj.outlet_temperature = temp

                elif unit_data['type'] == 'Valve':
                    press = st.number_input("Outlet Pressure (Pa)", value=unit_data['config'].get('outlet_pressure', 101325.0),
                                          min_value=1000.0, max_value=1e7, step=1000.0, key=f"valve_press_{selected_unit}")
                    unit_data['config']['outlet_pressure'] = press
                    unit_obj.outlet_pressure = press

                elif unit_data['type'] == 'Pump':
                    press = st.number_input("Outlet Pressure (Pa)", value=unit_data['config'].get('outlet_pressure', 2e5),
                                          min_value=1000.0, max_value=1e8, step=10000.0, key=f"pump_press_{selected_unit}")
                    unit_data['config']['outlet_pressure'] = press
                    unit_obj.outlet_pressure = press

                elif unit_data['type'] == 'Splitter':
                    st.subheader("Split Ratios")
                    ratios = unit_data['config'].get('split_ratios', [0.5, 0.5])
                    col_a, col_b = st.columns(2)
                    with col_a:
                        ratio1 = st.slider("Outlet 1 Ratio", 0.0, 1.0, ratios[0], 0.01, key=f"split1_{selected_unit}")
                    with col_b:
                        ratio2 = st.slider("Outlet 2 Ratio", 0.0, 1.0, ratios[1], 0.01, key=f"split2_{selected_unit}")

                    unit_data['config']['split_ratios'] = [ratio1, ratio2]
                    unit_obj.split_ratios = [ratio1, ratio2]

                elif unit_data['type'] == 'Reactor':
                    st.subheader("Reactor Properties")
                    volume = st.number_input("Volume (m³)", value=unit_data['config'].get('volume', 1.0),
                                           min_value=0.1, max_value=100.0, step=0.1, key=f"reactor_vol_{selected_unit}")
                    temp = st.number_input("Temperature (K)", value=unit_data['config'].get('temperature', 400.0),
                                         min_value=273.0, max_value=1000.0, step=10.0, key=f"reactor_temp_{selected_unit}")
                    rate_const = st.number_input("Reaction Rate Constant (1/s)", value=unit_data['config'].get('reaction_rate_constant', 0.1),
                                               min_value=0.001, max_value=10.0, step=0.01, key=f"reactor_rate_{selected_unit}")

                    unit_data['config']['volume'] = volume
                    unit_data['config']['temperature'] = temp
                    unit_data['config']['reaction_rate_constant'] = rate_const
                    unit_obj.volume = volume
                    unit_obj.temperature = temp
                    unit_obj.reaction_rate_constant = rate_const

                elif unit_data['type'] == 'HeatExchanger':
                    st.subheader("Heat Exchanger Properties")
                    ua = st.number_input("UA (W/K)", value=unit_data['config'].get('ua', 1000.0),
                                       min_value=1.0, max_value=100000.0, step=100.0, key=f"hx_ua_{selected_unit}")
                    area = st.number_input("Area (m²)", value=unit_data['config'].get('area', 10.0),
                                         min_value=0.1, max_value=1000.0, step=1.0, key=f"hx_area_{selected_unit}")

                    unit_data['config']['ua'] = ua
                    unit_data['config']['area'] = area
                    unit_obj.ua = ua
                    unit_obj.area = area

                # Show unit results if available
                if st.session_state.calculation_results and selected_unit in st.session_state.calculation_results.get('unit_operations', {}):
                    st.subheader("Calculation Results")
                    results = st.session_state.calculation_results['unit_operations'][selected_unit]
                    for key, value in results.items():
                        st.metric(key.replace('_', ' ').title(), f"{value}")
        else:
            st.info("Add unit operations to edit their properties")


if __name__ == "__main__":
    main()