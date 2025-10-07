#!/usr/bin/env python3
"""
Simple DWSIMpy runner that avoids import conflicts
"""

import sys
import os

# Add the dwsimpy directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dwsimpy'))

def run_simple_simulation():
    """Run a simple simulation without complex imports."""
    print("DWSIMpy - Chemical Process Simulator")
    print("====================================")
    print()
    
    # Simple property calculation without full module imports
    print("Running simple mass and energy balance...")
    
    # Feed stream 1
    feed1_mass_flow = 100.0  # kg/h
    feed1_temp = 25.0        # °C
    feed1_pressure = 101325.0  # Pa
    print(f"Feed 1: {feed1_mass_flow} kg/h at {feed1_temp}°C, {feed1_pressure/1000:.1f} kPa")
    
    # Feed stream 2  
    feed2_mass_flow = 50.0   # kg/h
    feed2_temp = 30.0        # °C
    feed2_pressure = 101325.0  # Pa
    print(f"Feed 2: {feed2_mass_flow} kg/h at {feed2_temp}°C, {feed2_pressure/1000:.1f} kPa")
    
    # Simple mixer calculation
    mixed_mass_flow = feed1_mass_flow + feed2_mass_flow
    mixed_temp = (feed1_mass_flow * feed1_temp + feed2_mass_flow * feed2_temp) / mixed_mass_flow
    mixed_pressure = min(feed1_pressure, feed2_pressure)  # Pressure drop
    
    print(f"Mixed stream: {mixed_mass_flow} kg/h at {mixed_temp:.1f}°C, {mixed_pressure/1000:.1f} kPa")
    
    # Simple heater calculation
    heat_duty = 10.0  # kW
    cp = 4.18  # kJ/kg·K (approximate for water)
    temp_rise = heat_duty * 3600 / (mixed_mass_flow * cp)  # Convert kW to kJ/h
    
    heated_temp = mixed_temp + temp_rise
    print(f"After heater (+{heat_duty} kW): {mixed_mass_flow} kg/h at {heated_temp:.1f}°C")
    
    print()
    print("Simple simulation completed successfully!")
    print()
    print("Available DWSIMpy applications:")
    print("1. Console version (this): Simple mass/energy balance")
    print("2. Desktop GUI: PyQt6 flowsheet editor")
    print("3. Web application: Browser-based interface")

if __name__ == "__main__":
    run_simple_simulation()