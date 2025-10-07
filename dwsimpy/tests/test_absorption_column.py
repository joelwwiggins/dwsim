"""
Tests for absorption column unit operation.
"""

import pytest
import numpy as np
from dwsimpy.unit_operations.absorption_column import AbsorptionColumn
from dwsimpy.material_stream import MaterialStream


class TestAbsorptionColumn:
    """Test cases for absorption column"""

    def test_initialization(self):
        """Test absorption column initialization"""
        config = {
            'number_of_stages': 5,
            'feed_stage': 1,
            'solvent_flow_rate': 100.0,
            'absorption_efficiency': 0.9,
            'target_component': 'CO2'
        }
        column = AbsorptionColumn('abs_col_1', config)
        
        assert column.id == 'abs_col_1'
        assert column.number_of_stages == 5
        assert column.feed_stage == 1
        assert column.target_component == 'CO2'
        assert len(column.stages) == 5

    def test_validation(self):
        """Test column validation"""
        config = {
            'number_of_stages': 0,  # Invalid
            'feed_stage': 1,
            'target_component': 'CO2'
        }
        column = AbsorptionColumn('abs_col_1', config)
        assert not column.validate()
        
        # Valid configuration
        config['number_of_stages'] = 5
        column = AbsorptionColumn('abs_col_2', config)
        assert column.validate()

    def test_solve_basic(self):
        """Test basic absorption column solving"""
        config = {
            'number_of_stages': 3,
            'feed_stage': 1,
            'solvent_flow_rate': 50.0,
            'absorption_efficiency': 0.8,
            'target_component': 'CO2'
        }
        column = AbsorptionColumn('abs_col_1', config)
        
        # Create inlet streams
        gas_feed = MaterialStream('gas_feed', {
            'temperature': 300.0,
            'pressure': 101325.0,
            'mass_flow_rate': 10.0,
            'composition': {'CO2': 0.1, 'N2': 0.9}
        })
        
        solvent_feed = MaterialStream('solvent_feed', {
            'temperature': 290.0,
            'pressure': 101325.0,
            'mass_flow_rate': 50.0,
            'composition': {'water': 1.0}
        })
        
        treated_gas = MaterialStream('treated_gas', {})
        rich_solvent = MaterialStream('rich_solvent', {})
        
        column.add_inlet_stream(gas_feed)
        column.add_inlet_stream(solvent_feed)
        column.add_outlet_stream(treated_gas)
        column.add_outlet_stream(rich_solvent)
        
        # Solve
        error = column.solve()
        
        # Check that streams have been updated
        assert treated_gas.temperature is not None
        assert treated_gas.pressure is not None
        assert treated_gas.mass_flow_rate is not None
        assert rich_solvent.temperature is not None
        assert rich_solvent.pressure is not None
        assert rich_solvent.mass_flow_rate is not None
        
        # Check results
        assert 'absorption_efficiency' in column.results
        assert 'treated_gas_flow' in column.results
        assert 'rich_solvent_flow' in column.results

    def test_missing_inlet_streams(self):
        """Test error handling for missing inlet streams"""
        config = {
            'number_of_stages': 3,
            'target_component': 'CO2'
        }
        column = AbsorptionColumn('abs_col_1', config)
        
        # Only add one inlet stream
        gas_feed = MaterialStream('gas_feed', {
            'temperature': 300.0,
            'pressure': 101325.0,
            'mass_flow_rate': 10.0,
            'composition': {'CO2': 0.1, 'N2': 0.9}
        })
        column.add_inlet_stream(gas_feed)
        
        treated_gas = MaterialStream('treated_gas', {})
        rich_solvent = MaterialStream('rich_solvent', {})
        column.add_outlet_stream(treated_gas)
        column.add_outlet_stream(rich_solvent)
        
        with pytest.raises(ValueError, match="requires exactly 2 inlet streams"):
            column.solve()

    def test_missing_outlet_streams(self):
        """Test error handling for missing outlet streams"""
        config = {
            'number_of_stages': 3,
            'target_component': 'CO2'
        }
        column = AbsorptionColumn('abs_col_1', config)
        
        gas_feed = MaterialStream('gas_feed', {
            'temperature': 300.0,
            'pressure': 101325.0,
            'mass_flow_rate': 10.0,
            'composition': {'CO2': 0.1, 'N2': 0.9}
        })
        solvent_feed = MaterialStream('solvent_feed', {
            'temperature': 290.0,
            'pressure': 101325.0,
            'mass_flow_rate': 50.0,
            'composition': {'water': 1.0}
        })
        
        column.add_inlet_stream(gas_feed)
        column.add_inlet_stream(solvent_feed)
        # Don't add outlet streams
        
        with pytest.raises(ValueError, match="requires exactly 2 outlet streams"):
            column.solve()
