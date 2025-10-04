# Use Python 3.11 base image
FROM python:3.11-slim

# Install system dependencies for GUI and PyQt
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libxcb-xinerama0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxss1 \
    libasound2 \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY dwsimpy/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project
COPY . .

# Install the package in editable mode
RUN pip install -e dwsimpy

# Expose port for web UI (if needed)
EXPOSE 8501

# Default command to run the desktop app with virtual display
CMD ["xvfb-run", "-a", "python", "dwsimpy/ui/desktop_app.py"]