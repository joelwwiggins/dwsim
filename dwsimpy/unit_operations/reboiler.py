"""
Reboiler unit operation for DWSIM Python implementation.
"""

from typing import Dict, Any, List, Optional
import numpy as np
from .base_unit import BaseUnitOperation
from ..material_stream import MaterialStream
from ..property_packages.ideal_property_package import IdealPropertyPackage


class Reboiler(BaseUnitOperation):
    """Reboiler unit operation - vaporizes liquid streams, typically used in distillation"""
    
    def __init__(self, unit_id: str, config: Dict[str, Any]):
        super().__init__(unit_id, config)
        
        # Reboiler specifications
        self.reboiler_type = config.get('reboiler_type', 'kettle')  # 'kettle' or 'thermosiphon'
        self.reboiler_pressure = config.get('reboiler_pressure', 101325)  # Pa
        self.reboiler_temperature = config.get('reboiler_temperature')  # K
        self.heat_duty = config.get('heat_duty')  # W
        
        # For thermosiphon reboilers
        self.vapor_fraction = config.get('vapor_fraction', 0.1)  # fraction of vapor generated
        
        # Heat transfer
        self.overall_heat_transfer_coeff = config.get('overall_heat_transfer_coeff', 1000.0)  # W/m²·K
        self.heat_transfer_area = config.get('heat_transfer_area')  # m²
        
        # Pressure drops
        self.pressure_drop = config.get('pressure_drop', 5000)  # Pa
        
        # Property package for phase equilibrium
        self.property_package = IdealPropertyPackage()
    
    def solve(self) -> float:
        """Solve the reboiler"""
        if len(self.inlet_streams) != 1:
            raise ValueError("Reboiler requires exactly 1 inlet stream")
        if len(self.outlet_streams) != 1 and len(self.outlet_streams) != 2:
            raise ValueError("Reboiler requires 1 outlet stream (total) or 2 outlet streams (partial)")
        
        inlet_stream = self.inlet_streams[0]
        
        if self.reboiler_type == 'kettle':
            # Kettle reboiler - single outlet stream, partial vaporization
            if len(self.outlet_streams) != 2:
                raise ValueError("Kettle reboiler requires exactly 2 outlet streams")
            
            liquid_outlet = self.outlet_streams[0]
            vapor_outlet = self.outlet_streams[1]
            
            self._solve_kettle_reboiler(inlet_stream, liquid_outlet, vapor_outlet)
            
        elif self.reboiler_type == 'thermosiphon':
            # Thermosiphon reboiler - typically single outlet stream with circulation
            if len(self.outlet_streams) != 1:
                raise ValueError("Thermosiphon reboiler requires exactly 1 outlet stream")
            
            outlet_stream = self.outlet_streams[0]
            
            self._solve_thermosiphon_reboiler(inlet_stream, outlet_stream)
        else:
            raise ValueError(f"Unknown reboiler type: {self.reboiler_type}")
        
        # Store results
        self.results = {
            'reboiler_type': self.reboiler_type,
            'reboiler_pressure': self.reboiler_pressure,
            'reboiler_temperature': self.reboiler_temperature,
            'heat_duty': self.heat_duty,
            'vapor_fraction': getattr(self, 'vapor_fraction', 0.0),
            'convergence_error': 0.0
        }
        
        return 0.0  # Simplified - no iteration needed for basic reboiler
    
    def _solve_kettle_reboiler(self, inlet: MaterialStream, liquid_outlet: MaterialStream, vapor_outlet: MaterialStream):
        """Solve kettle reboiler (partial vaporization)"""
        # Set pressures
        liquid_outlet.pressure = self.reboiler_pressure
        vapor_outlet.pressure = self.reboiler_pressure - self.pressure_drop
        
        if self.heat_duty is not None:
            # Heat duty specified - calculate temperature and vapor fraction
            self._solve_by_heat_duty_kettle(inlet, liquid_outlet, vapor_outlet)
        elif self.reboiler_temperature is not None:
            # Temperature specified - calculate heat duty and vapor fraction
            self._solve_by_temperature_kettle(inlet, liquid_outlet, vapor_outlet)
        elif self.vapor_fraction is not None:
            # Vapor fraction specified
            self._solve_by_vapor_fraction_kettle(inlet, liquid_outlet, vapor_outlet)
        else:
            raise ValueError("Kettle reboiler requires heat_duty, reboiler_temperature, or vapor_fraction")
    
    def _solve_by_heat_duty_kettle(self, inlet: MaterialStream, liquid_outlet: MaterialStream, vapor_outlet: MaterialStream):
        """Solve kettle reboiler with specified heat duty"""
        # Simplified: assume constant latent heat
        lambda_vap = 2260000  # J/kg latent heat of vaporization (water approximation)
        
        # Estimate vapor fraction from heat duty
        self.vapor_fraction = min(0.5, self.heat_duty / (inlet.mass_flow_rate * lambda_vap))
        
        # Set temperatures (assume saturated conditions)
        self.reboiler_temperature = self._calculate_bubble_point_temperature(inlet)
        liquid_outlet.temperature = self.reboiler_temperature
        vapor_outlet.temperature = self.reboiler_temperature
        
        # Set flows
        total_flow = inlet.mass_flow_rate
        vapor_outlet.mass_flow_rate = total_flow * self.vapor_fraction
        liquid_outlet.mass_flow_rate = total_flow * (1 - self.vapor_fraction)
        
        # Compositions (simplified - assume same composition)
        liquid_outlet.composition = inlet.composition.copy()
        vapor_outlet.composition = inlet.composition.copy()
    
    def _solve_by_temperature_kettle(self, inlet: MaterialStream, liquid_outlet: MaterialStream, vapor_outlet: MaterialStream):
        """Solve kettle reboiler with specified temperature"""
        liquid_outlet.temperature = self.reboiler_temperature
        vapor_outlet.temperature = self.reboiler_temperature
        
        # Simplified: estimate vapor fraction based on temperature difference from bubble point
        bubble_temp = self._calculate_bubble_point_temperature(inlet)
        temp_diff = self.reboiler_temperature - bubble_temp
        
        if temp_diff > 0:
            self.vapor_fraction = min(0.5, temp_diff / 20.0)  # Simplified correlation
        else:
            self.vapor_fraction = 0.01  # Minimum vapor fraction
        
        # Set flows
        total_flow = inlet.mass_flow_rate
        vapor_outlet.mass_flow_rate = total_flow * self.vapor_fraction
        liquid_outlet.mass_flow_rate = total_flow * (1 - self.vapor_fraction)
        
        # Compositions
        liquid_outlet.composition = inlet.composition.copy()
        vapor_outlet.composition = inlet.composition.copy()
        
        # Calculate heat duty
        lambda_vap = 2260000  # J/kg
        self.heat_duty = vapor_outlet.mass_flow_rate * lambda_vap
    
    def _solve_by_vapor_fraction_kettle(self, inlet: MaterialStream, liquid_outlet: MaterialStream, vapor_outlet: MaterialStream):
        """Solve kettle reboiler with specified vapor fraction"""
        # Set temperatures (assume saturated)
        self.reboiler_temperature = self._calculate_bubble_point_temperature(inlet)
        liquid_outlet.temperature = self.reboiler_temperature
        vapor_outlet.temperature = self.reboiler_temperature
        
        # Set flows
        total_flow = inlet.mass_flow_rate
        vapor_outlet.mass_flow_rate = total_flow * self.vapor_fraction
        liquid_outlet.mass_flow_rate = total_flow * (1 - self.vapor_fraction)
        
        # Compositions
        liquid_outlet.composition = inlet.composition.copy()
        vapor_outlet.composition = inlet.composition.copy()
        
        # Calculate heat duty
        lambda_vap = 2260000  # J/kg
        self.heat_duty = vapor_outlet.mass_flow_rate * lambda_vap
    
    def _solve_thermosiphon_reboiler(self, inlet: MaterialStream, outlet: MaterialStream):
        """Solve thermosiphon reboiler"""
        # Simplified: thermosiphon reboilers provide some vaporization for circulation
        vapor_fraction = 0.05  # Typical small vapor fraction for circulation
        
        # Set conditions
        outlet.temperature = self._calculate_bubble_point_temperature(inlet)
        outlet.pressure = self.reboiler_pressure
        outlet.mass_flow_rate = inlet.mass_flow_rate
        outlet.composition = inlet.composition.copy()
        
        # Calculate heat duty
        lambda_vap = 2260000  # J/kg
        self.heat_duty = outlet.mass_flow_rate * vapor_fraction * lambda_vap
        
        self.vapor_fraction = vapor_fraction
        self.reboiler_temperature = outlet.temperature
    
    def _calculate_bubble_point_temperature(self, stream: MaterialStream) -> float:
        """Calculate bubble point temperature at reboiler pressure"""
        # Simplified - assume ideal mixture
        # In real implementation, would use flash calculation
        return stream.temperature + 10  # Simplified approximation
    
    def validate(self) -> bool:
        """Validate reboiler configuration"""
        if len(self.inlet_streams) != 1:
            return False
        if self.reboiler_type == 'kettle' and len(self.outlet_streams) != 2:
            return False
        if self.reboiler_type == 'thermosiphon' and len(self.outlet_streams) != 1:
            return False
        if self.reboiler_pressure <= 0:
            return False
        return True
