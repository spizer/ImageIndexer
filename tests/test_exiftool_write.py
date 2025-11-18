#!/usr/bin/env python3
"""
Integration tests for ExifTool write operations
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

def test_write_keywords_roundtrip():
    """Test writing keywords and reading them back"""
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
                # Write keywords
                test_keywords = ["write_test1", "write_test2", "write_test3"]
                metadata = {
                    "MWG:Keywords": test_keywords,
                    "MWG:Description": "Write test description"
                }
                
                result = helper.write_metadata(test_file, metadata, no_backup=True)
                assert result == True, "Write should succeed"
                
                # Read back
                read_metadata = helper.read_metadata(test_file)
                
                # Check keywords in XMP:Subject
                keywords = read_metadata.get("XMP:Subject", [])
                
                # Convert to list if string
                if isinstance(keywords, str):
                    keywords = [k.strip() for k in keywords.split(',')] if keywords else []
                elif not isinstance(keywords, list):
                    keywords = []
                
                # Verify keywords were written
                assert len(keywords) > 0, f"Keywords should be readable from XMP:Subject, got: {keywords}"
                # Check that our keywords are present (case-insensitive)
                keywords_lower = [kw.lower() for kw in keywords]
                for test_kw in test_keywords:
                    assert test_kw.lower() in keywords_lower, f"Keyword '{test_kw}' should be present in {keywords_lower}"
                
                print("✓ Write/read keywords roundtrip works")
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

def test_write_description_roundtrip():
    """Test writing description and reading it back"""
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
                # Write description
                test_description = "This is a test description for write/read roundtrip"
                metadata = {
                    "MWG:Description": test_description
                }
                
                result = helper.write_metadata(test_file, metadata, no_backup=True)
                assert result == True, "Write should succeed"
                
                # Read back
                read_metadata = helper.read_metadata(test_file)
                
                # Check description in XMP:Description
                description = read_metadata.get("XMP:Description")
                
                assert description == test_description, f"Description mismatch: got '{description}', expected '{test_description}'"
                
                print("✓ Write/read description roundtrip works")
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

def test_two_pass_write_prevents_duplicates():
    """Test that two-pass write (delete then write) prevents duplicates"""
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
                # Read existing keywords from XMP:Subject
                initial_metadata = helper.read_metadata(test_file)
                initial_keywords = initial_metadata.get("XMP:Subject", [])
                # Convert to list if string
                if isinstance(initial_keywords, str):
                    initial_keywords = [k.strip() for k in initial_keywords.split(',')] if initial_keywords else []
                elif not isinstance(initial_keywords, list):
                    initial_keywords = []
                initial_count = len(initial_keywords)
                
                # Write new keywords (should clear old ones first)
                new_keywords = ["new1", "new2", "new3"]
                metadata = {
                    "MWG:Keywords": new_keywords
                }
                
                result = helper.write_metadata(test_file, metadata, no_backup=True)
                assert result == True, "Write should succeed"
                
                # Read back from XMP:Subject
                read_metadata = helper.read_metadata(test_file)
                final_keywords = read_metadata.get("XMP:Subject", [])
                # Convert to list if string
                if isinstance(final_keywords, str):
                    final_keywords = [k.strip() for k in final_keywords.split(',')] if final_keywords else []
                elif not isinstance(final_keywords, list):
                    final_keywords = []
                
                # Should only have new keywords (no duplicates from old ones)
                final_count = len(final_keywords)
                assert final_count == len(new_keywords), f"Should have {len(new_keywords)} keywords, got {final_count}"
                
                # Verify no old keywords remain
                final_lower = [kw.lower() for kw in final_keywords]
                for old_kw in initial_keywords:
                    assert old_kw.lower() not in final_lower, f"Old keyword '{old_kw}' should not be present"
                
                print("✓ Two-pass write prevents duplicates")
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
    """Run all write tests"""
    print("Testing ExifTool Write Operations...\n")
    
    tests = [
        test_write_keywords_roundtrip,
        test_write_description_roundtrip,
        test_two_pass_write_prevents_duplicates,
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
        print("✓ All write tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())

