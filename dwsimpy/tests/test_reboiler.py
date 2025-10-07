"""
Tests for reboiler unit operation.
"""

import pytest
import numpy as np
from dwsimpy.unit_operations.reboiler import Reboiler
from dwsimpy.material_stream import MaterialStream


class TestReboiler:
    """Test cases for reboiler"""

    def test_kettle_reboiler_initialization(self):
        """Test kettle reboiler initialization"""
        config = {
            'reboiler_type': 'kettle',
            'reboiler_pressure': 101325.0,
            'heat_duty': 50000.0,
            'vapor_fraction': 0.1
        }
        reboiler = Reboiler('reb_1', config)
        
        assert reboiler.id == 'reb_1'
        assert reboiler.reboiler_type == 'kettle'
        assert reboiler.reboiler_pressure == 101325.0
        assert reboiler.heat_duty == 50000.0

    def test_thermosiphon_reboiler_initialization(self):
        """Test thermosiphon reboiler initialization"""
        config = {
            'reboiler_type': 'thermosiphon',
            'reboiler_pressure': 101325.0
        }
        reboiler = Reboiler('reb_2', config)
        
        assert reboiler.reboiler_type == 'thermosiphon'

    def test_validation(self):
        """Test reboiler validation"""
        # Invalid: kettle reboiler with 1 outlet
        config = {
            'reboiler_type': 'kettle'
        }
        reboiler = Reboiler('reb_1', config)
        reboiler.add_inlet_stream(MaterialStream('in', {}))
        reboiler.add_outlet_stream(MaterialStream('out', {}))
        assert not reboiler.validate()
        
        # Valid: kettle reboiler with 2 outlets
        reboiler = Reboiler('reb_2', config)
        reboiler.add_inlet_stream(MaterialStream('in', {}))
        reboiler.add_outlet_stream(MaterialStream('liquid', {}))
        reboiler.add_outlet_stream(MaterialStream('vapor', {}))
        assert reboiler.validate()

    def test_solve_kettle_reboiler_by_heat_duty(self):
        """Test kettle reboiler solving by heat duty"""
        config = {
            'reboiler_type': 'kettle',
            'reboiler_pressure': 101325.0,
            'heat_duty': 25000.0
        }
        reboiler = Reboiler('reb_1', config)
        
        inlet = MaterialStream('liquid_in', {
            'temperature': 350.0,
            'pressure': 101325.0,
            'mass_flow_rate': 100.0,
            'composition': {'water': 1.0}
        })
        
        liquid_outlet = MaterialStream('liquid_out', {})
        vapor_outlet = MaterialStream('vapor_out', {})
        
        reboiler.add_inlet_stream(inlet)
        reboiler.add_outlet_stream(liquid_outlet)
        reboiler.add_outlet_stream(vapor_outlet)
        
        error = reboiler.solve()
        
        assert liquid_outlet.temperature is not None
        assert vapor_outlet.temperature is not None
        assert liquid_outlet.pressure == 101325.0
        assert vapor_outlet.pressure == 96325.0  # With pressure drop
        assert liquid_outlet.mass_flow_rate + vapor_outlet.mass_flow_rate == pytest.approx(100.0, abs=1e-6)
        assert reboiler.vapor_fraction is not None

    def test_solve_kettle_reboiler_by_temperature(self):
        """Test kettle reboiler solving by temperature"""
        config = {
            'reboiler_type': 'kettle',
            'reboiler_pressure': 101325.0,
            'reboiler_temperature': 380.0
        }
        reboiler = Reboiler('reb_2', config)
        
        inlet = MaterialStream('liquid_in', {
            'temperature': 350.0,
            'pressure': 101325.0,
            'mass_flow_rate': 80.0,
            'composition': {'water': 1.0}
        })
        
        liquid_outlet = MaterialStream('liquid_out', {})
        vapor_outlet = MaterialStream('vapor_out', {})
        
        reboiler.add_inlet_stream(inlet)
        reboiler.add_outlet_stream(liquid_outlet)
        reboiler.add_outlet_stream(vapor_outlet)
        
        error = reboiler.solve()
        
        assert liquid_outlet.temperature == 380.0
        assert vapor_outlet.temperature == 380.0
        assert reboiler.heat_duty is not None
        assert reboiler.heat_duty > 0  # Reboiling requires heat input

    def test_solve_thermosiphon_reboiler(self):
        """Test thermosiphon reboiler solving"""
        config = {
            'reboiler_type': 'thermosiphon',
            'reboiler_pressure': 101325.0
        }
        reboiler = Reboiler('reb_3', config)
        
        inlet = MaterialStream('liquid_in', {
            'temperature': 360.0,
            'pressure': 101325.0,
            'mass_flow_rate': 120.0,
            'composition': {'water': 1.0}
        })
        
        outlet = MaterialStream('mixed_out', {})
        
        reboiler.add_inlet_stream(inlet)
        reboiler.add_outlet_stream(outlet)
        
        error = reboiler.solve()
        
        assert outlet.temperature is not None
        assert outlet.pressure == 101325.0
        assert outlet.mass_flow_rate == 120.0
        assert reboiler.heat_duty is not None
        assert reboiler.vapor_fraction == 0.05  # Default small vapor fraction

    def test_missing_inlet_stream(self):
        """Test error handling for missing inlet stream"""
        config = {
            'reboiler_type': 'kettle'
        }
        reboiler = Reboiler('reb_1', config)
        
        # Don't add inlet stream
        liquid_outlet = MaterialStream('liquid_out', {})
        vapor_outlet = MaterialStream('vapor_out', {})
        reboiler.add_outlet_stream(liquid_outlet)
        reboiler.add_outlet_stream(vapor_outlet)
        
        with pytest.raises(ValueError, match="requires exactly 1 inlet stream"):
            reboiler.solve()
