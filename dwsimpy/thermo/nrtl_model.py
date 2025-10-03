"""
NRTL Model for Activity Coefficients

Converted from VB.NET to Python.
This module implements the NRTL equation for calculating
activity coefficients in liquid mixtures.
"""

import math
from typing import Dict, List, Tuple, Any
from .base_model import IActivityCoefficientBase


class NRTLIPData:
    """NRTL Interaction Parameter Data."""

    def __init__(self):
        self.id1: str = ""
        self.id2: str = ""
        self.a12: float = 0.0
        self.a21: float = 0.0
        self.alpha12: float = 0.0
        self.comment: str = ""
        self.b12: float = 0.0
        self.b21: float = 0.0
        self.c12: float = 0.0
        self.c21: float = 0.0

    def clone(self) -> 'NRTLIPData':
        new_data = NRTLIPData()
        new_data.id1 = self.id1
        new_data.id2 = self.id2
        new_data.a12 = self.a12
        new_data.a21 = self.a21
        new_data.alpha12 = self.alpha12
        new_data.comment = self.comment
        new_data.b12 = self.b12
        new_data.b21 = self.b21
        new_data.c12 = self.c12
        new_data.c21 = self.c21
        return new_data


class NRTLModel(IActivityCoefficientBase):
    """
    NRTL Binary Interaction Parameters.

    IPs: First key is Compound 1 CAS ID, Second key is Compound 2 CAS ID,
    Value is NRTL_IPData object.
    """

    def __init__(self):
        self.ips: Dict[str, Dict[str, NRTLIPData]] = {}

        # Load IP data from embedded CSV
        # Placeholder - replace with actual nrtl_ips.csv content
        csv_data = """# Placeholder CSV data - replace with actual
ID1;ID2;A12;A21;alpha12;comment
50-00-0;64-19-7;0;0;0.3;
# Add more lines...
"""
        lines = csv_data.strip().split('\n')[1:]  # Skip header

        for line in lines:
            if not line.strip():
                continue
            parts = line.split(';')
            if len(parts) >= 5:
                id1 = parts[0]
                id2 = parts[1]
                try:
                    a12 = float(parts[2])
                    a21 = float(parts[3])
                    alpha12 = float(parts[4])
                    comment = parts[5] if len(parts) > 5 else ""
                except ValueError:
                    continue

                ip_data = NRTLIPData()
                ip_data.id1 = id1
                ip_data.id2 = id2
                ip_data.a12 = a12
                ip_data.a21 = a21
                ip_data.alpha12 = alpha12
                ip_data.comment = comment

                if id1 not in self.ips:
                    self.ips[id1] = {}
                self.ips[id1][id2] = ip_data

    def get_ips(self, id1: str, id2: str) -> NRTLIPData:
        """Get IP data for compound pair."""
        if id1 in self.ips and id2 in self.ips[id1]:
            return self.ips[id1][id2]
        elif id2 in self.ips and id1 in self.ips[id2]:
            # Symmetric, but need to swap a12/a21
            ip = self.ips[id2][id1].clone()
            ip.a12, ip.a21 = ip.a21, ip.a12
            ip.id1, ip.id2 = id1, id2
            return ip
        else:
            # Default
            default_ip = NRTLIPData()
            default_ip.id1 = id1
            default_ip.id2 = id2
            default_ip.alpha12 = 0.3
            return default_ip

    def calc_activity_coefficients(self, T: float, Vx: List[float], otherargs: Any) -> List[float]:
        """
        Calculate activity coefficients using NRTL equation.

        T: Temperature in K
        Vx: Liquid phase molar composition
        otherargs: Tuple of (CAS IDs,)
        """
        try:
            cas_ids: List[str] = otherargs[0]

            n = len(Vx)
            gamma = [0.0] * n

            # Calculate tau_ij = a_ij / (R*T), G_ij = exp(-alpha_ij * tau_ij)
            tau = [[0.0 for _ in range(n)] for _ in range(n)]
            G = [[0.0 for _ in range(n)] for _ in range(n)]

            for i in range(n):
                for j in range(n):
                    if i != j:
                        ip = self.get_ips(cas_ids[i], cas_ids[j])
                        tau[i][j] = ip.a12 / (8.314 * T / 1000)  # Convert to J/mol
                        G[i][j] = math.exp(-ip.alpha12 * tau[i][j])
                    else:
                        tau[i][j] = 0.0
                        G[i][j] = 1.0

            # Calculate activity coefficients
            for i in range(n):
                sum1 = 0.0
                for j in range(n):
                    sum1 += Vx[j] * tau[j][i] * G[j][i]

                sum2 = 0.0
                for j in range(n):
                    sum2_inner = 0.0
                    for k in range(n):
                        sum2_inner += Vx[k] * G[k][j]
                    sum2 += Vx[j] * G[j][i] / sum2_inner

                sum3 = 0.0
                for j in range(n):
                    sum3_inner1 = 0.0
                    for m in range(n):
                        sum3_inner1 += Vx[m] * tau[m][j] * G[m][j]
                    sum3_inner2 = 0.0
                    for k in range(n):
                        sum3_inner2 += Vx[k] * G[k][j]
                    sum3 += Vx[j] * G[i][j] / sum3_inner2 * (tau[i][j] - sum3_inner1 / sum3_inner2)

                ln_gamma = sum1 / sum2 + sum3
                gamma[i] = math.exp(ln_gamma)

            return gamma

        except Exception as e:
            raise ValueError("Error calculating activity coefficients: "
                             f"{str(e)}")

    def calc_excess_enthalpy(self, T: float, Vx: List[float], otherargs: Any) -> float:
        """Calculate excess enthalpy in kJ/kmol."""
        try:
            epsilon = 0.01
            gamma1 = self.calc_activity_coefficients(T - epsilon, Vx, otherargs)
            gamma2 = self.calc_activity_coefficients(T + epsilon, Vx, otherargs)

            total = 0.0
            for i in range(len(Vx)):
                total += Vx[i] * (math.log(gamma2[i]) - math.log(gamma1[i])) / (2 * epsilon)

            hex_value = -8.314 * T ** 2 * total
            return hex_value

        except Exception as e:
            raise ValueError(f"Error calculating excess enthalpy: {str(e)}")

    def calc_excess_heat_capacity(self, T: float, Vx: List[float], otherargs: Any) -> float:
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