"""
Metadata read/write operations using ExifTool
"""
import os
import exiftool


# Comprehensive list of keyword fields to read/write
KEYWORD_FIELDS = [
    "Keywords", "IPTC:Keywords", "Composite:keywords", "Subject",
    "DC:Subject", "XMP:Subject", "XMP-dc:Subject", "MWG:Keywords"
]

# Comprehensive list of caption/description fields to read/write
CAPTION_FIELDS = [
    "Description", "XMP:Description", "ImageDescription", "DC:Description",
    "EXIF:ImageDescription", "Composite:Description", "Caption", "IPTC:Caption",
    "Composite:Caption", "IPTC:Caption-Abstract", "XMP-dc:Description",
    "PNG:Description", "MWG:Description"
]

# Fields to delete when clearing metadata
DELETE_KEYWORD_FIELDS = [
    "-Keywords=",
    "-IPTC:Keywords=",
    "-XMP:Subject=",
    "-XMP-dc:Subject=",
    "-DC:Subject=",
    "-Subject=",
    "-Composite:Keywords=",
    "-MWG:Keywords=",
]

DELETE_DESCRIPTION_FIELDS = [
    "-Description=",
    "-XMP:Description=",
    "-XMP-dc:Description=",
    "-DC:Description=",
    "-ImageDescription=",
    "-EXIF:ImageDescription=",
    "-Composite:Description=",
    "-Caption=",
    "-IPTC:Caption=",
    "-IPTC:Caption-Abstract=",
    "-MWG:Description="
]


def read_metadata(file_path, et, use_sidecar=False):
    """
    Read current metadata from file using ExifTool.
    
    Args:
        file_path: Path to the image file
        et: ExifToolHelper instance
        use_sidecar: Whether to read from sidecar .xmp file
        
    Returns:
        Dictionary of metadata fields, or empty dict on error
    """
    try:
        # Check for sidecar file
        if use_sidecar and os.path.exists(file_path + ".xmp"):
            file_path = file_path + ".xmp"
        
        # Read metadata - request all keyword and caption fields
        # This ensures we read metadata regardless of which field ExifTool returns it in
        exiftool_fields = (
            ["SourceFile", "XMP:Identifier", "XMP:Status"] +
            KEYWORD_FIELDS +
            CAPTION_FIELDS
        )
        
        result = et.get_tags([file_path], tags=exiftool_fields)
        if result and len(result) > 0:
            return result[0]
        return {}
    except Exception as e:
        print(f"Error reading metadata: {e}")
        return {}


def write_metadata(file_path, metadata, et, use_sidecar=False, no_backup=False, dry_run=False):
    """
    Write metadata to file using ExifTool with two-pass approach:
    1. Delete all existing keyword/description fields using separate ExifTool instance
    2. Write new metadata using main ExifTool instance
    
    Args:
        file_path: Path to the image file
        metadata: Metadata dictionary to write
        et: Main ExifToolHelper instance for writing
        use_sidecar: Whether to write to sidecar .xmp file
        no_backup: Whether to skip creating backup files
        dry_run: If True, don't actually write (for testing)
        
    Returns:
        True if successful, False otherwise
    """
    if dry_run:
        print("Dry run. Not writing.")
        return True
    
    try:
        params = ["-P"]
        
        if no_backup or use_sidecar:
            params.append("-overwrite_original")
        
        # Adjust file path for sidecar if needed
        write_path = file_path
        if use_sidecar:
            write_path = file_path + ".xmp"
        
        # FIRST PASS: Use a SEPARATE ExifTool instance for deletion
        # This prevents any state/cache issues from interfering with deletion
        # The deletion instance is created, used, and terminated before writing
        delete_et = None
        try:
            # Create a fresh ExifTool instance specifically for deletion
            delete_et = exiftool.ExifToolHelper(encoding='utf-8')
            
            # Delete ALL keyword and description fields comprehensively
            delete_params = DELETE_KEYWORD_FIELDS + DELETE_DESCRIPTION_FIELDS
            
            if no_backup or use_sidecar:
                delete_params.append("-overwrite_original")
            
            delete_params.append("-P")
            delete_params.append(write_path)
            
            # Execute deletion with separate instance
            print(f"DEBUG WRITE: Deleting with separate ExifTool instance, params: {delete_params}")
            delete_et.execute(*delete_params)
            print(f"DEBUG WRITE: Deletion completed with separate instance")
            
        except Exception as delete_error:
            print(f"DEBUG WRITE: Warning - deletion failed: {delete_error}")
            # Continue anyway - the write might still work
        finally:
            # CRITICAL: Terminate the deletion instance before proceeding
            # This ensures no state is carried over to the main instance
            if delete_et is not None:
                try:
                    delete_et.terminate()
                    print(f"DEBUG WRITE: Deletion instance terminated")
                except Exception as term_error:
                    print(f"DEBUG WRITE: Warning - termination error: {term_error}")
        
        # SECOND PASS: Use the main instance for writing
        # The deletion instance is now terminated, so this is a clean write
        print(f"DEBUG WRITE: Writing metadata with main instance, keywords: {metadata.get('MWG:Keywords', 'NOT FOUND')}")
        et.set_tags(write_path, tags=metadata, params=params)
        
        return True
        
    except Exception as e:
        print(f"Error writing metadata to {file_path}: {str(e)}")
        return False

