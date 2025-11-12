#!/bin/bash

echo "Starting..."

VENV_NAME="llmii_env"

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

if ! command_exists python3; then
    echo "Python 3 is not found. Please ensure Python 3 is installed and added to your PATH."
    read -p "Press Enter to exit..."
    exit 1
fi

if ! command_exists exiftool; then
    bash setup.sh
fi

if [ ! -d "$VENV_NAME" ]; then
    bash setup.sh
fi

source "$VENV_NAME/bin/activate"

python3 -m src.llmii_gui

# Clear screen after GUI exits to remove any LLM server output
# Add delay to allow any pending output to appear, then clear
sleep 1
clear
# Clear again after a brief moment to catch any late output
sleep 0.2
clear

echo "Done."

deactivate
