#!/usr/bin/env python3
"""
Test launcher for Settings Dialog
Run this to test the settings dialog independently
"""
import sys
import os

# Get the v2 directory (parent of this script)
v2_dir = os.path.dirname(os.path.abspath(__file__))
# Add v2 directory to path so Python recognizes 'src' as a package
if v2_dir not in sys.path:
    sys.path.insert(0, v2_dir)

from PyQt6.QtWidgets import QApplication
from src.ui.settings_dialog import SettingsDialog
from src.ui.theme import apply_dark_theme
from src.core.config import Config

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Apply dark theme
    apply_dark_theme(app)
    
    # Load config
    config = Config.load_from_file()
    
    # Create and show settings dialog
    dialog = SettingsDialog(config=config)
    dialog.show()
    
    # Run event loop
    result = app.exec()
    
    # If dialog was accepted, show what was saved
    if result == QApplication.ExitCode.Accepted:
        print("\nSettings saved successfully!")
        print(f"  - both_query_method: {config.both_query_method}")
        print(f"  - mark_ignore: {config.mark_ignore}")
        print(f"  - auto_save: {config.auto_save}")
        print(f"  - api_url: {config.api_url}")
    else:
        print("\nSettings dialog cancelled.")
    
    sys.exit(result)

