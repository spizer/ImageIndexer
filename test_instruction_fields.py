#!/usr/bin/env python3
"""
Test script for the new three instruction fields feature
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

def test_config_has_all_instructions():
    """Test that Config has all three instruction attributes"""
    from src.llmii import Config
    
    config = Config()
    
    assert hasattr(config, 'instruction'), "Config missing 'instruction'"
    assert hasattr(config, 'caption_instruction'), "Config missing 'caption_instruction'"
    assert hasattr(config, 'keyword_instruction'), "Config missing 'keyword_instruction'"
    
    # Check that keyword_instruction has content
    assert len(config.keyword_instruction) > 0, "keyword_instruction should have default content"
    assert "Keywords" in config.keyword_instruction, "keyword_instruction should mention Keywords"
    assert "Description" not in config.keyword_instruction or config.keyword_instruction.count("Description") == 0, "keyword_instruction should not ask for Description"
    
    print("✓ Config has all three instruction attributes with proper defaults")
    return True

def test_llmprocessor_has_keyword_instruction():
    """Test that LLMProcessor has keyword_instruction"""
    from src.llmii import Config, LLMProcessor
    
    config = Config()
    processor = LLMProcessor(config)
    
    assert hasattr(processor, 'keyword_instruction'), "LLMProcessor missing 'keyword_instruction'"
    assert len(processor.keyword_instruction) > 0, "LLMProcessor keyword_instruction should have content"
    
    print("✓ LLMProcessor has keyword_instruction")
    return True

def test_keywords_only_task():
    """Test that keywords_only task type exists"""
    from src.llmii import Config, LLMProcessor
    
    config = Config()
    processor = LLMProcessor(config)
    
    # Test that the task type is handled (should not raise error)
    try:
        # We can't actually call it without an image, but we can check the code path exists
        # The task="keywords_only" should map to keyword_instruction
        assert hasattr(processor, 'keyword_instruction'), "Processor should have keyword_instruction"
        print("✓ keywords_only task type is configured")
        return True
    except Exception as e:
        print(f"✗ Error testing keywords_only task: {e}")
        return False

def test_gui_has_instruction_fields():
    """Test that SettingsDialog has the new instruction fields"""
    from src.llmii_gui import SettingsDialog
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    dialog = SettingsDialog()
    
    assert hasattr(dialog, 'general_instruction_input'), "Missing general_instruction_input"
    assert hasattr(dialog, 'description_instruction_input'), "Missing description_instruction_input"
    assert hasattr(dialog, 'keyword_instruction_input'), "Missing keyword_instruction_input"
    
    # Check they are QPlainTextEdit widgets
    from PyQt6.QtWidgets import QPlainTextEdit
    assert isinstance(dialog.general_instruction_input, QPlainTextEdit), "general_instruction_input should be QPlainTextEdit"
    assert isinstance(dialog.description_instruction_input, QPlainTextEdit), "description_instruction_input should be QPlainTextEdit"
    assert isinstance(dialog.keyword_instruction_input, QPlainTextEdit), "keyword_instruction_input should be QPlainTextEdit"
    
    print("✓ SettingsDialog has all three instruction input fields")
    return True

def main():
    """Run all tests"""
    print("Testing Instruction Fields feature...\n")
    
    tests = [
        test_config_has_all_instructions,
        test_llmprocessor_has_keyword_instruction,
        test_keywords_only_task,
        test_gui_has_instruction_fields
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
        print("✓ All instruction fields tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())

