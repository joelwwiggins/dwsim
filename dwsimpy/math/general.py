"""
General Math Functions

Converted from DWSIM.Math/General.vb to Python.
Common mathematical utilities.
"""

import numpy as np
from typing import List, Any


class Common:
    """Common mathematical functions."""

    @staticmethod
    def copy_to_vector(arr: List[List[float]], index: int) -> np.ndarray:
        """Copy values from a specific index in array of arrays to a vector."""
        return np.array([row[index] for row in arr])

    @staticmethod
    def max_with_condition(vv: np.ndarray, vz: np.ndarray) -> float:
        """Find maximum value where vz is not zero."""
        mask = vz != 0
        if not np.any(mask):
            return 0.0
        return np.max(vv[mask])

    @staticmethod
    def min_with_condition(vv: np.ndarray, vz: np.ndarray) -> float:
        """Find minimum value where vz is not zero."""
        mask = vz != 0
        if not np.any(mask):
            return 0.0
        return np.min(vv[mask])

    @staticmethod
    def sum_with_condition(vv: np.ndarray, vz: np.ndarray) -> float:
        """Sum values where vz is not zero."""
        mask = vz != 0
        return np.sum(vv[mask])

    @staticmethod
    def average_with_condition(vv: np.ndarray, vz: np.ndarray) -> float:
        """Average values where vz is not zero."""
        mask = vz != 0
        if not np.any(mask):
            return 0.0
        return np.mean(vv[mask])