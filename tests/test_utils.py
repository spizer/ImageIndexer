#!/usr/bin/env python3
"""
Test utilities for ExifTool integration tests
"""
import os
import shutil
import tempfile
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
FIXTURES_DIR = PROJECT_ROOT / "tests" / "fixtures"

def verify_exiftool_available():
    """Check if ExifTool is installed and accessible"""
    try:
        import exiftool
        et = exiftool.ExifToolHelper()
        et.terminate()
        return True
    except Exception as e:
        print(f"ExifTool not available: {e}")
        return False

def setup_temp_directory():
    """Create temporary directory for test files"""
    return tempfile.mkdtemp(prefix="exiftool_test_")

def cleanup_temp_directory(directory):
    """Remove temporary directory and all contents"""
    if directory and os.path.exists(directory):
        shutil.rmtree(directory, ignore_errors=True)

def copy_fixture(fixture_name, destination_dir, new_name=None):
    """
    Copy a fixture file to a test directory, always overwriting if it exists.
    
    Args:
        fixture_name: Name of fixture file (e.g., "test_image.jpg")
        destination_dir: Directory to copy to
        new_name: Optional new name for the copied file (default: same as fixture)
    
    Returns:
        Path to the copied file
    """
    fixture_path = FIXTURES_DIR / fixture_name
    
    if not fixture_path.exists():
        raise FileNotFoundError(f"Fixture not found: {fixture_path}")
    
    if new_name is None:
        new_name = fixture_name
    
    dest_path = os.path.join(destination_dir, new_name)
    
    # Always overwrite - remove existing file if it exists
    if os.path.exists(dest_path):
        os.remove(dest_path)
    
    shutil.copy2(fixture_path, dest_path)
    
    return dest_path

def copy_fixture_with_sidecar(fixture_name, destination_dir, new_name=None):
    """
    Copy a fixture file and its sidecar (.xmp) if it exists, always overwriting.
    
    Args:
        fixture_name: Name of fixture file (e.g., "test_image.jpg")
        destination_dir: Directory to copy to
        new_name: Optional new name for the copied file
    
    Returns:
        Tuple of (image_path, sidecar_path or None)
    """
    image_path = copy_fixture(fixture_name, destination_dir, new_name)
    
    # Check if sidecar exists
    fixture_sidecar = FIXTURES_DIR / (fixture_name + ".xmp")
    sidecar_path = None
    
    if fixture_sidecar.exists():
        if new_name is None:
            new_name = fixture_name
        sidecar_path = os.path.join(destination_dir, new_name + ".xmp")
        
        # Always overwrite - remove existing sidecar if it exists
        if os.path.exists(sidecar_path):
            os.remove(sidecar_path)
        
        shutil.copy2(fixture_sidecar, sidecar_path)
    
    return (image_path, sidecar_path)

def check_backup_file_exists(file_path):
    """
    Check if ExifTool created a backup file
    
    Args:
        file_path: Path to the original file
    
    Returns:
        Path to backup file if it exists, None otherwise
    """
    backup_path = file_path + "_original"
    if os.path.exists(backup_path):
        return backup_path
    return None

def restore_from_backup(file_path):
    """
    Restore a file from its ExifTool backup
    
    Args:
        file_path: Path to the file to restore
    
    Returns:
        True if restored, False if backup doesn't exist
    """
    backup_path = check_backup_file_exists(file_path)
    if backup_path:
        shutil.copy2(backup_path, file_path)
        return True
    return False

def find_all_backup_files(directory):
    """
    Find all ExifTool backup files (_original) in a directory
    
    Args:
        directory: Directory to search
    
    Returns:
        List of backup file paths
    """
    backup_files = []
    if not os.path.exists(directory):
        return backup_files
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith("_original"):
                backup_files.append(os.path.join(root, file))
    
    return backup_files

def cleanup_backup_files(directory, file_paths=None):
    """
    Remove ExifTool backup files
    
    Args:
        directory: Directory to clean (if file_paths is None, finds all backups)
        file_paths: Optional list of specific file paths to clean backups for
    
    Returns:
        Number of backup files removed
    """
    removed_count = 0
    
    if file_paths:
        # Clean backups for specific files
        for file_path in file_paths:
            backup_path = check_backup_file_exists(file_path)
            if backup_path and os.path.exists(backup_path):
                os.remove(backup_path)
                removed_count += 1
    else:
        # Clean all backups in directory
        backup_files = find_all_backup_files(directory)
        for backup_path in backup_files:
            try:
                os.remove(backup_path)
                removed_count += 1
            except Exception as e:
                print(f"Warning: Could not remove backup {backup_path}: {e}")
    
    return removed_count

def get_fixture_list():
    """Get list of available fixture files"""
    if not FIXTURES_DIR.exists():
        return []
    
    fixtures = []
    for file in FIXTURES_DIR.iterdir():
        if file.is_file() and not file.name.startswith('.') and not file.suffix == '.xmp':
            fixtures.append(file.name)
    
    return sorted(fixtures)

