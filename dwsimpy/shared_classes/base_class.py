"""
Base Class for Simulation Objects

Converted from VB.NET to Python.
This module defines the base class for all simulation objects.
"""

from abc import ABC, abstractmethod
from typing import Any
import logging
import json
import xml.etree.ElementTree as ET
from ..interfaces.iflowsheet import IFlowsheet
from ..interfaces.igraphicobject import IGraphicObject


logger = logging.getLogger(__name__)


class BaseClass(ABC):
    """
    Abstract base class for simulation objects.

    All unit operations inherit from this class.
    """

    def __init__(self):
        self.class_id: str = ""
        self.flowsheet: IFlowsheet = None
        self._is_dirty: bool = True
        self._can_use_previous_results: bool = False
        self.dynamics_spec = None  # DynamicsSpecType
        self.dynamics_only: bool = False
        self.extra_properties = {}
        self.extra_properties_unit_types = {}
        self.extra_properties_descriptions = {}
        self.extra_properties_types = {}
        self.visible: bool = True
        self.override_calculation_routine: bool = False
        self.store_detailed_debug_report: bool = False
        self.detailed_debug_report: str = ""
        self.is_functional: bool = True
        self.component_description: str = ""
        self.component_name: str = ""
        self.graphic_object: IGraphicObject = None
        self.attached_utilities = []
        self.preferred_flash_algorithm_tag: str = ""
        self.calculated: bool = False
        self.debug_mode: bool = False
        self.debug_text: str = ""
        self.last_updated = None  # datetime
        self.error_message: str = ""
        self.annotation: str = ""
        self.is_adjust_attached: bool = False
        self.attached_adjust_id: str = ""
        self.adjust_var_type = None
        self.is_spec_attached: bool = False
        self.attached_spec_id: str = ""
        self.spec_var_type = None
        self.object_class = None
        self.supports_dynamic_mode: bool = False
        self.has_properties_for_dynamic_mode: bool = False
        self.launch_external_property_editor = None
        self.extra_properties_editor = None
        self.calculation_routine_override = None
        self.user_defined_chart_names = []
        self.create_chart_action = None
        self.fd = None  # DynamicsPropertyEditor
        self.ghg_emission_data = None

    @property
    def is_dirty(self) -> bool:
        return self._is_dirty

    @property
    def can_use_previous_results(self) -> bool:
        return self._can_use_previous_results

    def clone(self) -> 'BaseClass':
        """Clone the object."""
        new_obj = self.__class__()
        new_obj.class_id = self.class_id
        new_obj.flowsheet = self.flowsheet
        new_obj._is_dirty = self._is_dirty
        new_obj._can_use_previous_results = self._can_use_previous_results
        new_obj.dynamics_spec = self.dynamics_spec
        new_obj.dynamics_only = self.dynamics_only
        new_obj.extra_properties = self.extra_properties.copy()
        new_obj.extra_properties_unit_types = self.extra_properties_unit_types.copy()
        new_obj.extra_properties_descriptions = self.extra_properties_descriptions.copy()
        new_obj.extra_properties_types = self.extra_properties_types.copy()
        new_obj.visible = self.visible
        new_obj.override_calculation_routine = self.override_calculation_routine
        new_obj.store_detailed_debug_report = self.store_detailed_debug_report
        new_obj.detailed_debug_report = self.detailed_debug_report
        new_obj.is_functional = self.is_functional
        new_obj.component_description = self.component_description
        new_obj.component_name = self.component_name
        new_obj.graphic_object = self.graphic_object
        new_obj.attached_utilities = self.attached_utilities.copy()
        new_obj.preferred_flash_algorithm_tag = self.preferred_flash_algorithm_tag
        new_obj.calculated = self.calculated
        new_obj.debug_mode = self.debug_mode
        new_obj.debug_text = self.debug_text
        new_obj.last_updated = self.last_updated
        new_obj.error_message = self.error_message
        new_obj.annotation = self.annotation
        new_obj.is_adjust_attached = self.is_adjust_attached
        new_obj.attached_adjust_id = self.attached_adjust_id
        new_obj.adjust_var_type = self.adjust_var_type
        new_obj.is_spec_attached = self.is_spec_attached
        new_obj.attached_spec_id = self.attached_spec_id
        new_obj.spec_var_type = self.spec_var_type
        new_obj.object_class = self.object_class
        new_obj.supports_dynamic_mode = self.supports_dynamic_mode
        new_obj.has_properties_for_dynamic_mode = self.has_properties_for_dynamic_mode
        new_obj.launch_external_property_editor = self.launch_external_property_editor
        new_obj.extra_properties_editor = self.extra_properties_editor
        new_obj.calculation_routine_override = self.calculation_routine_override
        new_obj.user_defined_chart_names = self.user_defined_chart_names.copy()
        new_obj.create_chart_action = self.create_chart_action
        new_obj.fd = self.fd
        new_obj.ghg_emission_data = self.ghg_emission_data
        return new_obj

    def dispose(self):
        """Dispose resources."""
        pass

    def load_data(self, data: list) -> bool:
        """Load from XML data."""
        return True

    def save_data(self) -> list:
        """Save to XML data."""
        return []

    def add_extra_property(self, pname: str, pvalue: Any):
        """Add an extra property."""
        if pname not in self.extra_properties:
            self.extra_properties[pname] = pvalue
        else:
            raise ValueError("Property already exists")

    def remove_extra_property(self, pname: str):
        """Remove an extra property."""
        if pname in self.extra_properties:
            del self.extra_properties[pname]
        else:
            raise ValueError("Property doesn't exist")

    def set_extra_property_value(self, pname: str, pvalue: Any):
        """Set value of an extra property."""
        if pname in self.extra_properties:
            self.extra_properties[pname] = pvalue
        else:
            raise ValueError("Property doesn't exist")

    def get_extra_property_value(self, pname: str) -> Any:
        """Get value of an extra property."""
        if pname in self.extra_properties:
            return self.extra_properties[pname]
        else:
            raise ValueError("Property doesn't exist")

    def clear_extra_properties(self):
        """Clear extra properties."""
        to_remove = []
        for p in self.extra_properties:
            if p not in self.extra_properties_descriptions or p not in self.extra_properties_unit_types:
                to_remove.append(p)
        for p in to_remove:
            del self.extra_properties[p]

    def add_dynamic_property(self, pname: str, pdesc: str, pvalue: float, punittype, ptype: type):
        """Add a dynamic property."""
        if pname not in self.extra_properties:
            self.extra_properties[pname] = pvalue
        if pname not in self.extra_properties_descriptions:
            self.extra_properties_descriptions[pname] = pdesc
        if pname not in self.extra_properties_unit_types:
            self.extra_properties_unit_types[pname] = punittype
        if pname not in self.extra_properties_types:
            self.extra_properties_types[pname] = ptype

    def set_dynamic_property(self, id: str, value: Any) -> bool:
        """Set dynamic property value."""
        self.extra_properties[id] = value
        return True

    def get_dynamic_property(self, id: str) -> Any:
        """Get dynamic property value."""
        return self.extra_properties.get(id)

    def get_dynamic_property_unit_type(self, id: str):
        """Get unit type of dynamic property."""
        return self.extra_properties_unit_types.get(id)

    def remove_dynamic_property(self, pname: str):
        """Remove a dynamic property."""
        if pname in self.extra_properties:
            del self.extra_properties[pname]
        if pname in self.extra_properties_descriptions:
            del self.extra_properties_descriptions[pname]
        if pname in self.extra_properties_unit_types:
            del self.extra_properties_unit_types[pname]
        if pname in self.extra_properties_types:
            del self.extra_properties_types[pname]

    def is_dynamic_property(self, pname: str) -> bool:
        """Check if property is dynamic."""
        return pname in self.extra_properties_descriptions

    @abstractmethod
    def get_display_name(self) -> str:
        """Get display name."""
        pass

    @abstractmethod
    def get_display_description(self) -> str:
        """Get display description."""
        pass

    @abstractmethod
    def get_icon_bitmap(self) -> Any:
        """Get icon bitmap."""
        pass

    def get_icon_bitmap_bytes(self) -> bytes:
        """Get icon bitmap bytes."""
        return b""

    def solve(self):
        """Solve the object."""
        if self.override_calculation_routine:
            # calculation_routine_override()
            pass
        else:
            self.calculate()

        self.calculated = True

    def calculate(self):
        """Calculate the object."""
        raise NotImplementedError

    def de_calculate(self):
        """De-calculate the object."""
        pass

    def run_dynamic_model(self):
        """Run dynamic model."""
        raise NotImplementedError("This Unit Operation is not yet supported in Dynamic Mode.")

    def perform_post_calc_validation(self):
        """Perform post calculation validation."""
        pass

    def validate(self):
        """Validate the object."""
        pass

    def get_debug_report(self) -> str:
        """Get debug report."""
        return "Error - function not implemented"

    def append_debug_line(self, text: str):
        """Append debug line."""
        self.debug_text += text + "\n\n"

    def check_spec(self, val: float, onlypositive: bool, paramname: str):
        """Check spec value."""
        if not val or (onlypositive and val < 0):
            raise ValueError(f"Invalid spec value for {paramname}: {val}")

    @abstractmethod
    def display_edit_form(self):
        """Display edit form."""
        pass

    @abstractmethod
    def update_edit_form(self):
        """Update edit form."""
        pass

    def get_editing_form(self):
        """Get editing form."""
        return None

    def get_properties(self, proptype) -> list[str]:
        """Get properties."""
        proplist = []
        for p in self.extra_properties:
            if p in self.extra_properties_descriptions and p in self.extra_properties_unit_types:
                proplist.append(p)
        return proplist

    def get_property_unit(self, prop: str) -> str:
        """Get property unit."""
        if prop in self.extra_properties_unit_types:
            utype = self.extra_properties_unit_types[prop]
            # return su.get_current_units(utype)
            return "unit"
        return ""

    def get_property_value(self, prop: str) -> Any:
        """Get property value."""
        if prop in self.extra_properties:
            return self.extra_properties[prop]
        return None

    def set_property_value(self, prop: str, propval: Any) -> bool:
        """Set property value."""
        if prop in self.extra_properties:
            self.extra_properties[prop] = propval
            return True
        return False

    def get_default_properties(self) -> list[str]:
        """Get default properties."""
        return self.get_properties(None)

    def get_property_description(self, prop: str) -> str:
        """Get property description."""
        return "No description is available for this property."

    def get_report(self, su, ci, numberformat: str) -> str:
        """Get report."""
        return "No report is available for this object."

    def get_version(self):
        """Get version."""
        return "1.0.0"

    @abstractmethod
    def close_edit_form(self):
        """Close edit form."""
        pass

    def clone_xml(self):
        """Clone XML."""
        root = ET.Element("BaseClass")
        for key, value in self.__dict__.items():
            if isinstance(value, (str, int, float, bool)):
                ET.SubElement(root, key).text = str(value)
        return ET.tostring(root, encoding='unicode')

    def clone_json(self):
        """Clone JSON."""
        return json.dumps(self.__dict__, default=str)

    @property
    def mobile_compatible(self) -> bool:
        """Mobile compatible."""
        return False

    def get_chart_model_names(self) -> list[str]:
        """Get chart model names."""
        return []

    def get_structured_report(self) -> list:
        """Get structured report."""
        return []

    def create_dynamic_properties(self):
        """Create dynamic properties."""
        pass

    def display_extra_properties_edit_form(self):
        """Display extra properties edit form."""
        pass

    def update_extra_properties_edit_form(self):
        """Update extra properties edit form."""
        pass

    def get_energy_balance_residual(self) -> float:
        """Get energy balance residual."""
        return 0.0

    def get_mass_balance_residual(self) -> float:
        """Get mass balance residual."""
        return 0.0

    def get_power_generated_or_consumed(self) -> float:
        """Get power generated or consumed."""
        return 0.0

    def get_dynamic_residence_time(self) -> float:
        """Get dynamic residence time."""
        return float('nan')

    def get_dynamic_volume(self) -> float:
        """Get dynamic volume."""
        return float('nan')

    def get_dynamic_contents(self) -> float:
        """Get dynamic contents."""
        return float('nan')

    def get_as_object(self):
        """Get as object."""
        return self

    @property
    def product_name(self) -> str:
        """Product name."""
        return self.get_display_name()

    @property
    def product_description(self) -> str:
        """Product description."""
        return self.get_display_description()

    @property
    def product_author(self) -> str:
        """Product author."""
        return "Daniel Wagner O. de Medeiros"

    @property
    def product_contact_info(self) -> str:
        """Product contact info."""
        return "https://dwsim.inforside.com.br"

    @property
    def product_page(self) -> str:
        """Product page."""
        return "https://dwsim.inforside.com.br"

    @property
    def product_version(self) -> str:
        """Product version."""
        return self.get_version()

    @property
    def product_assembly(self) -> str:
        """Product assembly."""
        return "dwsimpy"

    @property
    def is_source(self) -> bool:
        """Is source."""
        return False

    @property
    def is_sink(self) -> bool:
        """Is sink."""
        return False

    def connect_feed_material_stream(self, stream, portnumber: int):
        """Connect feed material stream."""
        pass

    def connect_product_material_stream(self, stream, portnumber: int):
        """Connect product material stream."""
        pass

    def connect_feed_energy_stream(self, stream, portnumber: int):
        """Connect feed energy stream."""
        pass

    def connect_product_energy_stream(self, stream, portnumber: int):
        """Connect product energy stream."""
        pass

    def connect_energy_stream(self, stream):
        """Connect energy stream."""
        pass

    def get_connection_ports_list(self) -> list[str]:
        """Get connection ports list."""
        return []

    def get_connection_ports_info(self) -> list:
        """Get connection ports info."""
        return []

    def set_dirty_status(self, value: bool):
        """Set dirty status."""
        self._is_dirty = value
        self._can_use_previous_results = not value

    def set_can_use_previous_results(self, value: bool):
        """Set can use previous results."""
        self._can_use_previous_results = value

    def check_dirty_status(self):
        """Check dirty status."""
        self.set_dirty_status(True)
        self.set_can_use_previous_results(False)

    def set_property_package_instance(self, pp):
        """Set property package instance."""
        pass

    def clear_property_package_instance(self) -> bool:
        """Clear property package instance."""
        return False

    def get_energy_consumption(self) -> float:
        """Get energy consumption."""
        return 0.0

    def get_preferred_graphic_object_width(self) -> float:
        """Get preferred graphic object width."""
        return 40.0

    def get_preferred_graphic_object_height(self) -> float:
        """Get preferred graphic object height."""
        return 40.0

    def get_properties2(self) -> list[str]:
        """Get properties 2."""
        return self.get_properties(None)

    def get_property_value2(self, propname: str, arg1: str, units: str):
        """Get property value 2."""
        value = self.get_property_value(propname)
        if isinstance(value, (int, float)):
            # convert from SI
            return value
        return value

    def set_property_value2(self, propname: str, arg1: str, units: str, value):
        """Set property value 2."""
        if isinstance(value, (int, float)):
            # convert to SI
            pass
        self.set_property_value(propname, value)

    def __str__(self):
        if self.graphic_object:
            return self.graphic_object.tag
        return super().__str__()