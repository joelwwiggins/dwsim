from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import sys
import os

# Add the dwsimpy package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dwsimpy.flowsheet_solver import FlowsheetSolver
from dwsimpy.unit_operations.mixer import Mixer
from dwsimpy.unit_operations.heater import Heater
from dwsimpy.unit_operations.valve import Valve
from dwsimpy.unit_operations.pump import Pump
from dwsimpy.unit_operations.splitter import Splitter
from dwsimpy.material_stream import MaterialStream
from dwsimpy.factories import UnitOperationFactory

# Register unit operations
UnitOperationFactory.register("mixer", Mixer)
UnitOperationFactory.register("heater", Heater)
UnitOperationFactory.register("valve", Valve)
UnitOperationFactory.register("pump", Pump)
UnitOperationFactory.register("splitter", Splitter)

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
    nodes: List[NodeData]
    edges: List[EdgeData]

class SimulationResult(BaseModel):
    success: bool
    message: str
    results: Optional[Dict[str, Any]] = None

# Global flowsheet solver instance
flowsheet_solver = FlowsheetSolver()

@app.post("/api/flowsheet/load", response_model=SimulationResult)
async def load_flowsheet(data: FlowsheetData):
    """Load a flowsheet from the UI"""
    try:
        # Convert UI nodes to unit operations
        unit_operations_list = []
        streams = []

        for node in data.nodes:
            unit_op = UnitOperationFactory.create_unit_operation(
                node.type,
                node.id,
                node.data
            )
            unit_operations_list.append(unit_op)

        # Create streams from edges
        for edge in data.edges:
            stream = MaterialStream(edge.id)
            streams.append(stream)

        # Load into solver
        flowsheet_solver.load_flowsheet(unit_operations_list, streams)

        return SimulationResult(
            success=True,
            message="Flowsheet loaded successfully",
            results={"unit_count": len(unit_operations_list), "stream_count": len(streams)}
        )

    except Exception as e:
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
            results = {
                "status": flowsheet_solver.get_status(),
                "progress": flowsheet_solver.get_progress()
            }
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