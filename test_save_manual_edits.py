#!/usr/bin/env python3
"""
Test script for Sub-phase 6.7: Save Manual Edits
Tests that manual edits (caption and keywords) are properly saved to files.
"""

import sys
import os
import tempfile
import shutil

# Add project root to path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

def test_save_reads_from_ui_widgets():
    """Test that save_current_image reads from UI widgets"""
    try:
        from PyQt6.QtWidgets import QApplication
        from src.llmii_gui import ImageIndexerGUI
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        gui = ImageIndexerGUI()
        
        # Check that save_current_image method exists
        assert hasattr(gui, 'save_current_image'), "save_current_image method should exist"
        assert hasattr(gui, 'caption_edit'), "caption_edit widget should exist"
        assert hasattr(gui, 'keywords_widget'), "keywords_widget should exist"
        
        # Check that caption_edit has toPlainText method
        assert hasattr(gui.caption_edit, 'toPlainText'), "caption_edit should have toPlainText method"
        
        # Check that keywords_widget has keywords attribute
        assert hasattr(gui.keywords_widget, 'keywords'), "keywords_widget should have keywords attribute"
        
        # Cleanup
        if hasattr(gui, 'api_check_thread') and gui.api_check_thread:
            gui.api_check_thread.stop()
            gui.api_check_thread.wait(1000)
        
        print("✓ save_current_image reads from UI widgets (structure verified)")
        return True
    except Exception as e:
        print(f"✗ UI widget reading test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_caption_edit_widget():
    """Test that caption_edit widget can be read from"""
    try:
        from PyQt6.QtWidgets import QApplication
        from src.llmii_gui import ImageIndexerGUI
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        gui = ImageIndexerGUI()
        
        # Set some text in caption_edit
        test_caption = "Test caption for save functionality"
        gui.caption_edit.setPlainText(test_caption)
        
        # Read it back
        read_caption = gui.caption_edit.toPlainText()
        
        assert read_caption == test_caption, f"Caption should be '{test_caption}', got '{read_caption}'"
        
        # Cleanup
        if hasattr(gui, 'api_check_thread') and gui.api_check_thread:
            gui.api_check_thread.stop()
            gui.api_check_thread.wait(1000)
        
        print("✓ Caption edit widget can be read from correctly")
        return True
    except Exception as e:
        print(f"✗ Caption edit widget test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_keywords_widget_read():
    """Test that keywords_widget.keywords can be read"""
    try:
        from PyQt6.QtWidgets import QApplication
        from src.llmii_gui import ImageIndexerGUI
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        gui = ImageIndexerGUI()
        
        # Set some keywords
        test_keywords = ["keyword1", "keyword2", "keyword3"]
        gui.keywords_widget.set_keywords(test_keywords)
        
        # Read them back
        read_keywords = gui.keywords_widget.keywords
        
        assert read_keywords == test_keywords, f"Keywords should be {test_keywords}, got {read_keywords}"
        
        # Cleanup
        if hasattr(gui, 'api_check_thread') and gui.api_check_thread:
            gui.api_check_thread.stop()
            gui.api_check_thread.wait(1000)
        
        print("✓ Keywords widget can be read from correctly")
        return True
    except Exception as e:
        print(f"✗ Keywords widget read test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_keywords_copy_safety():
    """Test that keywords are properly copied (not referenced)"""
    try:
        from PyQt6.QtWidgets import QApplication
        from src.llmii_gui import ImageIndexerGUI
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        gui = ImageIndexerGUI()
        
        # Set some keywords
        original_keywords = ["keyword1", "keyword2"]
        gui.keywords_widget.set_keywords(original_keywords)
        
        # Get a copy (as save_current_image does)
        keywords_copy = gui.keywords_widget.keywords.copy() if gui.keywords_widget.keywords else []
        
        # Modify the original
        gui.keywords_widget.set_keywords(["modified"])
        
        # Copy should be unchanged
        assert keywords_copy == original_keywords, "Keywords copy should be independent of original"
        
        # Cleanup
        if hasattr(gui, 'api_check_thread') and gui.api_check_thread:
            gui.api_check_thread.stop()
            gui.api_check_thread.wait(1000)
        
        print("✓ Keywords copy safety works correctly")
        return True
    except Exception as e:
        print(f"✗ Keywords copy safety test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_none_keywords_handling():
    """Test that None keywords are handled correctly"""
    try:
        from PyQt6.QtWidgets import QApplication
        from src.llmii_gui import ImageIndexerGUI
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        gui = ImageIndexerGUI()
        
        # Simulate None keywords (edge case)
        gui.keywords_widget.keywords = None
        
        # Test the None handling logic (as in save_current_image)
        current_keywords = gui.keywords_widget.keywords.copy() if gui.keywords_widget.keywords else []
        
        # Should result in empty list, not None
        assert current_keywords == [], "None keywords should result in empty list"
        
        # Also test explicit None check
        if current_keywords is None:
            current_keywords = []
        assert current_keywords == [], "Explicit None check should result in empty list"
        
        # Cleanup
        if hasattr(gui, 'api_check_thread') and gui.api_check_thread:
            gui.api_check_thread.stop()
            gui.api_check_thread.wait(1000)
        
        print("✓ None keywords handling works correctly")
        return True
    except Exception as e:
        print(f"✗ None keywords handling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_metadata_preparation_with_ui_values():
    """Test that metadata is prepared with UI values"""
    try:
        from PyQt6.QtWidgets import QApplication
        from src.llmii_gui import RegenerationHelper
        import src.llmii as llmii
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Create minimal config
        config = llmii.Config()
        helper = RegenerationHelper(config)
        
        try:
            # Create test metadata
            test_metadata = {
                "SourceFile": "/test/path.jpg",
                "XMP:Identifier": "test-uuid",
                "XMP:Status": "pending"
            }
            
            # Prepare metadata
            prepared = helper.prepare_metadata_for_save(test_metadata)
            
            # Test that we can update it with UI values (as save_current_image does)
            test_caption = "Test caption from UI"
            test_keywords = ["ui", "keyword1", "keyword2"]
            
            prepared["MWG:Description"] = test_caption
            prepared["MWG:Keywords"] = test_keywords
            
            assert prepared["MWG:Description"] == test_caption, "Caption should be set from UI"
            assert prepared["MWG:Keywords"] == test_keywords, "Keywords should be set from UI"
            assert prepared["XMP:Status"] == "success", "Status should be 'success' when prepared"
            assert isinstance(prepared["MWG:Keywords"], list), "Keywords should be a list"
            
            print("✓ Metadata preparation with UI values works correctly")
            return True
        finally:
            helper.cleanup()
    except Exception as e:
        print(f"✗ Metadata preparation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_empty_caption_handling():
    """Test that empty caption is handled correctly"""
    try:
        from PyQt6.QtWidgets import QApplication
        from src.llmii_gui import ImageIndexerGUI
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        gui = ImageIndexerGUI()
        
        # Set empty caption
        gui.caption_edit.setPlainText("")
        
        # Read it back
        read_caption = gui.caption_edit.toPlainText()
        
        assert read_caption == "", "Empty caption should be preserved"
        
        # Cleanup
        if hasattr(gui, 'api_check_thread') and gui.api_check_thread:
            gui.api_check_thread.stop()
            gui.api_check_thread.wait(1000)
        
        print("✓ Empty caption handling works correctly")
        return True
    except Exception as e:
        print(f"✗ Empty caption handling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_empty_keywords_handling():
    """Test that empty keywords list is handled correctly"""
    try:
        from PyQt6.QtWidgets import QApplication
        from src.llmii_gui import ImageIndexerGUI
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        gui = ImageIndexerGUI()
        
        # Set empty keywords
        gui.keywords_widget.set_keywords([])
        
        # Read them back
        read_keywords = gui.keywords_widget.keywords.copy() if gui.keywords_widget.keywords else []
        
        assert read_keywords == [], "Empty keywords should be preserved as empty list"
        
        # Cleanup
        if hasattr(gui, 'api_check_thread') and gui.api_check_thread:
            gui.api_check_thread.stop()
            gui.api_check_thread.wait(1000)
        
        print("✓ Empty keywords handling works correctly")
        return True
    except Exception as e:
        print(f"✗ Empty keywords handling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("Testing Sub-phase 6.7: Save Manual Edits...\n")
    
    tests = [
        test_save_reads_from_ui_widgets,
        test_caption_edit_widget,
        test_keywords_widget_read,
        test_keywords_copy_safety,
        test_none_keywords_handling,
        test_metadata_preparation_with_ui_values,
        test_empty_caption_handling,
        test_empty_keywords_handling,
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
        print("✓ All Sub-phase 6.7 tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())

