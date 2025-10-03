"""
Unit tests for BaseClass.

Generated using pytest.
"""

import pytest
from dwsimpy.shared_classes.base_class import BaseClass


class ConcreteBaseClass(BaseClass):
    """Concrete implementation for testing."""

    def get_display_name(self) -> str:
        return "Test"

    def get_display_description(self) -> str:
        return "Test description"

    def get_icon_bitmap(self):
        return None

    def clone_xml(self):
        return self.__class__()

    def clone_json(self):
        return self.__class__()

    def display_edit_form(self):
        pass

    def update_edit_form(self):
        pass

    def close_edit_form(self):
        pass


class TestBaseClass:
    """Test cases for BaseClass."""

    def test_init(self):
        """Test initialization."""
        obj = ConcreteBaseClass()
        assert obj.class_id == ""
        assert obj.flowsheet is None
        assert obj._is_dirty is True
        assert obj._can_use_previous_results is False
        assert obj.visible is True
        assert obj.calculated is False

    def test_is_dirty_property(self):
        """Test is_dirty property."""
        obj = ConcreteBaseClass()
        assert obj.is_dirty is True
        obj._is_dirty = False
        assert obj.is_dirty is False

    def test_can_use_previous_results_property(self):
        """Test can_use_previous_results property."""
        obj = ConcreteBaseClass()
        assert obj.can_use_previous_results is False
        obj._can_use_previous_results = True
        assert obj.can_use_previous_results is True

    def test_clone(self):
        """Test cloning."""
        obj = ConcreteBaseClass()
        obj.class_id = "test"
        cloned = obj.clone()
        assert isinstance(cloned, BaseClass)
        assert cloned.class_id == "test"

    def test_load_save_data(self):
        """Test load and save data."""
        obj = ConcreteBaseClass()
        data = obj.save_data()
        assert isinstance(data, list)
        result = obj.load_data(data)
        assert result is True

    def test_extra_properties(self):
        """Test extra properties management."""
        obj = ConcreteBaseClass()
        obj.add_extra_property("test_prop", "value")
        assert "test_prop" in obj.extra_properties
        assert obj.get_extra_property_value("test_prop") == "value"
        obj.set_extra_property_value("test_prop", "new_value")
        assert obj.get_extra_property_value("test_prop") == "new_value"
        obj.remove_extra_property("test_prop")
        assert "test_prop" not in obj.extra_properties

    def test_calculate_raises(self):
        """Test calculate raises NotImplementedError."""
        obj = ConcreteBaseClass()
        with pytest.raises(NotImplementedError):
            obj.calculate()