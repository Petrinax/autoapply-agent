#!/bin/bash

# This script runs the main_collect.py script from anywhere on the system.
# It ensures that the virtual environment is activated and runs the script from the project root.

# Get the absolute path of the directory where the script is located.
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)

# The project root is two levels up from the script's directory.
PROJECT_ROOT=$(cd "$SCRIPT_DIR/../.." &>/dev/null && pwd)

echo "PROJECT_ROOT: $PROJECT_ROOT"
echo "SCRIPT_DIR: $SCRIPT_DIR"


# Define paths relative to the project root
VENV_ACTIVATE="$PROJECT_ROOT/venv/bin/activate"
PYTHON_SCRIPT="src/scripts/main_collect.py"

# Check if the virtual environment activation script exists
if [ ! -f "$VENV_ACTIVATE" ]; then
    echo "Error: Virtual environment not found. Please ensure 'venv' is set up in the project root."
    exit 1
fi

# Activate the virtual environment
source "$VENV_ACTIVATE"

# Navigate to the project root to ensure correct relative path handling
cd "$PROJECT_ROOT"

# Run the Python script, passing along any arguments
echo "Starting data collection..."
python "$PYTHON_SCRIPT" "$@"
echo "Data collection finished."

# Deactivate the virtual environment
deactivate 