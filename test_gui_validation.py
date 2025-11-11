#!/usr/bin/env python3
"""
Basic validation script for GUI functionality.
Run this before and after making changes to ensure no regressions.
"""

import sys
import os

# Add project root to path for module imports
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

def test_imports():
    """Test that all required modules can be imported"""
    try:
        from src.llmii_gui import ImageIndexerGUI, GuiConfig
        from src.llmii import Config, FileProcessor
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_gui_config():
    """Test that GuiConfig has expected attributes"""
    try:
        from src.llmii_gui import GuiConfig
        
        required_attrs = [
            'WINDOW_WIDTH', 'WINDOW_HEIGHT',
            'IMAGE_PREVIEW_WIDTH', 'IMAGE_PREVIEW_HEIGHT',
            'METADATA_WIDTH', 'METADATA_HEIGHT',
            'COLOR_KEYWORD_BG', 'COLOR_KEYWORD_TEXT'
        ]
        
        for attr in required_attrs:
            if not hasattr(GuiConfig, attr):
                print(f"✗ GuiConfig missing attribute: {attr}")
                return False
        
        print("✓ GuiConfig has all required attributes")
        return True
    except Exception as e:
        print(f"✗ GuiConfig test failed: {e}")
        return False

def test_config_defaults():
    """Test that Config has expected defaults"""
    try:
        from src.llmii import Config
        
        config = Config()
        
        # Check some critical defaults
        assert config.gen_count == 250, f"Expected gen_count=250, got {config.gen_count}"
        assert config.res_limit == 448, f"Expected res_limit=448, got {config.res_limit}"
        assert hasattr(config, 'instruction'), "Config missing instruction attribute"
        
        print("✓ Config defaults are correct")
        return True
    except Exception as e:
        print(f"✗ Config defaults test failed: {e}")
        return False

def main():
    """Run all validation tests"""
    print("Running GUI validation tests...\n")
    
    tests = [
        test_imports,
        test_gui_config,
        test_config_defaults
    ]
    
    results = []
    for test in tests:
        results.append(test())
        print()
    
    if all(results):
        print("✓ All validation tests passed!")
        return 0
    else:
        print("✗ Some validation tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())

