"""
Equilibrium reactor unit operation for DWSIM Python implementation.
"""

from typing import Dict, Any, List, Optional
import numpy as np
from .base_unit import BaseUnitOperation
from ..math.newton_solver import NewtonSolver


class EquilibriumReaction:
    """Represents an equilibrium reaction"""
    
    def __init__(self, reaction_id: str, stoichiometry: Dict[str, float], equilibrium_constant: float = 1.0, temperature: float = 298.15):
        self.reaction_id = reaction_id
        self.stoichiometry = stoichiometry  # component_id -> stoichiometric coefficient
        self.equilibrium_constant = equilibrium_constant  # K_eq at reference conditions
        self.reference_temperature = temperature  # K
        self.extent = 0.0  # reaction extent (mol)


class EquilibriumReactor(BaseUnitOperation):
    """Equilibrium reactor unit operation - reactions proceed to chemical equilibrium"""
    
    def __init__(self, unit_id: str, config: Dict[str, Any]):
        super().__init__(unit_id, config)
        
        # Reactor specifications
        self.operation_mode = config.get('operation_mode', 'adiabatic')  # 'isothermal', 'adiabatic'
        self.target_temperature = config.get('target_temperature')  # K (for isothermal)
        self.pressure_drop = config.get('pressure_drop', 0.0)  # Pa
        
        # Reactions
        self.reactions: List[EquilibriumReaction] = []
        reactions_config = config.get('reactions', [])
        for rxn_config in reactions_config:
            reaction = EquilibriumReaction(
                reaction_id=rxn_config['id'],
                stoichiometry=rxn_config['stoichiometry'],
                equilibrium_constant=rxn_config.get('equilibrium_constant', 1.0),
                temperature=rxn_config.get('reference_temperature', 298.15)
            )
            self.reactions.append(reaction)
        
        # Property package for enthalpy calculations
        from ..property_packages.ideal_property_package import IdealPropertyPackage
        self.property_package = IdealPropertyPackage()
        
        # Solver settings
        self.max_iterations = 100
        self.tolerance = 1e-6
    
    def solve(self) -> float:
        """Solve the equilibrium reactor"""
        if len(self.inlet_streams) != 1:
            raise ValueError("Equilibrium reactor requires exactly 1 inlet stream")
            
        if len(self.outlet_streams) != 1:
            raise ValueError("Equilibrium reactor requires exactly 1 outlet stream")
        
        inlet_stream = self.inlet_streams[0]
        outlet_stream = self.outlet_streams[0]
        
        # Solve for equilibrium extents
        convergence_error = self._solve_equilibrium(inlet_stream)
        
        # Calculate outlet composition
        outlet_composition = self._calculate_outlet_composition(inlet_stream)
        
        # Calculate outlet temperature
        outlet_temperature = self._calculate_energy_balance(inlet_stream)
        
        # Set outlet stream properties
        outlet_stream.mass_flow_rate = inlet_stream.mass_flow_rate
        outlet_stream.pressure = inlet_stream.pressure - self.pressure_drop
        outlet_stream.temperature = outlet_temperature
        outlet_stream.composition = outlet_composition.copy()
        
        # Store results
        self.results = {
            'operation_mode': self.operation_mode,
            'outlet_temperature': outlet_temperature,
            'pressure_drop': self.pressure_drop,
            'reactions': [
                {
                    'id': rxn.reaction_id,
                    'extent': rxn.extent,
                    'equilibrium_constant': rxn.equilibrium_constant
                }
                for rxn in self.reactions
            ],
            'convergence_error': convergence_error
        }
        
        return convergence_error
    
    def _solve_equilibrium(self, inlet_stream: Any) -> float:
        """Solve for equilibrium reaction extents"""
        if not self.reactions:
            return 0.0
        
        # Convert mass flow rates to molar flow rates
        molar_flow_rate = inlet_stream.mass_flow_rate / 18.015  # kg/s to kmol/s
        
        # Initial molar flows
        initial_moles = {}
        for component_id, mole_fraction in inlet_stream.composition.items():
            initial_moles[component_id] = molar_flow_rate * mole_fraction
        
        # Simplified equilibrium solution - assume single reaction for now
        # In a full implementation, this would solve the system of equations for multiple reactions
        for reaction in self.reactions:
            extent = self._solve_single_reaction_equilibrium(reaction, initial_moles, inlet_stream.temperature, inlet_stream.pressure)
            reaction.extent = extent
        
        return 0.0  # Simplified - no convergence checking
    
    def _solve_single_reaction_equilibrium(self, reaction: EquilibriumReaction, initial_moles: Dict[str, float], temperature: float, pressure: float) -> float:
        """Solve equilibrium for a single reaction using simplified approach"""
        
        # Calculate equilibrium constant at current temperature (simplified)
        # In reality, this should use van't Hoff equation
        k_eq = reaction.equilibrium_constant
        
        # Calculate reaction quotient Q
        q = 1.0
        for component_id, coeff in reaction.stoichiometry.items():
            mole_conc = initial_moles.get(component_id, 0.0) / sum(initial_moles.values())
            if coeff > 0:  # Product
                q *= mole_conc ** coeff
            elif coeff < 0:  # Reactant
                q /= mole_conc ** abs(coeff)
        
        # For equilibrium, Q = K_eq, so extent adjustment needed
        # This is a very simplified approach - real equilibrium solving is more complex
        
        # Estimate extent based on how far Q is from K_eq
        if q > 0:
            extent_factor = min(1.0, k_eq / q)  # How much to adjust toward equilibrium
        else:
            extent_factor = 0.0
        
        # Calculate maximum possible extent (limited by reactants)
        max_extent = float('inf')
        for component_id, coeff in reaction.stoichiometry.items():
            if coeff < 0:  # Reactant
                reactant_moles = initial_moles.get(component_id, 0.0)
                if reactant_moles > 0:
                    max_extent = min(max_extent, reactant_moles / abs(coeff))
        
        # Apply extent factor
        extent = max_extent * extent_factor * 0.5  # Conservative approach
        
        return extent
    
    def _calculate_outlet_composition(self, inlet_stream: Any) -> Dict[str, float]:
        """Calculate outlet composition after equilibrium reactions"""
        # Convert mass flow rates to molar flow rates
        molar_flow_rate = inlet_stream.mass_flow_rate / 18.015  # kg/s to kmol/s
        
        # Start with inlet molar flows
        outlet_molar_flows = {}
        for component_id, mole_fraction in inlet_stream.composition.items():
            outlet_molar_flows[component_id] = molar_flow_rate * mole_fraction
        
        # Apply reaction extents
        for reaction in self.reactions:
            for component_id, coeff in reaction.stoichiometry.items():
                outlet_molar_flows[component_id] = outlet_molar_flows.get(component_id, 0.0) + coeff * reaction.extent
        
        # Convert back to mole fractions
        total_outlet_molar_flow = sum(outlet_molar_flows.values())
        if total_outlet_molar_flow > 0:
            outlet_composition = {
                comp: flow / total_outlet_molar_flow
                for comp, flow in outlet_molar_flows.items()
                if flow > 0  # Only include components with positive flows
            }
        else:
            outlet_composition = inlet_stream.composition.copy()
        
        return outlet_composition
    
    def _calculate_energy_balance(self, inlet_stream: Any) -> float:
        """Calculate outlet temperature based on energy balance"""
        if self.operation_mode == 'isothermal':
            return self.target_temperature
        else:  # adiabatic
            # Calculate adiabatic temperature change due to reaction enthalpy
            # Simplified: assume some heat effects
            total_heat = 0.0
            for reaction in self.reactions:
                # Simplified heat of reaction (exothermic for many reactions)
                if any('hydrogen' in comp for comp in reaction.stoichiometry):
                    total_heat -= 100000 * reaction.extent  # Assume exothermic
                else:
                    total_heat -= 50000 * reaction.extent  # Assume moderately exothermic
            
            # Temperature change
            cp_avg = 2000  # J/kg·K
            delta_t = total_heat / (inlet_stream.mass_flow_rate * cp_avg)
            return inlet_stream.temperature + delta_t
    
    def validate(self) -> bool:
        """Validate reactor configuration"""
        if len(self.inlet_streams) != 1 or len(self.outlet_streams) != 1:
            return False
        if not self.reactions:
            return False
        for reaction in self.reactions:
            if not reaction.stoichiometry:
                return False
            if reaction.equilibrium_constant <= 0:
                return False
        return True
    
    def add_reaction(self, reaction_id: str, stoichiometry: Dict[str, float], equilibrium_constant: float = 1.0) -> None:
        """Add an equilibrium reaction"""
        reaction = EquilibriumReaction(reaction_id, stoichiometry, equilibrium_constant)
        self.reactions.append(reaction)
    
    def remove_reaction(self, reaction_id: str) -> None:
        """Remove an equilibrium reaction"""
        self.reactions = [r for r in self.reactions if r.reaction_id != reaction_id]
    
    def set_equilibrium_constant(self, reaction_id: str, k_eq: float) -> None:
        """Set equilibrium constant for a reaction"""
        for reaction in self.reactions:
            if reaction.reaction_id == reaction_id:
                reaction.equilibrium_constant = k_eq
                break
