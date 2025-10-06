"""
Pipe unit operation for DWSIM Python implementation.
"""

from typing import Dict, Any, List, Optional
import numpy as np
from .base_unit import BaseUnitOperation


class Pipe(BaseUnitOperation):
    """Pipe unit operation - calculates pressure drop and heat loss"""
    
    def __init__(self, unit_id: str, config: Dict[str, Any]):
        super().__init__(unit_id, config)
        
        # Pipe specifications
        self.length = config.get('length', 100.0)  # m
        self.diameter = config.get('diameter', 0.1)  # m
        self.roughness = config.get('roughness', 0.000046)  # m (commercial steel)
        self.elevation_change = config.get('elevation_change', 0.0)  # m
        
        # Operating conditions
        self.ambient_temperature = config.get('ambient_temperature', 298.15)  # K
        self.heat_transfer_coeff_outside = config.get('heat_transfer_coeff_outside', 5.0)  # W/m²·K
        
        # Insulation properties
        self.insulation_thickness = config.get('insulation_thickness', 0.0)  # m
        self.insulation_conductivity = config.get('insulation_conductivity', 0.04)  # W/m·K
        
        # Flow regime
        self.flow_regime = config.get('flow_regime', 'turbulent')  # 'laminar', 'transitional', 'turbulent'
        
        # Property package
        from ..property_packages.ideal_property_package import IdealPropertyPackage
        self.property_package = IdealPropertyPackage()
    
    def solve(self) -> float:
        """Solve the pipe equations"""
        if len(self.inlet_streams) != 1:
            raise ValueError("Pipe requires exactly 1 inlet stream")
            
        if len(self.outlet_streams) != 1:
            raise ValueError("Pipe requires exactly 1 outlet stream")
        
        inlet_stream = self.inlet_streams[0]
        outlet_stream = self.outlet_streams[0]
        
        # Calculate pressure drop
        pressure_drop = self._calculate_pressure_drop(inlet_stream)
        
        # Calculate heat loss/gain
        temperature_change = self._calculate_heat_transfer(inlet_stream)
        
        # Set outlet stream properties
        outlet_stream.mass_flow_rate = inlet_stream.mass_flow_rate
        outlet_stream.pressure = inlet_stream.pressure - pressure_drop
        outlet_stream.temperature = inlet_stream.temperature + temperature_change
        outlet_stream.composition = inlet_stream.composition.copy()
        
        # Store results
        reynolds = self._calculate_reynolds_number(inlet_stream)
        friction_factor = self._calculate_friction_factor(reynolds)
        
        self.results = {
            'pressure_drop': pressure_drop,
            'temperature_change': temperature_change,
            'outlet_pressure': outlet_stream.pressure,
            'outlet_temperature': outlet_stream.temperature,
            'reynolds_number': reynolds,
            'friction_factor': friction_factor,
            'velocity': self._calculate_velocity(inlet_stream),
            'length': self.length,
            'diameter': self.diameter
        }
        
        return 0.0  # Perfect convergence for pipe calculations
    
    def _calculate_pressure_drop(self, inlet_stream: Any) -> float:
        """Calculate total pressure drop in the pipe"""
        # Major losses (friction)
        friction_loss = self._calculate_friction_loss(inlet_stream)
        
        # Minor losses (fittings, valves, etc.) - simplified
        minor_loss = 0.0  # Could be extended
        
        # Elevation head
        density = 1000  # kg/m³ approximation
        elevation_loss = density * 9.81 * self.elevation_change
        
        total_pressure_drop = friction_loss + minor_loss + elevation_loss
        
        return max(0, total_pressure_drop)  # Ensure non-negative
    
    def _calculate_friction_loss(self, inlet_stream: Any) -> float:
        """Calculate pressure drop due to friction"""
        # Calculate velocity
        velocity = self._calculate_velocity(inlet_stream)
        
        # Calculate Reynolds number
        reynolds = self._calculate_reynolds_number(inlet_stream)
        
        # Calculate friction factor
        friction_factor = self._calculate_friction_factor(reynolds)
        
        # Darcy-Weisbach equation
        density = 1000  # kg/m³ approximation
        pressure_drop = friction_factor * (self.length / self.diameter) * density * velocity**2 / 2
        
        return pressure_drop
    
    def _calculate_velocity(self, inlet_stream: Any) -> float:
        """Calculate fluid velocity in the pipe"""
        density = 1000  # kg/m³ approximation
        area = np.pi * (self.diameter / 2)**2
        volumetric_flow = inlet_stream.mass_flow_rate / density
        velocity = volumetric_flow / area
        return velocity
    
    def _calculate_reynolds_number(self, inlet_stream: Any) -> float:
        """Calculate Reynolds number"""
        velocity = self._calculate_velocity(inlet_stream)
        density = 1000  # kg/m³
        viscosity = 0.001  # Pa·s (water approximation)
        
        reynolds = density * velocity * self.diameter / viscosity
        return reynolds
    
    def _calculate_friction_factor(self, reynolds: float) -> float:
        """Calculate friction factor using appropriate correlation"""
        if reynolds < 2100:
            # Laminar flow - Hagen-Poiseuille
            return 64 / reynolds
        elif reynolds < 4000:
            # Transitional flow - approximation
            return 0.3164 / reynolds**0.25  # Blasius approximation
        else:
            # Turbulent flow - Blasius correlation (simplified)
            return 0.3164 / reynolds**0.25
    
    def _calculate_heat_transfer(self, inlet_stream: Any) -> float:
        """Calculate heat loss/gain to/from ambient"""
        if self.insulation_thickness > 0:
            # With insulation
            k_ins = self.insulation_conductivity
            r_ins = self.insulation_thickness / k_ins
            r_conv = 1 / (self.heat_transfer_coeff_outside * np.pi * (self.diameter + 2*self.insulation_thickness) * self.length)
            r_total = r_ins + r_conv
            ua = 1 / r_total
        else:
            # Without insulation
            perimeter = np.pi * self.diameter
            ua = self.heat_transfer_coeff_outside * perimeter * self.length
        
        # Simplified heat transfer calculation
        delta_t = inlet_stream.temperature - self.ambient_temperature
        cp = 4186  # J/kg·K approximation
        
        if ua > 0:
            # Calculate heat transfer rate
            q = ua * delta_t
            # Temperature change
            temperature_change = -q / (inlet_stream.mass_flow_rate * cp)
        else:
            temperature_change = 0.0
        
        return temperature_change
    
    def validate(self) -> bool:
        """Validate pipe configuration"""
        if len(self.inlet_streams) != 1 or len(self.outlet_streams) != 1:
            return False
        if self.length <= 0 or self.diameter <= 0:
            return False
        if self.diameter <= 2 * self.insulation_thickness:
            return False  # Insulation can't be thicker than pipe radius
        return True
