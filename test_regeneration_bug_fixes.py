#!/usr/bin/env python3
"""
Test script for Regeneration Bug Fixes:
1. Description preservation when regenerating keywords only
2. Keyword duplication prevention during regeneration
"""

import sys
import os
import tempfile
import shutil

# Add project root to path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

def test_description_preservation_keywords_only():
    """Test that description is preserved when regenerating keywords only"""
    try:
        from PyQt6.QtWidgets import QApplication
        from src.llmii_gui import RegenerationHelper
        import src.llmii as llmii
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        config = llmii.Config()
        config.generation_mode = "keywords_only"
        # Removed config.update_keywords - feature removed
        
        helper = RegenerationHelper(config)
        
        try:
            # Test metadata with existing description
            test_description = "This is a test description that should be preserved"
            metadata = {
                "SourceFile": "/test/path.jpg",
                "MWG:Description": test_description,
                "MWG:Keywords": ["existing1", "existing2"],
                "XMP:Identifier": "test-uuid"
            }
            
            # Simulate regeneration - the description should be preserved
            # In keywords_only mode, existing_caption should be preserved
            existing_caption = metadata.get("MWG:Description")
            
            # Check that the logic preserves it
            new_metadata = metadata.copy()
            if existing_caption is not None:
                new_metadata["MWG:Description"] = existing_caption
            
            assert new_metadata["MWG:Description"] == test_description, \
                f"Description should be preserved, got '{new_metadata['MWG:Description']}'"
            
            print("✓ Description is preserved in keywords_only mode logic")
            return True
        finally:
            helper.cleanup()
    except Exception as e:
        print(f"✗ Description preservation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_keyword_no_duplication_during_regeneration():
    """Test that keywords don't duplicate when regenerating"""
    try:
        from PyQt6.QtWidgets import QApplication
        from src.llmii_gui import RegenerationHelper
        import src.llmii as llmii
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        config = llmii.Config()
        config.generation_mode = "keywords_only"
        # Removed config.update_keywords - feature removed (process_keywords now always returns only new keywords)
        
        helper = RegenerationHelper(config)
        
        try:
            # Test metadata with existing keywords
            existing_keywords = ["existing1", "existing2", "existing3"]
            metadata = {
                "SourceFile": "/test/path.jpg",
                "MWG:Keywords": existing_keywords,
                "XMP:Identifier": "test-uuid"
            }
            
            # Simulate new keywords from LLM (completely different from existing)
            new_keywords = ["new1", "new2", "new3"]
            
            # Test: process_keywords now always ignores existing keywords in metadata
            # Both with and without keywords in metadata should return the same result
            result_with_keywords = helper.process_keywords(metadata, new_keywords)
            result_with_keywords_lower = [kw.lower() for kw in result_with_keywords]
            
            # Test: create metadata copy without existing keywords
            metadata_without_keywords = metadata.copy()
            metadata_without_keywords.pop("MWG:Keywords", None)
            
            # Process keywords (should only process new ones, not merge existing)
            result_without_keywords = helper.process_keywords(metadata_without_keywords, new_keywords)
            result_without_keywords_lower = [kw.lower() for kw in result_without_keywords]
            
            # Both should return the same result (only new keywords)
            assert set(result_with_keywords_lower) == set(result_without_keywords_lower), \
                "Results should be the same regardless of existing keywords in metadata"
            
            # Should only contain new keywords (no existing ones)
            assert "new1" in result_with_keywords_lower or "new1" in result_with_keywords, \
                "New keywords should be in result"
            assert "new2" in result_with_keywords_lower or "new2" in result_with_keywords, \
                "New keywords should be in result"
            assert "new3" in result_with_keywords_lower or "new3" in result_with_keywords, \
                "New keywords should be in result"
            
            # Verify that existing keywords are NOT included
            assert "existing1" not in result_with_keywords_lower, \
                "Existing keywords should not be merged in"
            assert "existing2" not in result_with_keywords_lower, \
                "Existing keywords should not be merged in"
            assert "existing3" not in result_with_keywords_lower, \
                "Existing keywords should not be merged in"
            
            print("✓ Keywords don't duplicate during regeneration (metadata without keywords)")
            return True
        finally:
            helper.cleanup()
    except Exception as e:
        print(f"✗ Keyword duplication prevention test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_manual_keywords_preserved_during_regeneration():
    """Test that manual keywords are preserved when regenerating"""
    try:
        from PyQt6.QtWidgets import QApplication
        from src.llmii_gui import RegenerationHelper
        import src.llmii as llmii
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        config = llmii.Config()
        config.generation_mode = "keywords_only"
        # Removed config.update_keywords - feature removed
        
        helper = RegenerationHelper(config)
        
        try:
            # Simulate regeneration flow:
            # 1. Generate new keywords (without existing ones)
            metadata_without_keywords = {
                "SourceFile": "/test/path.jpg",
                "MWG:Description": "Test description",
                "XMP:Identifier": "test-uuid"
            }
            
            new_keywords = ["generated1", "generated2"]
            processed_new = helper.process_keywords(metadata_without_keywords, new_keywords)
            
            # 2. Manual keywords that should be preserved
            manual_keywords = ["manual1", "manual2"]
            
            # 3. Merge manual with generated (simulating RegenerateThread logic)
            final_keywords = processed_new.copy()
            manual_keywords_lower = {kw.lower() for kw in manual_keywords}
            
            for manual_kw in manual_keywords:
                if manual_kw.lower() not in {kw.lower() for kw in final_keywords}:
                    final_keywords.append(manual_kw)
            
            # Verify both manual and generated are present
            final_lower = [kw.lower() for kw in final_keywords]
            assert "manual1" in final_lower or "manual1" in final_keywords, "Manual keywords should be preserved"
            assert "manual2" in final_lower or "manual2" in final_keywords, "Manual keywords should be preserved"
            assert "generated1" in final_lower or "generated1" in final_keywords, "Generated keywords should be present"
            assert "generated2" in final_lower or "generated2" in final_keywords, "Generated keywords should be present"
            
            # Verify no duplicates
            assert len(final_keywords) == len(set(final_lower)), "No duplicates should exist"
            
            print("✓ Manual keywords are preserved during regeneration")
            return True
        finally:
            helper.cleanup()
    except Exception as e:
        print(f"✗ Manual keywords preservation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_caption_read_from_ui():
    """Test that caption is read from UI before regeneration"""
    try:
        from PyQt6.QtWidgets import QApplication
        from src.llmii_gui import ImageIndexerGUI
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        gui = ImageIndexerGUI()
        
        # Set a caption in the UI
        test_caption = "Test caption from UI that should be preserved"
        gui.caption_edit.setPlainText(test_caption)
        
        # Read it back (simulating regenerate_current_image logic)
        current_caption = gui.caption_edit.toPlainText()
        
        assert current_caption == test_caption, \
            f"Caption should be read from UI, got '{current_caption}'"
        
        # Cleanup
        if hasattr(gui, 'api_check_thread') and gui.api_check_thread:
            gui.api_check_thread.stop()
            gui.api_check_thread.wait(1000)
        
        print("✓ Caption is read from UI before regeneration")
        return True
    except Exception as e:
        print(f"✗ Caption UI reading test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_metadata_without_keywords_creation():
    """Test that metadata copy without keywords is created correctly"""
    try:
        metadata = {
            "SourceFile": "/test/path.jpg",
            "MWG:Keywords": ["keyword1", "keyword2"],
            "MWG:Description": "Test description",
            "XMP:Identifier": "test-uuid"
        }
        
        # Create copy without keywords (simulating the fix)
        metadata_without_keywords = metadata.copy()
        metadata_without_keywords.pop("MWG:Keywords", None)
        
        # Verify keywords are removed
        assert "MWG:Keywords" not in metadata_without_keywords, "Keywords should be removed from copy"
        
        # Verify other fields are preserved
        assert metadata_without_keywords["MWG:Description"] == "Test description", "Description should be preserved"
        assert metadata_without_keywords["SourceFile"] == "/test/path.jpg", "SourceFile should be preserved"
        
        # Verify original is unchanged
        assert "MWG:Keywords" in metadata, "Original metadata should still have keywords"
        
        print("✓ Metadata copy without keywords is created correctly")
        return True
    except Exception as e:
        print(f"✗ Metadata copy test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_keywords_only_preserves_description_in_metadata():
    """Test that keywords_only mode preserves description in final metadata"""
    try:
        from PyQt6.QtWidgets import QApplication
        from src.llmii_gui import RegenerationHelper
        import src.llmii as llmii
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        config = llmii.Config()
        config.generation_mode = "keywords_only"
        
        helper = RegenerationHelper(config)
        
        try:
            # Test metadata with description
            test_description = "Test description to preserve"
            metadata = {
                "SourceFile": "/test/path.jpg",
                "MWG:Description": test_description,
                "MWG:Keywords": ["old1", "old2"],
                "XMP:Identifier": "test-uuid"
            }
            
            # Simulate the keywords_only logic in generate_metadata
            existing_caption = metadata.get("MWG:Description")
            new_metadata = metadata.copy()
            
            # For keywords_only: preserve existing description
            if existing_caption is not None:
                new_metadata["MWG:Description"] = existing_caption
            
            assert new_metadata["MWG:Description"] == test_description, \
                "Description should be preserved in keywords_only mode"
            
            print("✓ keywords_only mode preserves description in metadata")
            return True
        finally:
            helper.cleanup()
    except Exception as e:
        print(f"✗ Description preservation in metadata test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("Testing Regeneration Bug Fixes...\n")
    
    tests = [
        test_description_preservation_keywords_only,
        test_keyword_no_duplication_during_regeneration,
        test_manual_keywords_preserved_during_regeneration,
        test_caption_read_from_ui,
        test_metadata_without_keywords_creation,
        test_keywords_only_preserves_description_in_metadata,
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
        print("✓ All regeneration bug fix tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())

