"""
Matrix Operations

Converted from DWSIM.Math/MatrixOps.vb to Python.
Matrix algebra utilities.
"""

import numpy as np
from numpy.linalg import inv, det, solve, eigvals, svd
from typing import Tuple


class MatrixOps:
    """Matrix operations utilities."""

    @staticmethod
    def invert_matrix(a: np.ndarray) -> np.ndarray:
        """Matrix inversion."""
        return inv(a)

    @staticmethod
    def determinant(a: np.ndarray) -> float:
        """Matrix determinant."""
        return det(a)

    @staticmethod
    def solve_linear_system(a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Solve linear system Ax = b."""
        return solve(a, b)

    @staticmethod
    def eigenvalues(a: np.ndarray) -> np.ndarray:
        """Compute eigenvalues."""
        return eigvals(a)

    @staticmethod
    def svd_decomposition(a: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Singular value decomposition."""
        U, s, Vt = svd(a)
        return U, s, Vt

    @staticmethod
    def cholesky_decomposition(a: np.ndarray) -> np.ndarray:
        """Cholesky decomposition for positive definite matrices."""
        return np.linalg.cholesky(a)

    @staticmethod
    def lu_decomposition(a: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """LU decomposition."""
        from scipy.linalg import lu
        P, L, U = lu(a)
        return P, L, U