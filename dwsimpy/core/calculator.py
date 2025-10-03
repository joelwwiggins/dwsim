"""
Calculator Utility Class

Converted from VB.NET to Python.
Provides utility functions for logging, localization, platform detection,
and computation setup.
"""

import os
import platform
import threading
import datetime
import gettext
from typing import Optional


class Calculator:
    """Utility class for DWSIM calculations."""

    _resource_manager: Optional[gettext.NullTranslations] = None
    culture = "en-US"
    excel_log_form = None  # Placeholder for log form

    @staticmethod
    def write_to_console(text: str, level: int) -> None:
        """Write debug message to console if level is sufficient."""
        # Placeholder for Settings - will be imported when available
        debug_level = 1  # Default debug level
        if level <= debug_level:
            thread_id = threading.current_thread().ident
            timestamp = datetime.datetime.now().isoformat()
            print(f"[Thread ID: {thread_id}][{timestamp}] {text}")

    @staticmethod
    def get_local_string(text: str) -> str:
        """Get localized string or return original text."""
        if Calculator._resource_manager is None:
            # Initialize gettext for localization
            try:
                Calculator._resource_manager = gettext.translation(
                    'dwsim_thermodynamics',
                    localedir='locale',
                    languages=[Calculator.culture.split('-')[0]],
                    fallback=True
                )
            except FileNotFoundError:
                Calculator._resource_manager = gettext.NullTranslations()

        if text:
            translated = Calculator._resource_manager.gettext(text)
            return translated if translated != text else text
        return ""

    @staticmethod
    def check_parallel_pinvoke() -> None:
        """Check and disable parallel processing if needed."""
        # Placeholder for Settings
        enable_parallel = False  # Default
        if enable_parallel:
            enable_parallel = False
            ex = InvalidOperationException(
                Calculator.get_local_string("ParallelPInvokeError")
            )
            ex.data["DetailedDescription"] = (
                "This calculation will use a native (C++/FORTRAN) library "
                "which doesn't support multithreading, that is, cannot do "
                "multiple calculations at once."
            )
            ex.data["UserAction"] = (
                "Go to the Global Settings Panel, disable the CPU Parallel "
                "Acceleration and try again."
            )
            raise ex

    @staticmethod
    def is_running_on_mono() -> bool:
        """Check if running on Mono runtime."""
        # Python doesn't run on Mono, so always False
        return False

    class Platform:
        """Enumeration for platform types."""
        WINDOWS = "Windows"
        LINUX = "Linux"
        MAC = "Mac"

    @staticmethod
    def running_platform() -> str:
        """Determine the running platform."""
        system = platform.system().lower()
        if system == "windows":
            return Calculator.Platform.WINDOWS
        elif system == "darwin":
            return Calculator.Platform.MAC
        else:
            # Check for Mac-specific directories on Unix-like systems
            if (os.path.exists("/Applications") and
                    os.path.exists("/System") and
                    os.path.exists("/Users") and
                    os.path.exists("/Volumes")):
                return Calculator.Platform.MAC
            else:
                return Calculator.Platform.LINUX

    @staticmethod
    def init_compute_device() -> None:
        """Initialize compute device (GPU/CPU)."""
        # GPU initialization code commented out in original VB.NET
        # Placeholder for future GPU support
        pass


class InvalidOperationException(Exception):
    """Custom exception for invalid operations."""

    def __init__(self, message: str):
        super().__init__(message)
        self.data = {}