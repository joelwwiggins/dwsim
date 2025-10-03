"""
Wilson Property Package Implementation
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

import uuid
from typing import List, Dict, Any, Optional
from datetime import timedelta

from dwsimpy.interfaces import (
    IPropertyPackage, IPropertyPackageMethods, IFlashAlgorithm,
    FlashCalculationResult, FlashCalculationType, FlashMethod,
    PhaseLabel, PhaseName, FlashSetting
)
from dwsimpy.thermo import wilson_model


class BasicFlashAlgorithm(IFlashAlgorithm):
    """Basic flash algorithm implementation."""

    def __init__(self):
        self._flash_settings: Dict[int, str] = {}
        self._tag = "Basic"
        self._order = 0

    @property
    def flash_settings(self) -> Dict[int, str]:
        return self._flash_settings

    @flash_settings.setter
    def flash_settings(self, value: Dict[int, str]):
        self._flash_settings = value

    def clone(self) -> 'IFlashAlgorithm':
        new_alg = BasicFlashAlgorithm()
        new_alg._flash_settings = self._flash_settings.copy()
        new_alg._tag = self._tag
        new_alg._order = self._order
        return new_alg

    def get_new_instance(self) -> 'IFlashAlgorithm':
        return BasicFlashAlgorithm()

    @property
    def algo_type(self) -> FlashMethod:
        return FlashMethod.NESTED_LOOPS_VLE

    @property
    def name(self) -> str:
        return "Basic Nested Loops VLE"

    @property
    def description(self) -> str:
        return "Basic nested loops VLE flash algorithm"

    @property
    def tag(self) -> str:
        return self._tag

    @tag.setter
    def tag(self, value: str):
        self._tag = value

    @property
    def internal_use_only(self) -> bool:
        return False

    @property
    def mobile_compatible(self) -> bool:
        return True

    @property
    def order(self) -> int:
        return self._order

    @order.setter
    def order(self, value: int):
        self._order = value


class WilsonPropertyPackage(IPropertyPackage, IPropertyPackageMethods):
    """Wilson property package implementation."""

    def __init__(self):
        self._unique_id = str(uuid.uuid4())
        self._name = "Wilson"
        self._tag = "Wilson"
        self._flash_algorithm = BasicFlashAlgorithm()
        self._current_material_stream = None
        self._flowsheet = None

        # Property package methods
        self._vapor_fugacity = "Wilson"
        self._vapor_enthalpy_entropy_cp_cv = "Ideal Gas"
        self._vapor_thermal_conductivity = "Ideal Gas"
        self._vapor_viscosity = "Ideal Gas"
        self._vapor_density = "Ideal Gas"
        self._liquid_fugacity = "Wilson"
        self._liquid_enthalpy_entropy_cp_cv = "Wilson"
        self._liquid_thermal_conductivity = "Liquid"
        self._liquid_viscosity = "Liquid"
        self._liquid_density = "Liquid"
        self._surface_tension = "Liquid"
        self._solid_density = "Solid"
        self._solid_enthalpy_entropy_cp_cv = "Solid"

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @unique_id.setter
    def unique_id(self, value: str):
        self._unique_id = value

    @property
    def name(self) -> str:
        return self._name

    @property
    def tag(self) -> str:
        return self._tag

    @tag.setter
    def tag(self, value: str):
        self._tag = value

    @property
    def flash_algorithm(self) -> IFlashAlgorithm:
        return self._flash_algorithm

    @flash_algorithm.setter
    def flash_algorithm(self, value: IFlashAlgorithm):
        self._flash_algorithm = value

    @property
    def current_material_stream(self) -> Any:
        return self._current_material_stream

    @current_material_stream.setter
    def current_material_stream(self, value: Any):
        self._current_material_stream = value

    def calculate_equilibrium(self, calctype: FlashCalculationType,
                            val1: float, val2: float,
                            mixmolefrac: List[float],
                            initial_kval: List[float],
                            initial_estimate: float) -> FlashCalculationResult:
        """Calculate equilibrium using Wilson model."""
        # Simplified implementation - would need full flash algorithm
        # For now, return a basic result
        n_comp = len(mixmolefrac)

        result = FlashCalculationResult(
            base_mole_amount=1.0,
            kvalues=initial_kval if initial_kval else [1.0] * n_comp,
            mixture_mole_amounts=mixmolefrac.copy(),
            vapor_phase_mole_amounts=[0.0] * n_comp,
            liquid_phase1_mole_amounts=mixmolefrac.copy(),
            liquid_phase2_mole_amounts=[0.0] * n_comp,
            solid_phase_mole_amounts=[0.0] * n_comp,
            calculated_temperature=val1 if calctype == FlashCalculationType.PRESSURE_TEMPERATURE else None,
            calculated_pressure=val2 if calctype == FlashCalculationType.PRESSURE_TEMPERATURE else None,
            flash_algorithm_type=self.flash_algorithm.name,
            iterations_taken=1,
            time_taken=timedelta(milliseconds=1)
        )

        return result

    def calculate_equilibrium2(self, calctype: FlashCalculationType,
                             val1: float, val2: float,
                             initial_estimate: float) -> FlashCalculationResult:
        """Calculate equilibrium (alternative method)."""
        # Simplified implementation
        return self.calculate_equilibrium(calctype, val1, val2, [], [], initial_estimate)

    def aux_delgig_rt(self, p1: float, t: float, id_list: List[str],
                     stcoef: List[float], bcidx: int, mode2: bool = False) -> float:
        """Calculate excess Gibbs energy using Wilson model."""
        # This would use the Wilson model implementation
        # For now, return 0
        return 0.0

    def aux_cpm(self, phase: PhaseLabel, ti: float) -> float:
        """Calculate heat capacity."""
        # Simplified implementation
        return 36.0  # J/mol.K, typical value

    def aux_mmm(self, phase: PhaseLabel) -> float:
        """Calculate molar mass."""
        # Simplified implementation
        return 18.0  # g/mol, water

    def aux_z(self, vx: List[float], t: float, p: float, state: PhaseName) -> float:
        """Calculate compressibility factor."""
        # Simplified implementation
        if state == PhaseName.VAPOR:
            return 1.0  # Ideal gas
        else:
            return 0.1  # Typical liquid value

    def clone(self) -> 'IPropertyPackage':
        """Clone the property package."""
        new_pp = WilsonPropertyPackage()
        new_pp._unique_id = str(uuid.uuid4())
        new_pp._tag = self._tag + "_clone"
        new_pp._flash_algorithm = self._flash_algorithm.clone()
        return new_pp

    @property
    def flowsheet(self) -> Any:
        return self._flowsheet

    @flowsheet.setter
    def flowsheet(self, value: Any):
        self._flowsheet = value

    def display_editing_form(self):
        """Display editing form."""
        # GUI implementation would go here
        pass

    def display_advanced_editing_form(self) -> Any:
        """Display advanced editing form."""
        # GUI implementation would go here
        return None

    def calc_additional_phase_properties(self):
        """Calculate additional phase properties."""
        # Implementation would go here
        pass

    @property
    def mobile_compatible(self) -> bool:
        return True

    @property
    def is_functional(self) -> bool:
        return True

    @property
    def should_use_kvalue_method2(self) -> bool:
        return False

    def return_instance(self, typename: str) -> Any:
        """Return instance of specified type."""
        # Simplified implementation
        return None

    def display_grouped_editing_form(self):
        """Display grouped editing form."""
        # GUI implementation would go here
        pass

    @property
    def display_name(self) -> str:
        return "Wilson Property Package"

    @property
    def display_description(self) -> str:
        return "Property package using Wilson activity coefficient model"

    @property
    def has_reactive_phase(self) -> bool:
        return False

    @property
    def should_use_kvalue_method3(self) -> bool:
        return False

    def get_as_object(self) -> Any:
        """Get as object."""
        return self

    # IPropertyPackageMethods implementation

    @property
    def vapor_fugacity(self) -> str:
        return self._vapor_fugacity

    @vapor_fugacity.setter
    def vapor_fugacity(self, value: str):
        self._vapor_fugacity = value

    @property
    def vapor_enthalpy_entropy_cp_cv(self) -> str:
        return self._vapor_enthalpy_entropy_cp_cv

    @vapor_enthalpy_entropy_cp_cv.setter
    def vapor_enthalpy_entropy_cp_cv(self, value: str):
        self._vapor_enthalpy_entropy_cp_cv = value

    @property
    def vapor_thermal_conductivity(self) -> str:
        return self._vapor_thermal_conductivity

    @vapor_thermal_conductivity.setter
    def vapor_thermal_conductivity(self, value: str):
        self._vapor_thermal_conductivity = value

    @property
    def vapor_viscosity(self) -> str:
        return self._vapor_viscosity

    @vapor_viscosity.setter
    def vapor_viscosity(self, value: str):
        self._vapor_viscosity = value

    @property
    def vapor_density(self) -> str:
        return self._vapor_density

    @vapor_density.setter
    def vapor_density(self, value: str):
        self._vapor_density = value

    @property
    def liquid_fugacity(self) -> str:
        return self._liquid_fugacity

    @liquid_fugacity.setter
    def liquid_fugacity(self, value: str):
        self._liquid_fugacity = value

    @property
    def liquid_enthalpy_entropy_cp_cv(self) -> str:
        return self._liquid_enthalpy_entropy_cp_cv

    @liquid_enthalpy_entropy_cp_cv.setter
    def liquid_enthalpy_entropy_cp_cv(self, value: str):
        self._liquid_enthalpy_entropy_cp_cv = value

    @property
    def liquid_thermal_conductivity(self) -> str:
        return self._liquid_thermal_conductivity

    @liquid_thermal_conductivity.setter
    def liquid_thermal_conductivity(self, value: str):
        self._liquid_thermal_conductivity = value

    @property
    def liquid_viscosity(self) -> str:
        return self._liquid_viscosity

    @liquid_viscosity.setter
    def liquid_viscosity(self, value: str):
        self._liquid_viscosity = value

    @property
    def liquid_density(self) -> str:
        return self._liquid_density

    @liquid_density.setter
    def liquid_density(self, value: str):
        self._liquid_density = value

    @property
    def surface_tension(self) -> str:
        return self._surface_tension

    @surface_tension.setter
    def surface_tension(self, value: str):
        self._surface_tension = value

    @property
    def solid_density(self) -> str:
        return self._solid_density

    @solid_density.setter
    def solid_density(self, value: str):
        self._solid_density = value

    @property
    def solid_enthalpy_entropy_cp_cv(self) -> str:
        return self._solid_enthalpy_entropy_cp_cv

    @solid_enthalpy_entropy_cp_cv.setter
    def solid_enthalpy_entropy_cp_cv(self, value: str):
        self._solid_enthalpy_entropy_cp_cv = value