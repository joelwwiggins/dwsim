"""
Stripping column unit operation for DWSIM Python implementation.
"""

from typing import Dict, Any, List, Optional
import numpy as np
from .base_unit import BaseUnitOperation
from ..material_stream import MaterialStream
from ..math.newton_solver import NewtonSolver
from ..property_packages.ideal_property_package import IdealPropertyPackage


class StrippingStage:
    """Represents a single stage (tray) in the stripping column"""
    
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


class StrippingColumn(BaseUnitOperation):
    """Stripping column unit operation - removes dissolved components from liquid using gas stripping"""
    
    def __init__(self, unit_id: str, config: Dict[str, Any]):
        super().__init__(unit_id, config)
        
        # Column specifications
        self.number_of_stages = config.get('number_of_stages', 10)
        self.feed_stage = config.get('feed_stage', 5)  # 1-based indexing
        
        # Specifications
        self.stripping_gas_flow_rate = config.get('stripping_gas_flow_rate')  # kmol/h
        self.stripping_efficiency = config.get('stripping_efficiency', 0.95)  # target stripping efficiency
        
        # Operating conditions
        self.feed_pressure = config.get('feed_pressure', 101325)  # Pa
        self.column_pressure_drop = config.get('column_pressure_drop', 0)  # Pa
        
        # Target component for stripping
        self.target_component = config.get('target_component', 'CO2')
        
        # Property package for equilibrium calculations
        self.property_package = IdealPropertyPackage()
        
        # Initialize stages
        self.stages: List[StrippingStage] = []
        self._initialize_stages()
    
    def _initialize_stages(self):
        """Initialize the stripping column stages"""
        self.stages = []
        for i in range(self.number_of_stages):
            # Pressure decreases from bottom to top (typical for stripping)
            pressure = self.feed_pressure - (self.column_pressure_drop * i / (self.number_of_stages - 1))
            stage = StrippingStage(i + 1, pressure)
            self.stages.append(stage)
    
    def solve(self) -> float:
        """Solve the stripping column"""
        if len(self.inlet_streams) != 2:
            raise ValueError("Stripping column requires exactly 2 inlet streams (liquid feed and stripping gas)")
        if len(self.outlet_streams) != 2:
            raise ValueError("Stripping column requires exactly 2 outlet streams (stripped liquid and rich gas)")
        
        liquid_feed = self.inlet_streams[0]  # Liquid stream to be stripped
        stripping_gas = self.inlet_streams[1]  # Stripping gas
        stripped_liquid = self.outlet_streams[0]  # Liquid with reduced target component
        rich_gas = self.outlet_streams[1]  # Gas with stripped component
        
        # Convert flows to molar rates (assuming kg/s to kmol/h conversion factor)
        liquid_flow_kmol_h = liquid_feed.mass_flow_rate * 3600 / 18.015  # Approximate for now
        gas_flow_kmol_h = stripping_gas.mass_flow_rate * 3600 / 18.015
        
        # Set up stages
        self._setup_stages(liquid_feed, stripping_gas)
        
        # Solve stripping column using simplified model
        convergence_error = self._solve_stripping()
        
        # Set outlet streams
        self._set_outlet_streams(stripped_liquid, rich_gas)
        
        return convergence_error
    
    def _setup_stages(self, liquid_feed: MaterialStream, stripping_gas: MaterialStream):
        """Set up the initial conditions for each stage"""
        # Liquid feed enters at top (stage 1)
        top_stage = self.stages[0]
        top_stage.liquid_composition = liquid_feed.composition.copy()
        top_stage.liquid_flow = liquid_feed.mass_flow_rate * 3600 / 18.015  # kmol/h
        top_stage.temperature = liquid_feed.temperature
        
        # Stripping gas enters at bottom (last stage)
        bottom_stage = self.stages[-1]
        bottom_stage.vapor_composition = stripping_gas.composition.copy()
        bottom_stage.vapor_flow = stripping_gas.mass_flow_rate * 3600 / 18.015  # kmol/h
        bottom_stage.temperature = stripping_gas.temperature
        
        # Initialize intermediate stages
        for stage in self.stages[1:-1]:
            stage.temperature = (liquid_feed.temperature + stripping_gas.temperature) / 2
            stage.liquid_composition = liquid_feed.composition.copy()
            stage.vapor_composition = stripping_gas.composition.copy()
    
    def _solve_stripping(self) -> float:
        """Solve the stripping column using simplified equilibrium stages"""
        max_iterations = 50
        tolerance = 1e-6
        
        for iteration in range(max_iterations):
            error = 0.0
            
            # Calculate stage-by-stage stripping
            for i, stage in enumerate(self.stages):
                if i == 0:  # Top stage
                    # Liquid from inlet, vapor from stage below
                    stage.vapor_flow = self.stages[i+1].vapor_flow if i+1 < len(self.stages) else 0
                    stage.vapor_composition = self.stages[i+1].vapor_composition.copy() if i+1 < len(self.stages) else {}
                elif i == len(self.stages) - 1:  # Bottom stage
                    # Vapor from inlet, liquid from stage above
                    stage.liquid_flow = self.stages[i-1].liquid_flow if i > 0 else stage.liquid_flow
                    stage.liquid_composition = self.stages[i-1].liquid_composition.copy() if i > 0 else stage.liquid_composition
                else:
                    # Intermediate stage
                    stage.vapor_flow = self.stages[i+1].vapor_flow
                    stage.vapor_composition = self.stages[i+1].vapor_composition.copy()
                    stage.liquid_flow = self.stages[i-1].liquid_flow
                    stage.liquid_composition = self.stages[i-1].liquid_composition.copy()
                
                # Perform equilibrium calculation
                stage_error = self._calculate_stage_equilibrium(stage)
                error = max(error, stage_error)
            
            if error < tolerance:
                break
        
        return error
    
    def _calculate_stage_equilibrium(self, stage: StrippingStage) -> float:
        """Calculate equilibrium for a single stage"""
        if not stage.liquid_composition or not stage.vapor_composition:
            return 0.0
        
        # Simplified equilibrium calculation
        # In a real implementation, this would use Henry's law or other correlations
        k_eq = 2.0  # Equilibrium constant (higher than absorption for stripping)
        
        if self.target_component in stage.vapor_composition and self.target_component in stage.liquid_composition:
            y = stage.vapor_composition[self.target_component]
            x = stage.liquid_composition[self.target_component]
            
            # Equilibrium relationship: y = K * x
            y_eq = k_eq * x
            error = abs(y - y_eq)
            
            # Update compositions based on efficiency
            if y < y_eq:
                # Stripping occurs
                transfer = self.stripping_efficiency * (y_eq - y)
                stage.vapor_composition[self.target_component] += transfer
                stage.liquid_composition[self.target_component] -= transfer
            else:
                # Absorption occurs (less common in stripping)
                transfer = self.stripping_efficiency * (y - y_eq)
                stage.vapor_composition[self.target_component] -= transfer
                stage.liquid_composition[self.target_component] += transfer
            
            return error
        
        return 0.0
    
    def _set_outlet_streams(self, stripped_liquid, rich_gas):
        """Set the outlet stream properties"""
        top_stage = self.stages[0]
        bottom_stage = self.stages[-1]
        
        # Stripped liquid (top liquid outlet)
        stripped_liquid.temperature = top_stage.temperature
        stripped_liquid.pressure = top_stage.pressure
        stripped_liquid.composition = top_stage.liquid_composition.copy()
        stripped_liquid.mass_flow_rate = top_stage.liquid_flow * 18.015 / 3600  # Convert back to kg/s
        
        # Rich gas (bottom vapor outlet)
        rich_gas.temperature = bottom_stage.temperature
        rich_gas.pressure = bottom_stage.pressure
        rich_gas.composition = bottom_stage.vapor_composition.copy()
        rich_gas.mass_flow_rate = bottom_stage.vapor_flow * 18.015 / 3600  # Convert back to kg/s
        
        # Calculate stripping efficiency
        inlet_target = self.inlet_streams[0].composition.get(self.target_component, 0)
        outlet_target = stripped_liquid.composition.get(self.target_component, 0)
        if inlet_target > 0:
            actual_efficiency = (inlet_target - outlet_target) / inlet_target
        else:
            actual_efficiency = 0.0
        
        # Store results
        self.results = {
            'number_of_stages': self.number_of_stages,
            'target_component': self.target_component,
            'stripping_efficiency': actual_efficiency,
            'stripped_liquid_flow': stripped_liquid.mass_flow_rate,
            'rich_gas_flow': rich_gas.mass_flow_rate,
            'top_temperature': top_stage.temperature,
            'bottom_temperature': bottom_stage.temperature,
            'convergence_error': 0.0
        }
    
    def validate(self) -> bool:
        """Validate column configuration"""
        if self.number_of_stages < 1:
            return False
        if self.feed_stage < 1 or self.feed_stage > self.number_of_stages:
            return False
        if len(self.inlet_streams) != 2 or len(self.outlet_streams) != 2:
            return False
        if not self.target_component:
            return False
        return True
