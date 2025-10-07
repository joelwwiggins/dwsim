"""
Tests for condenser unit operation.
"""

import pytest
import numpy as np
from dwsimpy.unit_operations.condenser import Condenser
from dwsimpy.material_stream import MaterialStream


class TestCondenser:
    """Test cases for condenser"""

    def test_total_condenser_initialization(self):
        """Test total condenser initialization"""
        config = {
            'condenser_type': 'total',
            'condenser_pressure': 101325.0,
            'heat_duty': None
        }
        condenser = Condenser('cond_1', config)
        
        assert condenser.id == 'cond_1'
        assert condenser.condenser_type == 'total'
        assert condenser.condenser_pressure == 101325.0

    def test_partial_condenser_initialization(self):
        """Test partial condenser initialization"""
        config = {
            'condenser_type': 'partial',
            'condenser_pressure': 200000.0,
            'condenser_temperature': 320.0,
            'vapor_fraction': 0.1
        }
        condenser = Condenser('cond_2', config)
        
        assert condenser.condenser_type == 'partial'
        assert condenser.condenser_temperature == 320.0
        assert condenser.vapor_fraction == 0.1

    def test_validation(self):
        """Test condenser validation"""
        # Invalid: total condenser with 2 outlets
        config = {
            'condenser_type': 'total'
        }
        condenser = Condenser('cond_1', config)
        condenser.add_inlet_stream(MaterialStream('in', {}))
        condenser.add_outlet_stream(MaterialStream('out1', {}))
        condenser.add_outlet_stream(MaterialStream('out2', {}))
        assert not condenser.validate()
        
        # Valid: total condenser with 1 outlet
        condenser = Condenser('cond_2', config)
        condenser.add_inlet_stream(MaterialStream('in', {}))
        condenser.add_outlet_stream(MaterialStream('out', {}))
        assert condenser.validate()

    def test_solve_total_condenser(self):
        """Test total condenser solving"""
        config = {
            'condenser_type': 'total',
            'condenser_pressure': 101325.0
        }
        condenser = Condenser('cond_1', config)
        
        inlet = MaterialStream('vapor_in', {
            'temperature': 380.0,
            'pressure': 200000.0,
            'mass_flow_rate': 50.0,
            'composition': {'water': 1.0}
        })
        
        outlet = MaterialStream('liquid_out', {})
        
        condenser.add_inlet_stream(inlet)
        condenser.add_outlet_stream(outlet)
        
        error = condenser.solve()
        
        assert outlet.temperature is not None
        assert outlet.pressure == 101325.0
        assert outlet.mass_flow_rate == 50.0
        assert condenser.heat_duty is not None
        assert condenser.heat_duty < 0  # Condensation is exothermic

    def test_solve_partial_condenser_by_temperature(self):
        """Test partial condenser solving by temperature"""
        config = {
            'condenser_type': 'partial',
            'condenser_pressure': 101325.0,
            'condenser_temperature': 320.0
        }
        condenser = Condenser('cond_2', config)
        
        inlet = MaterialStream('vapor_in', {
            'temperature': 380.0,
            'pressure': 200000.0,
            'mass_flow_rate': 100.0,
            'composition': {'water': 1.0}
        })
        
        liquid_outlet = MaterialStream('liquid_out', {})
        vapor_outlet = MaterialStream('vapor_out', {})
        
        condenser.add_inlet_stream(inlet)
        condenser.add_outlet_stream(liquid_outlet)
        condenser.add_outlet_stream(vapor_outlet)
        
        error = condenser.solve()
        
        assert liquid_outlet.temperature == 320.0
        assert vapor_outlet.temperature == 320.0
        assert liquid_outlet.pressure == 101325.0
        assert vapor_outlet.pressure == 93125.0  # With pressure drop
        assert liquid_outlet.mass_flow_rate + vapor_outlet.mass_flow_rate == pytest.approx(100.0, abs=1e-6)

    def test_solve_partial_condenser_by_vapor_fraction(self):
        """Test partial condenser solving by vapor fraction"""
        config = {
            'condenser_type': 'partial',
            'condenser_pressure': 101325.0,
            'vapor_fraction': 0.2
        }
        condenser = Condenser('cond_3', config)
        
        inlet = MaterialStream('vapor_in', {
            'temperature': 380.0,
            'pressure': 200000.0,
            'mass_flow_rate': 75.0,
            'composition': {'water': 1.0}
        })
        
        liquid_outlet = MaterialStream('liquid_out', {})
        vapor_outlet = MaterialStream('vapor_out', {})
        
        condenser.add_inlet_stream(inlet)
        condenser.add_outlet_stream(liquid_outlet)
        condenser.add_outlet_stream(vapor_outlet)
        
        error = condenser.solve()
        
        assert vapor_outlet.mass_flow_rate == pytest.approx(15.0, abs=1e-6)  # 20% of 75
        assert liquid_outlet.mass_flow_rate == pytest.approx(60.0, abs=1e-6)  # 80% of 75
        assert condenser.condenser_temperature is not None
