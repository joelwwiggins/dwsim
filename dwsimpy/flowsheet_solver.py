"""
Flowsheet solver for DWSIM Python implementation.
Handles the simulation of interconnected unit operations.
"""

import numpy as np
from typing import List, Dict, Any, Optional
from .interfaces.iflowsheet_solver import IFlowsheetSolver
from .interfaces.iunit_operation import IUnitOperation
from .material_stream import MaterialStream


class FlowsheetSolver(IFlowsheetSolver):
    """Main flowsheet solver implementing sequential modular approach"""

    def __init__(self):
        self.unit_operations: Dict[str, IUnitOperation] = {}
        self.streams: Dict[str, MaterialStream] = {}
        self.convergence_tolerance = 1e-6
        self.max_iterations = 100
        self.status = "idle"
        self.progress = 0.0

    def load_flowsheet(self, unit_operations: List[IUnitOperation],
                      streams: List[MaterialStream]) -> None:
        """Load unit operations and streams into the solver"""
        self.unit_operations = {u.id: u for u in unit_operations}
        self.streams = {s.id: s for s in streams}

        # Connect streams to unit operations based on connectivity
        self._connect_streams()

    def _connect_streams(self) -> None:
        """Connect streams to unit operations based on their connectivity"""
        # This would be implemented based on the edge data from the UI
        # For now, we'll assume streams are already connected
        pass

    def solve_flowsheet(self, flowsheet: Any) -> List[Exception]:
        """Solve the flowsheet using sequential modular approach"""
        self.status = "running"
        self.progress = 0.0

        try:
            # Initialize all unit operations
            for unit_op in self.unit_operations.values():
                unit_op.initialize()
                self.progress += 10 / len(self.unit_operations)

            # Sequential solution loop
            converged = False
            iteration = 0

            while not converged and iteration < self.max_iterations:
                iteration += 1
                max_error = 0.0

                # Solve each unit operation
                for unit_op in self.unit_operations.values():
                    error = unit_op.solve()
                    max_error = max(max_error, error)

                # Check convergence
                if max_error < self.convergence_tolerance:
                    converged = True

                self.progress = min(90, 10 + (iteration / self.max_iterations) * 80)

            if converged:
                self.status = "converged"
                results = self._collect_results()
                return []  # No exceptions
            else:
                self.status = "failed"
                return [Exception("Maximum iterations exceeded")]

        except Exception as e:
            self.status = "error"
            return [e]

    def _collect_results(self) -> Dict[str, Any]:
        """Collect results from all unit operations and streams"""
        results = {
            "unit_operations": {},
            "streams": {}
        }

        for unit_id, unit_op in self.unit_operations.items():
            results["unit_operations"][unit_id] = unit_op.get_results()

        for stream_id, stream in self.streams.items():
            results["streams"][stream_id] = stream.get_properties()

        return results

    def get_status(self) -> str:
        """Get current solver status"""
        return self.status

    def get_progress(self) -> float:
        """Get solution progress (0-100)"""
        return self.progress

    def reset(self) -> None:
        """Reset the solver state"""
        self.status = "idle"
        self.progress = 0.0
        self.unit_operations.clear()
        self.streams.clear()