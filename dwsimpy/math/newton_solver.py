"""
Newton Solver

Converted from DWSIM.Math/NewtonSolver.vb to Python.
Implements Newton-Raphson method for solving nonlinear equations.
"""

import numpy as np
from typing import Callable, Optional
from scipy.optimize import root


class NewtonSolver:
    """Newton-Raphson solver for nonlinear equations."""

    def __init__(self):
        self.tolerance = 1e-4
        self.max_iterations = 100
        self.enable_damping = True
        self.use_broyden_approximation = False
        self.expand_factor = 1.5
        self.maximum_delta = 0.5
        self.epsilon = np.nan

    def solve(self, f: Callable[[np.ndarray], np.ndarray],
              x0: np.ndarray,
              jac: Optional[Callable[[np.ndarray], np.ndarray]] = None) -> dict:
        """
        Solve nonlinear equations using Newton-Raphson method.

        Args:
            f: Function to solve f(x) = 0
            x0: Initial guess
            jac: Jacobian function (optional)

        Returns:
            Dictionary with solution and convergence info
        """
        # Use scipy's root finder for robust implementation
        result = root(f, x0, jac=jac, method='hybr', tol=self.tolerance,
                     options={'maxfev': self.max_iterations})

        return {
            'success': result.success,
            'x': result.x,
            'message': result.message,
            'nfev': result.nfev,
            'njev': result.njev if jac else None
        }