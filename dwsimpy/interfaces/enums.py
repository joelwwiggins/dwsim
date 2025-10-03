"""
DWSIM Python Interface definitions
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

from enum import Enum


class FlashCalculationType(Enum):
    """Enumeration for different types of flash calculations."""
    PRESSURE_TEMPERATURE = 0
    PRESSURE_ENTHALPY = 1
    PRESSURE_ENTROPY = 2
    TEMPERATURE_ENTHALPY = 3
    TEMPERATURE_ENTROPY = 4
    PRESSURE_VAPOR_FRACTION = 5
    TEMPERATURE_VAPOR_FRACTION = 6
    PRESSURE_SOLID_FRACTION = 7
    TEMPERATURE_SOLID_FRACTION = 8
    VOLUME_TEMPERATURE = 9
    VOLUME_PRESSURE = 10
    VOLUME_ENTHALPY = 11
    VOLUME_ENTROPY = 12


class FlashMethod(Enum):
    """Enumeration for different flash calculation methods."""
    DEFAULT_ALGORITHM = 0
    NESTED_LOOPS_VLE = 1
    NESTED_LOOPS_VLLE = 2
    NESTED_LOOPS_IMMISCIBLE_VLLE = 3
    INSIDE_OUT_VLE = 4
    INSIDE_OUT_VLLE = 5
    GIBBS_MINIMIZATION_VLE = 6
    GIBBS_MINIMIZATION_VLLE = 7
    SIMPLE_LLE = 8
    NESTED_LOOPS_SLE_EUTECTIC = 9
    NESTED_LOOPS_SLE_SOLID_SOLUTION = 10
    BLACK_OIL = 11
    ELECTROLYTE = 12
    SEA_WATER = 13
    SOUR_WATER = 14
    CAPE_OPEN_EQUILIBRIUM_SERVER = 15
    STEAM_TABLES = 16
    NESTED_LOOPS_SVLLE = 17
    COOLPROP_INCOMPRESSIBLES = 18
    COOLPROP_INCOMPRESSIBLE_MIXTURES = 19
    USER_DEFINED = 20
    GIBBS_MINIMIZATION_MULTIPHASE = 21
    UNIVERSAL = 22
    CUSTOM = 23


class PhaseName(Enum):
    """Enumeration for phase names."""
    LIQUID = "Liquid"
    VAPOR = "Vapor"
    MIXTURE = "Mixture"
    SOLID = "Solid"


class PhaseLabel(Enum):
    """Enumeration for phase labels."""
    MIXTURE = "Mixture"
    VAPOR = "Vapor"
    LIQUID_MIXTURE = "LiquidMixture"
    LIQUID1 = "Liquid1"
    LIQUID2 = "Liquid2"
    LIQUID3 = "Liquid3"
    AQUEOUS = "Aqueous"
    SOLID = "Solid"


class FlashSetting(Enum):
    """Enumeration for flash algorithm settings."""
    PTFLASH_EXTERNAL_LOOP_TOLERANCE = 0
    PTFLASH_INTERNAL_LOOP_TOLERANCE = 1
    PTFLASH_MAXIMUM_NUMBER_OF_EXTERNAL_ITERATIONS = 2
    PTFLASH_MAXIMUM_NUMBER_OF_INTERNAL_ITERATIONS = 3
    PHFLASH_INTERNAL_LOOP_TOLERANCE = 4
    PHFLASH_EXTERNAL_LOOP_TOLERANCE = 5
    PHFLASH_MAXIMUM_NUMBER_OF_INTERNAL_ITERATIONS = 6
    PHFLASH_MAXIMUM_NUMBER_OF_EXTERNAL_ITERATIONS = 7
    THREE_PHASE_FLASH_STAB_TEST_SEVERITY = 8
    THREE_PHASE_FLASH_STAB_TEST_COMP_IDS = 9
    CALCULATE_BUBBLE_AND_DEW_POINTS = 10
    VALIDATE_EQUILIBRIUM_CALC = 11
    VALIDATION_GIBBS_TOLERANCE = 12