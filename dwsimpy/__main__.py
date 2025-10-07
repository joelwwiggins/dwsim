"""
Main entry point for DWSIMpy.

Launches the backend API server and Svelte frontend.
"""

import subprocess
import sys
import os
import signal
import time

def main():
    print("Starting DWSIMpy...")
    print("Backend will run on http://localhost:8000")
    print("Frontend will run on http://localhost:5173")

    # Start backend
    backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'main.py')
    backend_process = subprocess.Popen([sys.executable, backend_path])

    # Wait a bit for backend to start
    time.sleep(3)

    # Start frontend
    ui_dir = os.path.join(os.path.dirname(__file__), '..', 'ui')
    frontend_process = subprocess.Popen(['npm', 'run', 'dev'], cwd=ui_dir)

    def signal_handler(sig, frame):
        print("Shutting down...")
        backend_process.terminate()
        frontend_process.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Wait for processes
    try:
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()
