"""
Heat exchanger unit operation for DWSIM Python implementation.
"""

from typing import Dict, Any, List, Optional
import numpy as np
from .base_unit import BaseUnitOperation


class HeatExchanger(BaseUnitOperation):
    """Heat exchanger unit operation - transfers heat between two streams"""
    
    def __init__(self, unit_id: str, config: Dict[str, Any]):
        super().__init__(unit_id, config)
        
        # Heat exchanger specifications
        self.calculation_mode = config.get('calculation_mode', 'heat_duty')  # 'heat_duty', 'outlet_temperatures', 'area'
        self.heat_transfer_area = config.get('heat_transfer_area', 10.0)  # m²
        self.overall_heat_transfer_coeff = config.get('overall_heat_transfer_coeff', 500.0)  # W/m²·K
        self.fouling_factor = config.get('fouling_factor', 0.0001)  # m²·K/W (resistance due to fouling)
        self.minimum_temperature_approach = config.get('minimum_temperature_approach', 10.0)  # K
        
        # Stream specifications
        self.hot_stream_inlet_temp = config.get('hot_stream_inlet_temp')  # K (for design mode)
        self.cold_stream_inlet_temp = config.get('cold_stream_inlet_temp')  # K (for design mode)
        self.hot_stream_outlet_temp = config.get('hot_stream_outlet_temp')  # K (for design mode)
        self.cold_stream_outlet_temp = config.get('cold_stream_outlet_temp')  # K (for design mode)
        
        # Heat duty specification
        self.heat_duty = config.get('heat_duty', 100000.0)  # W
        
        # Flow configuration
        self.flow_direction = config.get('flow_direction', 'counter_current')  # 'counter_current', 'co_current'
        
        # Equipment type
        self.equipment_type = config.get('equipment_type', 'shell_and_tube')  # 'shell_and_tube', 'double_pipe', 'plate'
        
        # Pressure drops
        self.hot_side_pressure_drop = config.get('hot_side_pressure_drop', 10000)  # Pa
        self.cold_side_pressure_drop = config.get('cold_side_pressure_drop', 10000)  # Pa
        
        # Property package for enthalpy calculations
        from ..property_packages.ideal_property_package import IdealPropertyPackage
        self.property_package = IdealPropertyPackage()
    
    def solve(self) -> float:
        """Solve the heat exchanger"""
        if len(self.inlet_streams) != 2:
            raise ValueError("Heat exchanger requires exactly 2 inlet streams")
            
        if len(self.outlet_streams) != 2:
            raise ValueError("Heat exchanger requires exactly 2 outlet streams")
        
        hot_inlet = self.inlet_streams[0]
        cold_inlet = self.inlet_streams[1]
        hot_outlet = self.outlet_streams[0]
        cold_outlet = self.outlet_streams[1]
        
        # Determine which stream is hot and which is cold
        if hot_inlet.temperature > cold_inlet.temperature:
            hot_stream_in = hot_inlet
            cold_stream_in = cold_inlet
            hot_stream_out = hot_outlet
            cold_stream_out = cold_outlet
        else:
            # Swap if needed
            hot_stream_in = cold_inlet
            cold_stream_in = hot_inlet
            hot_stream_out = cold_outlet
            cold_stream_out = hot_outlet
        
        # Calculate heat transfer
        if self.calculation_mode == 'heat_duty':
            self._calculate_from_heat_duty(hot_stream_in, cold_stream_in, hot_stream_out, cold_stream_out)
        elif self.calculation_mode == 'outlet_temperatures':
            self._calculate_from_temperatures(hot_stream_in, cold_stream_in, hot_stream_out, cold_stream_out)
        elif self.calculation_mode == 'area':
            self._calculate_area(hot_stream_in, cold_stream_in)
        else:
            # Default to heat duty calculation
            self._calculate_from_heat_duty(hot_stream_in, cold_stream_in, hot_stream_out, cold_stream_out)
        
        return 0.0  # Perfect convergence for heat transfer calculations
    
    def _calculate_from_heat_duty(self, hot_in: Any, cold_in: Any, hot_out: Any, cold_out: Any):
        """Calculate outlet temperatures from specified heat duty"""
        # Simplified heat transfer calculation
        cp_hot = 2000  # J/kg·K approximation
        cp_cold = 2000  # J/kg·K approximation
        
        # Calculate temperature changes
        delta_t_hot = self.heat_duty / (hot_in.mass_flow_rate * cp_hot)
        delta_t_cold = self.heat_duty / (cold_in.mass_flow_rate * cp_cold)
        
        # Set outlet temperatures
        hot_out.temperature = hot_in.temperature - delta_t_hot
        cold_out.temperature = cold_in.temperature + delta_t_cold
        
        # Ensure minimum temperature approach
        if hot_out.temperature - cold_out.temperature < self.minimum_temperature_approach:
            # Adjust temperatures to maintain minimum approach
            avg_temp = (hot_out.temperature + cold_out.temperature) / 2
            hot_out.temperature = avg_temp + self.minimum_temperature_approach / 2
            cold_out.temperature = avg_temp - self.minimum_temperature_approach / 2
        
        # Set other outlet properties
        self._set_outlet_properties(hot_in, cold_in, hot_out, cold_out)
        
        # Store results
        self.results = {
            'calculation_mode': self.calculation_mode,
            'heat_duty': self.heat_duty,
            'hot_outlet_temperature': hot_out.temperature,
            'cold_outlet_temperature': cold_out.temperature,
            'temperature_approach': hot_out.temperature - cold_out.temperature,
            'lmtd': self._calculate_lmtd(hot_in.temperature, hot_out.temperature, cold_in.temperature, cold_out.temperature),
            'heat_transfer_area': self.heat_transfer_area,
            'overall_heat_transfer_coeff': self.overall_heat_transfer_coeff
        }
    
    def _calculate_from_temperatures(self, hot_in: Any, cold_in: Any, hot_out: Any, cold_out: Any):
        """Calculate heat duty from specified outlet temperatures"""
        # Use specified outlet temperatures if provided, otherwise calculate
        if self.hot_stream_outlet_temp is not None:
            hot_out.temperature = self.hot_stream_outlet_temp
        else:
            hot_out.temperature = hot_in.temperature - 20  # Default cooling
        
        if self.cold_stream_outlet_temp is not None:
            cold_out.temperature = self.cold_stream_outlet_temp
        else:
            cold_out.temperature = cold_in.temperature + 20  # Default heating
        
        # Ensure minimum temperature approach
        if hot_out.temperature - cold_out.temperature < self.minimum_temperature_approach:
            cold_out.temperature = hot_out.temperature - self.minimum_temperature_approach
        
        # Calculate heat duty
        cp_hot = 2000  # J/kg·K approximation
        cp_cold = 2000  # J/kg·K approximation
        
        q_hot = hot_in.mass_flow_rate * cp_hot * (hot_in.temperature - hot_out.temperature)
        q_cold = cold_in.mass_flow_rate * cp_cold * (cold_out.temperature - cold_in.temperature)
        
        # Use the smaller heat transfer (limited by the colder fluid)
        self.heat_duty = min(q_hot, q_cold)
        
        # Set other outlet properties
        self._set_outlet_properties(hot_in, cold_in, hot_out, cold_out)
        
        # Store results
        self.results = {
            'calculation_mode': self.calculation_mode,
            'heat_duty': self.heat_duty,
            'hot_outlet_temperature': hot_out.temperature,
            'cold_outlet_temperature': cold_out.temperature,
            'temperature_approach': hot_out.temperature - cold_out.temperature,
            'lmtd': self._calculate_lmtd(hot_in.temperature, hot_out.temperature, cold_in.temperature, cold_out.temperature),
            'heat_transfer_area': self.heat_transfer_area,
            'overall_heat_transfer_coeff': self.overall_heat_transfer_coeff
        }
    
    def _calculate_area(self, hot_in: Any, cold_in: Any):
        """Calculate required heat transfer area"""
        # Estimate temperatures for area calculation
        hot_out_temp = hot_in.temperature - 30  # Assume 30K cooling
        cold_out_temp = cold_in.temperature + 30  # Assume 30K heating
        
        # Calculate LMTD
        lmtd = self._calculate_lmtd(hot_in.temperature, hot_out_temp, cold_in.temperature, cold_out_temp)
        
        if lmtd > 0:
            # Calculate required area: Q = U * A * LMTD
            cp_avg = 2000  # J/kg·K
            delta_t_avg = 30  # K
            flow_rate_avg = (hot_in.mass_flow_rate + cold_in.mass_flow_rate) / 2
            q_max = flow_rate_avg * cp_avg * delta_t_avg
            
            self.heat_transfer_area = q_max / (self.overall_heat_transfer_coeff * lmtd)
        
        # Store results
        self.results = {
            'calculation_mode': self.calculation_mode,
            'heat_transfer_area': self.heat_transfer_area,
            'estimated_lmtd': lmtd,
            'overall_heat_transfer_coeff': self.overall_heat_transfer_coeff
        }
    
    def _calculate_lmtd(self, t_h1: float, t_h2: float, t_c1: float, t_c2: float) -> float:
        """Calculate Log Mean Temperature Difference"""
        if self.flow_direction == 'counter_current':
            delta_t1 = t_h1 - t_c2
            delta_t2 = t_h2 - t_c1
        else:  # co_current
            delta_t1 = t_h1 - t_c1
            delta_t2 = t_h2 - t_c2
        
        # Ensure positive temperature differences
        delta_t1 = max(delta_t1, 0.1)
        delta_t2 = max(delta_t2, 0.1)
        
        if abs(delta_t1 - delta_t2) < 1e-6:
            return (delta_t1 + delta_t2) / 2
        else:
            return (delta_t1 - delta_t2) / np.log(delta_t1 / delta_t2)
    
    def _set_outlet_properties(self, hot_in: Any, cold_in: Any, hot_out: Any, cold_out: Any):
        """Set outlet stream properties (composition, pressure, etc.)"""
        # Hot stream outlet
        hot_out.mass_flow_rate = hot_in.mass_flow_rate
        hot_out.pressure = hot_in.pressure - self.hot_side_pressure_drop
        hot_out.composition = hot_in.composition.copy()
        
        # Cold stream outlet
        cold_out.mass_flow_rate = cold_in.mass_flow_rate
        cold_out.pressure = cold_in.pressure - self.cold_side_pressure_drop
        cold_out.composition = cold_in.composition.copy()
    
    def validate(self) -> bool:
        """Validate heat exchanger configuration"""
        if len(self.inlet_streams) != 2 or len(self.outlet_streams) != 2:
            return False
        if self.heat_transfer_area <= 0:
            return False
        if self.overall_heat_transfer_coeff <= 0:
            return False
        if self.minimum_temperature_approach <= 0:
            return False
        return True
