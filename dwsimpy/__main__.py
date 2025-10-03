"""
Main entry point for DWSIMpy.

Launches the web UI using Streamlit.
"""

import subprocess
import sys
import os

def main():
    # Path to the UI app
    ui_path = os.path.join(os.path.dirname(__file__), 'ui', 'app.py')

    # Run Streamlit
    try:
        subprocess.run([sys.executable, '-m', 'streamlit', 'run', ui_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()