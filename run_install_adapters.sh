#!/bin/bash

echo "Starting run_install_adapters.sh"

# Activate the virtual environment
source /root/iobroker_winkelhus/venv/bin/activate

echo "Virtual environment activated"

# Print Python version and path
echo "Python version:"
python3 --version
echo "Python path:"
which python3

# Run the Python script with debug output
echo "Running install_adapters.py"
python3 -u /root/iobroker_winkelhus/install_adapters.py

echo "install_adapters.py execution completed"

# Deactivate the virtual environment
deactivate

echo "Virtual environment deactivated"
echo "run_install_adapters.sh completed"