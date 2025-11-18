#!/usr/bin/env python3
"""
Performance tests for ExifTool operations
"""
import sys
import os
import time

project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from tests.test_utils import (
    verify_exiftool_available,
    setup_temp_directory,
    cleanup_temp_directory,
    copy_fixture
)

def test_write_performance():
    """Test performance of write operations"""
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
                # Measure write time
                metadata = {
                    "MWG:Keywords": ["perf1", "perf2", "perf3"],
                    "MWG:Description": "Performance test"
                }
                
                start_time = time.time()
                result = helper.write_metadata(test_file, metadata, no_backup=True)
                write_time = time.time() - start_time
                
                assert result == True, "Write should succeed"
                
                # Write should complete in reasonable time (< 5 seconds)
                assert write_time < 5.0, f"Write took {write_time:.2f}s, should be < 5s"
                
                print(f"✓ Write performance: {write_time:.3f}s")
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

def test_read_performance():
    """Test performance of read operations"""
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
                # Measure read time
                start_time = time.time()
                metadata = helper.read_metadata(test_file)
                read_time = time.time() - start_time
                
                assert isinstance(metadata, dict), "Should return metadata"
                
                # Read should complete in reasonable time (< 2 seconds)
                assert read_time < 2.0, f"Read took {read_time:.2f}s, should be < 2s"
                
                print(f"✓ Read performance: {read_time:.3f}s")
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

def test_multiple_write_performance():
    """Test performance of multiple sequential writes"""
    if not verify_exiftool_available():
        print("✗ ExifTool not available - skipping test")
        return False
    
    try:
        from src.llmii_gui import RegenerationHelper
        import src.llmii as llmii
        
        temp_dir = setup_temp_directory()
        
        # Create multiple test files
        test_files = []
        for i in range(5):
            test_file = copy_fixture("test_image.jpg", temp_dir, f"test_{i}.jpg")
            test_files.append(test_file)
        
        try:
            config = llmii.Config()
            helper = RegenerationHelper(config)
            
            try:
                # Measure time for multiple writes
                start_time = time.time()
                
                for i, test_file in enumerate(test_files):
                    metadata = {
                        "MWG:Keywords": [f"keyword_{i}"],
                        "MWG:Description": f"Test {i}"
                    }
                    helper.write_metadata(test_file, metadata, no_backup=True)
                
                total_time = time.time() - start_time
                avg_time = total_time / len(test_files)
                
                # Average write should be reasonable (< 3 seconds per file)
                assert avg_time < 3.0, f"Average write time {avg_time:.2f}s, should be < 3s"
                
                print(f"✓ Multiple writes performance: {avg_time:.3f}s per file ({total_time:.3f}s total)")
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
    """Run all performance tests"""
    print("Testing ExifTool Performance...\n")
    
    tests = [
        test_write_performance,
        test_read_performance,
        test_multiple_write_performance,
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
        print("✓ All performance tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())


