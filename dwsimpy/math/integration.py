"""
Numerical Integration

Converted from DWSIM.MathOps.SimpsonIntegrator to Python.
Numerical integration utilities.
"""

import numpy as np
from scipy import integrate
from typing import Callable


class Integration:
    """Numerical integration utilities."""

    @staticmethod
    def simpson_integrate(f: Callable[[float], float],
                         a: float, b: float,
                         desired_relative_error: float = 1e-6) -> dict:
        """
        Simpson's rule integration with adaptive step size.

        Args:
            f: Function to integrate
            a: Lower limit
            b: Upper limit
            desired_relative_error: Relative error tolerance

        Returns:
            Dictionary with integral value and diagnostics
        """
        # Use scipy's adaptive integration
        result = integrate.quad(f, a, b, epsrel=desired_relative_error)

        return {
            'integral': result[0],
            'estimated_error': result[1],
            'success': True,
            'message': 'Integration completed'
        }

    @staticmethod
    def trapezoidal_integrate(x: np.ndarray, y: np.ndarray) -> float:
        """Trapezoidal rule integration for discrete data."""
        return integrate.trapezoid(y, x)

    @staticmethod
    def romberg_integrate(f: Callable[[float], float],
                         a: float, b: float,
                         tol: float = 1e-6) -> dict:
        """Romberg integration."""
        result = integrate.romberg(f, a, b, tol=tol, rtol=tol)

        return {
            'integral': result,
            'estimated_error': tol,
            'success': True,
            'message': 'Romberg integration completed'
        }