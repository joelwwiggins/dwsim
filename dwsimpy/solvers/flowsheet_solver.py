"""
Flowsheet Solver

Converted from VB.NET to Python.
This module implements the sequential modular flowsheet solver.
"""

from typing import List, Dict, Any
import logging
import copy

logger = logging.getLogger(__name__)


class FlowsheetSolver:
    """
    Sequential modular flowsheet solver.

    Solves the flowsheet by calculating unit operations in sequence.
    """

    def __init__(self):
        self.max_iterations = 50
        self.tolerance = 1e-6
        self.unit_operations = []  # List of unit ops to solve
        self.streams = {}  # Dict of streams
        self.recycle_streams = []  # List of recycle stream names
        self.convergence_vars = {}  # Variables to check for convergence

    def add_unit_operation(self, unit_op):
        """Add a unit operation to the solver."""
        self.unit_operations.append(unit_op)

    def add_stream(self, name, stream):
        """Add a stream to the solver."""
        self.streams[name] = stream

    def add_recycle_stream(self, name):
        """Mark a stream as a recycle stream."""
        if name not in self.recycle_streams:
            self.recycle_streams.append(name)

    def solve(self) -> bool:
        """
        Solve the flowsheet.

        Returns True if converged, False otherwise.
        """
        logger.info("Starting flowsheet calculation")

        # Initialize convergence tracking
        prev_values = self._get_convergence_values()

        for iteration in range(self.max_iterations):
            logger.info(f"Iteration {iteration + 1}")

            # Store previous values for convergence check
            prev_values = self._get_convergence_values()

            converged = True
            errors = []

            for unit_op in self.unit_operations:
                try:
                    unit_op.calculate()
                    logger.debug(f"Calculated {unit_op.component_name}")
                except Exception as e:
                    logger.error(f"Error calculating {unit_op.component_name}: {e}")
                    errors.append(str(e))
                    converged = False

            # Check convergence
            if converged and self._check_convergence(prev_values):
                logger.info("Flowsheet converged")
                return True

            # Handle recycles - tear streams
            self._update_recycle_streams()

        logger.warning("Flowsheet did not converge")
        return False

    def _get_convergence_values(self) -> Dict[str, float]:
        """Get current values of variables to check for convergence."""
        values = {}
        for stream_name, stream in self.streams.items():
            if hasattr(stream, 'mass_flow'):
                values[f"{stream_name}_mass_flow"] = stream.mass_flow
            if hasattr(stream, 'temperature'):
                values[f"{stream_name}_temperature"] = stream.temperature
            if hasattr(stream, 'pressure'):
                values[f"{stream_name}_pressure"] = stream.pressure
        return values

    def _check_convergence(self, prev_values: Dict[str, float]) -> bool:
        """Check if the solution has converged."""
        current_values = self._get_convergence_values()

        for key, current_val in current_values.items():
            if key in prev_values:
                prev_val = prev_values[key]
                if abs(current_val - prev_val) > self.tolerance:
                    return False
        return True

    def _update_recycle_streams(self):
        """Update recycle streams for next iteration."""
        # For now, simple copy - in reality, would use acceleration
        pass

    def reset(self):
        """Reset all unit operations and streams."""
        for unit_op in self.unit_operations:
            unit_op._is_dirty = True

        for stream in self.streams.values():
            stream.calculated = False