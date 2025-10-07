"""
Condenser unit operation for DWSIM Python implementation.
"""

from typing import Dict, Any, List, Optional
import numpy as np
from .base_unit import BaseUnitOperation
from ..material_stream import MaterialStream
from ..property_packages.ideal_property_package import IdealPropertyPackage


class Condenser(BaseUnitOperation):
    """Condenser unit operation - condenses vapor streams to liquid"""
    
    def __init__(self, unit_id: str, config: Dict[str, Any]):
        super().__init__(unit_id, config)
        
        # Condenser specifications
        self.condenser_type = config.get('condenser_type', 'total')  # 'total' or 'partial'
        self.condenser_pressure = config.get('condenser_pressure', 101325)  # Pa
        self.condenser_temperature = config.get('condenser_temperature')  # K (for partial condenser)
        self.heat_duty = config.get('heat_duty')  # W (calculated if not specified)
        
        # For partial condensers
        self.vapor_fraction = config.get('vapor_fraction', 0.0)  # fraction of vapor leaving
        
        # Heat transfer
        self.overall_heat_transfer_coeff = config.get('overall_heat_transfer_coeff', 500.0)  # W/m²·K
        self.heat_transfer_area = config.get('heat_transfer_area')  # m²
        
        # Pressure drops
        self.pressure_drop = config.get('pressure_drop', 10000)  # Pa
        
        # Property package for phase equilibrium
        self.property_package = IdealPropertyPackage()
    
    def solve(self) -> float:
        """Solve the condenser"""
        if len(self.inlet_streams) != 1:
            raise ValueError("Condenser requires exactly 1 inlet stream")
        if len(self.outlet_streams) != 1 and len(self.outlet_streams) != 2:
            raise ValueError("Condenser requires 1 outlet stream (total) or 2 outlet streams (partial)")
        
        inlet_stream = self.inlet_streams[0]
        
        if self.condenser_type == 'total':
            # Total condenser - single outlet stream
            if len(self.outlet_streams) != 1:
                raise ValueError("Total condenser requires exactly 1 outlet stream")
            
            outlet_stream = self.outlet_streams[0]
            
            # For total condenser, condense everything to saturated liquid
            outlet_stream.temperature = self._calculate_dew_point_temperature(inlet_stream)
            outlet_stream.pressure = self.condenser_pressure
            outlet_stream.composition = inlet_stream.composition.copy()
            outlet_stream.mass_flow_rate = inlet_stream.mass_flow_rate
            
            # Calculate heat duty
            self.heat_duty = self._calculate_condensation_heat_duty(inlet_stream, outlet_stream)
            
        elif self.condenser_type == 'partial':
            # Partial condenser - two outlet streams
            if len(self.outlet_streams) != 2:
                raise ValueError("Partial condenser requires exactly 2 outlet streams")
            
            liquid_outlet = self.outlet_streams[0]
            vapor_outlet = self.outlet_streams[1]
            
            if self.condenser_temperature is not None:
                # Temperature specified
                self._solve_partial_condenser_by_temperature(inlet_stream, liquid_outlet, vapor_outlet)
            elif self.vapor_fraction is not None:
                # Vapor fraction specified
                self._solve_partial_condenser_by_vapor_fraction(inlet_stream, liquid_outlet, vapor_outlet)
            else:
                raise ValueError("Partial condenser requires either condenser_temperature or vapor_fraction")
            
            # Calculate heat duty
            total_enthalpy_out = (liquid_outlet.mass_flow_rate * self._calculate_liquid_enthalpy(liquid_outlet) + 
                                vapor_outlet.mass_flow_rate * self._calculate_vapor_enthalpy(vapor_outlet))
            inlet_enthalpy = inlet_stream.mass_flow_rate * self._calculate_vapor_enthalpy(inlet_stream)
            self.heat_duty = inlet_enthalpy - total_enthalpy_out
        else:
            raise ValueError(f"Unknown condenser type: {self.condenser_type}")
        
        # Store results
        self.results = {
            'condenser_type': self.condenser_type,
            'condenser_pressure': self.condenser_pressure,
            'condenser_temperature': self.condenser_temperature,
            'heat_duty': self.heat_duty,
            'vapor_fraction': getattr(self, 'vapor_fraction', 0.0),
            'convergence_error': 0.0
        }
        
        return 0.0  # Simplified - no iteration needed for basic condenser
    
    def _calculate_dew_point_temperature(self, stream: MaterialStream) -> float:
        """Calculate dew point temperature at condenser pressure"""
        # Simplified - assume ideal mixture
        # In real implementation, would use flash calculation
        return stream.temperature - 10  # Simplified approximation
    
    def _calculate_condensation_heat_duty(self, inlet: MaterialStream, outlet: MaterialStream) -> float:
        """Calculate heat duty for condensation"""
        # Simplified enthalpy calculation
        lambda_cond = 2260000  # J/kg latent heat of vaporization (water approximation)
        return inlet.mass_flow_rate * lambda_cond
    
    def _calculate_liquid_enthalpy(self, stream: MaterialStream) -> float:
        """Calculate liquid enthalpy"""
        # Simplified - Cp * (T - T_ref)
        cp_liquid = 4186  # J/kg·K (water)
        t_ref = 273.15  # K
        return cp_liquid * (stream.temperature - t_ref)
    
    def _calculate_vapor_enthalpy(self, stream: MaterialStream) -> float:
        """Calculate vapor enthalpy"""
        # Simplified - Cp * (T - T_ref) + lambda
        cp_vapor = 2000  # J/kg·K (approximate)
        lambda_vap = 2260000  # J/kg
        t_ref = 273.15  # K
        return cp_vapor * (stream.temperature - t_ref) + lambda_vap
    
    def _solve_partial_condenser_by_temperature(self, inlet: MaterialStream, liquid_outlet: MaterialStream, vapor_outlet: MaterialStream):
        """Solve partial condenser with specified temperature"""
        # Set temperatures
        liquid_outlet.temperature = self.condenser_temperature
        vapor_outlet.temperature = self.condenser_temperature
        
        # Set pressures (with pressure drop)
        liquid_outlet.pressure = self.condenser_pressure
        vapor_outlet.pressure = self.condenser_pressure - self.pressure_drop
        
        # Simplified: assume equilibrium at condenser temperature
        # In reality, would need flash calculation
        total_flow = inlet.mass_flow_rate
        
        # Estimate vapor fraction based on temperature difference
        temp_diff = inlet.temperature - self.condenser_temperature
        if temp_diff > 0:
            self.vapor_fraction = min(0.9, temp_diff / 50.0)  # Simplified correlation
        else:
            self.vapor_fraction = 0.0
        
        vapor_outlet.mass_flow_rate = total_flow * self.vapor_fraction
        liquid_outlet.mass_flow_rate = total_flow * (1 - self.vapor_fraction)
        
        # Compositions (simplified - same for both phases)
        liquid_outlet.composition = inlet.composition.copy()
        vapor_outlet.composition = inlet.composition.copy()
    
    def _solve_partial_condenser_by_vapor_fraction(self, inlet: MaterialStream, liquid_outlet: MaterialStream, vapor_outlet: MaterialStream):
        """Solve partial condenser with specified vapor fraction"""
        # Set temperatures (simplified)
        condenser_temp = inlet.temperature - 20  # Approximate condensation temperature
        liquid_outlet.temperature = condenser_temp
        vapor_outlet.temperature = condenser_temp
        
        # Set pressures
        liquid_outlet.pressure = self.condenser_pressure
        vapor_outlet.pressure = self.condenser_pressure - self.pressure_drop
        
        # Set flows
        total_flow = inlet.mass_flow_rate
        vapor_outlet.mass_flow_rate = total_flow * self.vapor_fraction
        liquid_outlet.mass_flow_rate = total_flow * (1 - self.vapor_fraction)
        
        # Compositions
        liquid_outlet.composition = inlet.composition.copy()
        vapor_outlet.composition = inlet.composition.copy()
        
        # Update condenser temperature
        self.condenser_temperature = condenser_temp
    
    def validate(self) -> bool:
        """Validate condenser configuration"""
        if len(self.inlet_streams) != 1:
            return False
        if self.condenser_type == 'total' and len(self.outlet_streams) != 1:
            return False
        if self.condenser_type == 'partial' and len(self.outlet_streams) != 2:
            return False
        if self.condenser_pressure <= 0:
            return False
        return True
