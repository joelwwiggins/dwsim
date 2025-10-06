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
        # Get additional properties from database if available
        comp_id = component.get('id')
        if comp_id and comp_id in self.component_database._components:
            db_comp = self.component_database._components[comp_id]
            # Merge database properties with provided component data
            merged_comp = db_comp.copy()
            merged_comp.update(component)
            component = merged_comp

        # Validate required properties for PR EOS
        required_props = ['critical_temperature', 'critical_pressure', 'acentric_factor']
        for prop in required_props:
            if prop not in component:
                raise ValueError(f"Component {component.get('id', 'unknown')} missing required property: {prop}")

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
        """Calculate mixture viscosity using proper correlations"""
        if phase.lower() == 'gas' or phase.lower() == 'vapor':
            return self._calculate_gas_viscosity(temperature, pressure, composition)
        else:
            return self._calculate_liquid_viscosity(temperature, pressure, composition)

    def calculate_thermal_conductivity(self, temperature: float, pressure: float,
                                      composition: Dict[str, float], phase: str = 'liquid') -> float:
        """Calculate mixture thermal conductivity using proper correlations"""
        if phase.lower() == 'gas' or phase.lower() == 'vapor':
            return self._calculate_gas_thermal_conductivity(temperature, pressure, composition)
        else:
            return self._calculate_liquid_thermal_conductivity(temperature, pressure, composition)

    def _calculate_gas_viscosity(self, temperature: float, pressure: float,
                                composition: Dict[str, float]) -> float:
        """Calculate gas mixture viscosity using Sutherland correlation"""
        total_viscosity = 0.0
        total_mw = 0.0

        for comp_id, mole_frac in composition.items():
            if comp_id in self.component_database._components:
                comp_data = self.component_database._components[comp_id]

                # Sutherland correlation: μ = μ0 * (T/T0)^(3/2) * (T0 + C)/(T + C)
                mu0 = comp_data.get('viscosity_sutherland_mu0', comp_data.get('viscosity', 1e-5))
                T0 = comp_data.get('viscosity_sutherland_T0', 273.15)
                C = comp_data.get('viscosity_sutherland_C', 100.0)

                viscosity = mu0 * (temperature / T0)**(3/2) * (T0 + C) / (temperature + C)
                mw = comp_data.get('molecular_weight', 28.97)

                total_viscosity += mole_frac * viscosity * math.sqrt(mw)
                total_mw += mole_frac * math.sqrt(mw)

        if total_mw > 0:
            # Herning-Zipperer mixing rule for gas mixtures
            return (total_viscosity / total_mw)**2
        else:
            return 1e-5

    def _calculate_liquid_viscosity(self, temperature: float, pressure: float,
                                   composition: Dict[str, float]) -> float:
        """Calculate liquid mixture viscosity using Andrade correlation"""
        total_viscosity = 0.0

        for comp_id, mole_frac in composition.items():
            if comp_id in self.component_database._components:
                comp_data = self.component_database._components[comp_id]

                # Andrade correlation: μ = A * exp(B/T)
                A = comp_data.get('viscosity_andrade_A', 0.001)
                B = comp_data.get('viscosity_andrade_B', 1000.0)

                viscosity = A * math.exp(B / temperature)

                # Apply pressure correction (simplified)
                pressure_correction = 1.0 + 1e-9 * (pressure - 101325)
                viscosity *= pressure_correction

                total_viscosity += mole_frac / viscosity

        if total_viscosity > 0:
            # Harmonic mean for liquid mixtures
            return 1.0 / total_viscosity
        else:
            return 0.001

    def _calculate_gas_thermal_conductivity(self, temperature: float, pressure: float,
                                           composition: Dict[str, float]) -> float:
        """Calculate gas mixture thermal conductivity using Eucken correlation"""
        total_k = 0.0
        total_mw = 0.0

        for comp_id, mole_frac in composition.items():
            if comp_id in self.component_database._components:
                comp_data = self.component_database._components[comp_id]

                # Eucken correlation: k = (Cp + 1.25*R/MW) * μ
                cp = comp_data.get('cp', 36.0)  # J/mol/K
                mw = comp_data.get('molecular_weight', 28.97)
                r_gas = 8.314  # J/mol/K

                # Get viscosity first
                viscosity = self._calculate_pure_gas_viscosity(comp_id, temperature)

                # Eucken correlation
                conductivity = (cp + 1.25 * r_gas / mw) * viscosity / 1000  # Convert to W/m·K

                total_k += mole_frac * conductivity * math.sqrt(mw)
                total_mw += mole_frac * math.sqrt(mw)

        if total_mw > 0:
            # Wassiljewa mixing rule
            return total_k / total_mw
        else:
            return 0.03

    def _calculate_liquid_thermal_conductivity(self, temperature: float, pressure: float,
                                              composition: Dict[str, float]) -> float:
        """Calculate liquid mixture thermal conductivity using Missenard correlation"""
        total_k = 0.0

        for comp_id, mole_frac in composition.items():
            if comp_id in self.component_database._components:
                comp_data = self.component_database._components[comp_id]

                # Missenard correlation: k = A * (Cp * MW)^(1/3) * ρ^(4/3) / T^(1/3)
                # Simplified version using reference values
                A = comp_data.get('thermal_conductivity_missenard_A', 0.000088)
                k_ref = comp_data.get('thermal_conductivity', 0.6)
                T_ref = 298.15

                # Temperature correction
                conductivity = k_ref * (temperature / T_ref)**(-1/3)

                total_k += mole_frac * conductivity

        return total_k if total_k > 0 else 0.6

    def _calculate_pure_gas_viscosity(self, comp_id: str, temperature: float) -> float:
        """Calculate pure gas viscosity using Sutherland correlation"""
        if comp_id in self.component_database._components:
            comp_data = self.component_database._components[comp_id]

            mu0 = comp_data.get('viscosity_sutherland_mu0', comp_data.get('viscosity', 1e-5))
            T0 = comp_data.get('viscosity_sutherland_T0', 273.15)
            C = comp_data.get('viscosity_sutherland_C', 100.0)

            return mu0 * (temperature / T0)**(3/2) * (T0 + C) / (temperature + C)
        else:
            return 1e-5

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
        z = self._calculate_compressibility_factor(temperature, pressure, a_mix, b_mix)
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

    def _calculate_mixture_parameters(self, temperature: float, composition: Dict[str, float]) -> Tuple[float, float]:
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

    def _calculate_compressibility_factor(self, temperature: float, pressure: float, a_mix: float, b_mix: float) -> float:
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
            return pressure / (self._r_gas * temperature / self._calculate_mw_avg({}))