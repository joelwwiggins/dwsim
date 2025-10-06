"""
Parameter Study and Sensitivity Analysis Module

Provides tools for parameter studies, sensitivity analysis, and optimization
of chemical process flowsheets.
"""

import numpy as np
from typing import Dict, Any, List, Callable, Optional
from ..flowsheet_solver import FlowsheetSolver
from ..material_stream import MaterialStream


class ParameterStudy:
    """Class for performing parameter studies on flowsheets"""

    def __init__(self, flowsheet: FlowsheetSolver):
        self.flowsheet = flowsheet
        self.base_results = None

    def run_parameter_study(self, parameter_path: str, parameter_values: List[float],
                           output_variables: List[str]) -> Dict[str, List[float]]:
        """
        Run parameter study by varying a single parameter and monitoring outputs

        Args:
            parameter_path: Dot-separated path to parameter (e.g., "streams.Stream1.temperature")
            parameter_values: List of parameter values to test
            output_variables: List of output variables to monitor (e.g., ["streams.Stream2.temperature"])

        Returns:
            Dictionary mapping output variable names to lists of values
        """
        results = {var: [] for var in output_variables}

        # Store original value
        original_value = self._get_parameter_value(parameter_path)

        try:
            for value in parameter_values:
                # Set parameter value
                self._set_parameter_value(parameter_path, value)

                # Solve flowsheet
                errors = self.flowsheet.solve_flowsheet(None)
                if not errors:
                    # Collect results
                    calc_results = self.flowsheet._collect_results()
                    for var in output_variables:
                        result_value = self._extract_result_value(calc_results, var)
                        results[var].append(result_value)
                else:
                    # Append NaN for failed calculations
                    for var in output_variables:
                        results[var].append(np.nan)

        finally:
            # Restore original value
            self._set_parameter_value(parameter_path, original_value)

        return results

    def sensitivity_analysis(self, parameter_path: str, base_value: float,
                           perturbation: float = 0.01, output_variables: List[str] = None) -> Dict[str, float]:
        """
        Perform sensitivity analysis by perturbing a parameter and measuring output changes

        Args:
            parameter_path: Dot-separated path to parameter
            base_value: Base value of parameter
            perturbation: Relative perturbation (e.g., 0.01 for 1%)
            output_variables: Output variables to analyze (if None, analyzes all numeric results)

        Returns:
            Dictionary mapping output variables to sensitivity coefficients
        """
        if output_variables is None:
            # Get all numeric results from base calculation
            errors = self.flowsheet.solve_flowsheet(None)
            if errors:
                raise RuntimeError("Base calculation failed")
            base_results = self.flowsheet._collect_results()
            output_variables = self._get_numeric_result_paths(base_results)

        sensitivities = {}

        # Calculate base case
        self._set_parameter_value(parameter_path, base_value)
        errors = self.flowsheet.solve_flowsheet(None)
        if errors:
            raise RuntimeError("Base calculation failed")
        base_calc_results = self.flowsheet._collect_results()

        # Calculate perturbed case
        perturbed_value = base_value * (1 + perturbation)
        self._set_parameter_value(parameter_path, perturbed_value)
        errors = self.flowsheet.solve_flowsheet(None)
        if errors:
            raise RuntimeError("Perturbed calculation failed")
        perturbed_calc_results = self.flowsheet._collect_results()

        # Calculate sensitivities
        for var in output_variables:
            base_val = self._extract_result_value(base_calc_results, var)
            perturbed_val = self._extract_result_value(perturbed_calc_results, var)

            if base_val != 0 and not (np.isnan(base_val) or np.isnan(perturbed_val)):
                sensitivity = (perturbed_val - base_val) / (base_value * perturbation)
                sensitivities[var] = sensitivity
            else:
                sensitivities[var] = 0.0

        # Restore original value
        self._set_parameter_value(parameter_path, base_value)

        return sensitivities

    def _get_parameter_value(self, parameter_path: str) -> Any:
        """Get parameter value from flowsheet using dot notation"""
        parts = parameter_path.split('.')
        obj = self.flowsheet

        for part in parts[:-1]:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            elif part in obj:  # Dictionary-like access
                obj = obj[part]
            else:
                raise ValueError(f"Cannot access {part} in {parameter_path}")

        attr = parts[-1]
        if hasattr(obj, attr):
            return getattr(obj, attr)
        elif attr in obj:  # Dictionary-like access
            return obj[attr]
        else:
            raise ValueError(f"Parameter {attr} not found")

    def _set_parameter_value(self, parameter_path: str, value: Any) -> None:
        """Set parameter value in flowsheet using dot notation"""
        parts = parameter_path.split('.')
        obj = self.flowsheet

        for part in parts[:-1]:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            elif part in obj:  # Dictionary-like access
                obj = obj[part]
            else:
                raise ValueError(f"Cannot access {part} in {parameter_path}")

        attr = parts[-1]
        if hasattr(obj, attr):
            setattr(obj, attr, value)
        elif attr in obj:  # Dictionary-like access
            obj[attr] = value
        else:
            raise ValueError(f"Parameter {attr} not found")

    def _extract_result_value(self, results: Dict[str, Any], variable_path: str) -> float:
        """Extract numeric value from results using dot notation"""
        parts = variable_path.split('.')
        obj = results

        for part in parts:
            if isinstance(obj, dict) and part in obj:
                obj = obj[part]
            else:
                return np.nan

        if isinstance(obj, (int, float)):
            return float(obj)
        else:
            return np.nan

    def _get_numeric_result_paths(self, results: Dict[str, Any], prefix: str = "") -> List[str]:
        """Recursively find all numeric result paths"""
        paths = []

        def traverse(obj, current_path):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_path = f"{current_path}.{key}" if current_path else key
                    if isinstance(value, (int, float)):
                        paths.append(new_path)
                    elif isinstance(value, dict):
                        traverse(value, new_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    new_path = f"{current_path}[{i}]"
                    if isinstance(item, (int, float)):
                        paths.append(new_path)
                    elif isinstance(item, dict):
                        traverse(item, new_path)

        traverse(results, prefix)
        return paths


class OptimizationProblem:
    """Class for defining and solving optimization problems"""

    def __init__(self, flowsheet: FlowsheetSolver):
        self.flowsheet = flowsheet
        self.objective_function = None
        self.constraints = []
        self.variables = []

    def set_objective(self, objective_func: Callable[[Dict[str, Any]], float]) -> None:
        """Set the objective function"""
        self.objective_function = objective_func

    def add_variable(self, name: str, bounds: tuple, initial_value: float = None) -> None:
        """Add optimization variable"""
        self.variables.append({
            'name': name,
            'bounds': bounds,
            'initial': initial_value or (bounds[0] + bounds[1]) / 2
        })

    def add_constraint(self, constraint_func: Callable[[Dict[str, Any]], float], bounds: tuple) -> None:
        """Add constraint function"""
        self.constraints.append({
            'function': constraint_func,
            'bounds': bounds
        })

    def optimize(self, method: str = 'SLSQP') -> Dict[str, Any]:
        """
        Perform optimization using scipy.optimize

        Returns:
            Dictionary with optimization results
        """
        try:
            from scipy.optimize import minimize
        except ImportError:
            raise ImportError("scipy is required for optimization")

        def objective(x):
            # Set variable values
            for i, var in enumerate(self.variables):
                self._set_parameter_value(var['name'], x[i])

            # Solve flowsheet
            errors = self.flowsheet.solve_flowsheet(None)
            if errors:
                return 1e10  # Large penalty for infeasible solutions

            # Calculate objective
            results = self.flowsheet._collect_results()
            return self.objective_function(results)

        def constraint_wrapper(x, constraint):
            # Set variable values
            for i, var in enumerate(self.variables):
                self._set_parameter_value(var['name'], x[i])

            # Solve flowsheet
            errors = self.flowsheet.solve_flowsheet(None)
            if errors:
                return -1e10  # Infeasible

            results = self.flowsheet._collect_results()
            return constraint['function'](results)

        # Set up constraints
        constraints = []
        for constraint in self.constraints:
            constraints.append({
                'type': 'ineq' if constraint['bounds'][0] == -np.inf else 'eq',
                'fun': lambda x, c=constraint: constraint_wrapper(x, c) - constraint['bounds'][0],
                'bounds': constraint['bounds']
            })

        # Initial values
        x0 = [var['initial'] for var in self.variables]
        bounds = [var['bounds'] for var in self.variables]

        # Perform optimization
        result = minimize(objective, x0, method=method, bounds=bounds, constraints=constraints)

        return {
            'success': result.success,
            'message': result.message,
            'optimal_variables': dict(zip([v['name'] for v in self.variables], result.x)),
            'optimal_objective': result.fun,
            'n_iterations': result.nit
        }

    def _set_parameter_value(self, parameter_path: str, value: Any) -> None:
        """Set parameter value using dot notation (same as ParameterStudy)"""
        parts = parameter_path.split('.')
        obj = self.flowsheet

        for part in parts[:-1]:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            elif part in obj:
                obj = obj[part]
            else:
                raise ValueError(f"Cannot access {part} in {parameter_path}")

        attr = parts[-1]
        if hasattr(obj, attr):
            setattr(obj, attr, value)
        elif attr in obj:
            obj[attr] = value
        else:
            raise ValueError(f"Parameter {attr} not found")