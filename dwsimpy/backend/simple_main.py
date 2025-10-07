from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import sys
import os
import json
from pathlib import Path

app = FastAPI(title="DWSIM Python API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://172.17.0.3:5173", "http://172.17.0.3:5174", "http://localhost:3000"],
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
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    streams: Optional[List[Dict[str, Any]]] = None

class SimulationResult(BaseModel):
    success: bool
    message: str
    results: Optional[Dict[str, Any]] = None

# Simple flowsheet simulation without complex imports
class SimpleFlowsheetSolver:
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.streams = []
        
    def load_flowsheet(self, nodes, edges, streams=None):
        self.nodes = nodes
        self.edges = edges
        self.streams = streams or []
        
    def solve(self):
        # Simple mass and energy balance calculation
        results = {}
        
        # Process each node based on type
        for node in self.nodes:
            node_type = node['data'].get('unitType', '').lower()
            node_id = node['id']
            
            if node_type == 'mixer':
                # Simple mixing calculation
                total_mass_flow = 0
                weighted_temp = 0
                min_pressure = float('inf')
                
                # Find input streams
                input_edges = [e for e in self.edges if e['target'] == node_id]
                for edge in input_edges:
                    # Get stream properties (use defaults if not provided)
                    stream_data = next((s for s in self.streams if s['id'] == edge['id']), {})
                    mass_flow = stream_data.get('mass_flow_rate', 10.0)
                    temp = stream_data.get('temperature', 298.15)
                    pressure = stream_data.get('pressure', 101325.0)
                    
                    total_mass_flow += mass_flow
                    weighted_temp += mass_flow * temp
                    min_pressure = min(min_pressure, pressure)
                
                if total_mass_flow > 0:
                    avg_temp = weighted_temp / total_mass_flow
                else:
                    avg_temp = 298.15
                    
                results[node_id] = {
                    'type': 'mixer',
                    'mass_flow_out': total_mass_flow,
                    'temperature_out': avg_temp,
                    'pressure_out': min_pressure if min_pressure != float('inf') else 101325.0
                }
                
            elif node_type == 'heater':
                # Simple heating calculation
                heat_duty = node['data'].get('heat_duty', 10.0)  # kW
                
                # Find input stream
                input_edges = [e for e in self.edges if e['target'] == node_id]
                if input_edges:
                    edge = input_edges[0]
                    stream_data = next((s for s in self.streams if s['id'] == edge['id']), {})
                    mass_flow = stream_data.get('mass_flow_rate', 10.0)
                    temp_in = stream_data.get('temperature', 298.15)
                    pressure = stream_data.get('pressure', 101325.0)
                    
                    # Simple heat balance (assuming water properties)
                    cp = 4.18  # kJ/kg·K
                    temp_rise = heat_duty * 3600 / (mass_flow * cp)  # Convert kW to kJ/h
                    temp_out = temp_in + temp_rise
                    
                    results[node_id] = {
                        'type': 'heater',
                        'mass_flow_out': mass_flow,
                        'temperature_in': temp_in,
                        'temperature_out': temp_out,
                        'pressure_out': pressure,
                        'heat_duty': heat_duty
                    }
        
        return results

# Global solver instance
flowsheet_solver = SimpleFlowsheetSolver()

@app.post("/api/flowsheet/load", response_model=SimulationResult)
async def load_flowsheet(data: FlowsheetData):
    """Load a flowsheet from the UI"""
    try:
        print(f"Loading flowsheet with {len(data.nodes)} nodes and {len(data.edges)} edges")
        flowsheet_solver.load_flowsheet(data.nodes, data.edges, data.streams)
        
        return SimulationResult(
            success=True,
            message="Flowsheet loaded successfully",
            results={"unit_count": len(data.nodes), "stream_count": len(data.edges)}
        )
        
    except Exception as e:
        print(f"Error in load_flowsheet: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to load flowsheet: {str(e)}")

@app.post("/api/simulation/run", response_model=SimulationResult)
async def run_simulation():
    """Run the flowsheet simulation"""
    try:
        results = flowsheet_solver.solve()
        
        return SimulationResult(
            success=True,
            message="Simulation completed successfully",
            results=results
        )
        
    except Exception as e:
        print(f"Error in simulation: {e}")
        return SimulationResult(
            success=False,
            message=f"Simulation failed: {str(e)}"
        )

@app.get("/api/unit-operations")
async def get_unit_operations():
    """Get available unit operation types"""
    return {
        "mixer": {"name": "Mixer", "description": "Mixes multiple input streams"},
        "heater": {"name": "Heater", "description": "Heats a stream by adding energy"},
        "cooler": {"name": "Cooler", "description": "Cools a stream by removing energy"},
        "valve": {"name": "Valve", "description": "Reduces pressure"},
        "pump": {"name": "Pump", "description": "Increases pressure"},
        "splitter": {"name": "Splitter", "description": "Splits one stream into multiple"}
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/api/simulation/status")
async def get_simulation_status():
    """Get current simulation status"""
    return {"status": "ready", "progress": 100}

if __name__ == "__main__":
    import uvicorn
    print("Starting DWSIMpy backend API...")
    print("API docs available at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)