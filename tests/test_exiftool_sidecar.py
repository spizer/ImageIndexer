#!/usr/bin/env python3
"""
Integration tests for ExifTool sidecar file operations
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

def test_write_to_sidecar():
    """Test writing metadata to sidecar file"""
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
                # Write metadata to sidecar
                test_keywords = ["sidecar1", "sidecar2"]
                test_description = "Sidecar test description"
                metadata = {
                    "MWG:Keywords": test_keywords,
                    "MWG:Description": test_description
                }
                
                result = helper.write_metadata(
                    test_file,
                    metadata,
                    use_sidecar=True,
                    no_backup=True
                )
                
                assert result == True, "Write should succeed"
                
                # Check sidecar was created
                sidecar_path = test_file + ".xmp"
                assert os.path.exists(sidecar_path), "Sidecar file should be created"
                
                # Read back (should read from sidecar when use_sidecar=True)
                config.use_sidecar = True
                read_metadata = helper.read_metadata(test_file)
                
                # Verify metadata was written
                keywords = read_metadata.get("XMP:Subject", [])
                # Convert to list if string
                if isinstance(keywords, str):
                    keywords = [k.strip() for k in keywords.split(',')] if keywords else []
                elif not isinstance(keywords, list):
                    keywords = []
                
                description = read_metadata.get("XMP:Description")
                
                assert len(keywords) > 0, "Keywords should be readable from sidecar (XMP:Subject)"
                assert description == test_description, "Description should match (XMP:Description)"
                
                print("✓ Write to sidecar works correctly")
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

def test_sidecar_takes_priority_when_enabled():
    """Test that sidecar takes priority when use_sidecar=True"""
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
                # First, write to image file directly
                image_metadata = {
                    "MWG:Keywords": ["image_keyword"],
                    "MWG:Description": "Image description"
                }
                helper.write_metadata(test_file, image_metadata, use_sidecar=False, no_backup=True)
                
                # Then write to sidecar
                sidecar_metadata = {
                    "MWG:Keywords": ["sidecar_keyword"],
                    "MWG:Description": "Sidecar description"
                }
                helper.write_metadata(test_file, sidecar_metadata, use_sidecar=True, no_backup=True)
                
                # Read with sidecar enabled - should get sidecar data
                config.use_sidecar = True
                read_metadata = helper.read_metadata(test_file)
                
                keywords = read_metadata.get("XMP:Subject", [])
                # Convert to list if string
                if isinstance(keywords, str):
                    keywords = [k.strip() for k in keywords.split(',')] if keywords else []
                elif not isinstance(keywords, list):
                    keywords = []
                
                description = read_metadata.get("XMP:Description")
                
                # Should read from sidecar, not image
                keywords_lower = [kw.lower() for kw in keywords]
                assert "sidecar_keyword" in keywords_lower, "Should read from sidecar (XMP:Subject)"
                assert "image_keyword" not in keywords_lower, "Should not read from image when sidecar exists"
                assert description == "Sidecar description", "Should read sidecar description (XMP:Description)"
                
                print("✓ Sidecar takes priority when enabled")
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

def test_sidecar_not_used_when_disabled():
    """Test that sidecar is not used when use_sidecar=False"""
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
                # Write to sidecar first
                sidecar_metadata = {
                    "MWG:Keywords": ["sidecar_keyword"],
                    "MWG:Description": "Sidecar description"
                }
                helper.write_metadata(test_file, sidecar_metadata, use_sidecar=True, no_backup=True)
                
                # Write to image
                image_metadata = {
                    "MWG:Keywords": ["image_keyword"],
                    "MWG:Description": "Image description"
                }
                helper.write_metadata(test_file, image_metadata, use_sidecar=False, no_backup=True)
                
                # Read with sidecar disabled - should get image data
                config.use_sidecar = False
                read_metadata = helper.read_metadata(test_file)
                
                keywords = read_metadata.get("XMP:Subject", [])
                # Convert to list if string
                if isinstance(keywords, str):
                    keywords = [k.strip() for k in keywords.split(',')] if keywords else []
                elif not isinstance(keywords, list):
                    keywords = []
                
                description = read_metadata.get("XMP:Description")
                
                # Should read from image, not sidecar
                keywords_lower = [kw.lower() for kw in keywords]
                assert "image_keyword" in keywords_lower, "Should read from image (XMP:Subject)"
                assert description == "Image description", "Should read image description (XMP:Description)"
                
                print("✓ Sidecar not used when disabled")
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
    """Run all sidecar tests"""
    print("Testing ExifTool Sidecar Operations...\n")
    
    tests = [
        test_write_to_sidecar,
        test_sidecar_takes_priority_when_enabled,
        test_sidecar_not_used_when_disabled,
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
        print("✓ All sidecar tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())

