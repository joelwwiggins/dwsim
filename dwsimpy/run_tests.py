#!/usr/bin/env python3
"""
Test runner for DWSIM Python.
"""

import sys
import subprocess
import os
from pathlib import Path


def run_tests():
    """Run the test suite"""
    project_root = Path(__file__).parent
    
    # Change to project directory
    os.chdir(project_root)
    
    # Install in development mode if not already
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], 
                      check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to install package: {e}")
        return False
    
    # Run pytest
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "--tb=short",
            "--cov=dwsimpy",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov"
        ], check=True)
        
        print("\n✅ All tests passed!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return False


def run_specific_test(test_path):
    """Run a specific test file"""
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            test_path,
            "--tb=short",
            "-v"
        ], check=True)
        
        print(f"\n✅ Test {test_path} passed!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Test {test_path} failed with exit code {e.returncode}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific test
        test_path = sys.argv[1]
        success = run_specific_test(test_path)
    else:
        # Run all tests
        print("Running DWSIM Python test suite...")
        success = run_tests()
    
    sys.exit(0 if success else 1)
