#!/usr/bin/env python3
"""
Test script for Backup Cleanup functionality (Phase 4)
Tests that backup files can be found and cleaned up properly.
"""
import sys
import os

project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from tests.test_utils import (
    verify_exiftool_available,
    setup_temp_directory,
    cleanup_temp_directory,
    copy_fixture,
    check_backup_file_exists,
    find_all_backup_files,
    cleanup_backup_files
)

def test_backup_file_creation():
    """Test that backup files are created when writing"""
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
                # Write metadata WITHOUT no_backup (should create backup)
                metadata = {
                    "MWG:Keywords": ["backup_test"],
                    "MWG:Description": "Testing backup creation"
                }
                
                result = helper.write_metadata(
                    test_file,
                    metadata,
                    use_sidecar=False,
                    no_backup=False  # Backups enabled
                )
                
                assert result == True, "Write should succeed"
                
                # Verify backup was created
                backup_path = check_backup_file_exists(test_file)
                assert backup_path is not None, "Backup file should be created"
                assert os.path.exists(backup_path), "Backup file should exist"
                
                print("✓ Backup file created correctly")
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

def test_find_all_backup_files():
    """Test finding all backup files in a directory"""
    if not verify_exiftool_available():
        print("✗ ExifTool not available - skipping test")
        return False
    
    try:
        from src.llmii_gui import RegenerationHelper
        import src.llmii as llmii
        
        temp_dir = setup_temp_directory()
        
        # Create multiple test files
        test_file1 = copy_fixture("test_image.jpg", temp_dir, "test1.jpg")
        test_file2 = copy_fixture("test_image.jpg", temp_dir, "test2.jpg")
        
        try:
            config = llmii.Config()
            helper = RegenerationHelper(config)
            
            try:
                # Write to both files (creating backups)
                metadata = {"MWG:Keywords": ["test"]}
                helper.write_metadata(test_file1, metadata, no_backup=False)
                helper.write_metadata(test_file2, metadata, no_backup=False)
                
                # Find all backups
                backup_files = find_all_backup_files(temp_dir)
                
                assert len(backup_files) == 2, f"Should find 2 backup files, found {len(backup_files)}"
                assert any("test1.jpg_original" in bf for bf in backup_files), "Should find test1 backup"
                assert any("test2.jpg_original" in bf for bf in backup_files), "Should find test2 backup"
                
                print("✓ Found all backup files correctly")
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

def test_cleanup_specific_backup():
    """Test cleaning up backup for a specific file"""
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
                # Create backup
                metadata = {"MWG:Keywords": ["test"]}
                helper.write_metadata(test_file, metadata, no_backup=False)
                
                # Verify backup exists
                assert check_backup_file_exists(test_file) is not None, "Backup should exist"
                
                # Clean up specific backup
                removed = cleanup_backup_files(temp_dir, [test_file])
                
                assert removed == 1, "Should remove 1 backup file"
                assert check_backup_file_exists(test_file) is None, "Backup should be removed"
                
                print("✓ Cleaned up specific backup file correctly")
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

def test_cleanup_all_backups():
    """Test cleaning up all backup files in a directory"""
    if not verify_exiftool_available():
        print("✗ ExifTool not available - skipping test")
        return False
    
    try:
        from src.llmii_gui import RegenerationHelper
        import src.llmii as llmii
        
        temp_dir = setup_temp_directory()
        
        # Create multiple test files
        test_file1 = copy_fixture("test_image.jpg", temp_dir, "test1.jpg")
        test_file2 = copy_fixture("test_image.jpg", temp_dir, "test2.jpg")
        
        try:
            config = llmii.Config()
            helper = RegenerationHelper(config)
            
            try:
                # Create backups for both files
                metadata = {"MWG:Keywords": ["test"]}
                helper.write_metadata(test_file1, metadata, no_backup=False)
                helper.write_metadata(test_file2, metadata, no_backup=False)
                
                # Verify backups exist
                assert len(find_all_backup_files(temp_dir)) == 2, "Should have 2 backups"
                
                # Clean up all backups
                removed = cleanup_backup_files(temp_dir)
                
                assert removed == 2, "Should remove 2 backup files"
                assert len(find_all_backup_files(temp_dir)) == 0, "Should have no backups remaining"
                
                print("✓ Cleaned up all backup files correctly")
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
    """Run all backup cleanup tests"""
    print("Testing Backup Cleanup Functionality (Phase 4)...\n")
    
    tests = [
        test_backup_file_creation,
        test_find_all_backup_files,
        test_cleanup_specific_backup,
        test_cleanup_all_backups,
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
        print("✓ All backup cleanup tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())


