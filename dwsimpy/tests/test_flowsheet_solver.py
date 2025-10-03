"""
Unit tests for FlowsheetSolver.

Generated using pytest.
"""

import pytest
from dwsimpy.solvers.flowsheet_solver import FlowsheetSolver
from dwsimpy.unit_ops.mixer import Mixer
from dwsimpy.unit_ops.splitter import Splitter


class MockStream:
    def __init__(self, name):
        self.name = name
        self.mass_flow = 0
        self.calculated = False
        self.temperature = 0
        self.pressure = 0


class TestFlowsheetSolver:
    """Test cases for FlowsheetSolver class."""

    @pytest.fixture
    def solver(self):
        """Fixture to create FlowsheetSolver instance."""
        return FlowsheetSolver()

    def test_initialization(self, solver):
        """Test that solver initializes correctly."""
        assert solver.max_iterations == 50
        assert solver.tolerance == 1e-6
        assert solver.unit_operations == []
        assert solver.streams == {}

    def test_add_unit_operation(self, solver):
        """Test adding unit operations."""
        mixer = Mixer()
        solver.add_unit_operation(mixer)
        assert len(solver.unit_operations) == 1
        assert solver.unit_operations[0] == mixer

    def test_add_stream(self, solver):
        """Test adding streams."""
        stream = MockStream("stream1")
        solver.add_stream("stream1", stream)
        assert "stream1" in solver.streams
        assert solver.streams["stream1"] == stream

    def test_solve_converged(self, solver):
        """Test solving a simple converged flowsheet."""
        # Create a simple flowsheet: inlet -> mixer -> splitter -> outlets

        inlet = MockStream("inlet")
        inlet.mass_flow = 100.0
        inlet.temperature = 300.0
        inlet.pressure = 101325.0
        inlet.calculated = True

        outlet1 = MockStream("outlet1")
        outlet2 = MockStream("outlet2")

        mixer = Mixer()
        mixer.input_streams = [inlet]
        mixer.output_stream = inlet  # Simplified
        mixer.component_name = "Mixer"

        splitter = Splitter()
        splitter.input_stream = inlet
        splitter.output_streams = [outlet1, outlet2]
        splitter.ratios = [0.6, 0.4, 0.0]  # Set ratios
        splitter.component_name = "Splitter"

        solver.add_unit_operation(mixer)
        solver.add_unit_operation(splitter)

        # Mock calculate methods
        def mock_mixer_calc():
            mixer.output_stream.mass_flow = sum(s.mass_flow for s in mixer.input_streams)
            mixer.output_stream.calculated = True

        def mock_splitter_calc():
            total_flow = splitter.input_stream.mass_flow
            for i, outlet in enumerate(splitter.output_streams):
                outlet.mass_flow = total_flow * splitter.ratios[i]
                outlet.calculated = True

        mixer.calculate = mock_mixer_calc
        splitter.calculate = mock_splitter_calc

        result = solver.solve()

        assert result is True
        assert outlet1.mass_flow == 60.0  # 100 * 0.6
        assert outlet2.mass_flow == 40.0  # 100 * 0.4

    def test_solve_not_converged(self, solver):
        """Test solving with non-convergent unit op."""
        mixer = Mixer()
        mixer.component_name = "Mixer"

        def failing_calc():
            raise ValueError("Calculation failed")

        mixer.calculate = failing_calc
        solver.add_unit_operation(mixer)

        result = solver.solve()

        assert result is False

    def test_convergence_checking(self, solver):
        """Test convergence checking with changing values."""
        stream = MockStream("stream")
        stream.mass_flow = 100.0
        stream.temperature = 300.0
        solver.add_stream("stream", stream)

        # First call
        prev = solver._get_convergence_values()
        assert prev["stream_mass_flow"] == 100.0

        # Change values
        stream.mass_flow = 100.0 + 1e-7  # Within tolerance
        stream.temperature = 300.0 + 1e-7

        assert solver._check_convergence(prev)

        # Change beyond tolerance
        stream.mass_flow = 101.0
        assert not solver._check_convergence(prev)

    def test_add_recycle_stream(self, solver):
        """Test adding recycle streams."""
        solver.add_recycle_stream("recycle1")
        assert "recycle1" in solver.recycle_streams

    def test_reset(self, solver):
        """Test resetting the solver."""
        mixer = Mixer()
        stream = MockStream("stream")
        stream.calculated = True

        solver.add_unit_operation(mixer)
        solver.add_stream("stream", stream)

        solver.reset()

        assert mixer._is_dirty is True
        assert stream.calculated is False