"""
Tests for stripping column unit operation.
"""

import pytest
import numpy as np
from dwsimpy.unit_operations.stripping_column import StrippingColumn
from dwsimpy.material_stream import MaterialStream


class TestStrippingColumn:
    """Test cases for stripping column"""

    def test_initialization(self):
        """Test stripping column initialization"""
        config = {
            'number_of_stages': 5,
            'feed_stage': 3,
            'stripping_gas_flow_rate': 100.0,
            'stripping_efficiency': 0.85,
            'target_component': 'CO2'
        }
        column = StrippingColumn('strip_col_1', config)
        
        assert column.id == 'strip_col_1'
        assert column.number_of_stages == 5
        assert column.feed_stage == 3
        assert column.target_component == 'CO2'
        assert len(column.stages) == 5

    def test_validation(self):
        """Test column validation"""
        config = {
            'number_of_stages': -1,  # Invalid
            'feed_stage': 1,
            'target_component': 'CO2'
        }
        column = StrippingColumn('strip_col_1', config)
        assert not column.validate()
        
        # Valid configuration
        config['number_of_stages'] = 5
        column = StrippingColumn('strip_col_2', config)
        assert column.validate()

    def test_solve_basic(self):
        """Test basic stripping column solving"""
        config = {
            'number_of_stages': 4,
            'feed_stage': 2,
            'stripping_gas_flow_rate': 30.0,
            'stripping_efficiency': 0.75,
            'target_component': 'CO2'
        }
        column = StrippingColumn('strip_col_1', config)
        
        # Create inlet streams
        liquid_feed = MaterialStream('liquid_feed', {
            'temperature': 310.0,
            'pressure': 101325.0,
            'mass_flow_rate': 100.0,
            'composition': {'water': 0.9, 'CO2': 0.1}
        })
        
        stripping_gas = MaterialStream('stripping_gas', {
            'temperature': 295.0,
            'pressure': 101325.0,
            'mass_flow_rate': 30.0,
            'composition': {'N2': 1.0}
        })
        
        stripped_liquid = MaterialStream('stripped_liquid', {})
        rich_gas = MaterialStream('rich_gas', {})
        
        column.add_inlet_stream(liquid_feed)
        column.add_inlet_stream(stripping_gas)
        column.add_outlet_stream(stripped_liquid)
        column.add_outlet_stream(rich_gas)
        
        # Solve
        error = column.solve()
        
        # Check that streams have been updated
        assert stripped_liquid.temperature is not None
        assert stripped_liquid.pressure is not None
        assert stripped_liquid.mass_flow_rate is not None
        assert rich_gas.temperature is not None
        assert rich_gas.pressure is not None
        assert rich_gas.mass_flow_rate is not None
        
        # Check results
        assert 'stripping_efficiency' in column.results
        assert 'stripped_liquid_flow' in column.results
        assert 'rich_gas_flow' in column.results

    def test_missing_inlet_streams(self):
        """Test error handling for missing inlet streams"""
        config = {
            'number_of_stages': 4,
            'target_component': 'CO2'
        }
        column = StrippingColumn('strip_col_1', config)
        
        # Only add one inlet stream
        liquid_feed = MaterialStream('liquid_feed', {
            'temperature': 310.0,
            'pressure': 101325.0,
            'mass_flow_rate': 100.0,
            'composition': {'water': 0.9, 'CO2': 0.1}
        })
        column.add_inlet_stream(liquid_feed)
        
        stripped_liquid = MaterialStream('stripped_liquid', {})
        rich_gas = MaterialStream('rich_gas', {})
        column.add_outlet_stream(stripped_liquid)
        column.add_outlet_stream(rich_gas)
        
        with pytest.raises(ValueError, match="requires exactly 2 inlet streams"):
            column.solve()
