"""
Integration tests for advanced unit operations working together.
"""

import pytest
from dwsimpy.flowsheet_solver import FlowsheetSolver
from dwsimpy.factories import UnitOperationFactory
from dwsimpy.material_stream import MaterialStream


class TestAdvancedIntegration:
    """Integration tests for advanced unit operations"""

    def test_absorption_stripping_system(self):
        """Test absorption column followed by stripping column"""
        # Create absorption column
        abs_config = {
            'number_of_stages': 4,
            'feed_stage': 1,
            'solvent_flow_rate': 100.0,
            'absorption_efficiency': 0.8,
            'target_component': 'CO2'
        }
        absorption = UnitOperationFactory.create_unit_operation('absorption_column', 'abs_col', abs_config)
        
        # Create stripping column
        strip_config = {
            'number_of_stages': 4,
            'feed_stage': 2,
            'stripping_gas_flow_rate': 50.0,
            'stripping_efficiency': 0.7,
            'target_component': 'CO2'
        }
        stripping = UnitOperationFactory.create_unit_operation('stripping_column', 'strip_col', strip_config)
        
        # Create streams
        gas_feed = MaterialStream('gas_feed', {
            'temperature': 300.0,
            'pressure': 101325.0,
            'mass_flow_rate': 20.0,
            'composition': {'CO2': 0.15, 'N2': 0.85}
        })
        
        lean_solvent = MaterialStream('lean_solvent', {
            'temperature': 290.0,
            'pressure': 101325.0,
            'mass_flow_rate': 100.0,
            'composition': {'water': 1.0}
        })
        
        treated_gas = MaterialStream('treated_gas', {})
        rich_solvent = MaterialStream('rich_solvent', {})
        stripped_solvent = MaterialStream('stripped_solvent', {})
        stripping_gas = MaterialStream('stripping_gas', {
            'temperature': 295.0,
            'pressure': 101325.0,
            'mass_flow_rate': 50.0,
            'composition': {'N2': 1.0}
        })
        
        # Connect absorption column
        absorption.add_inlet_stream(gas_feed)
        absorption.add_inlet_stream(lean_solvent)
        absorption.add_outlet_stream(treated_gas)
        absorption.add_outlet_stream(rich_solvent)
        
        # Connect stripping column
        stripping.add_inlet_stream(rich_solvent)  # Rich solvent from absorption
        stripping.add_inlet_stream(stripping_gas)
        stripping.add_outlet_stream(stripped_solvent)
        stripping.add_outlet_stream(stripping_gas)  # This would normally be a different stream
        
        # Solve absorption
        error1 = absorption.solve()
        assert error1 >= 0
        
        # Update rich solvent composition for stripping
        # In a real system, this would be handled by the flowsheet solver
        rich_solvent.composition = absorption.outlet_streams[1].composition
        rich_solvent.temperature = absorption.outlet_streams[1].temperature
        
        # Solve stripping
        error2 = stripping.solve()
        assert error2 >= 0
        
        # Check that CO2 has been absorbed and then stripped
        initial_co2 = gas_feed.composition.get('CO2', 0)
        treated_co2 = treated_gas.composition.get('CO2', 0)
        assert treated_co2 < initial_co2  # CO2 reduced in treated gas

    def test_condenser_reboiler_system(self):
        """Test condenser and reboiler working together"""
        # Create condenser
        cond_config = {
            'condenser_type': 'total',
            'condenser_pressure': 101325.0
        }
        condenser = UnitOperationFactory.create_unit_operation('condenser', 'condenser', cond_config)
        
        # Create reboiler
        reb_config = {
            'reboiler_type': 'kettle',
            'reboiler_pressure': 101325.0,
            'heat_duty': 30000.0
        }
        reboiler = UnitOperationFactory.create_unit_operation('reboiler', 'reboiler', reb_config)
        
        # Create streams
        vapor_stream = MaterialStream('vapor', {
            'temperature': 380.0,
            'pressure': 200000.0,
            'mass_flow_rate': 60.0,
            'composition': {'water': 1.0}
        })
        
        condensate = MaterialStream('condensate', {})
        
        liquid_feed = MaterialStream('liquid_feed', {
            'temperature': 350.0,
            'pressure': 101325.0,
            'mass_flow_rate': 100.0,
            'composition': {'water': 1.0}
        })
        
        reboiler_liquid = MaterialStream('reboiler_liquid', {})
        reboiler_vapor = MaterialStream('reboiler_vapor', {})
        
        # Connect condenser
        condenser.add_inlet_stream(vapor_stream)
        condenser.add_outlet_stream(condensate)
        
        # Connect reboiler
        reboiler.add_inlet_stream(liquid_feed)
        reboiler.add_outlet_stream(reboiler_liquid)
        reboiler.add_outlet_stream(reboiler_vapor)
        
        # Solve both units
        error1 = condenser.solve()
        error2 = reboiler.solve()
        
        assert error1 >= 0
        assert error2 >= 0
        
        # Check results
        assert condensate.temperature is not None
        assert condensate.pressure == 101325.0
        assert condenser.heat_duty < 0  # Condensation releases heat
        
        assert reboiler_liquid.temperature is not None
        assert reboiler_vapor.temperature is not None
        assert reboiler.heat_duty > 0  # Reboiling requires heat

    def test_heat_exchanger_distillation_integration(self):
        """Test heat exchanger integrated with distillation"""
        # Create heat exchanger
        hx_config = {
            'calculation_mode': 'heat_duty',
            'heat_duty': 50000.0,
            'overall_heat_transfer_coeff': 500.0
        }
        heat_exchanger = UnitOperationFactory.create_unit_operation('heat_exchanger', 'heater', hx_config)
        
        # Create distillation column
        dist_config = {
            'number_of_stages': 5,
            'feed_stage': 3,
            'reflux_ratio': 2.0
        }
        distillation = UnitOperationFactory.create_unit_operation('distillation_column', 'dist_col', dist_config)
        
        # Create streams
        cold_feed = MaterialStream('cold_feed', {
            'temperature': 300.0,
            'pressure': 101325.0,
            'mass_flow_rate': 100.0,
            'composition': {'water': 0.5, 'ethanol': 0.5}
        })
        
        hot_stream = MaterialStream('hot_stream', {
            'temperature': 400.0,
            'pressure': 101325.0,
            'mass_flow_rate': 80.0,
            'composition': {'water': 1.0}
        })
        
        heated_feed = MaterialStream('heated_feed', {})
        cooled_hot = MaterialStream('cooled_hot', {})
        
        feed_stream = MaterialStream('feed', {})
        distillate = MaterialStream('distillate', {})
        bottoms = MaterialStream('bottoms', {})
        
        # Connect heat exchanger
        heat_exchanger.add_inlet_stream(hot_stream)
        heat_exchanger.add_inlet_stream(cold_feed)
        heat_exchanger.add_outlet_stream(cooled_hot)
        heat_exchanger.add_outlet_stream(heated_feed)
        
        # Connect distillation (feed from heat exchanger)
        distillation.add_inlet_stream(heated_feed)
        distillation.add_outlet_stream(distillate)
        distillation.add_outlet_stream(bottoms)
        
        # Solve heat exchanger first
        error1 = heat_exchanger.solve()
        assert error1 >= 0
        
        # Update feed stream for distillation
        heated_feed.composition = heat_exchanger.outlet_streams[1].composition
        heated_feed.temperature = heat_exchanger.outlet_streams[1].temperature
        
        # Solve distillation
        error2 = distillation.solve()
        assert error2 >= 0
        
        # Check that temperatures increased through heat exchanger
        assert heated_feed.temperature > cold_feed.temperature
        assert cooled_hot.temperature < hot_stream.temperature
