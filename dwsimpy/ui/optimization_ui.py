"""
Optimization UI Components for DWSIMpy

Provides UI components for parameter studies, sensitivity analysis, and optimization.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List
import numpy as np
from ..optimization.parameter_study import ParameterStudy, OptimizationProblem


def render_optimization_tab(flowsheet_solver, flowsheet_data):
    """Render the optimization tab in the main UI"""

    st.header("🔬 Optimization & Analysis")

    # Create tabs for different analysis types
    tab1, tab2, tab3 = st.tabs(["📊 Parameter Study", "🎯 Sensitivity Analysis", "⚡ Optimization"])

    with tab1:
        render_parameter_study_tab(flowsheet_solver, flowsheet_data)

    with tab2:
        render_sensitivity_analysis_tab(flowsheet_solver, flowsheet_data)

    with tab3:
        render_optimization_tab_content(flowsheet_solver, flowsheet_data)


def render_parameter_study_tab(flowsheet_solver, flowsheet_data):
    """Render parameter study interface"""

    st.subheader("Parameter Study")
    st.markdown("Vary a single parameter and observe how outputs change")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("**Parameter to Vary**")

        # Get available parameters
        available_params = get_available_parameters(flowsheet_data)
        selected_param = st.selectbox("Select Parameter", available_params, key="param_study_param")

        if selected_param:
            current_value = get_parameter_current_value(flowsheet_solver, selected_param)

            # Parameter range
            st.markdown(f"Current value: {current_value}")
            min_val = st.number_input("Minimum Value", value=current_value * 0.5, key="param_min")
            max_val = st.number_input("Maximum Value", value=current_value * 1.5, key="param_max")
            n_points = st.slider("Number of Points", 5, 50, 10, key="param_points")

            parameter_values = np.linspace(min_val, max_val, n_points)

    with col2:
        st.markdown("**Output Variables to Monitor**")

        # Get available outputs
        available_outputs = get_available_outputs(flowsheet_data)
        selected_outputs = st.multiselect("Select Outputs", available_outputs, key="param_study_outputs")

    # Run study button
    if st.button("🚀 Run Parameter Study", type="primary"):
        if selected_param and selected_outputs:
            with st.spinner("Running parameter study..."):
                study = ParameterStudy(flowsheet_solver)
                results = study.run_parameter_study(selected_param, parameter_values.tolist(), selected_outputs)

                # Display results
                st.success("Parameter study completed!")

                # Create plot
                fig = go.Figure()
                for output_var in selected_outputs:
                    fig.add_trace(go.Scatter(
                        x=parameter_values,
                        y=results[output_var],
                        mode='lines+markers',
                        name=output_var.split('.')[-1]
                    ))

                fig.update_layout(
                    title=f"Parameter Study: {selected_param.split('.')[-1]}",
                    xaxis_title=selected_param.split('.')[-1],
                    yaxis_title="Output Value",
                    height=400
                )

                st.plotly_chart(fig, use_container_width=True)

                # Display data table
                df_data = {"Parameter Value": parameter_values}
                df_data.update(results)
                df = pd.DataFrame(df_data)
                st.dataframe(df, use_container_width=True)

                # Download button
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Results as CSV",
                    data=csv,
                    file_name="parameter_study_results.csv",
                    mime="text/csv",
                    key="download_param_study"
                )
        else:
            st.error("Please select a parameter and at least one output variable")


def render_sensitivity_analysis_tab(flowsheet_solver, flowsheet_data):
    """Render sensitivity analysis interface"""

    st.subheader("Sensitivity Analysis")
    st.markdown("Analyze how sensitive outputs are to parameter changes")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("**Parameter to Analyze**")

        available_params = get_available_parameters(flowsheet_data)
        selected_param = st.selectbox("Select Parameter", available_params, key="sens_param")

        if selected_param:
            current_value = get_parameter_current_value(flowsheet_solver, selected_param)
            st.markdown(f"Current value: {current_value}")

            perturbation = st.slider("Perturbation (%)", 0.1, 10.0, 1.0, 0.1, key="sens_perturbation") / 100.0

    with col2:
        st.markdown("**Analysis Options**")
        analyze_all = st.checkbox("Analyze all outputs", value=True, key="sens_all_outputs")

        if not analyze_all:
            available_outputs = get_available_outputs(flowsheet_data)
            selected_outputs = st.multiselect("Select specific outputs", available_outputs, key="sens_outputs")
        else:
            selected_outputs = None

    if st.button("🔍 Run Sensitivity Analysis", type="primary"):
        if selected_param:
            with st.spinner("Running sensitivity analysis..."):
                study = ParameterStudy(flowsheet_solver)
                sensitivities = study.sensitivity_analysis(
                    selected_param, current_value, perturbation, selected_outputs
                )

                # Display results
                st.success("Sensitivity analysis completed!")

                # Create bar chart
                variables = list(sensitivities.keys())
                values = list(sensitivities.values())

                fig = go.Figure(data=[
                    go.Bar(
                        x=variables,
                        y=values,
                        marker_color=['red' if v < 0 else 'blue' for v in values]
                    )
                ])

                fig.update_layout(
                    title=f"Sensitivity Analysis: {selected_param.split('.')[-1]}",
                    xaxis_title="Output Variable",
                    yaxis_title="Sensitivity Coefficient",
                    height=400
                )

                st.plotly_chart(fig, use_container_width=True)

                # Display table
                df = pd.DataFrame({
                    "Output Variable": variables,
                    "Sensitivity Coefficient": values,
                    "Absolute Sensitivity": np.abs(values)
                }).sort_values("Absolute Sensitivity", ascending=False)

                st.dataframe(df, use_container_width=True)

                # Most sensitive variables
                most_sensitive = df.iloc[0]["Output Variable"]
                st.info(f"📈 Most sensitive output: **{most_sensitive}**")

        else:
            st.error("Please select a parameter to analyze")


def render_optimization_tab_content(flowsheet_solver, flowsheet_data):
    """Render optimization interface"""

    st.subheader("Process Optimization")
    st.markdown("Optimize process parameters to maximize/minimize objectives")

    # Objective function setup
    st.markdown("**Objective Function**")
    objective_type = st.selectbox("Objective Type", ["Minimize", "Maximize"], key="opt_objective_type")

    available_outputs = get_available_outputs(flowsheet_data)
    objective_var = st.selectbox("Objective Variable", available_outputs, key="opt_objective_var")

    # Decision variables
    st.markdown("**Decision Variables**")
    st.markdown("Add parameters to optimize:")

    if 'opt_variables' not in st.session_state:
        st.session_state.opt_variables = []

    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        new_var = st.selectbox("Parameter", get_available_parameters(flowsheet_data), key="opt_new_var")
    with col2:
        var_min = st.number_input("Min", value=0.0, key="opt_var_min")
    with col3:
        var_max = st.number_input("Max", value=100.0, key="opt_var_max")
    with col4:
        if st.button("➕ Add Variable", key="opt_add_var"):
            if new_var:
                st.session_state.opt_variables.append({
                    'name': new_var,
                    'bounds': (var_min, var_max),
                    'initial': (var_min + var_max) / 2
                })
                st.success(f"Added {new_var}")

    # Display current variables
    if st.session_state.opt_variables:
        st.markdown("**Current Variables:**")
        for i, var in enumerate(st.session_state.opt_variables):
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            with col1:
                st.write(f"{var['name']}")
            with col2:
                st.write(f"{var['bounds'][0]:.2f}")
            with col3:
                st.write(f"{var['bounds'][1]:.2f}")
            with col4:
                if st.button("🗑️", key=f"opt_remove_{i}"):
                    st.session_state.opt_variables.pop(i)
                    st.rerun()

    # Constraints
    st.markdown("**Constraints**")
    if 'opt_constraints' not in st.session_state:
        st.session_state.opt_constraints = []

    constraint_var = st.selectbox("Constraint Variable", available_outputs, key="opt_constraint_var")
    constraint_type = st.selectbox("Constraint Type", ["<=", ">=", "="], key="opt_constraint_type")
    constraint_value = st.number_input("Value", value=0.0, key="opt_constraint_value")

    if st.button("➕ Add Constraint", key="opt_add_constraint"):
        if constraint_var:
            st.session_state.opt_constraints.append({
                'variable': constraint_var,
                'type': constraint_type,
                'value': constraint_value
            })
            st.success(f"Added constraint: {constraint_var} {constraint_type} {constraint_value}")

    # Display constraints
    if st.session_state.opt_constraints:
        st.markdown("**Current Constraints:**")
        for i, constraint in enumerate(st.session_state.opt_constraints):
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            with col1:
                st.write(f"{constraint['variable']}")
            with col2:
                st.write(f"{constraint['type']}")
            with col3:
                st.write(f"{constraint['value']}")
            with col4:
                if st.button("🗑️", key=f"opt_remove_constraint_{i}"):
                    st.session_state.opt_constraints.pop(i)
                    st.rerun()

    # Run optimization
    if st.button("⚡ Run Optimization", type="primary"):
        if st.session_state.opt_variables and objective_var:
            with st.spinner("Running optimization..."):
                try:
                    # Create optimization problem
                    opt_problem = OptimizationProblem(flowsheet_solver)

                    # Set objective
                    def objective_func(results):
                        value = extract_nested_value(results, objective_var)
                        return value if objective_type == "Minimize" else -value

                    opt_problem.set_objective(objective_func)

                    # Add variables
                    for var in st.session_state.opt_variables:
                        current_val = get_parameter_current_value(flowsheet_solver, var['name'])
                        opt_problem.add_variable(var['name'], var['bounds'], current_val)

                    # Add constraints
                    for constraint in st.session_state.opt_constraints:
                        def constraint_func(results, c=constraint):
                            value = extract_nested_value(results, c['variable'])
                            if c['type'] == '<=':
                                return c['value'] - value  # value <= constraint_value
                            elif c['type'] == '>=':
                                return value - c['value']  # value >= constraint_value
                            else:  # '='
                                return abs(value - c['value'])

                        opt_problem.add_constraint(constraint_func, (0, np.inf))

                    # Solve
                    result = opt_problem.optimize()

                    if result['success']:
                        st.success("🎉 Optimization completed successfully!")

                        # Display results
                        st.subheader("Optimal Solution")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Objective Value", f"{result['optimal_objective']:.4f}")
                        with col2:
                            st.metric("Iterations", result['n_iterations'])

                        st.markdown("**Optimal Variable Values:**")
                        for var_name, value in result['optimal_variables'].items():
                            st.write(f"- {var_name.split('.')[-1]}: {value:.4f}")

                    else:
                        st.error(f"❌ Optimization failed: {result['message']}")

                except Exception as e:
                    st.error(f"❌ Optimization error: {e}")
        else:
            st.error("Please add at least one variable and select an objective")


def get_available_parameters(flowsheet_data):
    """Get list of available parameters for optimization"""
    params = []

    # Stream parameters
    for stream_id in flowsheet_data.get('streams', {}):
        params.extend([
            f"streams.{stream_id}.temperature",
            f"streams.{stream_id}.pressure",
            f"streams.{stream_id}.mass_flow_rate"
        ])

    # Unit operation parameters
    for unit in flowsheet_data.get('unit_operations', []):
        unit_id = unit['id']
        unit_type = unit['type']

        if unit_type == 'Heater':
            params.append(f"unit_operations.{unit_id}.outlet_temperature")
        elif unit_type == 'Valve':
            params.append(f"unit_operations.{unit_id}.outlet_pressure")
        elif unit_type == 'Pump':
            params.append(f"unit_operations.{unit_id}.outlet_pressure")
        elif unit_type == 'Reactor':
            params.extend([
                f"unit_operations.{unit_id}.temperature",
                f"unit_operations.{unit_id}.volume"
            ])

    return params


def get_available_outputs(flowsheet_data):
    """Get list of available output variables"""
    outputs = []

    # Stream outputs
    for stream_id in flowsheet_data.get('streams', {}):
        outputs.extend([
            f"streams.{stream_id}.temperature",
            f"streams.{stream_id}.pressure",
            f"streams.{stream_id}.mass_flow_rate"
        ])

    # Unit operation outputs
    for unit in flowsheet_data.get('unit_operations', []):
        unit_id = unit['id']
        unit_type = unit['type']

        if unit_type in ['Heater', 'Valve', 'Pump', 'Reactor']:
            outputs.extend([
                f"unit_operations.{unit_id}.results.outlet_temperature",
                f"unit_operations.{unit_id}.results.outlet_pressure"
            ])

    return outputs


def get_parameter_current_value(flowsheet_solver, parameter_path):
    """Get current value of a parameter"""
    try:
        parts = parameter_path.split('.')
        obj = flowsheet_solver

        for part in parts[:-1]:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            elif part in obj:
                obj = obj[part]
            else:
                return 0.0

        attr = parts[-1]
        if hasattr(obj, attr):
            return getattr(obj, attr)
        elif attr in obj:
            return obj[attr]
        else:
            return 0.0
    except:
        return 0.0


def extract_nested_value(data, path):
    """Extract value from nested dictionary using dot notation"""
    try:
        parts = path.split('.')
        obj = data

        for part in parts:
            if isinstance(obj, dict) and part in obj:
                obj = obj[part]
            else:
                return 0.0

        return float(obj) if isinstance(obj, (int, float)) else 0.0
    except:
        return 0.0