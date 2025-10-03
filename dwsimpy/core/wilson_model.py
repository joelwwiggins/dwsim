"""
Wilson Model for Activity Coefficients

Converted from VB.NET to Python.
This module implements the Wilson equation for calculating
activity coefficients in liquid mixtures.
"""

import math
from typing import Dict, List, Tuple, Any


class IActivityCoefficientBase:
    """Interface for activity coefficient models."""

    def calc_activity_coefficients(self, T: float, Vx: List[float],
                                   otherargs: Any) -> List[float]:
        """Calculate activity coefficients."""
        raise NotImplementedError

    def calc_excess_enthalpy(self, T: float, Vx: List[float],
                             otherargs: Any) -> float:
        """Calculate excess enthalpy."""
        raise NotImplementedError

    def calc_excess_heat_capacity(self, T: float, Vx: List[float>,
                                  otherargs: Any) -> float:
        """Calculate excess heat capacity."""
        raise NotImplementedError


class WilsonModel(IActivityCoefficientBase):
    """
    Wilson Binary Interaction Parameters.

    BIPs: First key is Compound 1 CAS ID, Second key is Compound 2 CAS ID,
    Value is a tuple containing the A12 and A21 parameters in cal/mol.
    """

    def __init__(self):
        self.bips: Dict[str, Dict[str, Tuple[float, float]]] = {}

        # Load BIP data from embedded CSV
        # (in Python, we'll assume it's in a file or string)
        # For now, placeholder - replace with actual wilson_bips.csv content
        csv_data = """# Placeholder CSV data - replace with actual
CAS1;CAS2;A12;A21
50-00-0;64-19-7;0;0
# Add more lines...
"""
        lines = csv_data.strip().split('\n')[1:]  # Skip header

        for line in lines:
            if not line.strip():
                continue
            parts = line.split(';')
            if len(parts) >= 4:
                cas1 = parts[0]
                cas2 = parts[1]
                try:
                    A12 = float(parts[2])
                    A21 = float(parts[3])
                except ValueError:
                    continue

                if cas1 not in self.bips:
                    self.bips[cas1] = {}
                self.bips[cas1][cas2] = (A12, A21)

    def get_bips(self, cas1: str, cas2: str) -> float:
        """Get BIP value for compound pair."""
        if cas1 in self.bips and cas2 in self.bips[cas1]:
            return self.bips[cas1][cas2][0]  # A12
        elif cas2 in self.bips and cas1 in self.bips[cas2]:
            return self.bips[cas2][cas1][1]  # A21
        else:
            return 0.0

    def calc_activity_coefficients(self, T: float, Vx: List[float],
                                   otherargs: Any) -> List[float]:
        """
        Calculate activity coefficients using Wilson equation.

        T: Temperature in K
        Vx: Liquid phase molar composition
        otherargs: Tuple of (CAS IDs, molar volumes)
        """
        try:
            cas_ids: List[str] = otherargs[0]
            molar_volumes: List[float] = otherargs[1]

            n = len(Vx) - 1
            lambda_ij = [[0.0 for _ in range(n + 1)] for _ in range(n + 1)]

            for i in range(n + 1):
                for j in range(n + 1):
                    bip = self.get_bips(cas_ids[i], cas_ids[j])
                    # BIP is in cal/mol, convert to consistent units
                    lambda_ij[i][j] = (molar_volumes[j] / molar_volumes[i] *
                                       math.exp(-bip / (1.9872 * T)))

            sum1 = [0.0] * (n + 1)
            for i in range(n + 1):
                for j in range(n + 1):
                    sum1[i] += Vx[j] * lambda_ij[i][j]

            sum2 = [0.0] * (n + 1)
            for i in range(n + 1):
                for k in range(n + 1):
                    sum2[i] += Vx[k] * lambda_ij[k][i] / sum1[k]

            ln_act_coeff = [0.0] * (n + 1)
            act_coeff = [0.0] * (n + 1)
            for i in range(n + 1):
                ln_act_coeff[i] = -math.log(sum1[i]) + 1 - sum2[i]
                act_coeff[i] = math.exp(ln_act_coeff[i])

            return act_coeff

        except Exception as e:
            raise ValueError("Error calculating activity coefficients: "
                             f"{str(e)}")

    def calc_excess_enthalpy(self, T: float, Vx: List[float],
                             otherargs: Any) -> float:
        """Calculate excess enthalpy in kJ/kmol."""
        try:
            gamma1 = self.calc_activity_coefficients(T - 0.01, Vx, otherargs)
            gamma2 = self.calc_activity_coefficients(T + 0.01, Vx, otherargs)

            total = 0.0
            for i in range(len(Vx)):
                total += Vx[i] * (gamma2[i] - gamma1[i]) / 0.02

            hex_value = -8.314 * T ** 2 * total
            return hex_value

        except Exception as e:
            raise ValueError(f"Error calculating excess enthalpy: {str(e)}")

    def calc_excess_heat_capacity(self, T: float, Vx: List[float>,
                                  otherargs: Any) -> float:
        """Calculate excess heat capacity in kJ/kmol.K."""
        try:
            epsilon = 0.001
            hex1 = self.calc_excess_enthalpy(T - epsilon, Vx, otherargs)
            hex2 = self.calc_excess_enthalpy(T + epsilon, Vx, otherargs)

            cpex = (hex2 - hex1) / (2 * epsilon)
            return cpex

        except Exception as e:
            raise ValueError("Error calculating excess heat capacity: "
                             f"{str(e)}")