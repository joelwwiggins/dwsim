"""
Optimization Algorithms

Converted from various DWSIM.Math optimization files to Python.
Optimization utilities using scipy.
"""

import numpy as np
from scipy.optimize import minimize, minimize_scalar
from typing import Callable, Optional


class Optimization:
    """Optimization utilities."""

    @staticmethod
    def bfgs_minimize(f: Callable[[np.ndarray], float],
                     x0: np.ndarray,
                     bounds: Optional[list] = None) -> dict:
        """BFGS minimization."""
        result = minimize(f, x0, method='BFGS', bounds=bounds)
        return {
            'success': result.success,
            'x': result.x,
            'fun': result.fun,
            'message': result.message,
            'nfev': result.nfev,
            'njev': result.njev
        }

    @staticmethod
    def lbfgs_minimize(f: Callable[[np.ndarray], float],
                      x0: np.ndarray,
                      bounds: Optional[list] = None) -> dict:
        """L-BFGS-B minimization."""
        result = minimize(f, x0, method='L-BFGS-B', bounds=bounds)
        return {
            'success': result.success,
            'x': result.x,
            'fun': result.fun,
            'message': result.message,
            'nfev': result.nfev,
            'njev': result.njev
        }

    @staticmethod
    def brent_minimize(f: Callable[[float], float],
                      a: float, b: float) -> dict:
        """Brent minimization for 1D functions."""
        result = minimize_scalar(f, method='brent', bracket=(a, b))
        return {
            'success': result.success,
            'x': result.x,
            'fun': result.fun,
            'message': result.message,
            'nfev': result.nfev
        }

    @staticmethod
    def nelder_mead_minimize(f: Callable[[np.ndarray], float],
                           x0: np.ndarray) -> dict:
        """Nelder-Mead simplex minimization."""
        result = minimize(f, x0, method='Nelder-Mead')
        return {
            'success': result.success,
            'x': result.x,
            'fun': result.fun,
            'message': result.message,
            'nfev': result.nfev
        }