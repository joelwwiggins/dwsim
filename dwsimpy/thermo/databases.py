"""
Thermodynamic Databases

Converted from DWSIM.Thermodynamics.Databases to Python.
Database interfaces for compound properties.
"""

import json
import os
from typing import Dict, List, Any, Optional
from ..shared_classes.base_class import BaseClass


class CompoundDatabase(BaseClass):
    """Base class for compound databases."""

    def __init__(self):
        super().__init__()
        self.compounds: Dict[str, Dict[str, Any]] = {}

    def load_database(self, filename: str):
        """Load database from file."""
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                self.compounds = json.load(f)

    def save_database(self, filename: str):
        """Save database to file."""
        with open(filename, 'w') as f:
            json.dump(self.compounds, f, indent=2)

    def get_compound(self, name: str) -> Optional[Dict[str, Any]]:
        """Get compound data by name."""
        return self.compounds.get(name)

    def add_compound(self, name: str, properties: Dict[str, Any]):
        """Add compound to database."""
        self.compounds[name] = properties

    def search_compounds(self, query: str) -> List[str]:
        """Search for compounds by name."""
        return [name for name in self.compounds.keys() if query.lower() in name.lower()]


class ChemSepDatabase(CompoundDatabase):
    """ChemSep database interface."""

    def __init__(self):
        super().__init__()
        # Load embedded ChemSep data
        self._load_embedded_data()

    def _load_embedded_data(self):
        """Load embedded ChemSep database."""
        # Placeholder - in real implementation, load from embedded JSON
        self.compounds = {
            "methane": {
                "formula": "CH4",
                "molecular_weight": 16.043,
                "critical_temperature": 190.56,
                "critical_pressure": 4599200,
                "acentric_factor": 0.0115,
                "cas_number": "74-82-8"
            },
            "ethane": {
                "formula": "C2H6",
                "molecular_weight": 30.07,
                "critical_temperature": 305.32,
                "critical_pressure": 4872000,
                "acentric_factor": 0.0995,
                "cas_number": "74-84-0"
            }
            # Add more compounds...
        }


class DWSIMDatabase(CompoundDatabase):
    """DWSIM compound database."""

    def __init__(self):
        super().__init__()
        self.filename = "dwsim_compounds.json"
        self.load_database(self.filename)