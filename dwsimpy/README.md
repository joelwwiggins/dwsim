# DWSIMpy

DWSIMpy is the Python version of DWSIM, a comprehensive, open-source chemical process simulator. This conversion brings DWSIM's powerful simulation capabilities to Python, enabling easier integration with scientific computing workflows.

## Features

- **Thermodynamic Calculations**: Peng-Robinson and Ideal property packages with flash calculations.
- **Unit Operations**: Mixer, Heater, Valve, Pump, Splitter, and more.
- **Flowsheet Solver**: Sequential modular solver with convergence acceleration.
- **Web UI**: Interactive flowsheet builder using Streamlit.
- **Extensible**: Modular design for adding new components.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/joelwwiggins/dwsim.git
   cd dwsim/dwsimpy
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv ../dwsimpy_env
   source ../dwsimpy_env/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

## Usage

### Command Line
```python
from dwsimpy.solvers.flowsheet_solver import FlowsheetSolver
from dwsimpy.unit_ops.mixer import Mixer
from dwsimpy.streams.material_stream import MaterialStream

# Create flowsheet
solver = FlowsheetSolver()

# Add streams and units
stream1 = MaterialStream()
stream1.mass_flow = 10.0
solver.add_stream("inlet1", stream1)

mixer = Mixer()
solver.add_unit_operation(mixer)

# Solve
success = solver.solve()
```

### Web UI
```bash
streamlit run ui/app.py
```

Navigate to http://localhost:8502 to build and solve flowsheets interactively.

## Testing

Run the test suite:
```bash
pytest
```

## Architecture

- `interfaces/`: Abstract base classes and enums.
- `shared_classes/`: Base simulation object class.
- `property_packages/`: Thermodynamic models.
- `unit_ops/`: Process unit operations.
- `solvers/`: Numerical and flowsheet solvers.
- `streams/`: Material and energy streams.
- `thermo/`: Activity coefficient models.
- `ui/`: Web interface.

## Contributing

Contributions are welcome! Please follow the existing code style and add tests for new features.

## License

GNU General Public License v3.0

## Acknowledgments

Based on the original DWSIM by Daniel Wagner O. de Medeiros.