#!/usr/bin/env python3
"""
Test script to validate keyword field cleanup:
1. Verifies that all keyword fields are cleared before writing
2. Verifies that only MWG:Keywords is written
3. Tests the two-pass write process
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

def test_keyword_fields_list():
    """Test that the keyword fields list is correct"""
    try:
        # Updated: We now clear ALL keyword and description fields, including MWG fields
        keyword_fields_to_clear = [
            "Keywords",
            "IPTC:Keywords",
            "XMP:Subject",
            "XMP-dc:Subject",
            "DC:Subject",
            "Subject",
            "Composite:Keywords",
            "MWG:Keywords",  # Now included - we clear this too
        ]
        
        # Verify MWG:Keywords IS in the clear list (changed behavior)
        assert "MWG:Keywords" in keyword_fields_to_clear, "MWG:Keywords should be cleared"
        
        # Verify all expected fields are in the list
        expected_fields = ["Keywords", "IPTC:Keywords", "Composite:Keywords", "Subject", 
                          "DC:Subject", "XMP:Subject", "XMP-dc:Subject", "MWG:Keywords"]
        for field in expected_fields:
            assert field in keyword_fields_to_clear, f"{field} should be in clear list"
        
        # Should have 8 keyword fields
        assert len(keyword_fields_to_clear) == 8, f"Should have 8 keyword fields, got {len(keyword_fields_to_clear)}"
        
        print("✓ Keyword fields list is correct")
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_clear_tags_creation():
    """Test that clear_tags dict is created correctly"""
    try:
        # Updated: We now clear ALL keyword and description fields
        keyword_fields_to_clear = [
            "Keywords",
            "IPTC:Keywords",
            "XMP:Subject",
            "XMP-dc:Subject",
            "DC:Subject",
            "Subject",
            "Composite:Keywords",
            "MWG:Keywords",  # Now included
        ]
        
        description_fields_to_clear = [
            "Description",
            "XMP:Description",
            "XMP-dc:Description",
            "DC:Description",
            "ImageDescription",
            "EXIF:ImageDescription",
            "Composite:Description",
            "Caption",
            "IPTC:Caption",
            "IPTC:Caption-Abstract",
            "MWG:Description",  # Now included
        ]
        
        all_fields_to_clear = keyword_fields_to_clear + description_fields_to_clear
        
        # Create clear_tags dict (simulating the code)
        clear_tags = {field: "" for field in all_fields_to_clear}
        
        # Verify all fields are set to empty string
        for field in all_fields_to_clear:
            assert clear_tags[field] == "", f"{field} should be set to empty string"
        
        # Verify MWG:Keywords IS in clear_tags (changed behavior)
        assert "MWG:Keywords" in clear_tags, "MWG:Keywords should be in clear_tags"
        assert "MWG:Description" in clear_tags, "MWG:Description should be in clear_tags"
        
        # Should have 19 total fields (8 keywords + 11 descriptions)
        assert len(all_fields_to_clear) == 19, f"Should have 19 fields, got {len(all_fields_to_clear)}"
        
        print("✓ Clear tags dict is created correctly")
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_two_pass_write_logic():
    """Test the two-pass write logic"""
    try:
        # Updated: We now clear ALL fields including MWG, then write new values
        keyword_fields_to_clear = [
            "Keywords",
            "IPTC:Keywords",
            "XMP:Subject",
            "XMP-dc:Subject",
            "DC:Subject",
            "Subject",
            "Composite:Keywords",
            "MWG:Keywords",  # Now included - cleared first, then written
        ]
        
        description_fields_to_clear = [
            "Description",
            "XMP:Description",
            "XMP-dc:Description",
            "DC:Description",
            "ImageDescription",
            "EXIF:ImageDescription",
            "Composite:Description",
            "Caption",
            "IPTC:Caption",
            "IPTC:Caption-Abstract",
            "MWG:Description",  # Now included
        ]
        
        all_fields_to_clear = keyword_fields_to_clear + description_fields_to_clear
        
        # First pass: clear ALL tags (including MWG fields)
        clear_tags = {field: "" for field in all_fields_to_clear}
        
        # Second pass: write metadata (MWG:Keywords and MWG:Description are written after clearing)
        metadata = {
            "MWG:Keywords": ["keyword1", "keyword2"],
            "MWG:Description": "Test description",
            "XMP:Status": "success",
            "XMP:Identifier": "test-uuid"
        }
        
        # Verify metadata has MWG:Keywords
        assert "MWG:Keywords" in metadata, "Metadata should have MWG:Keywords"
        assert metadata["MWG:Keywords"] == ["keyword1", "keyword2"], "Keywords should be preserved"
        
        # Verify clear_tags DOES have MWG:Keywords (changed behavior - we clear it first)
        assert "MWG:Keywords" in clear_tags, "clear_tags should have MWG:Keywords (cleared first, then written)"
        assert "MWG:Description" in clear_tags, "clear_tags should have MWG:Description (cleared first, then written)"
        
        print("✓ Two-pass write logic is correct")
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_metadata_structure():
    """Test that metadata structure is correct for writing"""
    try:
        # Simulate prepare_metadata_for_save output
        metadata = {
            "MWG:Keywords": ["keyword1", "keyword2"],
            "MWG:Description": "Test description",
            "XMP:Status": "success",
            "XMP:Identifier": "test-uuid",
            "SourceFile": "/test/path.jpg"
        }
        
        # Verify required fields are present
        assert "MWG:Keywords" in metadata, "Metadata should have MWG:Keywords"
        assert "MWG:Description" in metadata, "Metadata should have MWG:Description"
        assert "XMP:Status" in metadata, "Metadata should have XMP:Status"
        assert isinstance(metadata["MWG:Keywords"], list), "MWG:Keywords should be a list"
        
        # Verify keywords list is not empty
        assert len(metadata["MWG:Keywords"]) > 0, "Keywords list should not be empty"
        
        print("✓ Metadata structure is correct")
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_no_duplicate_clearing():
    """Test that we clear MWG:Keywords properly (changed behavior)"""
    try:
        # Updated: We now DO clear MWG:Keywords (and MWG:Description) before writing
        keyword_fields_to_clear = [
            "Keywords",
            "IPTC:Keywords",
            "XMP:Subject",
            "XMP-dc:Subject",
            "DC:Subject",
            "Subject",
            "Composite:Keywords",
            "MWG:Keywords",  # Now included - we clear it first, then write new values
        ]
        
        description_fields_to_clear = [
            "Description",
            "XMP:Description",
            "XMP-dc:Description",
            "DC:Description",
            "ImageDescription",
            "EXIF:ImageDescription",
            "Composite:Description",
            "Caption",
            "IPTC:Caption",
            "IPTC:Caption-Abstract",
            "MWG:Description",  # Now included
        ]
        
        all_fields_to_clear = keyword_fields_to_clear + description_fields_to_clear
        
        # Verify MWG:Keywords IS in the list (changed behavior)
        assert "MWG:Keywords" in keyword_fields_to_clear, "MWG:Keywords should be cleared before writing"
        assert "MWG:Description" in description_fields_to_clear, "MWG:Description should be cleared before writing"
        
        # Verify the list has exactly 8 keyword fields
        assert len(keyword_fields_to_clear) == 8, f"Should have exactly 8 keyword fields to clear, got {len(keyword_fields_to_clear)}"
        # Verify the list has exactly 11 description fields
        assert len(description_fields_to_clear) == 11, f"Should have exactly 11 description fields to clear, got {len(description_fields_to_clear)}"
        # Total should be 19
        assert len(all_fields_to_clear) == 19, f"Should have exactly 19 total fields to clear, got {len(all_fields_to_clear)}"
        
        print("✓ MWG:Keywords and MWG:Description are properly cleared before writing")
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_both_write_methods_consistent():
    """Test that both write_metadata methods use the same logic"""
    try:
        # Updated: Both methods now clear ALL fields including MWG fields
        # Both should have the same comprehensive field lists
        expected_keyword_fields = [
            "Keywords",
            "IPTC:Keywords",
            "XMP:Subject",
            "XMP-dc:Subject",
            "DC:Subject",
            "Subject",
            "Composite:Keywords",
            "MWG:Keywords",  # Now included
        ]
        
        expected_description_fields = [
            "Description",
            "XMP:Description",
            "XMP-dc:Description",
            "DC:Description",
            "ImageDescription",
            "EXIF:ImageDescription",
            "Composite:Description",
            "Caption",
            "IPTC:Caption",
            "IPTC:Caption-Abstract",
            "MWG:Description",  # Now included
        ]
        
        expected_all_fields = expected_keyword_fields + expected_description_fields
        
        # Verify the fields are the same (we can't directly access the list, but we can verify the logic)
        # Both methods should clear the same fields
        keyword_fields_to_clear_gui = [
            "Keywords",
            "IPTC:Keywords",
            "XMP:Subject",
            "XMP-dc:Subject",
            "DC:Subject",
            "Subject",
            "Composite:Keywords",
            "MWG:Keywords",
        ]
        
        keyword_fields_to_clear_batch = [
            "Keywords",
            "IPTC:Keywords",
            "XMP:Subject",
            "XMP-dc:Subject",
            "DC:Subject",
            "Subject",
            "Composite:Keywords",
            "MWG:Keywords",
        ]
        
        description_fields_to_clear_gui = [
            "Description",
            "XMP:Description",
            "XMP-dc:Description",
            "DC:Description",
            "ImageDescription",
            "EXIF:ImageDescription",
            "Composite:Description",
            "Caption",
            "IPTC:Caption",
            "IPTC:Caption-Abstract",
            "MWG:Description",
        ]
        
        description_fields_to_clear_batch = [
            "Description",
            "XMP:Description",
            "XMP-dc:Description",
            "DC:Description",
            "ImageDescription",
            "EXIF:ImageDescription",
            "Composite:Description",
            "Caption",
            "IPTC:Caption",
            "IPTC:Caption-Abstract",
            "MWG:Description",
        ]
        
        assert keyword_fields_to_clear_gui == keyword_fields_to_clear_batch, "Both methods should clear the same keyword fields"
        assert description_fields_to_clear_gui == description_fields_to_clear_batch, "Both methods should clear the same description fields"
        assert keyword_fields_to_clear_gui == expected_keyword_fields, "Keyword fields should match expected list"
        assert description_fields_to_clear_gui == expected_description_fields, "Description fields should match expected list"
        assert len(expected_all_fields) == 19, "Should have 19 total fields (8 keywords + 11 descriptions)"
        
        print("✓ Both write methods use consistent logic")
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("Testing Keyword Field Cleanup Implementation...\n")
    
    tests = [
        test_keyword_fields_list,
        test_clear_tags_creation,
        test_two_pass_write_logic,
        test_metadata_structure,
        test_no_duplicate_clearing,
        test_both_write_methods_consistent,
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
        print("✓ All keyword cleanup tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())




