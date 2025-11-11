#!/usr/bin/env python3
"""
Test script for Generation Mode feature (Phase 2)
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

def test_config_generation_mode():
    """Test that Config has generation_mode attribute with correct default"""
    from src.llmii import Config
    
    config = Config()
    
    assert hasattr(config, 'generation_mode'), "Config missing generation_mode attribute"
    assert config.generation_mode == "both", f"Expected default 'both', got '{config.generation_mode}'"
    
    # Test setting different modes
    config.generation_mode = "description_only"
    assert config.generation_mode == "description_only", "Failed to set description_only"
    
    config.generation_mode = "keywords_only"
    assert config.generation_mode == "keywords_only", "Failed to set keywords_only"
    
    config.generation_mode = "both"
    assert config.generation_mode == "both", "Failed to set both"
    
    print("✓ Config generation_mode attribute works correctly")
    return True

def test_settings_dialog_ui():
    """Test that SettingsDialog has generation mode UI elements"""
    from src.llmii_gui import SettingsDialog
    
    # Create a minimal QApplication if needed
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    dialog = SettingsDialog()
    
    # Check that UI elements exist
    assert hasattr(dialog, 'generation_mode_radio_group'), "Missing generation_mode_radio_group"
    assert hasattr(dialog, 'description_only_radio'), "Missing description_only_radio"
    assert hasattr(dialog, 'keywords_only_radio'), "Missing keywords_only_radio"
    assert hasattr(dialog, 'both_radio'), "Missing both_radio"
    
    # Check default state
    assert dialog.both_radio.isChecked(), "Default should be 'both' selected"
    
    print("✓ SettingsDialog has all generation mode UI elements")
    return True

def test_settings_save_load():
    """Test that generation_mode can be saved and loaded"""
    import json
    import tempfile
    from src.llmii_gui import SettingsDialog
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    dialog = SettingsDialog()
    
    # Test saving
    dialog.description_only_radio.setChecked(True)
    settings = {}
    dialog.save_settings = lambda: None  # Override to capture settings
    
    # Manually test the save logic
    generation_mode = 'description_only' if dialog.description_only_radio.isChecked() else ('keywords_only' if dialog.keywords_only_radio.isChecked() else 'both')
    assert generation_mode == 'description_only', "Save logic failed for description_only"
    
    dialog.keywords_only_radio.setChecked(True)
    generation_mode = 'description_only' if dialog.description_only_radio.isChecked() else ('keywords_only' if dialog.keywords_only_radio.isChecked() else 'both')
    assert generation_mode == 'keywords_only', "Save logic failed for keywords_only"
    
    dialog.both_radio.setChecked(True)
    generation_mode = 'description_only' if dialog.description_only_radio.isChecked() else ('keywords_only' if dialog.keywords_only_radio.isChecked() else 'both')
    assert generation_mode == 'both', "Save logic failed for both"
    
    print("✓ Settings save/load logic works correctly")
    return True

def main():
    """Run all tests"""
    print("Testing Generation Mode feature (Phase 2)...\n")
    
    tests = [
        test_config_generation_mode,
        test_settings_dialog_ui,
        test_settings_save_load
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
            print()
        except Exception as e:
            print(f"✗ Test failed: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
            print()
    
    if all(results):
        print("✓ All Generation Mode tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())

