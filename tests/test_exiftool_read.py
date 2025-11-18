#!/usr/bin/env python3
"""
Integration tests for ExifTool read operations
"""
import sys
import os

project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from tests.test_utils import (
    verify_exiftool_available,
    setup_temp_directory,
    cleanup_temp_directory,
    copy_fixture
)

def test_read_metadata_from_clean_file():
    """Test reading metadata from a file with no existing metadata"""
    if not verify_exiftool_available():
        print("✗ ExifTool not available - skipping test")
        return False
    
    try:
        from src.llmii_gui import RegenerationHelper
        import src.llmii as llmii
        
        temp_dir = setup_temp_directory()
        test_file = copy_fixture("test_image.jpg", temp_dir)
        
        try:
            config = llmii.Config()
            helper = RegenerationHelper(config)
            
            try:
                # Read metadata
                metadata = helper.read_metadata(test_file)
                
                # Should return a dict (may be empty)
                assert isinstance(metadata, dict), "Metadata should be a dictionary"
                assert "SourceFile" in metadata, "Should have SourceFile"
                
                print("✓ Read metadata from clean file")
                return True
                
            finally:
                helper.cleanup()
                
        finally:
            cleanup_temp_directory(temp_dir)
            
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_read_existing_keywords():
    """Test reading keywords from a file with existing keywords"""
    if not verify_exiftool_available():
        print("✗ ExifTool not available - skipping test")
        return False
    
    try:
        from src.llmii_gui import RegenerationHelper
        import src.llmii as llmii
        
        temp_dir = setup_temp_directory()
        test_file = copy_fixture("test_with_keywords.jpg", temp_dir)
        
        try:
            config = llmii.Config()
            helper = RegenerationHelper(config)
            
            try:
                # Read metadata
                metadata = helper.read_metadata(test_file)
                
                # Check for keywords in XMP:Subject
                keywords = metadata.get("XMP:Subject", [])
                
                # Convert to list if string
                if isinstance(keywords, str):
                    keywords = [k.strip() for k in keywords.split(',')] if keywords else []
                elif not isinstance(keywords, list):
                    keywords = []
                
                # Should have some keywords
                assert len(keywords) > 0, f"Should read existing keywords from XMP:Subject, got: {keywords}"
                
                print("✓ Read existing keywords correctly")
                return True
                
            finally:
                helper.cleanup()
                
        finally:
            cleanup_temp_directory(temp_dir)
            
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_read_existing_description():
    """Test reading description from a file with existing description"""
    if not verify_exiftool_available():
        print("✗ ExifTool not available - skipping test")
        return False
    
    try:
        from src.llmii_gui import RegenerationHelper
        import src.llmii as llmii
        
        temp_dir = setup_temp_directory()
        test_file = copy_fixture("test_with_description.jpg", temp_dir)
        
        try:
            config = llmii.Config()
            helper = RegenerationHelper(config)
            
            try:
                # Read metadata
                metadata = helper.read_metadata(test_file)
                
                # Check for description in XMP:Description
                description = metadata.get("XMP:Description")
                
                assert description is not None, f"Should read existing description from XMP:Description, got keys: {list(metadata.keys())}"
                assert len(description) > 0, "Description should not be empty"
                
                print("✓ Read existing description correctly")
                return True
                
            finally:
                helper.cleanup()
                
        finally:
            cleanup_temp_directory(temp_dir)
            
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all read tests"""
    print("Testing ExifTool Read Operations...\n")
    
    tests = [
        test_read_metadata_from_clean_file,
        test_read_existing_keywords,
        test_read_existing_description,
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
        print("✓ All read tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())

