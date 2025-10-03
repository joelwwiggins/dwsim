"""
Newton-Raphson Solver

Converted from VB.NET to Python.
This module implements the Newton-Raphson method for solving nonlinear equations.
"""

import numpy as np
from typing import Callable, List, Any


class NewtonRaphsonSolver:
    """
    Newton-Raphson solver for nonlinear equations.
    """

    def __init__(self, max_iterations: int = 100, tolerance: float = 1e-6):
        self.max_iterations = max_iterations
        self.tolerance = tolerance

    def solve(self, f: Callable[[List[float]], List[float]], 
              df: Callable[[List[float]], np.ndarray], 
              x0: List[float]) -> List[float]:
        """
        Solve f(x) = 0 using Newton-Raphson method.

        f: function that returns residuals
        df: Jacobian matrix function
        x0: initial guess
        """
        x = np.array(x0, dtype=float)
        
        for iteration in range(self.max_iterations):
            residuals = np.array(f(x))
            jacobian = np.array(df(x))
            
            # Check convergence
            if np.linalg.norm(residuals) < self.tolerance:
                return x.tolist()
            
            # Solve J * dx = -f
            try:
                dx = np.linalg.solve(jacobian, -residuals)
                x += dx
            except np.linalg.LinAlgError:
                raise ValueError("Jacobian is singular")
        
        raise ValueError("Newton-Raphson did not converge")