from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import sys
import os
import json
from pathlib import Path

# Add the dwsimpy package to the path
dwsimpy_path = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, dwsimpy_path)
os.environ['PYTHONPATH'] = dwsimpy_path

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
from dwsimpy.energy_stream import EnergyStream
from dwsimpy.factories import UnitOperationFactory
from dwsimpy.property_packages.ideal_property_package import IdealPropertyPackage
from dwsimpy.property_packages.peng_robinson_property_package import PengRobinsonPropertyPackage

app = FastAPI(title="DWSIM Python API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://172.17.0.3:5173", "http://172.17.0.3:5174", "http://192.168.1.102:5173", "http://192.168.1.102:5174"],  # Svelte dev server
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
    import traceback
    traceback.print_exc()
    flowsheet_solver = None
    property_package = None

# Ensure the flowsheet storage directory exists
FLOWsheet_STORAGE_DIR = Path(__file__).parent / "flowsheets"
FLOWsheet_STORAGE_DIR.mkdir(exist_ok=True)

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
            unit_type = node['data']['unitType'].lower()  # Convert to lowercase for factory
            unit_op = UnitOperationFactory.create_unit_operation(
                unit_type,
                node['id'],
                node['data']
            )
            unit_operations_list.append(unit_op)

        # Create streams from provided data or edges
        streams = []
        if data.streams:
            for stream_data in data.streams:
                stream_type = stream_data.get('stream_type', 'material')
                if stream_type == 'energy':
                    stream = EnergyStream(stream_data['id'], stream_data.get('name', stream_data['id']))
                    # Set energy-specific properties
                    if 'energy_flow' in stream_data:
                        stream.energy_flow = stream_data['energy_flow']
                    if 'temperature_low' in stream_data:
                        stream.temperature_low = stream_data['temperature_low']
                    if 'temperature_high' in stream_data:
                        stream.temperature_high = stream_data['temperature_high']
                else:
                    # Material stream
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

        # Initialize property packages
        ideal_pp = IdealPropertyPackage()
        pr_pp = PengRobinsonPropertyPackage()
        
        # Assign property packages to streams
        for stream in flowsheet_solver.streams.values():
            stream.property_package = pr_pp  # Use Peng-Robinson for more accurate calculations

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

@app.post("/api/flowsheet/save")
async def save_flowsheet(data: FlowsheetData, filename: str = "default"):
    """Save a flowsheet to storage using flowsheet solver serialization"""
    try:
        if flowsheet_solver is None:
            raise HTTPException(status_code=500, detail="Flowsheet solver not initialized")

        print(f"Saving flowsheet with {len(data.nodes)} nodes and {len(data.streams or [])} streams")

        # First load the flowsheet data into the solver
        load_result = await load_flowsheet(data)
        print(f"Load result: {load_result}")

        # Then save using the solver's serialization method
        file_path = FLOWsheet_STORAGE_DIR / f"{filename}.json"
        flowsheet_solver.save_to_file(str(file_path))
        print(f"Flowsheet saved to {file_path}")

        return SimulationResult(
            success=True,
            message=f"Flowsheet saved as {filename}.json"
        )

    except Exception as e:
        print(f"Error in save_flowsheet: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to save flowsheet: {str(e)}")

@app.get("/api/flowsheet/load/{filename}")
async def load_saved_flowsheet(filename: str):
    """Load a flowsheet from storage using flowsheet solver deserialization"""
    try:
        if flowsheet_solver is None:
            raise HTTPException(status_code=500, detail="Flowsheet solver not initialized")

        file_path = FLOWsheet_STORAGE_DIR / f"{filename}.json"

        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"Flowsheet {filename} not found")

        # Load flowsheet using solver's deserialization
        loaded_solver = FlowsheetSolver.load_from_file(str(file_path))

        # Convert to UI-compatible format
        ui_data = {
            "nodes": [
                {
                    "id": unit.id,
                    "type": unit.__class__.__name__.lower(),  # Convert to lowercase for UI
                    "position": {"x": 100 + i * 200, "y": 100},  # Default positions
                    "data": {
                        "unitType": unit.__class__.__name__,
                        "name": unit.name,
                        **unit.parameters
                    }
                }
                for i, unit in enumerate(loaded_solver.unit_operations.values())
            ],
            "edges": getattr(loaded_solver, 'edges', []),
            "streams": [
                {
                    "id": stream.id,
                    "name": stream.name,
                    "temperature": stream.temperature,
                    "pressure": stream.pressure,
                    "mass_flow_rate": stream.mass_flow_rate,
                    "composition": stream.composition,
                    # Include calculated transport properties
                    "viscosity": stream.property_package.calculate_viscosity(stream.temperature, stream.pressure, stream.phase) if stream.property_package else None,
                    "thermal_conductivity": stream.property_package.calculate_thermal_conductivity(stream.temperature, stream.pressure, stream.phase) if stream.property_package else None
                }
                for stream in loaded_solver.streams.values()
            ]
        }

        return ui_data

    except Exception as e:
        print(f"Error in load_saved_flowsheet: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to load flowsheet: {str(e)}")

@app.get("/api/flowsheet/list")
async def list_saved_flowsheets():
    """List all saved flowsheets"""
    try:
        files = [f.stem for f in FLOWsheet_STORAGE_DIR.glob("*.json")]
        return {"flowsheets": files}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list flowsheets: {str(e)}")

@app.post("/api/flowsheet/add-object", response_model=SimulationResult)
async def add_object_to_flowsheet(data: Dict[str, Any]):
    """Add a unit operation or stream to the flowsheet"""
    try:
        if flowsheet_solver is None:
            raise HTTPException(status_code=500, detail="Flowsheet solver not initialized")

        object_type = data.get('type')
        object_id = data.get('id')
        object_data = data.get('data', {})

        if object_type == 'unit_operation':
            # Create unit operation
            unit_type = object_data.get('unitType', '').lower()
            unit_op = UnitOperationFactory.create_unit_operation(
                unit_type,
                object_id,
                object_data
            )
            flowsheet_solver.add_unit_operation(unit_op)

        elif object_type == 'stream':
            # Create stream
            stream_type = object_data.get('unitType', '')
            if stream_type == 'material_stream':
                stream = MaterialStream(object_id, object_data.get('name', object_id))
            elif stream_type == 'energy_stream':
                stream = EnergyStream(object_id, object_data.get('name', object_id))
                # Set energy-specific properties
                if 'energy_flow' in object_data:
                    stream.energy_flow = object_data['energy_flow']
                if 'temperature_low' in object_data:
                    stream.temperature_low = object_data['temperature_low']
                if 'temperature_high' in object_data:
                    stream.temperature_high = object_data['temperature_high']
            else:
                raise HTTPException(status_code=400, detail=f"Unknown stream type: {stream_type}")

            # Set common properties for material streams
            if stream_type == 'material_stream':
                # Set default properties
                stream.temperature = object_data.get('temperature', 298.15)
                stream.pressure = object_data.get('pressure', 101325)
                stream.mass_flow_rate = object_data.get('mass_flow_rate', 0.0)
                stream.composition = object_data.get('composition', {})
                stream.property_package = property_package

            flowsheet_solver.add_stream(stream)

        else:
            raise HTTPException(status_code=400, detail=f"Unknown object type: {object_type}")

        return SimulationResult(
            success=True,
            message=f"{object_type} added successfully",
            results={"object_id": object_id, "object_type": object_type}
        )

    except Exception as e:
        print(f"Error adding object: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Failed to add object: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)