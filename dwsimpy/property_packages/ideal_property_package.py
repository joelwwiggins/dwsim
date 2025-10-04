"""
Ideal Property Package

Converted from VB.NET to Python.
This module implements the Ideal (Raoult's Law) property package.
"""

import math
from typing import Dict, List, Any, Optional


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


# Simple component database
_component_db = {
    'water': {
        'id': 'water',
        'name': 'Water',
        'formula': 'H2O',
        'molecular_weight': 18.015,
        'critical_temperature': 647.1,
        'critical_pressure': 220.64e5,
        'acentric_factor': 0.344,
        'cp': 36.0,
        't_ref': 298.15,
        'h_formation': -285830,
        's_ref': 69.95,
        'vapor_pressure_func': lambda t: 1e5 * (t > 373 and 0.1 or 1.0)  # Simplified
    },
    'methane': {
        'id': 'methane',
        'name': 'Methane',
        'formula': 'CH4',
        'molecular_weight': 16.043,
        'critical_temperature': 190.6,
        'critical_pressure': 45.99e5,
        'acentric_factor': 0.011,
        'cp': 35.7,
        't_ref': 298.15,
        'h_formation': -74850,
        's_ref': 186.25,
        'vapor_pressure_func': lambda t: 1e5 * (t > 111 and 0.1 or 1.0)  # Simplified
    }
}


class IdealPropertyPackage(IPropertyPackage):
    """
    Ideal Property Package using Raoult's Law.

    For vapor-liquid equilibrium calculations.
    """

    def __init__(self):
        self._components: List[Dict[str, Any]] = []
        self._name = "Ideal (Raoult's Law)"

    @property
    def name(self) -> str:
        return self._name

    @property
    def components(self) -> List[Dict[str, Any]]:
        return self._components.copy()

    def add_component(self, component: Dict[str, Any]) -> None:
        """Add a component to the package"""
        # Get full component data from database
        comp_data = _component_db.get(component['id'])
        if comp_data:
            self._components.append(comp_data)
        else:
            # If not in database, use provided data
            self._components.append(component)

    def calculate_properties(self, temperature: float, pressure: float,
                           composition: Dict[str, float]) -> Dict[str, float]:
        """Calculate thermodynamic properties"""
        # For ideal gas, enthalpy and entropy are functions of temperature only
        # This is a simplified implementation
        enthalpy = self._calculate_ideal_gas_enthalpy(temperature, composition)
        entropy = self._calculate_ideal_gas_entropy(temperature, pressure, composition)

        return {
            'temperature': temperature,
            'pressure': pressure,
            'enthalpy': enthalpy,
            'entropy': entropy,
            'density': self._calculate_density(temperature, pressure, composition)
        }

    def calculate_flash(self, temperature: float, pressure: float,
                       composition: Dict[str, float], flash_type: str = "PT") -> Dict[str, Any]:
        """Perform flash calculation"""
        if flash_type == "PT":
            return self._pt_flash(temperature, pressure, composition)
        else:
            raise NotImplementedError(f"Flash type {flash_type} not implemented")

    def calculate_enthalpy(self, temperature: float, pressure: float,
                          composition: Dict[str, float]) -> float:
        """Calculate mixture enthalpy"""
        return self._calculate_ideal_gas_enthalpy(temperature, composition)

    def calculate_entropy(self, temperature: float, pressure: float,
                         composition: Dict[str, float]) -> float:
        """Calculate mixture entropy"""
        return self._calculate_ideal_gas_entropy(temperature, pressure, composition)

    def _calculate_ideal_gas_enthalpy(self, temperature: float, composition: Dict[str, float]) -> float:
        """Calculate ideal gas enthalpy"""
        total_enthalpy = 0.0
        for comp_id, mole_frac in composition.items():
            # Find component
            comp = next((c for c in self._components if c.get('id') == comp_id), None)
            if comp:
                # Use Cp * (T - T0) + H_formation as approximation
                cp = comp.get('cp', 36.0)  # J/mol/K
                t_ref = comp.get('t_ref', 298.15)
                h_formation = comp.get('h_formation', 0.0)
                total_enthalpy += mole_frac * (h_formation + cp * (temperature - t_ref))
        return total_enthalpy

    def _calculate_ideal_gas_entropy(self, temperature: float, pressure: float,
                                   composition: Dict[str, float]) -> float:
        """Calculate ideal gas entropy"""
        # S = Cp*ln(T/T0) - R*ln(P/P0) + S0
        total_entropy = 0.0
        r_gas = 8.314  # J/mol/K
        p_ref = 101325  # Pa

        for comp_id, mole_frac in composition.items():
            comp = next((c for c in self._components if c.get('id') == comp_id), None)
            if comp:
                cp = comp.get('cp', 36.0)
                t_ref = comp.get('t_ref', 298.15)
                s_ref = comp.get('s_ref', 0.0)
                entropy = mole_frac * (s_ref + cp * math.log(temperature/t_ref) - r_gas * math.log(pressure/p_ref))
                total_entropy += entropy

        return total_entropy

    def _calculate_density(self, temperature: float, pressure: float,
                          composition: Dict[str, float]) -> float:
        """Calculate density using ideal gas law"""
        r_gas = 8.314  # J/mol/K
        mw_avg = self._calculate_average_molecular_weight(composition)
        return (pressure * mw_avg) / (r_gas * temperature * 1000)  # kg/m³

    def _calculate_average_molecular_weight(self, composition: Dict[str, float]) -> float:
        """Calculate average molecular weight"""
        total_mw = 0.0
        for comp_id, mole_frac in composition.items():
            comp = next((c for c in self._components if c.get('id') == comp_id), None)
            if comp:
                mw = comp.get('molecular_weight', 28.97)  # Default air
                total_mw += mole_frac * mw
        return total_mw

    def _pt_flash(self, temperature: float, pressure: float,
                  composition: Dict[str, float]) -> Dict[str, Any]:
        """PT flash calculation using Raoult's Law"""
        # Simplified PT flash
        # Assume all components are condensable
        vapor_fraction = 0.0
        liquid_composition = composition.copy()
        vapor_composition = {comp: 0.0 for comp in composition}

        # Calculate bubble point pressure
        bubble_p = 0.0
        for comp_id, x in composition.items():
            comp = next((c for c in self._components if c.get('id') == comp_id), None)
            if comp and 'vapor_pressure_func' in comp:
                p_sat = comp['vapor_pressure_func'](temperature)
                bubble_p += x * p_sat

        if pressure < bubble_p:
            # All vapor
            vapor_fraction = 1.0
            vapor_composition = composition.copy()
            liquid_composition = {comp: 0.0 for comp in composition}
        elif pressure > bubble_p:
            # All liquid
            vapor_fraction = 0.0
        else:
            # Two-phase - simplified
            vapor_fraction = 0.5
            # In real implementation, would solve Rachford-Rice equation

        return {
            'vapor_fraction': vapor_fraction,
            'liquid_composition': liquid_composition,
            'vapor_composition': vapor_composition,
            'temperature': temperature,
            'pressure': pressure
        }