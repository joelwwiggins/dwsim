"""
Conversion reactor unit operation for DWSIM Python implementation.
"""

from typing import Dict, Any, List, Optional
import numpy as np
from .base_unit import BaseUnitOperation


class Reaction:
    """Represents a single chemical reaction"""
    
    def __init__(self, reaction_id: str, stoichiometry: Dict[str, float], conversion: float = 0.0):
        self.reaction_id = reaction_id
        self.stoichiometry = stoichiometry  # component_id -> stoichiometric coefficient
        self.conversion = conversion  # fraction (0-1)
        self.extent = 0.0  # reaction extent (mol)


class ConversionReactor(BaseUnitOperation):
    """Conversion reactor unit operation - reactions proceed to specified conversions"""
    
    def __init__(self, unit_id: str, config: Dict[str, Any]):
        super().__init__(unit_id, config)
        
        # Reactor specifications
        self.operation_mode = config.get('operation_mode', 'adiabatic')  # 'isothermal', 'adiabatic', 'heat_duty'
        self.target_temperature = config.get('target_temperature')  # K (for isothermal)
        self.heat_duty = config.get('heat_duty', 0.0)  # W (for heat_duty mode)
        self.pressure_drop = config.get('pressure_drop', 0.0)  # Pa
        
        # Reactions
        self.reactions: List[Reaction] = []
        reactions_config = config.get('reactions', [])
        for rxn_config in reactions_config:
            reaction = Reaction(
                reaction_id=rxn_config['id'],
                stoichiometry=rxn_config['stoichiometry'],
                conversion=rxn_config.get('conversion', 0.0)
            )
            self.reactions.append(reaction)
        
        # Property package for enthalpy calculations
        from ..property_packages.ideal_property_package import IdealPropertyPackage
        self.property_package = IdealPropertyPackage()
    
    def solve(self) -> float:
        """Solve the conversion reactor"""
        if len(self.inlet_streams) != 1:
            raise ValueError("Conversion reactor requires exactly 1 inlet stream")
            
        if len(self.outlet_streams) != 1:
            raise ValueError("Conversion reactor requires exactly 1 outlet stream")
        
        inlet_stream = self.inlet_streams[0]
        outlet_stream = self.outlet_streams[0]
        
        # Calculate reaction extents
        self._calculate_reaction_extents(inlet_stream)
        
        # Calculate outlet composition
        outlet_composition = self._calculate_outlet_composition(inlet_stream)
        
        # Calculate outlet temperature and energy balance
        outlet_temperature = self._calculate_energy_balance(inlet_stream)
        
        # Set outlet stream properties
        outlet_stream.mass_flow_rate = inlet_stream.mass_flow_rate
        outlet_stream.pressure = inlet_stream.pressure - self.pressure_drop
        outlet_stream.temperature = outlet_temperature
        outlet_stream.composition = outlet_composition.copy()
        
        # Store results
        total_heat_released = self._calculate_total_heat_effect(inlet_stream, outlet_temperature)
        self.results = {
            'operation_mode': self.operation_mode,
            'outlet_temperature': outlet_temperature,
            'heat_duty': self.heat_duty if self.operation_mode == 'heat_duty' else total_heat_released,
            'pressure_drop': self.pressure_drop,
            'reactions': [
                {
                    'id': rxn.reaction_id,
                    'conversion': rxn.conversion,
                    'extent': rxn.extent
                }
                for rxn in self.reactions
            ]
        }
        
        return 0.0  # Perfect convergence for stoichiometric calculations
    
    def _calculate_reaction_extents(self, inlet_stream: Any) -> None:
        """Calculate reaction extents based on specified conversions"""
        # Convert mass flow rates to molar flow rates (assuming average MW for simplicity)
        molar_flow_rate = inlet_stream.mass_flow_rate / 18.015  # kg/s to kmol/s (water equivalent)
        
        for reaction in self.reactions:
            # Find limiting reactant
            limiting_extent = float('inf')
            
            for component_id, coeff in reaction.stoichiometry.items():
                if coeff < 0:  # Reactant (negative coefficient)
                    inlet_mole_fraction = inlet_stream.composition.get(component_id, 0.0)
                    inlet_molar_flow = molar_flow_rate * inlet_mole_fraction
                    max_extent = inlet_molar_flow / abs(coeff)
                    limiting_extent = min(limiting_extent, max_extent)
            
            # Calculate actual extent based on conversion
            reaction.extent = limiting_extent * reaction.conversion
    
    def _calculate_outlet_composition(self, inlet_stream: Any) -> Dict[str, float]:
        """Calculate outlet composition after reactions"""
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
            }
        else:
            outlet_composition = inlet_stream.composition.copy()
        
        return outlet_composition
    
    def _calculate_energy_balance(self, inlet_stream: Any) -> float:
        """Calculate outlet temperature based on energy balance"""
        if self.operation_mode == 'isothermal':
            return self.target_temperature
        elif self.operation_mode == 'adiabatic':
            # Calculate adiabatic temperature rise
            heat_released = self._calculate_total_heat_effect(inlet_stream, inlet_stream.temperature)
            # Simplified: assume constant heat capacity
            cp_avg = 2000  # J/kg·K approximation
            delta_t = -heat_released / (inlet_stream.mass_flow_rate * cp_avg)  # Negative because exothermic
            return inlet_stream.temperature + delta_t
        elif self.operation_mode == 'heat_duty':
            # Calculate temperature change from heat duty
            cp_avg = 2000  # J/kg·K approximation
            delta_t = self.heat_duty / (inlet_stream.mass_flow_rate * cp_avg)
            return inlet_stream.temperature + delta_t
        else:
            return inlet_stream.temperature
    
    def _calculate_total_heat_effect(self, inlet_stream: Any, temperature: float) -> float:
        """Calculate total heat released/absorbed by reactions"""
        # Simplified heat of reaction calculation
        # In a real implementation, this would use thermodynamic data
        total_heat = 0.0
        
        # Example: assume some heat effects for common reactions
        for reaction in self.reactions:
            # Simplified: assign arbitrary heat effects for demonstration
            if 'methane' in reaction.stoichiometry and 'oxygen' in reaction.stoichiometry:
                # Combustion: CH4 + 2O2 -> CO2 + 2H2O (exothermic)
                heat_effect = -890  # kJ/mol CH4 (simplified)
                total_heat += heat_effect * 1000 * reaction.extent  # Convert to J
            elif 'hydrogen' in reaction.stoichiometry and 'oxygen' in reaction.stoichiometry:
                # H2 + 0.5O2 -> H2O (exothermic)
                heat_effect = -286  # kJ/mol H2
                total_heat += heat_effect * 1000 * reaction.extent
            # Add more reaction types as needed
        
        return total_heat
    
    def validate(self) -> bool:
        """Validate reactor configuration"""
        if len(self.inlet_streams) != 1 or len(self.outlet_streams) != 1:
            return False
        if not self.reactions:
            return False
        for reaction in self.reactions:
            if not reaction.stoichiometry:
                return False
            if not (0 <= reaction.conversion <= 1):
                return False
        return True
    
    def add_reaction(self, reaction_id: str, stoichiometry: Dict[str, float], conversion: float = 0.0) -> None:
        """Add a reaction to the reactor"""
        reaction = Reaction(reaction_id, stoichiometry, conversion)
        self.reactions.append(reaction)
    
    def remove_reaction(self, reaction_id: str) -> None:
        """Remove a reaction from the reactor"""
        self.reactions = [r for r in self.reactions if r.reaction_id != reaction_id]
    
    def set_conversion(self, reaction_id: str, conversion: float) -> None:
        """Set conversion for a reaction"""
        for reaction in self.reactions:
            if reaction.reaction_id == reaction_id:
                reaction.conversion = max(0.0, min(1.0, conversion))
                break
