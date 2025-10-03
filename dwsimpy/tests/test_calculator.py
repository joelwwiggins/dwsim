"""
Unit tests for Calculator.

Generated using pytest.
"""

from dwsimpy.core.calculator import Calculator


class TestCalculator:
    """Test cases for Calculator class."""

    def test_write_to_console(self, capsys):
        """Test console writing."""
        Calculator.write_to_console("Test message", 1)
        captured = capsys.readouterr()
        assert "Test message" in captured.out

    def test_get_local_string(self):
        """Test localization (returns original if no translation)."""
        result = Calculator.get_local_string("test")
        assert result == "test"

    def test_check_parallel_pinvoke(self):
        """Test parallel PInvoke check (should not raise with default)."""
        Calculator.check_parallel_pinvoke()  # Should not raise

    def test_is_running_on_mono(self):
        """Test Mono detection."""
        assert Calculator.is_running_on_mono() is False

    def test_running_platform(self):
        """Test platform detection."""
        platform = Calculator.running_platform()
        valid_platforms = [
            Calculator.Platform.WINDOWS,
            Calculator.Platform.LINUX,
            Calculator.Platform.MAC
        ]
        assert platform in valid_platforms

    def test_init_compute_device(self):
        """Test compute device initialization (placeholder)."""
        Calculator.init_compute_device()  # Should not raise