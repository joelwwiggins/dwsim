"""
DWSIM Python Property Package Interfaces
Copyright 2024 Daniel Wagner O. de Medeiros

This file is part of DWSIM.

DWSIM is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

DWSIM is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with DWSIM.  If not, see <http://www.gnu.org/licenses/>.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import timedelta

from .enums import FlashCalculationType, FlashMethod, PhaseLabel, PhaseName


@dataclass
class FlashCalculationResult:
    """Result of a flash calculation."""

    base_mole_amount: float
    kvalues: List[float]
    mixture_mole_amounts: List[float]
    vapor_phase_mole_amounts: List[float]
    liquid_phase1_mole_amounts: List[float]
    liquid_phase2_mole_amounts: List[float]
    solid_phase_mole_amounts: List[float]
    calculated_temperature: Optional[float] = None
    calculated_pressure: Optional[float] = None
    calculated_enthalpy: Optional[float] = None
    calculated_entropy: Optional[float] = None
    compound_properties: List[Any] = None  # List of ICompoundConstantProperties
    flash_algorithm_type: str = ""
    result_exception: Optional[Exception] = None
    iterations_taken: int = 0
    time_taken: timedelta = timedelta()

    def get_vapor_phase_mole_fractions(self) -> List[float]:
        """Get vapor phase mole fractions."""
        total = sum(self.vapor_phase_mole_amounts)
        if total == 0:
            return [0.0] * len(self.vapor_phase_mole_amounts)
        return [x / total for x in self.vapor_phase_mole_amounts]

    def get_liquid_phase1_mole_fractions(self) -> List[float]:
        """Get liquid phase 1 mole fractions."""
        total = sum(self.liquid_phase1_mole_amounts)
        if total == 0:
            return [0.0] * len(self.liquid_phase1_mole_amounts)
        return [x / total for x in self.liquid_phase1_mole_amounts]

    def get_liquid_phase2_mole_fractions(self) -> List[float]:
        """Get liquid phase 2 mole fractions."""
        total = sum(self.liquid_phase2_mole_amounts)
        if total == 0:
            return [0.0] * len(self.liquid_phase2_mole_amounts)
        return [x / total for x in self.liquid_phase2_mole_amounts]

    def get_solid_phase_mole_fractions(self) -> List[float]:
        """Get solid phase mole fractions."""
        total = sum(self.solid_phase_mole_amounts)
        if total == 0:
            return [0.0] * len(self.solid_phase_mole_amounts)
        return [x / total for x in self.solid_phase_mole_amounts]

    def get_vapor_phase_mole_fraction(self) -> float:
        """Get vapor phase mole fraction."""
        return sum(self.vapor_phase_mole_amounts) / self.base_mole_amount

    def get_liquid_phase1_mole_fraction(self) -> float:
        """Get liquid phase 1 mole fraction."""
        return sum(self.liquid_phase1_mole_amounts) / self.base_mole_amount

    def get_liquid_phase2_mole_fraction(self) -> float:
        """Get liquid phase 2 mole fraction."""
        return sum(self.liquid_phase2_mole_amounts) / self.base_mole_amount

    def get_solid_phase_mole_fraction(self) -> float:
        """Get solid phase mole fraction."""
        return sum(self.solid_phase_mole_amounts) / self.base_mole_amount

    def get_vapor_phase_mass_fractions(self) -> List[float]:
        """Get vapor phase mass fractions."""
        # This would require molecular weights - simplified for now
        return self.get_vapor_phase_mole_fractions()

    def get_liquid_phase1_mass_fractions(self) -> List[float]:
        """Get liquid phase 1 mass fractions."""
        return self.get_liquid_phase1_mole_fractions()

    def get_liquid_phase2_mass_fractions(self) -> List[float]:
        """Get liquid phase 2 mass fractions."""
        return self.get_liquid_phase2_mole_fractions()

    def get_solid_phase_mass_fractions(self) -> List[float]:
        """Get solid phase mass fractions."""
        return self.get_solid_phase_mole_fractions()

    def convert_to_mass_fractions(self, vz: List[float]) -> List[float]:
        """Convert mole fractions to mass fractions."""
        # Simplified - would need molecular weights
        return vz.copy()

    def calc_molar_weight(self, vz: List[float]) -> float:
        """Calculate molar weight from mole fractions."""
        # Simplified - would need molecular weights
        return 1.0

    def get_vapor_phase_mass_fraction(self) -> float:
        """Get vapor phase mass fraction."""
        return self.get_vapor_phase_mole_fraction()

    def get_liquid_phase1_mass_fraction(self) -> float:
        """Get liquid phase 1 mass fraction."""
        return self.get_liquid_phase1_mole_fraction()

    def get_liquid_phase2_mass_fraction(self) -> float:
        """Get liquid phase 2 mass fraction."""
        return self.get_liquid_phase2_mole_fraction()

    def get_solid_phase_mass_fraction(self) -> float:
        """Get solid phase mass fraction."""
        return self.get_solid_phase_mole_fraction()


class IFlashAlgorithm(ABC):
    """Interface for flash algorithms."""

    @property
    @abstractmethod
    def flash_settings(self) -> Dict[int, str]:
        """Flash algorithm settings."""
        pass

    @flash_settings.setter
    @abstractmethod
    def flash_settings(self, value: Dict[int, str]):
        """Set flash algorithm settings."""
        pass

    @abstractmethod
    def clone(self) -> 'IFlashAlgorithm':
        """Clone the flash algorithm."""
        pass

    @abstractmethod
    def get_new_instance(self) -> 'IFlashAlgorithm':
        """Get a new instance of the flash algorithm."""
        pass

    @property
    @abstractmethod
    def algo_type(self) -> FlashMethod:
        """Algorithm type."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Algorithm name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Algorithm description."""
        pass

    @property
    @abstractmethod
    def tag(self) -> str:
        """Algorithm tag."""
        pass

    @tag.setter
    @abstractmethod
    def tag(self, value: str):
        """Set algorithm tag."""
        pass

    @property
    @abstractmethod
    def internal_use_only(self) -> bool:
        """Whether algorithm is for internal use only."""
        pass

    @property
    @abstractmethod
    def mobile_compatible(self) -> bool:
        """Whether algorithm is mobile compatible."""
        pass

    @property
    @abstractmethod
    def order(self) -> int:
        """Algorithm order."""
        pass

    @order.setter
    @abstractmethod
    def order(self, value: int):
        """Set algorithm order."""
        pass


class IPropertyPackage(ABC):
    """Interface for property packages."""

    @property
    @abstractmethod
    def unique_id(self) -> str:
        """Unique identifier."""
        pass

    @unique_id.setter
    @abstractmethod
    def unique_id(self, value: str):
        """Set unique identifier."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Property package name."""
        pass

    @property
    @abstractmethod
    def tag(self) -> str:
        """Property package tag."""
        pass

    @tag.setter
    @abstractmethod
    def tag(self, value: str):
        """Set property package tag."""
        pass

    @property
    @abstractmethod
    def flash_algorithm(self) -> IFlashAlgorithm:
        """Flash algorithm."""
        pass

    @flash_algorithm.setter
    @abstractmethod
    def flash_algorithm(self, value: IFlashAlgorithm):
        """Set flash algorithm."""
        pass

    @property
    @abstractmethod
    def current_material_stream(self) -> Any:  # IMaterialStream
        """Current material stream."""
        pass

    @current_material_stream.setter
    @abstractmethod
    def current_material_stream(self, value: Any):
        """Set current material stream."""
        pass

    @abstractmethod
    def calculate_equilibrium(self, calctype: FlashCalculationType,
                            val1: float, val2: float,
                            mixmolefrac: List[float],
                            initial_kval: List[float],
                            initial_estimate: float) -> FlashCalculationResult:
        """Calculate equilibrium."""
        pass

    @abstractmethod
    def calculate_equilibrium2(self, calctype: FlashCalculationType,
                             val1: float, val2: float,
                             initial_estimate: float) -> FlashCalculationResult:
        """Calculate equilibrium (alternative method)."""
        pass

    @abstractmethod
    def aux_delgig_rt(self, p1: float, t: float, id_list: List[str],
                     stcoef: List[float], bcidx: int, mode2: bool = False) -> float:
        """Calculate excess Gibbs energy."""
        pass

    @abstractmethod
    def aux_cpm(self, phase: PhaseLabel, ti: float) -> float:
        """Calculate heat capacity."""
        pass

    @abstractmethod
    def aux_mmm(self, phase: PhaseLabel) -> float:
        """Calculate molar mass."""
        pass

    @abstractmethod
    def aux_z(self, vx: List[float], t: float, p: float, state: PhaseName) -> float:
        """Calculate compressibility factor."""
        pass

    @abstractmethod
    def clone(self) -> 'IPropertyPackage':
        """Clone the property package."""
        pass

    @property
    @abstractmethod
    def flowsheet(self) -> Any:  # IFlowsheet
        """Flowsheet."""
        pass

    @flowsheet.setter
    @abstractmethod
    def flowsheet(self, value: Any):
        """Set flowsheet."""
        pass

    @abstractmethod
    def display_editing_form(self):
        """Display editing form."""
        pass

    @abstractmethod
    def display_advanced_editing_form(self) -> Any:
        """Display advanced editing form."""
        pass

    @abstractmethod
    def calc_additional_phase_properties(self):
        """Calculate additional phase properties."""
        pass

    @property
    @abstractmethod
    def mobile_compatible(self) -> bool:
        """Whether property package is mobile compatible."""
        pass

    @property
    @abstractmethod
    def is_functional(self) -> bool:
        """Whether property package is functional."""
        pass

    @property
    @abstractmethod
    def should_use_kvalue_method2(self) -> bool:
        """Whether to use K-value method 2."""
        pass

    @abstractmethod
    def return_instance(self, typename: str) -> Any:
        """Return instance of specified type."""
        pass

    @abstractmethod
    def display_grouped_editing_form(self):
        """Display grouped editing form."""
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Display name."""
        pass

    @property
    @abstractmethod
    def display_description(self) -> str:
        """Display description."""
        pass

    @property
    @abstractmethod
    def has_reactive_phase(self) -> bool:
        """Whether property package has reactive phase."""
        pass

    @property
    @abstractmethod
    def should_use_kvalue_method3(self) -> bool:
        """Whether to use K-value method 3."""
        pass

    @abstractmethod
    def get_as_object(self) -> Any:
        """Get as object."""
        pass


class IPropertyPackageMethods(ABC):
    """Interface for property package methods."""

    @property
    @abstractmethod
    def vapor_fugacity(self) -> str:
        """Vapor fugacity method."""
        pass

    @vapor_fugacity.setter
    @abstractmethod
    def vapor_fugacity(self, value: str):
        """Set vapor fugacity method."""
        pass

    @property
    @abstractmethod
    def vapor_enthalpy_entropy_cp_cv(self) -> str:
        """Vapor enthalpy/entropy/Cp/Cv method."""
        pass

    @vapor_enthalpy_entropy_cp_cv.setter
    @abstractmethod
    def vapor_enthalpy_entropy_cp_cv(self, value: str):
        """Set vapor enthalpy/entropy/Cp/Cv method."""
        pass

    @property
    @abstractmethod
    def vapor_thermal_conductivity(self) -> str:
        """Vapor thermal conductivity method."""
        pass

    @vapor_thermal_conductivity.setter
    @abstractmethod
    def vapor_thermal_conductivity(self, value: str):
        """Set vapor thermal conductivity method."""
        pass

    @property
    @abstractmethod
    def vapor_viscosity(self) -> str:
        """Vapor viscosity method."""
        pass

    @vapor_viscosity.setter
    @abstractmethod
    def vapor_viscosity(self, value: str):
        """Set vapor viscosity method."""
        pass

    @property
    @abstractmethod
    def vapor_density(self) -> str:
        """Vapor density method."""
        pass

    @vapor_density.setter
    @abstractmethod
    def vapor_density(self, value: str):
        """Set vapor density method."""
        pass

    @property
    @abstractmethod
    def liquid_fugacity(self) -> str:
        """Liquid fugacity method."""
        pass

    @liquid_fugacity.setter
    @abstractmethod
    def liquid_fugacity(self, value: str):
        """Set liquid fugacity method."""
        pass

    @property
    @abstractmethod
    def liquid_enthalpy_entropy_cp_cv(self) -> str:
        """Liquid enthalpy/entropy/Cp/Cv method."""
        pass

    @liquid_enthalpy_entropy_cp_cv.setter
    @abstractmethod
    def liquid_enthalpy_entropy_cp_cv(self, value: str):
        """Set liquid enthalpy/entropy/Cp/Cv method."""
        pass

    @property
    @abstractmethod
    def liquid_thermal_conductivity(self) -> str:
        """Liquid thermal conductivity method."""
        pass

    @liquid_thermal_conductivity.setter
    @abstractmethod
    def liquid_thermal_conductivity(self, value: str):
        """Set liquid thermal conductivity method."""
        pass

    @property
    @abstractmethod
    def liquid_viscosity(self) -> str:
        """Liquid viscosity method."""
        pass

    @liquid_viscosity.setter
    @abstractmethod
    def liquid_viscosity(self, value: str):
        """Set liquid viscosity method."""
        pass

    @property
    @abstractmethod
    def liquid_density(self) -> str:
        """Liquid density method."""
        pass

    @liquid_density.setter
    @abstractmethod
    def liquid_density(self, value: str):
        """Set liquid density method."""
        pass

    @property
    @abstractmethod
    def surface_tension(self) -> str:
        """Surface tension method."""
        pass

    @surface_tension.setter
    @abstractmethod
    def surface_tension(self, value: str):
        """Set surface tension method."""
        pass

    @property
    @abstractmethod
    def solid_density(self) -> str:
        """Solid density method."""
        pass

    @solid_density.setter
    @abstractmethod
    def solid_density(self, value: str):
        """Set solid density method."""
        pass

    @property
    @abstractmethod
    def solid_enthalpy_entropy_cp_cv(self) -> str:
        """Solid enthalpy/entropy/Cp/Cv method."""
        pass

    @solid_enthalpy_entropy_cp_cv.setter
    @abstractmethod
    def solid_enthalpy_entropy_cp_cv(self, value: str):
        """Set solid enthalpy/entropy/Cp/Cv method."""
        pass