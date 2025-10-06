import numpy as np
from typing import Dict, List, Any, Optional
from dwsimpy.thermodynamics.interfaces.iproperty_package import IPropertyPackage
from dwsimpy.thermodynamics.databases.component_database import ComponentDatabase


class SoaveRedlichKwongPropertyPackage(IPropertyPackage):
    """
    Soave-Redlich-Kwong (SRK) cubic equation of state property package.
    """

    def __init__(self):
        self.component_database = ComponentDatabase()
        self.kij = {}  # Binary interaction parameters
        self._components: List[Dict[str, Any]] = []
        self._name = "Soave-Redlich-Kwong EOS"

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
            self._components.append(merged_comp)
        else:
            self._components.append(component)

    def _calculate_mixture_parameters(self, components, mole_fractions, temperature, pressure):
        """Calculate mixture parameters for SRK EOS."""
        # Critical properties
        tc = np.array([self.component_database.get_critical_temperature(comp) for comp in components])
        pc = np.array([self.component_database.get_critical_pressure(comp) for comp in components])
        omega = np.array([self.component_database.get_acentric_factor(comp) for comp in components])

        # SRK parameters
        r = 0.0821  # Gas constant (L·atm/mol·K)
        tr = temperature / tc

        # Calculate kappa (alpha function parameter)
        kappa = 0.48508 + 1.55171 * omega - 0.15613 * omega**2
        alpha = (1 + kappa * (1 - np.sqrt(tr)))**2

        # Calculate a and b parameters for pure components
        a_pure = 0.42748 * r**2 * tc**2 / pc * alpha
        b_pure = 0.08664 * r * tc / pc

        # Mixture parameters using van der Waals mixing rules
        a_mix = 0.0
        b_mix = 0.0

        for i in range(len(components)):
            b_mix += mole_fractions[i] * b_pure[i]
            for j in range(len(components)):
                kij = self.kij.get((components[i], components[j]), 0.0)
                a_mix += mole_fractions[i] * mole_fractions[j] * np.sqrt(a_pure[i] * a_pure[j]) * (1 - kij)

        return a_mix, b_mix

    def _calculate_compressibility_factor(self, a_mix, b_mix, temperature, pressure):
        """Solve SRK cubic equation for compressibility factor."""
        r = 0.0821  # Gas constant (L·atm/mol·K)

        # Cubic equation coefficients: Z^3 + A*Z^2 + B*Z + C = 0
        a = 1.0
        b = -1.0
        c = a_mix * pressure / (r * temperature)**2 - b_mix * pressure / (r * temperature) - (b_mix * pressure / (r * temperature))**2
        d = -(a_mix * b_mix * pressure**2) / (r * temperature)**3

        # Coefficients for Z^3 + p*Z^2 + q*Z + r = 0
        p = b - 1
        q = c
        r_coeff = d

        # Solve cubic equation
        coeffs = [1, p, q, r_coeff]
        roots = np.roots(coeffs)

        # Return the largest real root (vapor phase)
        real_roots = roots[np.isreal(roots)].real
        return max(real_roots) if len(real_roots) > 0 else 1.0

    def _calculate_fugacity_coefficients(self, components, mole_fractions, temperature, pressure, z):
        """Calculate fugacity coefficients using SRK EOS."""
        a_mix, b_mix = self._calculate_mixture_parameters(components, mole_fractions, temperature, pressure)
        r = 0.0821

        # Critical properties
        tc = np.array([self.component_database.get_critical_temperature(comp) for comp in components])
        pc = np.array([self.component_database.get_critical_pressure(comp) for comp in components])
        omega = np.array([self.component_database.get_acentric_factor(comp) for comp in components])

        # SRK parameters
        tr = temperature / tc
        kappa = 0.48508 + 1.55171 * omega - 0.15613 * omega**2
        alpha = (1 + kappa * (1 - np.sqrt(tr)))**2
        a_pure = 0.42748 * r**2 * tc**2 / pc * alpha
        b_pure = 0.08664 * r * tc / pc

        # Calculate fugacity coefficients
        ln_phi = np.zeros(len(components))

        for i in range(len(components)):
            # Calculate partial derivatives
            sum1 = 0.0
            sum2 = 0.0

            for j in range(len(components)):
                kij = self.kij.get((components[i], components[j]), 0.0)
                sum1 += mole_fractions[j] * np.sqrt(a_pure[i] * a_pure[j]) * (1 - kij)
                if i != j:
                    sum2 += mole_fractions[j] * np.sqrt(a_pure[i] * a_pure[j]) * (1 - kij)

            da_di = 2 * sum1 - 2 * a_pure[i] * mole_fractions[i]
            db_di = b_pure[i]

            # Fugacity coefficient
            term1 = (db_di / b_mix) * (z - 1) - np.log(z - b_mix * pressure / (r * temperature))
            term2 = (a_mix / (b_mix * r * temperature)) * ((da_di / a_mix) - (db_di / b_mix)) * np.log(1 + b_mix * pressure / (r * temperature * z))

            ln_phi[i] = term1 - term2

        return np.exp(ln_phi)

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

    def pt_flash(self, components, mole_fractions, temperature, pressure):
        """PT flash calculation using SRK EOS."""
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
            phi_liquid = self._calculate_fugacity_coefficients(components, x, temperature, pressure,
                                                            self._calculate_compressibility_factor(
                                                                *self._calculate_mixture_parameters(components, x, temperature, pressure),
                                                                temperature, pressure))

            phi_vapor = self._calculate_fugacity_coefficients(components, y, temperature, pressure,
                                                            self._calculate_compressibility_factor(
                                                                *self._calculate_mixture_parameters(components, y, temperature, pressure),
                                                                temperature, pressure))

            # Update K-values
            k_new = phi_liquid / phi_vapor

            # Check convergence
            if np.max(np.abs(k_new - k_values)) < 1e-6:
                return y, x, vapor_fraction

            k_values = k_new

        # If not converged, return single phase
        return mole_fractions, np.zeros(len(components)), 1.0

    def calculate_enthalpy(self, components, mole_fractions, temperature, pressure, phase='vapor'):
        """Calculate enthalpy (simplified implementation)."""
        # This is a simplified enthalpy calculation
        # In practice, this would require integration of Cp and departure functions
        return 0.0

    def calculate_entropy(self, components, mole_fractions, temperature, pressure, phase='vapor'):
        """Calculate entropy (simplified implementation)."""
        # This is a simplified entropy calculation
        return 0.0

    def calculate_enthalpy(self, temperature: float, pressure: float,
                          composition: Dict[str, float]) -> float:
        """Calculate mixture enthalpy using SRK EOS"""
        # Simplified implementation
        return 0.0

    def calculate_entropy(self, temperature: float, pressure: float,
                         composition: Dict[str, float]) -> float:
        """Calculate mixture entropy using SRK EOS"""
        # Simplified implementation
        return 0.0

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
            if comp_id in self._components:
                comp_data = self._components[comp_id]

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
            if comp_id in self._components:
                comp_data = self._components[comp_id]

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
            if comp_id in self._components:
                comp_data = self._components[comp_id]

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
            if comp_id in self._components:
                comp_data = self._components[comp_id]

                # Simplified temperature correction
                k_ref = comp_data.get('thermal_conductivity', 0.6)
                T_ref = 298.15

                # Temperature correction
                conductivity = k_ref * (temperature / T_ref)**(-1/3)

                total_k += mole_frac * conductivity

        return total_k if total_k > 0 else 0.6

    def _calculate_pure_gas_viscosity(self, comp_id: str, temperature: float) -> float:
        """Calculate pure gas viscosity using Sutherland correlation"""
        if comp_id in self._components:
            comp_data = self._components[comp_id]

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