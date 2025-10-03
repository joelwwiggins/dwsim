"""
Property Package Methods Configuration

Converted from VB.NET to Python.
This class holds default method names for various thermodynamic
property calculations.
"""

from typing import Protocol


class IPropertyPackageMethods(Protocol):
    """Interface for property package methods."""

    @property
    def vapor_fugacity(self) -> str: ...

    @property
    def vapor_enthalpy_entropy_cpcv(self) -> str: ...

    @property
    def vapor_thermal_conductivity(self) -> str: ...

    @property
    def vapor_viscosity(self) -> str: ...

    @property
    def vapor_density(self) -> str: ...

    @property
    def liquid_fugacity(self) -> str: ...

    @property
    def liquid_enthalpy_entropy_cpcv(self) -> str: ...

    @property
    def liquid_thermal_conductivity(self) -> str: ...

    @property
    def liquid_viscosity(self) -> str: ...

    @property
    def liquid_density(self) -> str: ...

    @property
    def surface_tension(self) -> str: ...

    @property
    def solid_density(self) -> str: ...

    @property
    def solid_enthalpy_entropy_cpcv(self) -> str: ...


class PropertyPackageMethods:
    """
    Holds default method names for thermodynamic property calculations.

    This is a configuration class specifying which calculation methods
    to use for various properties.
    """

    def __init__(self):
        self.vapor_fugacity: str = ""
        self.vapor_enthalpy_entropy_cpcv: str = ""
        self.vapor_thermal_conductivity: str = "Experimental / Ely-Hanley"
        self.vapor_viscosity: str = ("Experimental / Lucas / "
                                     "Jossi-Stiel-Thodos")
        self.vapor_density: str = ""
        self.liquid_fugacity: str = ""
        self.liquid_enthalpy_entropy_cpcv: str = ""
        self.liquid_thermal_conductivity: str = "Experimental / Latini"
        self.liquid_viscosity: str = "Experimental / Letsou-Stiel"
        self.liquid_density: str = "Experimental / Rackett / COSTALD"
        self.surface_tension: str = "Experimental / Brock-Bird"
        self.solid_density: str = "Experimental Data / User-Defined"
        self.solid_enthalpy_entropy_cpcv: str = ("Experimental Solid Cp / "
                                                 "From Liquid Phase Enthalpy + "
                                                 "Enthalpy of Fusion")

    # Property getters for interface compliance
    @property
    def vapor_fugacity_prop(self) -> str:
        return self.vapor_fugacity

    @property
    def vapor_enthalpy_entropy_cpcv_prop(self) -> str:
        return self.vapor_enthalpy_entropy_cpcv

    @property
    def vapor_thermal_conductivity_prop(self) -> str:
        return self.vapor_thermal_conductivity

    @property
    def vapor_viscosity_prop(self) -> str:
        return self.vapor_viscosity

    @property
    def vapor_density_prop(self) -> str:
        return self.vapor_density

    @property
    def liquid_fugacity_prop(self) -> str:
        return self.liquid_fugacity

    @property
    def liquid_enthalpy_entropy_cpcv_prop(self) -> str:
        return self.liquid_enthalpy_entropy_cpcv

    @property
    def liquid_thermal_conductivity_prop(self) -> str:
        return self.liquid_thermal_conductivity

    @property
    def liquid_viscosity_prop(self) -> str:
        return self.liquid_viscosity

    @property
    def liquid_density_prop(self) -> str:
        return self.liquid_density

    @property
    def surface_tension_prop(self) -> str:
        return self.surface_tension

    @property
    def solid_density_prop(self) -> str:
        return self.solid_density

    @property
    def solid_enthalpy_entropy_cpcv_prop(self) -> str:
        return self.solid_enthalpy_entropy_cpcv