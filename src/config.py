import os
import sys

def _get_project_root():
    """Get project root directory, handling both normal execution and app bundle"""
    # Check if we're running from an app bundle
    if getattr(sys, 'frozen', False):
        # Running from py2app bundle
        # sys.executable points to the app bundle's executable
        # We need to go up to Contents/Resources/
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller style (not used here, but for compatibility)
            base_path = sys._MEIPASS
        else:
            # py2app: sys.executable is the app bundle executable
            # Go from MacOS/executable to Contents/Resources/
            bundle_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.executable))))
            # In app bundle, resources are in Contents/Resources/resources/
            resources_path = os.path.join(bundle_dir, "Contents", "Resources")
            # Check if resources directory exists there
            if os.path.exists(os.path.join(resources_path, "resources")):
                return resources_path
            else:
                # Fallback: use the bundle directory as project root
                return bundle_dir
    else:
        # Normal execution: project root is two levels up from src/config.py
        return os.path.normpath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Get project root directory 
PROJECT_ROOT = _get_project_root()

# Resources directory at project root level
# In app bundle, this will be Contents/Resources/resources/
# In normal execution, this will be project_root/resources/
RESOURCES_DIR = os.path.normpath(os.path.join(PROJECT_ROOT, "resources"))

