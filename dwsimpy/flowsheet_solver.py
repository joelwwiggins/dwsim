"""
Flowsheet solver for DWSIM Python implementation.
Handles the simulation of interconnected unit operations.
"""

import numpy as np
from typing import List, Dict, Any, Optional
from .interfaces.iflowsheet_solver import IFlowsheetSolver
from .interfaces.iunit_operation import IUnitOperation
from .material_stream import MaterialStream


class FlowsheetSolver(IFlowsheetSolver):
    """Main flowsheet solver implementing sequential modular approach"""

    def __init__(self):
        self.unit_operations: Dict[str, IUnitOperation] = {}
        self.streams: Dict[str, MaterialStream] = {}
        self.convergence_tolerance = 1e-6
        self.max_iterations = 100
        self.status = "idle"
        self.progress = 0.0

    def load_flowsheet(self, unit_operations: List[IUnitOperation],
                      streams: List[MaterialStream], edges: List[Dict] = None) -> None:
        """Load unit operations and streams into the solver"""
        self.unit_operations = {u.id: u for u in unit_operations}
        self.streams = {s.id: s for s in streams}
        self.edges = edges or []

        # Connect streams to unit operations based on connectivity
        self._connect_streams()

    def _connect_streams(self) -> None:
        """Connect streams to unit operations based on their connectivity"""
        if not self.edges:
            return

        # Clear existing connections
        for unit_op in self.unit_operations.values():
            unit_op.inlet_streams.clear()
            unit_op.outlet_streams.clear()

        # Helper to safely add a stream once
        def ensure_stream(stream_id: str) -> MaterialStream:
            if stream_id not in self.streams:
                self.streams[stream_id] = MaterialStream(stream_id)
            return self.streams[stream_id]

        # Connect streams based on edges. Extended logic:
        # - unit -> unit (existing): edge id (or generated) is the stream between them
        # - stream -> unit: stream id is edge.source; attach as inlet to target
        # - unit -> stream: stream id is edge.target; attach as outlet from source
        for edge in self.edges:
            source_id = edge.get('source')
            target_id = edge.get('target')
            source_handle = edge.get('sourceHandle', '')
            target_handle = edge.get('targetHandle', '')

            # Case 1: unit -> unit
            if source_id in self.unit_operations and target_id in self.unit_operations:
                stream_id = edge.get('id', f"stream_{source_id}_{target_id}")
                stream = ensure_stream(stream_id)
                if 'output' in source_handle:
                    if stream not in self.unit_operations[source_id].outlet_streams:
                        self.unit_operations[source_id].add_outlet_stream(stream)
                if 'input' in target_handle:
                    if stream not in self.unit_operations[target_id].inlet_streams:
                        self.unit_operations[target_id].add_inlet_stream(stream)
                continue

            # Case 2: stream -> unit (source is a stream id, target is unit)
            if source_id in self.streams and target_id in self.unit_operations:
                stream = ensure_stream(source_id)
                if stream not in self.unit_operations[target_id].inlet_streams:
                    self.unit_operations[target_id].add_inlet_stream(stream)
                continue

            # Case 3: unit -> stream (source is unit, target is existing or new stream id)
            if source_id in self.unit_operations and target_id not in self.unit_operations:
                stream = ensure_stream(target_id)
                if stream not in self.unit_operations[source_id].outlet_streams:
                    self.unit_operations[source_id].add_outlet_stream(stream)
                continue

            # Case 4: stream -> stream edges are ignored (no unit connectivity)
            # They can be used later for stream mapping if needed.

            # Post-processing: enforce mixer outlet rule (exactly 1 outlet stream)
            for unit in self.unit_operations.values():
                # Identify mixers by class name (simple heuristic)
                if type(unit).__name__.lower() == 'mixer':
                    if len(unit.outlet_streams) == 0:
                        # Create a synthetic outlet stream if none defined
                        synthetic_id = f"{unit.id}_out"
                        stream = ensure_stream(synthetic_id)
                        unit.add_outlet_stream(stream)
                    elif len(unit.outlet_streams) > 1:
                        # Collapse to first outlet stream, drop extras (they remain in global streams but not attached)
                        primary = unit.outlet_streams[0]
                        unit.outlet_streams = [primary]

    def solve_flowsheet(self, flowsheet: Any) -> List[Exception]:
        """Solve the flowsheet using sequential modular approach"""
        self.status = "running"
        self.progress = 0.0

        try:
            # Initialize all unit operations
            for unit_op in self.unit_operations.values():
                unit_op.initialize()
                self.progress += 10 / len(self.unit_operations)

            # Sequential solution loop
            converged = False
            iteration = 0

            while not converged and iteration < self.max_iterations:
                iteration += 1
                max_error = 0.0

                # Solve each unit operation
                for unit_op in self.unit_operations.values():
                    error = unit_op.solve()
                    max_error = max(max_error, error)

                # Check convergence
                if max_error < self.convergence_tolerance:
                    converged = True

                self.progress = min(90, 10 + (iteration / self.max_iterations) * 80)

            if converged:
                self.status = "converged"
                results = self._collect_results()
                return []  # No exceptions
            else:
                self.status = "failed"
                return [Exception("Maximum iterations exceeded")]

        except Exception as e:
            self.status = "error"
            return [e]

    def _collect_results(self) -> Dict[str, Any]:
        """Collect results from all unit operations and streams"""
        results = {
            "unit_operations": {},
            "streams": {}
        }

        for unit_id, unit_op in self.unit_operations.items():
            results["unit_operations"][unit_id] = unit_op.get_results()

        for stream_id, stream in self.streams.items():
            results["streams"][stream_id] = stream.get_properties()

        return results

    def get_status(self) -> str:
        """Get current solver status"""
        return self.status

    def get_progress(self) -> float:
        """Get solution progress (0-100)"""
        return self.progress

    def reset(self) -> None:
        """Reset the solver state"""
        self.status = "idle"
        self.progress = 0.0
        self.unit_operations.clear()
        self.streams.clear()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize flowsheet to dictionary"""
        return {
            'unit_operations': [
                {
                    'id': unit.id,
                    'type': type(unit).__name__,
                    'config': unit.parameters,
                    'name': unit.name
                }
                for unit in self.unit_operations.values()
            ],
            'streams': [stream.to_dict() for stream in self.streams.values()],
            'edges': getattr(self, 'edges', []),
            'solver_settings': {
                'convergence_tolerance': self.convergence_tolerance,
                'max_iterations': self.max_iterations
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], property_packages: Dict[str, Any] = None) -> 'FlowsheetSolver':
        """Deserialize flowsheet from dictionary"""
        solver = cls()
        
        # Restore solver settings
        settings = data.get('solver_settings', {})
        solver.convergence_tolerance = settings.get('convergence_tolerance', 1e-6)
        solver.max_iterations = settings.get('max_iterations', 100)
        
        # Create unit operations
        unit_operations = []
        for unit_data in data.get('unit_operations', []):
            unit_type = unit_data['type']
            unit_id = unit_data['id']
            config = unit_data.get('config', {})
            
            # Import unit operation classes dynamically
            if unit_type == 'Mixer':
                from .unit_operations.mixer import Mixer
                unit = Mixer(unit_id, config)
            elif unit_type == 'Heater':
                from .unit_operations.heater import Heater
                unit = Heater(unit_id, config)
            elif unit_type == 'Valve':
                from .unit_operations.valve import Valve
                unit = Valve(unit_id, config)
            elif unit_type == 'Pump':
                from .unit_operations.pump import Pump
                unit = Pump(unit_id, config)
            elif unit_type == 'Splitter':
                from .unit_operations.splitter import Splitter
                unit = Splitter(unit_id, config)
            else:
                raise ValueError(f"Unknown unit operation type: {unit_type}")
            
            unit_operations.append(unit)
        
        # Create streams
        streams = []
        property_packages = property_packages or {}
        for stream_data in data.get('streams', []):
            stream_type = stream_data.get('type', 'material_stream')
            if stream_type == 'energy_stream':
                from .energy_stream import EnergyStream
                stream = EnergyStream.from_dict(stream_data)
            else:
                # Get property package for this stream
                pp_type = stream_data.get('property_package_type')
                pp = property_packages.get(pp_type) if pp_type else None
                from .material_stream import MaterialStream
                stream = MaterialStream.from_dict(stream_data, pp)
            streams.append(stream)
        
        # Load flowsheet
        edges = data.get('edges', [])
        solver.load_flowsheet(unit_operations, streams, edges)
        
        return solver

    def save_to_file(self, filepath: str) -> None:
        """Save flowsheet to JSON file"""
        import json
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_file(cls, filepath: str, property_packages: Dict[str, Any] = None) -> 'FlowsheetSolver':
        """Load flowsheet from JSON file"""
        import json
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data, property_packages)

    def add_unit_operation(self, unit_operation: IUnitOperation) -> None:
        """Add a single unit operation to the flowsheet"""
        self.unit_operations[unit_operation.id] = unit_operation

    def add_stream(self, stream: MaterialStream) -> None:
        """Add a single stream to the flowsheet"""
        self.streams[stream.id] = stream

    def add_edge(self, edge: Dict) -> None:
        """Add a single edge to the flowsheet"""
        if not hasattr(self, 'edges'):
            self.edges = []
        self.edges.append(edge)
        self._connect_streams()