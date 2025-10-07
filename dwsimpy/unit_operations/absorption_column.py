"""
Absorption column unit operation for DWSIM Python implementation.
"""

from typing import Dict, Any, List, Optional, TYPE_CHECKING
import numpy as np
from .base_unit import BaseUnitOperation
from ..math.newton_solver import NewtonSolver
from ..property_packages.ideal_property_package import IdealPropertyPackage

if TYPE_CHECKING:
    from ..material_stream import MaterialStream


class AbsorptionStage:
    """Represents a single stage (tray) in the absorption column"""
    
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


class AbsorptionColumn(BaseUnitOperation):
    """Absorption column unit operation - absorbs gas components into liquid solvent"""
    
    def __init__(self, unit_id: str, config: Dict[str, Any]):
        super().__init__(unit_id, config)
        
        # Column specifications
        self.number_of_stages = config.get('number_of_stages', 10)
        self.feed_stage = config.get('feed_stage', 1)  # 1-based indexing, usually top feed for absorption
        
        # Specifications
        self.solvent_flow_rate = config.get('solvent_flow_rate')  # kmol/h
        self.absorption_efficiency = config.get('absorption_efficiency', 0.95)  # target absorption efficiency
        
        # Operating conditions
        self.feed_pressure = config.get('feed_pressure', 101325)  # Pa
        self.column_pressure_drop = config.get('column_pressure_drop', 0)  # Pa
        
        # Target component for absorption
        self.target_component = config.get('target_component', 'CO2')
        
        # Property package for equilibrium calculations
        self.property_package = IdealPropertyPackage()
        
        # Initialize stages
        self.stages: List[AbsorptionStage] = []
        self._initialize_stages()
    
    def _initialize_stages(self):
        """Initialize the absorption column stages"""
        self.stages = []
        for i in range(self.number_of_stages):
            # Pressure decreases from bottom to top (typical for absorption)
            pressure = self.feed_pressure - (self.column_pressure_drop * i / (self.number_of_stages - 1))
            stage = AbsorptionStage(i + 1, pressure)
            self.stages.append(stage)
    
    def solve(self) -> float:
        """Solve the absorption column"""
        if len(self.inlet_streams) != 2:
            raise ValueError("Absorption column requires exactly 2 inlet streams (gas feed and solvent)")
        if len(self.outlet_streams) != 2:
            raise ValueError("Absorption column requires exactly 2 outlet streams (treated gas and rich solvent)")
        
        gas_feed = self.inlet_streams[0]  # Gas stream to be treated
        solvent_feed = self.inlet_streams[1]  # Lean solvent
        treated_gas = self.outlet_streams[0]  # Gas with reduced target component
        rich_solvent = self.outlet_streams[1]  # Solvent with absorbed component
        
        # Convert flows to molar rates (assuming kg/s to kmol/h conversion factor)
        gas_flow_kmol_h = gas_feed.mass_flow_rate * 3600 / 18.015  # Approximate for now
        solvent_flow_kmol_h = solvent_feed.mass_flow_rate * 3600 / 18.015
        
        # Set up stages
        self._setup_stages(gas_feed, solvent_feed)
        
        # Solve absorption column using simplified model
        convergence_error = self._solve_absorption()
        
        # Set outlet streams
        self._set_outlet_streams(treated_gas, rich_solvent)
        
        return convergence_error
    
    def _setup_stages(self, gas_feed: "MaterialStream", solvent_feed: "MaterialStream"):
        """Set up the initial conditions for each stage"""
        # Gas feed enters at top (stage 1)
        top_stage = self.stages[0]
        top_stage.vapor_composition = gas_feed.composition.copy()
        top_stage.vapor_flow = gas_feed.mass_flow_rate * 3600 / 18.015  # kmol/h
        top_stage.temperature = gas_feed.temperature
        
        # Solvent feed enters at bottom (last stage)
        bottom_stage = self.stages[-1]
        bottom_stage.liquid_composition = solvent_feed.composition.copy()
        bottom_stage.liquid_flow = solvent_feed.mass_flow_rate * 3600 / 18.015  # kmol/h
        bottom_stage.temperature = solvent_feed.temperature
        
        # Initialize intermediate stages
        for stage in self.stages[1:-1]:
            stage.temperature = (gas_feed.temperature + solvent_feed.temperature) / 2
            stage.liquid_composition = solvent_feed.composition.copy()
            stage.vapor_composition = gas_feed.composition.copy()
    
    def _solve_absorption(self) -> float:
        """Solve the absorption column using simplified equilibrium stages"""
        max_iterations = 50
        tolerance = 1e-6
        
        for iteration in range(max_iterations):
            error = 0.0
            
            # Calculate stage-by-stage absorption
            for i, stage in enumerate(self.stages):
                if i == 0:  # Top stage
                    # Gas from inlet, liquid from stage below
                    stage.liquid_flow = self.stages[i+1].liquid_flow if i+1 < len(self.stages) else 0
                    stage.liquid_composition = self.stages[i+1].liquid_composition.copy() if i+1 < len(self.stages) else {}
                elif i == len(self.stages) - 1:  # Bottom stage
                    # Liquid from inlet, vapor from stage above
                    stage.vapor_flow = self.stages[i-1].vapor_flow if i > 0 else stage.vapor_flow
                    stage.vapor_composition = self.stages[i-1].vapor_composition.copy() if i > 0 else stage.vapor_composition
                else:
                    # Intermediate stage
                    stage.liquid_flow = self.stages[i+1].liquid_flow
                    stage.liquid_composition = self.stages[i+1].liquid_composition.copy()
                    stage.vapor_flow = self.stages[i-1].vapor_flow
                    stage.vapor_composition = self.stages[i-1].vapor_composition.copy()
                
                # Perform equilibrium calculation
                stage_error = self._calculate_stage_equilibrium(stage)
                error = max(error, stage_error)
            
            if error < tolerance:
                break
        
        return error
    
    def _calculate_stage_equilibrium(self, stage: AbsorptionStage) -> float:
        """Calculate equilibrium for a single stage"""
        if not stage.liquid_composition or not stage.vapor_composition:
            return 0.0
        
        # Simplified equilibrium calculation
        # In a real implementation, this would use Henry's law or other correlations
        k_eq = 0.5  # Equilibrium constant (simplified)
        
        if self.target_component in stage.vapor_composition and self.target_component in stage.liquid_composition:
            y = stage.vapor_composition[self.target_component]
            x = stage.liquid_composition[self.target_component]
            
            # Equilibrium relationship: y = K * x
            y_eq = k_eq * x
            error = abs(y - y_eq)
            
            # Update compositions based on efficiency
            if y > y_eq:
                # Absorption occurs
                transfer = self.efficiency * (y - y_eq)
                stage.vapor_composition[self.target_component] -= transfer
                stage.liquid_composition[self.target_component] += transfer
            else:
                # Desorption occurs (less common in absorption)
                transfer = self.efficiency * (y_eq - y)
                stage.vapor_composition[self.target_component] += transfer
                stage.liquid_composition[self.target_component] -= transfer
            
            return error
        
        return 0.0
    
    def _set_outlet_streams(self, treated_gas, rich_solvent):
        """Set the outlet stream properties"""
        top_stage = self.stages[0]
        bottom_stage = self.stages[-1]
        
        # Treated gas (top vapor outlet)
        treated_gas.temperature = top_stage.temperature
        treated_gas.pressure = top_stage.pressure
        treated_gas.composition = top_stage.vapor_composition.copy()
        treated_gas.mass_flow_rate = top_stage.vapor_flow * 18.015 / 3600  # Convert back to kg/s
        
        # Rich solvent (bottom liquid outlet)
        rich_solvent.temperature = bottom_stage.temperature
        rich_solvent.pressure = bottom_stage.pressure
        rich_solvent.composition = bottom_stage.liquid_composition.copy()
        rich_solvent.mass_flow_rate = bottom_stage.liquid_flow * 18.015 / 3600  # Convert back to kg/s
        
        # Calculate absorption efficiency
        inlet_target = self.inlet_streams[0].composition.get(self.target_component, 0)
        outlet_target = treated_gas.composition.get(self.target_component, 0)
        if inlet_target > 0:
            actual_efficiency = (inlet_target - outlet_target) / inlet_target
        else:
            actual_efficiency = 0.0
        
        # Store results
        self.results = {
            'number_of_stages': self.number_of_stages,
            'target_component': self.target_component,
            'absorption_efficiency': actual_efficiency,
            'treated_gas_flow': treated_gas.mass_flow_rate,
            'rich_solvent_flow': rich_solvent.mass_flow_rate,
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
