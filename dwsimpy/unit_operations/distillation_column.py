"""
Distillation column unit operation for DWSIM Python implementation.
"""

from typing import Dict, Any, List, Optional
import numpy as np
from .base_unit import BaseUnitOperation
from ..math.newton_solver import NewtonSolver
from ..property_packages.ideal_property_package import IdealPropertyPackage


class Stage:
    """Represents a single stage (tray) in the distillation column"""
    
    def __init__(self, stage_number: int, pressure: float = 101325):
        self.stage_number = stage_number
        self.pressure = pressure
        self.temperature = 300.0  # Initial estimate
        self.liquid_composition: Dict[str, float] = {}
        self.vapor_composition: Dict[str, float] = {}
        self.liquid_flow = 0.0
        self.vapor_flow = 0.0
        self.feed_flow = 0.0
        self.feed_composition: Dict[str, float] = {}
        self.efficiency = 1.0  # Murphree efficiency


class DistillationColumn(BaseUnitOperation):
    """Distillation column unit operation"""
    
    def __init__(self, unit_id: str, config: Dict[str, Any]):
        super().__init__(unit_id, config)
        
        # Column specifications
        self.number_of_stages = config.get('number_of_stages', 10)
        self.feed_stage = config.get('feed_stage', 5)  # 1-based indexing
        self.condenser_type = config.get('condenser_type', 'total')  # 'total' or 'partial'
        self.reboiler_type = config.get('reboiler_type', 'kettle')  # 'kettle' or 'thermosiphon'
        
        # Specifications (only one should be active)
        self.reflux_ratio = config.get('reflux_ratio')  # L/D
        self.distillate_rate = config.get('distillate_rate')  # kmol/h
        self.bottoms_rate = config.get('bottoms_rate')  # kmol/h
        self.reboiler_duty = config.get('reboiler_duty')  # kW
        self.condenser_duty = config.get('condenser_duty')  # kW
        
        # Operating conditions
        self.feed_pressure = config.get('feed_pressure', 101325)  # Pa
        self.column_pressure_drop = config.get('column_pressure_drop', 0)  # Pa
        self.condenser_pressure = config.get('condenser_pressure', 101325)  # Pa
        
        # Initialize stages
        self.stages: List[Stage] = []
        for i in range(self.number_of_stages):
            pressure = self.condenser_pressure + (self.feed_pressure - self.condenser_pressure) * (i / (self.number_of_stages - 1))
            self.stages.append(Stage(i + 1, pressure))
        
        # Property package
        self.property_package = IdealPropertyPackage()
        
        # Convergence parameters
        self.max_iterations = 100
        self.tolerance = 1e-6
    
    def solve(self) -> float:
        """Solve the distillation column"""
        if len(self.inlet_streams) != 1:
            raise ValueError("Distillation column requires exactly 1 inlet stream")
            
        if len(self.outlet_streams) != 2:
            raise ValueError("Distillation column requires exactly 2 outlet streams")
        
        feed_stream = self.inlet_streams[0]
        distillate_stream = self.outlet_streams[0]
        bottoms_stream = self.outlet_streams[1]
        
        # Initialize stage compositions and flows
        self._initialize_stages(feed_stream)
        
        # Solve the column using simplified approach
        convergence_error = self._solve_column()
        
        # Set outlet streams
        self._set_outlet_streams(distillate_stream, bottoms_stream)
        
        return convergence_error
    
    def _initialize_stages(self, feed_stream):
        """Initialize stage temperatures, compositions, and flows"""
        # Simple initialization - linear temperature profile
        feed_temp = feed_stream.temperature
        feed_composition = feed_stream.composition
        
        # Estimate distillate and bottoms compositions
        light_keys = ['methane', 'ethane', 'propane', 'butane']  # Components that tend to go to distillate
        heavy_keys = ['ethanol', 'benzene', 'toluene']  # Components that tend to go to bottoms
        
        distillate_comp = {}
        bottoms_comp = {}
        
        for comp, frac in feed_composition.items():
            if comp in light_keys:
                distillate_comp[comp] = frac * 0.8  # Mostly to distillate
                bottoms_comp[comp] = frac * 0.2
            elif comp in heavy_keys:
                distillate_comp[comp] = frac * 0.2
                bottoms_comp[comp] = frac * 0.8
            else:
                distillate_comp[comp] = frac * 0.5
                bottoms_comp[comp] = frac * 0.5
        
        # Normalize
        total_d = sum(distillate_comp.values())
        total_b = sum(bottoms_comp.values())
        if total_d > 0:
            for comp in distillate_comp:
                distillate_comp[comp] /= total_d
        if total_b > 0:
            for comp in bottoms_comp:
                bottoms_comp[comp] /= total_b
        
        # Set stage compositions - linear interpolation
        for stage in self.stages:
            if stage.stage_number <= self.feed_stage:
                # Above feed - more like distillate
                factor = (self.feed_stage - stage.stage_number) / self.feed_stage if self.feed_stage > 0 else 0
                for comp in feed_composition:
                    stage.liquid_composition[comp] = (distillate_comp.get(comp, 0) * factor + 
                                                    feed_composition.get(comp, 0) * (1 - factor))
                    stage.vapor_composition[comp] = stage.liquid_composition[comp] * 1.2  # Slightly richer in lights
            else:
                # Below feed - more like bottoms
                factor = (stage.stage_number - self.feed_stage) / (self.number_of_stages - self.feed_stage) if (self.number_of_stages - self.feed_stage) > 0 else 0
                for comp in feed_composition:
                    stage.liquid_composition[comp] = (feed_composition.get(comp, 0) * (1 - factor) + 
                                                    bottoms_comp.get(comp, 0) * factor)
                    stage.vapor_composition[comp] = stage.liquid_composition[comp] * 0.8  # Slightly leaner in lights
            
            # Normalize compositions
            total_liq = sum(stage.liquid_composition.values())
            total_vap = sum(stage.vapor_composition.values())
            if total_liq > 0:
                for comp in stage.liquid_composition:
                    stage.liquid_composition[comp] /= total_liq
            if total_vap > 0:
                for comp in stage.vapor_composition:
                    stage.vapor_composition[comp] /= total_vap
        
        # Set feed stage
        if 1 <= self.feed_stage <= self.number_of_stages:
            feed_stage = self.stages[self.feed_stage - 1]
            feed_stage.feed_flow = feed_stream.mass_flow_rate / 18.015  # Convert to kmol/h (assuming water MW)
            feed_stage.feed_composition = feed_composition.copy()
        
        # Initial temperature estimates
        for stage in self.stages:
            if stage.stage_number <= self.feed_stage:
                stage.temperature = feed_temp - 10 * (self.feed_stage - stage.stage_number)  # Cooler above feed
            else:
                stage.temperature = feed_temp + 10 * (stage.stage_number - self.feed_stage)  # Warmer below feed
    
    def _solve_column(self) -> float:
        """Solve the distillation column using simplified approach"""
        # For now, implement a basic multi-stage flash approach
        # This is a simplified version - full rigorous solution would use MESH equations
        
        max_error = 0.0
        converged = False
        
        for iteration in range(self.max_iterations):
            max_error = 0.0
            
            # Calculate stage-by-stage from top to bottom
            for i, stage in enumerate(self.stages):
                # Perform flash calculation for this stage
                try:
                    flash_result = self.property_package.calculate_flash(
                        stage.temperature,
                        stage.pressure,
                        stage.liquid_composition
                    )
                    
                    # Update vapor composition
                    if 'vapor_composition' in flash_result:
                        stage.vapor_composition = flash_result['vapor_composition']
                    
                    # Calculate flows (simplified)
                    if i == 0:  # Condenser
                        # Assume some reflux ratio
                        reflux_ratio = self.reflux_ratio or 2.0
                        distillate_flow = stage.liquid_flow / (1 + reflux_ratio) if stage.liquid_flow > 0 else 1.0
                        reflux_flow = distillate_flow * reflux_ratio
                        stage.vapor_flow = reflux_flow + distillate_flow  # Simplified
                    elif i == len(self.stages) - 1:  # Reboiler
                        # Assume some boilup ratio
                        boilup_ratio = 1.5  # V/B
                        bottoms_flow = stage.liquid_flow / (1 + boilup_ratio) if stage.liquid_flow > 0 else 1.0
                        boilup_flow = bottoms_flow * boilup_ratio
                        stage.liquid_flow = bottoms_flow + boilup_flow  # Simplified
                    else:
                        # Intermediate stage
                        stage.liquid_flow = stage.vapor_flow * 0.5 if stage.vapor_flow > 0 else 1.0  # Simplified
                        stage.vapor_flow = stage.liquid_flow * 2.0
                    
                    # Check convergence (temperature change)
                    new_temp = self._calculate_stage_temperature(stage)
                    temp_error = abs(new_temp - stage.temperature)
                    max_error = max(max_error, temp_error)
                    stage.temperature = 0.5 * (stage.temperature + new_temp)  # Relaxation
                    
                except Exception as e:
                    print(f"Flash calculation failed for stage {stage.stage_number}: {e}")
                    continue
            
            if max_error < self.tolerance:
                converged = True
                break
        
        if not converged:
            print(f"Column did not converge after {self.max_iterations} iterations. Max error: {max_error}")
        
        return max_error
    
    def _calculate_stage_temperature(self, stage: Stage) -> float:
        """Calculate stage temperature based on energy balance (simplified)"""
        # Simplified - assume bubble point temperature
        try:
            # Use dew point of vapor composition as approximation
            flash_result = self.property_package.calculate_flash(
                stage.temperature,
                stage.pressure,
                stage.vapor_composition,
                flash_type="PT"
            )
            if 'dew_point_temperature' in flash_result:
                return flash_result['dew_point_temperature']
        except:
            pass
        
        return stage.temperature  # Keep current if calculation fails
    
    def _set_outlet_streams(self, distillate_stream, bottoms_stream):
        """Set the outlet stream properties"""
        condenser_stage = self.stages[0]
        reboiler_stage = self.stages[-1]
        
        # Distillate (condenser liquid product)
        distillate_stream.temperature = condenser_stage.temperature
        distillate_stream.pressure = condenser_stage.pressure
        distillate_stream.composition = condenser_stage.liquid_composition.copy()
        distillate_stream.mass_flow_rate = condenser_stage.liquid_flow * 18.015  # Convert back to kg/s
        
        # Bottoms (reboiler liquid product)
        bottoms_stream.temperature = reboiler_stage.temperature
        bottoms_stream.pressure = reboiler_stage.pressure
        bottoms_stream.composition = reboiler_stage.liquid_composition.copy()
        bottoms_stream.mass_flow_rate = reboiler_stage.liquid_flow * 18.015  # Convert back to kg/s
        
        # Store results
        self.results = {
            'number_of_stages': self.number_of_stages,
            'feed_stage': self.feed_stage,
            'condenser_temperature': condenser_stage.temperature,
            'reboiler_temperature': reboiler_stage.temperature,
            'reflux_ratio': self.reflux_ratio,
            'distillate_flow': distillate_stream.mass_flow_rate,
            'bottoms_flow': bottoms_stream.mass_flow_rate,
            'convergence_error': 0.0
        }
    
    def validate(self) -> bool:
        """Validate column configuration"""
        if self.number_of_stages < 2:
            return False
        if self.feed_stage < 1 or self.feed_stage > self.number_of_stages:
            return False
        if len(self.inlet_streams) != 1 or len(self.outlet_streams) != 2:
            return False
        return True
