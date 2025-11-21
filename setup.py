"""
Setup script for creating macOS .app bundle using py2app
"""
from setuptools import setup
import py2app
import os
import sys

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
RESOURCES_DIR = os.path.join(PROJECT_ROOT, "resources")

# Collect all Python files in src directory
py_modules = []
for root, dirs, files in os.walk(SRC_DIR):
    # Skip __pycache__ directories
    dirs[:] = [d for d in dirs if d != "__pycache__"]
    for file in files:
        if file.endswith(".py"):
            rel_path = os.path.relpath(os.path.join(root, file), PROJECT_ROOT)
            module_name = rel_path.replace(os.sep, ".").replace(".py", "")
            py_modules.append(module_name)

# Collect resource files to include
# For py2app, we'll include the entire resources directory
resource_files = []
if os.path.exists(RESOURCES_DIR):
    for root, dirs, files in os.walk(RESOURCES_DIR):
        # Skip hidden files and directories
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for file in files:
            if not file.startswith("."):
                file_path = os.path.join(root, file)
                resource_files.append(file_path)

APP = [{
    "script": os.path.join(SRC_DIR, "llmii_gui.py"),
    "iconfile": None,  # Can add icon file path here if available
    "plist": {
        "CFBundleName": "ImageIndexer",
        "CFBundleDisplayName": "Image Indexer",
        "CFBundleIdentifier": "com.imageindexer.app",
        "CFBundleVersion": "1.0.0",
        "CFBundleShortVersionString": "1.0.0",
        "NSHighResolutionCapable": True,
        "NSRequiresAquaSystemAppearance": False,
        "LSMinimumSystemVersion": "10.13",
    }
}]

# Include resources directory in DATA_FILES
# py2app will place these in Contents/Resources/
# DATA_FILES format: (destination_dir, [list of source file paths])
DATA_FILES = []
if resource_files:
    # Include all resource files
    # Organize by subdirectory to preserve directory structure
    file_dict = {}
    for file_path in resource_files:
        # Get relative path from RESOURCES_DIR
        rel_path = os.path.relpath(file_path, RESOURCES_DIR)
        # Get the subdirectory (if any)
        subdir = os.path.dirname(rel_path)
        if subdir:
            if subdir not in file_dict:
                file_dict[subdir] = []
            file_dict[subdir].append(file_path)
        else:
            # Files in root of resources directory
            if '' not in file_dict:
                file_dict[''] = []
            file_dict[''].append(file_path)
    
    # Create DATA_FILES entries for each subdirectory
    for subdir, files in file_dict.items():
        dest_dir = os.path.join("resources", subdir) if subdir else "resources"
        DATA_FILES.append((dest_dir, files))

OPTIONS = {
    "argv_emulation": False,
    "packages": [
        "PyQt6",
        "PIL",
        "pillow_heif",
        "rawpy",
        "json_repair",
        "exiftool",
        "requests",
        "regex",
        "numpy",
    ],
    "includes": [
        "PIL",
        "PIL.Image",
        "src.llmii",
        "src.llmii_gui",
        "src.llmii_setup",
        "src.llmii_utils",
        "src.config",
        "src.help_text",
        "src.image_processor",
    ],
    "excludes": [
        "tkinter",
        "matplotlib",
        "scipy",
    ],
    "iconfile": None,  # Can specify icon path here
    "plist": {
        "CFBundleName": "ImageIndexer",
        "CFBundleDisplayName": "Image Indexer",
        "CFBundleIdentifier": "com.imageindexer.app",
        "CFBundleVersion": "1.0.0",
        "CFBundleShortVersionString": "1.0.0",
        "NSHighResolutionCapable": True,
        "NSRequiresAquaSystemAppearance": False,
        "LSMinimumSystemVersion": "10.13",
    },
}

setup(
    name="ImageIndexer",
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)

