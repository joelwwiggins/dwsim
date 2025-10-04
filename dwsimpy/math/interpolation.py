"""
Interpolation Functions

Converted from DWSIM.Math/Interpolation.vb to Python.
Various interpolation methods.
"""

import numpy as np
from scipy import interpolate
from typing import List, Tuple


class Interpolation:
    """Interpolation utilities."""

    @staticmethod
    def linear_interpolation(x: np.ndarray, y: np.ndarray, x_interp: float) -> float:
        """Linear interpolation."""
        return np.interp(x_interp, x, y)

    @staticmethod
    def spline_interpolation(x: np.ndarray, y: np.ndarray, x_interp: float,
                           kind: str = 'cubic') -> float:
        """Spline interpolation."""
        f = interpolate.interp1d(x, y, kind=kind)
        return float(f(x_interp))

    @staticmethod
    def bilinear_interpolation(x1: np.ndarray, x2: np.ndarray,
                             z: np.ndarray, x1_interp: float, x2_interp: float) -> float:
        """Bilinear interpolation."""
        f = interpolate.interp2d(x1, x2, z, kind='linear')
        return float(f(x1_interp, x2_interp))

    @staticmethod
    def extrapolate_linear(x: np.ndarray, y: np.ndarray, x_extrap: float) -> float:
        """Linear extrapolation."""
        if x_extrap < x[0]:
            # Extrapolate left
            slope = (y[1] - y[0]) / (x[1] - x[0])
            return y[0] + slope * (x_extrap - x[0])
        elif x_extrap > x[-1]:
            # Extrapolate right
            slope = (y[-1] - y[-2]) / (x[-1] - x[-2])
            return y[-1] + slope * (x_extrap - x[-1])
        else:
            # Interpolate
            return np.interp(x_extrap, x, y)