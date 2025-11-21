#!/bin/bash

# Build script for creating macOS .app bundle using py2app

echo "Building ImageIndexer.app bundle..."
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment
VENV_NAME="llmii_env"
if [ ! -d "$VENV_NAME" ]; then
    echo "Error: Virtual environment not found at $VENV_NAME"
    echo "Please run setup first."
    exit 1
fi

echo "Activating virtual environment..."
source "$VENV_NAME/bin/activate"

# Check if py2app is installed
if ! python3 -c "import py2app" 2>/dev/null; then
    echo "py2app is not installed. Installing..."
    pip install py2app
fi

# Clean previous builds
echo "Cleaning previous builds..."
# Try to remove build and dist directories, but don't fail if they're locked
rm -rf build 2>/dev/null || true
# For dist, try to remove the app bundle first if it exists
if [ -d "dist/ImageIndexer.app" ]; then
    echo "Removing existing app bundle..."
    rm -rf "dist/ImageIndexer.app" 2>/dev/null || {
        echo "Warning: Could not remove dist/ImageIndexer.app (it may be in use)"
        echo "Please close the app if it's running and try again."
        exit 1
    }
fi
rm -rf dist 2>/dev/null || true

# Build the app
echo "Building app bundle..."
python3 setup.py py2app

echo ""
echo "Build complete!"
echo "The app bundle is located at: dist/ImageIndexer.app"
echo ""
echo "To test the app, run:"
echo "  open dist/ImageIndexer.app"

deactivate

