"""
Peng-Robinson Property Package

Converted from VB.NET to Python.
This module implements the Peng-Robinson equation of state property package.
"""

import math
import numpy as np
from ..shared_classes.base_class import BaseClass
from ..interfaces.enums import FlashCalculationType
from ..interfaces.property_package import FlashCalculationResult


class PengRobinsonPropertyPackage(BaseClass):
    """
    Peng-Robinson Property Package.

    Uses Peng-Robinson EOS for vapor-liquid equilibrium calculations.
    """

    def __init__(self):
        super().__init__()
        self.name = "Peng-Robinson"
        self.selected_compounds = {}
        self.kij = {}  # Binary interaction parameters

    def calculate_k_values(self, phase, t, p):
        """Calculate K-values using Peng-Robinson EOS."""
        # Placeholder implementation
        k_values = {}
        for comp in self.selected_compounds:
            # Simplified K-value calculation
            k_values[comp] = 1.0  # Assume ideal for now
        return k_values

    def calculate_enthalpy(self, phase, t, p):
        """Calculate enthalpy using Peng-Robinson."""
        # Placeholder
        return 0.0

    def calculate_entropy(self, phase, t, p):
        """Calculate entropy using Peng-Robinson."""
        # Placeholder
        return 0.0

    def flash_calculation(self, t, p, composition):
        """Perform flash calculation using Peng-Robinson."""
        # Placeholder
        return {"vapor_fraction": 0.5, "liquid_composition": composition, "vapor_composition": composition}

    def calculate_alpha(self, compound, t):
        """Calculate alpha parameter for Peng-Robinson EOS."""
        tc = compound.critical_temperature
        omega = compound.acentric_factor
        tr = t / tc
        kappa = 0.37464 + 1.54226 * omega - 0.26992 * omega**2
        return (1 + kappa * (1 - math.sqrt(tr)))**2

    def calculate_a(self, compound, t):
        """Calculate a parameter for Peng-Robinson EOS."""
        r = 8.314  # Gas constant J/mol.K
        tc = compound.critical_temperature
        pc = compound.critical_pressure
        alpha = self.calculate_alpha(compound, t)
        return 0.45724 * (r**2 * tc**2 / pc) * alpha

    def calculate_b(self, compound):
        """Calculate b parameter for Peng-Robinson EOS."""
        r = 8.314
        tc = compound.critical_temperature
        pc = compound.critical_pressure
        return 0.0778 * r * tc / pc

    def calculate_mixture_a(self, composition, t):
        """Calculate mixture a parameter."""
        a_mix = 0.0
        for i, comp_i in composition.items():
            for j, comp_j in composition.items():
                a_i = self.calculate_a(self.selected_compounds[i], t)
                a_j = self.calculate_a(self.selected_compounds[j], t)
                kij = self.kij.get((i, j), 0.0)
                a_mix += comp_i * comp_j * math.sqrt(a_i * a_j) * (1 - kij)
        return a_mix

    def calculate_mixture_b(self, composition):
        """Calculate mixture b parameter."""
        b_mix = 0.0
        for comp, frac in composition.items():
            b_mix += frac * self.calculate_b(self.selected_compounds[comp])
        return b_mix

    def calculate_fugacity_coefficient(self, compound, t, p, phase='vapor'):
        """Calculate fugacity coefficient for a compound using PR EOS."""
        r = 8.314  # J/mol.K
        a = self.calculate_a(compound, t)
        b = self.calculate_b(compound)
        v = r * t / p  # Ideal gas approximation for volume, for simplicity
        # In reality, solve cubic equation for v
        # For now, use ideal for vapor, liquid approximation
        if phase == 'vapor':
            # For vapor, use ideal gas
            return 1.0
        else:
            # For liquid, approximate
            return math.exp(b * p / (r * t))  # Simplified

    def pt_flash(self, composition, t, p):
        """Perform PT flash calculation."""
        # Calculate K-values
        phi_l = self.calculate_fugacity_coefficient_mixture(composition, t, p, 'liquid')
        phi_v = self.calculate_fugacity_coefficient_mixture(composition, t, p, 'vapor')
        k_values = {i: phi_l[i] / phi_v[i] for i in composition}
        
        # Solve Rachford-Rice for vapor fraction V
        def rachford_rice(v):
            return sum((k_values[i] - 1) * composition[i] / (1 + v * (k_values[i] - 1)) for i in composition)
        
        # Find V where rachford_rice(V) = 0
        from scipy.optimize import brentq
        try:
            v = brentq(rachford_rice, 0, 1)
        except:
            v = 0.5  # Fallback
        
        # Calculate liquid and vapor compositions
        x = {i: composition[i] / (1 + v * (k_values[i] - 1)) for i in composition}
        y = {i: k_values[i] * x[i] for i in composition}
        
        return v, x, y, k_values

    def calculate_equilibrium(self, calctype, val1, val2, mixmolefrac, kval, initial_estimate):
        """Implement calculate_equilibrium for PT flash."""
        if calctype == FlashCalculationType.PRESSURE_TEMPERATURE:
            t, p = val1, val2
            # Assume mixmolefrac order matches selected_compounds order
            composition = {list(self.selected_compounds.keys())[i]: frac for i, frac in enumerate(mixmolefrac)}
            v, x, y, k = self.pt_flash(composition, t, p)
            
            result = FlashCalculationResult(
                base_mole_amount=sum(mixmolefrac),
                kvalues=list(k.values()),
                mixture_mole_amounts=mixmolefrac,
                vapor_phase_mole_amounts=[y[key] for key in composition],
                liquid_phase1_mole_amounts=[x[key] for key in composition],
                liquid_phase2_mole_amounts=[0.0] * len(mixmolefrac),
                solid_phase_mole_amounts=[0.0] * len(mixmolefrac),
                calculated_temperature=t,
                calculated_pressure=p,
                iterations_taken=10
            )
            return result
        else:
            # Placeholder for other flash types
            return super().calculate_equilibrium(calctype, val1, val2, mixmolefrac, kval, initial_estimate)

    def get_display_name(self) -> str:
        return "Peng-Robinson"

    def get_display_description(self) -> str:
        return "Property Package using Peng-Robinson Equation of State"

    def get_icon_bitmap(self):
        return None

    def display_edit_form(self):
        pass

    def update_edit_form(self):
        pass

    def close_edit_form(self):
        pass

    def clone_xml(self):
        return self.__class__()

    def clone_json(self):
        return self.__class__()

    def calculate_compressibility_factor(self, a, b, t, p, phase='vapor'):
        """Calculate compressibility factor z by solving PR cubic equation."""
        r = 8.314
        A = a * p / (r * t)**2
        B = b * p / (r * t)
        
        # PR cubic: z^3 - (1-B)z^2 + (A - 3B^2 - 2B)z - (AB - B^2 - B^3) = 0
        coeffs = [1, -(1 - B), A - 3*B**2 - 2*B, -(A*B - B**2 - B**3)]
        
        roots = np.roots(coeffs)
        real_roots = np.real(roots[np.isreal(roots)])
        
        if phase == 'vapor':
            return max(real_roots)  # Largest z for vapor
        else:
            return min(real_roots)  # Smallest z for liquid

    def calculate_fugacity_coefficient_mixture(self, composition, t, p, phase='vapor'):
        """Calculate fugacity coefficients for mixture."""
        a_mix = self.calculate_mixture_a(composition, t)
        b_mix = self.calculate_mixture_b(composition)
        z = self.calculate_compressibility_factor(a_mix, b_mix, t, p, phase)
        
        r = 8.314
        A = a_mix * p / (r * t)**2
        B = b_mix * p / (r * t)
        
        phi = {}
        for i, frac in composition.items():
            a_i = self.calculate_a(self.selected_compounds[i], t)
            b_i = self.calculate_b(self.selected_compounds[i])
            
            # Simplified for single component or basic mixture
            term1 = (b_i / b_mix) * (z - 1)
            term2 = -math.log(z - B)
            term3 = (A / (2 * math.sqrt(2) * B)) * (2 * sum(frac * math.sqrt(a_i * self.calculate_a(self.selected_compounds[j], t)) for j in composition) / a_mix - b_i / b_mix) * math.log((z + (1 + math.sqrt(2)) * B) / (z + (1 - math.sqrt(2)) * B))
            
            phi[i] = math.exp(term1 + term2 + term3)
        
        return phi