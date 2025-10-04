from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import sys
import os

# Add the dwsimpy package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from dwsimpy.flowsheet_solver import FlowsheetSolver
from dwsimpy.unit_operations.mixer import Mixer
from dwsimpy.unit_operations.heater import Heater
from dwsimpy.unit_operations.cooler import Cooler
from dwsimpy.unit_operations.valve import Valve
from dwsimpy.unit_operations.pump import Pump
from dwsimpy.unit_operations.splitter import Splitter
# from dwsimpy.unit_operations.tank import Tank
from dwsimpy.unit_ops.compressor import Compressor
from dwsimpy.unit_ops.expander import Expander
from dwsimpy.unit_ops.heat_exchanger import HeatExchanger
from dwsimpy.unit_ops.pipe import Pipe
from dwsimpy.unit_ops.vessel import Vessel
from dwsimpy.unit_ops.component_separator import ComponentSeparator
from dwsimpy.unit_ops.filter import Filter
from dwsimpy.unit_ops.orifice_plate import OrificePlate
from dwsimpy.unit_ops.relief_valve import ReliefValve
from dwsimpy.unit_operations.base_unit import BaseUnitOperation

from dwsimpy.material_stream import MaterialStream
from dwsimpy.factories import UnitOperationFactory
from dwsimpy.property_packages.ideal_property_package import IdealPropertyPackage

app = FastAPI(title="DWSIM Python API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Svelte dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API
class NodeData(BaseModel):
    id: str
    type: str
    position: Dict[str, float]
    data: Dict[str, Any]

class EdgeData(BaseModel):
    id: str
    source: str
    target: str
    sourceHandle: Optional[str] = None
    targetHandle: Optional[str] = None

class FlowsheetData(BaseModel):
    nodes: List[Dict[str, Any]]  # Simplified
    edges: List[Dict[str, Any]]  # Simplified
    streams: Optional[List[Dict[str, Any]]] = None  # Stream properties

class SimulationResult(BaseModel):
    success: bool
    message: str
    results: Optional[Dict[str, Any]] = None

# Global flowsheet solver instance
try:
    flowsheet_solver = FlowsheetSolver()
    property_package = IdealPropertyPackage()
    # Add some basic components
    property_package.add_component({'id': 'water'})
    property_package.add_component({'id': 'methane'})
    print("Flowsheet solver and property package initialized successfully")
except Exception as e:
    print(f"Error initializing flowsheet solver: {e}")
    flowsheet_solver = None
    property_package = None

@app.post("/api/flowsheet/load", response_model=SimulationResult)
async def load_flowsheet(data: FlowsheetData):
    """Load a flowsheet from the UI"""
    try:
        if flowsheet_solver is None:
            raise HTTPException(status_code=500, detail="Flowsheet solver not initialized")

        # Convert UI nodes to unit operations
        unit_operations_list = []

        for node in data.nodes:
            print(f"Creating unit operation: {node['data']['unitType']}, {node['id']}")
            unit_op = UnitOperationFactory.create_unit_operation(
                node['data']['unitType'],
                node['id'],
                node['data']
            )
            unit_operations_list.append(unit_op)

        # Create streams from provided data or edges
        streams = []
        if data.streams:
            for stream_data in data.streams:
                stream = MaterialStream(stream_data['id'], stream_data.get('name', stream_data['id']))
                # Set properties if provided
                if 'temperature' in stream_data:
                    stream.temperature = stream_data['temperature']
                if 'pressure' in stream_data:
                    stream.pressure = stream_data['pressure']
                if 'mass_flow_rate' in stream_data:
                    stream.mass_flow_rate = stream_data['mass_flow_rate']
                if 'composition' in stream_data:
                    stream.composition = stream_data['composition']
                stream.property_package = property_package
                streams.append(stream)
        else:
            for edge in data.edges:
                stream = MaterialStream(edge['id'])
                stream.property_package = property_package
                streams.append(stream)

        print(f"Loading flowsheet with {len(unit_operations_list)} units and {len(streams)} streams")
        # Load into solver with edge connectivity
        flowsheet_solver.load_flowsheet(unit_operations_list, streams, data.edges)
        print("Flowsheet loaded successfully")

        return SimulationResult(
            success=True,
            message="Flowsheet loaded successfully",
            results={"unit_count": len(unit_operations_list), "stream_count": len(streams)}
        )

    except Exception as e:
        print(f"Error in load_flowsheet: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Failed to load flowsheet: {str(e)}")

@app.post("/api/simulation/run", response_model=SimulationResult)
async def run_simulation():
    """Run the flowsheet simulation"""
    try:
        exceptions = flowsheet_solver.solve_flowsheet(None)  # flowsheet parameter not used in current implementation

        if exceptions:
            return SimulationResult(
                success=False,
                message=f"Simulation failed: {str(exceptions[0])}"
            )
        else:
            # Get results from solver
            results = flowsheet_solver._collect_results()
            return SimulationResult(
                success=True,
                message="Simulation completed successfully",
                results=results
            )

    except Exception as e:
        return SimulationResult(
            success=False,
            message=f"Simulation failed: {str(e)}"
        )

@app.get("/api/simulation/status")
async def get_simulation_status():
    """Get current simulation status"""
    return {
        "status": flowsheet_solver.get_status(),
        "progress": flowsheet_solver.get_progress()
    }

@app.get("/api/unit-operations")
async def get_unit_operations():
    """Get available unit operation types"""
    return UnitOperationFactory.get_available_types()

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)