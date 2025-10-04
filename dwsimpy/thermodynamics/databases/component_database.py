"""
Basic component database for DWSIM Python implementation.
"""

import math
from typing import Dict, Any, List


class ComponentDatabase:
    """Database of chemical components with properties"""

    def __init__(self):
        self._components: Dict[str, Dict[str, Any]] = {}
        self._load_basic_components()

    def _load_basic_components(self):
        """Load basic components"""
        # Water
        self._components['water'] = {
            'id': 'water',
            'name': 'Water',
            'formula': 'H2O',
            'molecular_weight': 18.015,
            'critical_temperature': 647.1,  # K
            'critical_pressure': 220.64e5,  # Pa
            'acentric_factor': 0.344,
            'cp': 36.0,  # J/mol/K
            't_ref': 298.15,
            'h_formation': -285830,  # J/mol
            's_ref': 69.95,  # J/mol/K
            'viscosity': 0.001,  # Pa·s at 298K
            'thermal_conductivity': 0.6,  # W/m·K at 298K
            'vapor_pressure_func': self._antoine_water
        }

        # Methane
        self._components['methane'] = {
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
            'viscosity': 0.000011,  # Pa·s at 298K (gas)
            'thermal_conductivity': 0.034,  # W/m·K at 298K (gas)
            'vapor_pressure_func': self._antoine_methane
        }

        # Ethane
        self._components['ethane'] = {
            'id': 'ethane',
            'name': 'Ethane',
            'formula': 'C2H6',
            'molecular_weight': 30.07,
            'critical_temperature': 305.3,
            'critical_pressure': 48.72e5,
            'acentric_factor': 0.099,
            'cp': 52.5,
            't_ref': 298.15,
            'h_formation': -83800,
            's_ref': 229.6,
            'vapor_pressure_func': self._antoine_ethane
        }

    def get_component(self, component_id: str) -> Dict[str, Any]:
        """Get component by ID"""
        return self._components.get(component_id)

    def get_all_components(self) -> List[Dict[str, Any]]:
        """Get all components"""
        return list(self._components.values())

    def search_components(self, query: str) -> List[Dict[str, Any]]:
        """Search components by name or formula"""
        results = []
        query_lower = query.lower()
        for comp in self._components.values():
            if (query_lower in comp['name'].lower() or
                query_lower in comp['formula'].lower()):
                results.append(comp)
        return results

    def _antoine_water(self, temperature: float) -> float:
        """Antoine equation for water vapor pressure (Pa)"""
        # Antoine constants for water (valid 1-100°C)
        # log10(P) = A - B/(T + C)
        # P in mmHg, T in °C
        if temperature < 274 or temperature > 373:
            return 1e5  # Rough estimate

        t_c = temperature - 273.15
        a, b, c = 5.00689, 1670.859, 231.494
        p_mmhg = 10**(a - b/(t_c + c))
        return p_mmhg * 133.322  # Convert to Pa

    def _antoine_methane(self, temperature: float) -> float:
        """Antoine equation for methane"""
        # Simplified
        if temperature < 100:
            return 1e5
        return 1e5 * math.exp(10 - 1000/temperature)

    def _antoine_ethane(self, temperature: float) -> float:
        """Antoine equation for ethane"""
        # Simplified
        if temperature < 150:
            return 1e5
        return 1e5 * math.exp(8 - 800/temperature)

    def get_critical_temperature(self, component_id: str) -> float:
        """Get critical temperature for component"""
        comp = self.get_component(component_id)
        return comp.get('critical_temperature', 300.0) if comp else 300.0

    def get_critical_pressure(self, component_id: str) -> float:
        """Get critical pressure for component"""
        comp = self.get_component(component_id)
        return comp.get('critical_pressure', 1e6) if comp else 1e6

    def get_acentric_factor(self, component_id: str) -> float:
        """Get acentric factor for component"""
        comp = self.get_component(component_id)
        return comp.get('acentric_factor', 0.0) if comp else 0.0

    def get_molecular_weight(self, component_id: str) -> float:
        """Get molecular weight for component"""
        comp = self.get_component(component_id)
        return comp.get('molecular_weight', 28.97) if comp else 28.97

    def get_critical_volume(self, component_id: str) -> float:
        """Get critical volume for component"""
        comp = self.get_component(component_id)
        return comp.get('critical_volume', 0.1) if comp else 0.1


# Global instance
component_db = ComponentDatabase()