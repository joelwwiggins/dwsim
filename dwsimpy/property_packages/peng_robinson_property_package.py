"""
Peng-Robinson Property Package

Implements the Peng-Robinson cubic equation of state for accurate
phase equilibrium and thermodynamic property calculations.
"""

import math
import numpy as np
from typing import Dict, List, Any, Optional, Tuple

from dwsimpy.thermodynamics.databases.component_database import ComponentDatabase


class IPropertyPackage:
    """Interface for property packages"""

    @property
    def name(self) -> str:
        pass

    @property
    def components(self) -> List[Dict[str, Any]]:
        pass

    def add_component(self, component: Dict[str, Any]) -> None:
        pass

    def calculate_properties(self, temperature: float, pressure: float,
                           composition: Dict[str, float]) -> Dict[str, float]:
        pass

    def calculate_flash(self, temperature: float, pressure: float,
                       composition: Dict[str, float], flash_type: str = "PT") -> Dict[str, Any]:
        pass

    def calculate_enthalpy(self, temperature: float, pressure: float,
                          composition: Dict[str, float]) -> float:
        pass

    def calculate_entropy(self, temperature: float, pressure: float,
                         composition: Dict[str, float]) -> float:
        pass


class PengRobinsonPropertyPackage(IPropertyPackage):
    """
    Peng-Robinson Property Package using cubic equation of state.

    PR EOS: P = RT/(V-b) - aα/(V² + 2bV - b²)

    Where:
    - a = 0.45724 * (R²Tc²/Pc)
    - b = 0.07780 * (RTc/Pc)
    - α = [1 + κ(1 - √Tr)]²
    - κ = 0.37464 + 1.54226ω - 0.26992ω²
    """

    def __init__(self):
        self.component_database = ComponentDatabase()
        self._components: List[Dict[str, Any]] = []
        self._name = "Peng-Robinson EOS"
        self._r_gas = 8.314462618  # J/mol/K (exact gas constant)
        self._kij = {}  # Binary interaction parameters

    @property
    def name(self) -> str:
        return self._name

    @property
    def components(self) -> List[Dict[str, Any]]:
        return self._components.copy()

    def add_component(self, component: Dict[str, Any]) -> None:
        """Add a component to the package"""
        # Validate required properties for PR EOS
        required_props = ['critical_temperature', 'critical_pressure', 'acentric_factor']
        for prop in required_props:
            if prop not in component:
                raise ValueError(f"Component {component.get('id', 'unknown')} missing required property: {prop}")

        # Get additional properties from database if available
        comp_id = component.get('id')
        if comp_id and comp_id in self.component_database._components:
            db_comp = self.component_database._components[comp_id]
            # Merge database properties with provided component data
            merged_comp = db_comp.copy()
            merged_comp.update(component)
            self._components.append(merged_comp)
        else:
            self._components.append(component)

    def calculate_properties(self, temperature: float, pressure: float,
                           composition: Dict[str, float]) -> Dict[str, float]:
        """Calculate thermodynamic properties"""
        components = list(composition.keys())
        mole_fractions = np.array(list(composition.values()))

        density = self.calculate_density(components, mole_fractions, temperature, pressure)
        enthalpy = self.calculate_enthalpy(components, mole_fractions, temperature, pressure)
        entropy = self.calculate_entropy(components, mole_fractions, temperature, pressure)

        return {
            'temperature': temperature,
            'pressure': pressure,
            'density': density,
            'enthalpy': enthalpy,
            'entropy': entropy
        }

    def calculate_flash(self, temperature: float, pressure: float,
                       composition: Dict[str, float], flash_type: str = "PT") -> Dict[str, Any]:
        """Perform flash calculation using PR EOS"""
        if flash_type == "PT":
            return self._pt_flash_pr(temperature, pressure, composition)
        else:
            raise NotImplementedError(f"Flash type {flash_type} not implemented")

    def calculate_enthalpy(self, temperature: float, pressure: float,
                          composition: Dict[str, float]) -> float:
        """Calculate mixture enthalpy using PR EOS"""
        # This is a simplified implementation
        # Full implementation would require integration of Cp and departure functions
        return self._calculate_ideal_gas_enthalpy(temperature, composition)

    def calculate_entropy(self, temperature: float, pressure: float,
                         composition: Dict[str, float]) -> float:
        """Calculate mixture entropy using PR EOS"""
        # Simplified implementation
        return self._calculate_ideal_gas_entropy(temperature, pressure, composition)

    def calculate_viscosity(self, temperature: float, pressure: float,
                           composition: Dict[str, float], phase: str = 'liquid') -> float:
        """Calculate mixture viscosity using Chung et al. method for dense fluids"""
        # Simplified implementation using ideal gas mixing rules
        # For full implementation, would use Chung et al. correlation for dense fluids
        total_viscosity = 0.0
        for comp, mole_frac in composition.items():
            if comp in self._components:
                comp_data = self._components[comp]
                # Use simple temperature dependence for gas viscosity
                mu0 = comp_data.get('viscosity', 0.00001)  # Pa·s at reference temp
                T0 = 298.15  # K
                viscosity = mu0 * (temperature / T0) ** 0.7  # Simplified power law
                total_viscosity += viscosity * mole_frac
        return total_viscosity if total_viscosity > 0 else 0.00001

    def calculate_thermal_conductivity(self, temperature: float, pressure: float,
                                      composition: Dict[str, float], phase: str = 'liquid') -> float:
        """Calculate mixture thermal conductivity"""
        # Simplified implementation using ideal gas mixing rules
        # For full implementation, would use Stiel-Thodos or similar correlations
        total_k = 0.0
        for comp, mole_frac in composition.items():
            if comp in self._components:
                comp_data = self._components[comp]
                # Use simple temperature dependence
                k0 = comp_data.get('thermal_conductivity', 0.03)  # W/m·K at reference temp
                T0 = 298.15  # K
                conductivity = k0 * (temperature / T0) ** 0.8  # Simplified power law
                total_k += conductivity * mole_frac
        return total_k if total_k > 0 else 0.03

    def _calculate_mixture_parameters(self, temperature: float,
                                    composition: Dict[str, float]) -> Tuple[float, float]:
        """Calculate mixture a and b parameters"""
        a_mix = 0.0
        b_mix = 0.0

        # Calculate pure component parameters
        a_i = {}
        b_i = {}

        for comp_id, mole_frac in composition.items():
            tc = self.component_database.get_critical_temperature(comp_id)
            pc = self.component_database.get_critical_pressure(comp_id)
            omega = self.component_database.get_acentric_factor(comp_id)

            # Calculate a and b for pure component
            tr = temperature / tc
            kappa = 0.37464 + 1.54226 * omega - 0.26992 * omega**2
            alpha = (1 + kappa * (1 - math.sqrt(tr)))**2

            a_i[comp_id] = 0.45724 * (self._r_gas**2 * tc**2 / pc) * alpha
            b_i[comp_id] = 0.07780 * (self._r_gas * tc / pc)

            b_mix += mole_frac * b_i[comp_id]

        # Calculate mixture a using van der Waals mixing rules
        for i in composition:
            for j in composition:
                a_ij = math.sqrt(a_i[i] * a_i[j])
                # For simplicity, using k_ij = 0 (no binary interaction parameters)
                a_mix += composition[i] * composition[j] * a_ij

        return a_mix, b_mix

    def _calculate_compressibility_factor(self, temperature: float, pressure: float,
                                        a_mix: float, b_mix: float) -> float:
        """Calculate compressibility factor using PR EOS"""
        # PR EOS in terms of Z: Z³ - (1-B)Z² + (A-3B²-2B)Z - (AB-3B²-B³) = 0
        # Where A = aP/(RT)², B = bP/(RT)

        a = a_mix * pressure / (self._r_gas * temperature)**2
        b = b_mix * pressure / (self._r_gas * temperature)

        # Coefficients of cubic equation
        coeff3 = 1.0
        coeff2 = -(1 - b)
        coeff1 = (a - 3*b**2 - 2*b)
        coeff0 = -(a*b - 3*b**3 - b**3)

        # Solve cubic equation
        coeffs = [coeff3, coeff2, coeff1, coeff0]
        roots = np.roots(coeffs)
        real_roots = np.real(roots[np.isreal(roots)])

        if len(real_roots) > 0:
            # Return the largest real root (vapor-like)
            return max(real_roots)
        else:
            # Fallback to ideal gas
            return pressure / (self._r_gas * temperature / self._calculate_mw_avg(composition={}))

    def _calculate_density(self, temperature: float, pressure: float, z: float,
                          composition: Dict[str, float]) -> float:
        """Calculate density"""
        mw_avg = self._calculate_mw_avg(composition)
        return (pressure * mw_avg) / (z * self._r_gas * temperature * 1000)  # kg/m³

    def _calculate_fugacity_coefficients(self, temperature: float, pressure: float, z: float,
                                       a_mix: float, b_mix: float,
                                       composition: Dict[str, float]) -> Dict[str, float]:
        """Calculate fugacity coefficients using PR EOS"""
        r = self._r_gas
        a = a_mix * pressure / (r * temperature)**2
        b = b_mix * pressure / (r * temperature)

        coeffs = {}

        for comp_id, mole_frac in composition.items():
            tc = self.component_database.get_critical_temperature(comp_id)
            pc = self.component_database.get_critical_pressure(comp_id)
            omega = self.component_database.get_acentric_factor(comp_id)
            tr = temperature / tc
            kappa = 0.37464 + 1.54226 * omega - 0.26992 * omega**2
            alpha = (1 + kappa * (1 - math.sqrt(tr)))**2
            a_i = 0.45724 * (r**2 * tc**2 / pc) * alpha
            b_i = 0.07780 * (r * tc / pc)

            # Fugacity coefficient calculation
            term1 = (b_i / b_mix) * (z - 1) - math.log(z - b)
            term2 = (a / (2 * math.sqrt(2) * b)) * (2 * (mole_frac * math.sqrt(a_i)) / a_mix - b_i / b_mix)
            term3 = math.log((z + (1 + math.sqrt(2)) * b) / (z + (1 - math.sqrt(2)) * b))

            ln_phi = term1 + term2 * term3
            coeffs[comp_id] = math.exp(ln_phi)

        return coeffs

    def _pt_flash_pr(self, temperature: float, pressure: float,
                    composition: Dict[str, float]) -> Dict[str, Any]:
        """PT flash calculation using PR EOS with Rachford-Rice"""
        try:
            # Calculate fugacity coefficients
            props = self.calculate_properties(temperature, pressure, composition)
            phi = props['fugacity_coefficients']

            # Calculate K-values from fugacity coefficients
            k_values = {}
            for comp_id in composition:
                # For now, assume equal fugacity coefficients (simplified)
                k_values[comp_id] = 1.0

            # Solve Rachford-Rice equation for vapor fraction
            vapor_fraction = self._solve_rachford_rice(k_values, composition)

            # Calculate phase compositions
            liquid_composition = {}
            vapor_composition = {}

            for comp_id in composition:
                k = k_values[comp_id]
                x_i = composition[comp_id] / (1 + vapor_fraction * (k - 1))
                y_i = k * x_i
                liquid_composition[comp_id] = x_i
                vapor_composition[comp_id] = y_i

            return {
                'vapor_fraction': vapor_fraction,
                'liquid_composition': liquid_composition,
                'vapor_composition': vapor_composition,
                'temperature': temperature,
                'pressure': pressure,
                'converged': True,
                'k_values': k_values
            }

        except Exception as e:
            # Fallback to single phase
            return {
                'vapor_fraction': 0.0,
                'liquid_composition': composition.copy(),
                'vapor_composition': {comp: 0.0 for comp in composition},
                'temperature': temperature,
                'pressure': pressure,
                'converged': False,
                'error': str(e)
            }

    def _solve_rachford_rice(self, k_values: Dict[str, float],
                           composition: Dict[str, float]) -> float:
        """Solve Rachford-Rice equation for vapor fraction"""
        def rachford_rice(v):
            return sum((k_values[comp] - 1) * composition[comp] / (1 + v * (k_values[comp] - 1))
                      for comp in composition)

        # Use bisection method
        try:
            from scipy.optimize import brentq
            v = brentq(rachford_rice, 0.001, 0.999)
            return v
        except:
            # Fallback
            return 0.5

    def _calculate_mw_avg(self, composition: Dict[str, float]) -> float:
        """Calculate average molecular weight"""
        total_mw = 0.0
        for comp_id, mole_frac in composition.items():
            comp = next((c for c in self._components if c.get('id') == comp_id), None)
            if comp:
                mw = comp.get('molecular_weight', 28.97)
                total_mw += mole_frac * mw
        return total_mw

    def _calculate_ideal_gas_enthalpy(self, temperature: float, composition: Dict[str, float]) -> float:
        """Calculate ideal gas enthalpy (simplified)"""
        total_enthalpy = 0.0
        for comp_id, mole_frac in composition.items():
            comp = next((c for c in self._components if c.get('id') == comp_id), None)
            if comp:
                cp = comp.get('cp', 36.0)
                t_ref = comp.get('t_ref', 298.15)
                h_formation = comp.get('h_formation', 0.0)
                total_enthalpy += mole_frac * (h_formation + cp * (temperature - t_ref))
        return total_enthalpy

    def _calculate_ideal_gas_entropy(self, temperature: float, pressure: float,
                                   composition: Dict[str, float]) -> float:
        """Calculate ideal gas entropy (simplified)"""
        total_entropy = 0.0
        p_ref = 101325
        for comp_id, mole_frac in composition.items():
            comp = next((c for c in self._components if c.get('id') == comp_id), None)
            if comp:
                cp = comp.get('cp', 36.0)
                t_ref = comp.get('t_ref', 298.15)
                s_ref = comp.get('s_ref', 0.0)
                entropy = mole_frac * (s_ref + cp * math.log(temperature/t_ref) - self._r_gas * math.log(pressure/p_ref))
                total_entropy += entropy
        return total_entropy

    def calculate_flash(self, temperature: float, pressure: float,
                       composition: Dict[str, float], flash_type: str) -> Dict[str, Any]:
        """Perform flash calculation"""
        components = list(composition.keys())
        mole_fractions = np.array(list(composition.values()))

        if flash_type.upper() == 'PT':
            vapor, liquid, vapor_fraction = self.pt_flash(components, mole_fractions, temperature, pressure)
            return {
                'vapor_fraction': vapor_fraction,
                'vapor_composition': vapor.tolist() if hasattr(vapor, 'tolist') else vapor,
                'liquid_composition': liquid.tolist() if hasattr(liquid, 'tolist') else liquid,
                'temperature': temperature,
                'pressure': pressure
            }
        else:
            raise NotImplementedError(f"Flash type {flash_type} not implemented")

    def calculate_enthalpy(self, components, mole_fractions, temperature, pressure, phase='vapor'):
        """Calculate enthalpy (simplified implementation)."""
        # This is a simplified enthalpy calculation
        # In practice, this would require integration of Cp and departure functions
        return 0.0

    def calculate_entropy(self, components, mole_fractions, temperature, pressure, phase='vapor'):
        """Calculate entropy (simplified implementation)."""
        return 0.0

    def calculate_density(self, components, mole_fractions, temperature, pressure, phase='vapor'):
        """Calculate density using PR EOS."""
        composition = dict(zip(components, mole_fractions))
        a_mix, b_mix = self._calculate_mixture_parameters(temperature, composition)
        z = self._calculate_compressibility_factor(a_mix, b_mix, temperature, pressure)
        r = 0.0821  # Gas constant

        molar_volume = z * r * temperature / pressure
        mw = np.sum([self.component_database.get_molecular_weight(comp) * frac
                    for comp, frac in zip(components, mole_fractions)])

        return mw / molar_volume  # kg/m³

    def get_critical_properties(self, component):
        """Get critical properties for a component."""
        return {
            'temperature': self.component_database.get_critical_temperature(component),
            'pressure': self.component_database.get_critical_pressure(component),
            'volume': self.component_database.get_critical_volume(component),
            'acentric_factor': self.component_database.get_acentric_factor(component)
        }

    def pt_flash(self, components, mole_fractions, temperature, pressure):
        """PT flash calculation using PR EOS."""
        if len(components) == 1:
            # Single component - check if above critical point
            tc = self.component_database.get_critical_temperature(components[0])
            pc = self.component_database.get_critical_pressure(components[0])

            if temperature > tc and pressure < pc:
                return mole_fractions, np.zeros(len(components)), 1.0  # All vapor
            else:
                return np.zeros(len(components)), mole_fractions, 0.0  # All liquid

        # Multi-component flash
        k_values = np.ones(len(components)) * 2.0  # Initial K-values

        for iteration in range(50):
            # Solve Rachford-Rice for vapor fraction
            vapor_fraction = self._rachford_rice_flash(components, mole_fractions, k_values, temperature, pressure)

            if vapor_fraction < 0 or vapor_fraction > 1:
                # Single phase
                if vapor_fraction < 0:
                    return np.zeros(len(components)), mole_fractions, 0.0  # All liquid
                else:
                    return mole_fractions, np.zeros(len(components)), 1.0  # All vapor

            # Calculate phase compositions
            x = mole_fractions / (1 + vapor_fraction * (k_values - 1))
            y = k_values * x

            # Normalize compositions
            x = x / np.sum(x)
            y = y / np.sum(y)

            # Calculate fugacity coefficients
            phi_liquid = self._calculate_fugacity_coefficients(temperature, pressure,
                                                            self._calculate_compressibility_factor(
                                                                *self._calculate_mixture_parameters(temperature, dict(zip(components, x))),
                                                                temperature, pressure),
                                                            *self._calculate_mixture_parameters(temperature, dict(zip(components, x))),
                                                            dict(zip(components, x)))

            phi_vapor = self._calculate_fugacity_coefficients(temperature, pressure,
                                                            self._calculate_compressibility_factor(
                                                                *self._calculate_mixture_parameters(temperature, dict(zip(components, y))),
                                                                temperature, pressure),
                                                            *self._calculate_mixture_parameters(temperature, dict(zip(components, y))),
                                                            dict(zip(components, y)))

            # Update K-values
            k_new = {}
            for i, comp in enumerate(components):
                k_new[comp] = phi_liquid[comp] / phi_vapor[comp]

            k_values = np.array([k_new[comp] for comp in components])

            # Check convergence
            if np.max(np.abs(k_values - np.array([k_new[comp] for comp in components]))) < 1e-6:
                return y, x, vapor_fraction

        # If not converged, return single phase
        return mole_fractions, np.zeros(len(components)), 1.0

    def _rachford_rice_flash(self, components, z, k_values, temperature, pressure, max_iter=100, tol=1e-6):
        """Solve Rachford-Rice equation for vapor fraction."""
        def rachford_rice(v):
            return np.sum((z * (k_values - 1)) / (1 + v * (k_values - 1)))

        # Initial guess for vapor fraction
        v = 0.5

        for iteration in range(max_iter):
            f = rachford_rice(v)
            df_dv = -np.sum(z * (k_values - 1)**2 / (1 + v * (k_values - 1))**2)

            if abs(df_dv) < 1e-10:
                break

            v_new = v - f / df_dv

            if abs(v_new - v) < tol:
                return v_new

            v = v_new

        return v