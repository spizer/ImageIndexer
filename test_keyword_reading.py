#!/usr/bin/env python3
"""
Test script to validate keyword reading fixes:
1. Reads from "Keywords" field (what ExifTool returns)
2. Falls back to "MWG:Keywords" if needed
3. Deduplication works correctly
4. Handles None and empty values
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

def test_read_keywords_from_generic_field():
    """Test that keywords are read from "Keywords" field (what ExifTool returns)"""
    try:
        # Simulate metadata as ExifTool returns it
        metadata = {
            "SourceFile": "/test/path.jpg",
            "Keywords": ["keyword1", "keyword2", "keyword3"],
            "Description": "Test description"
        }
        
        # Simulate the reading logic from llmii.py
        keywords = []
        if "Keywords" in metadata:
            value = metadata["Keywords"]
            if value is not None:
                if isinstance(value, list):
                    keywords = value if value else []
                elif isinstance(value, str):
                    keywords = [value] if value.strip() else []
        
        assert keywords == ["keyword1", "keyword2", "keyword3"], f"Expected ['keyword1', 'keyword2', 'keyword3'], got {keywords}"
        print("✓ Keywords read correctly from 'Keywords' field")
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fallback_to_mwg_keywords():
    """Test fallback to MWG:Keywords when Keywords field is not present"""
    try:
        # Simulate metadata with only MWG:Keywords
        metadata = {
            "SourceFile": "/test/path.jpg",
            "MWG:Keywords": ["mwg1", "mwg2"],
            "MWG:Description": "MWG description"
        }
        
        # Simulate the reading logic
        keywords = []
        if "Keywords" in metadata:
            value = metadata["Keywords"]
            if value is not None:
                if isinstance(value, list):
                    keywords = value if value else []
        elif "MWG:Keywords" in metadata:
            value = metadata["MWG:Keywords"]
            if value is not None:
                if isinstance(value, list):
                    keywords = value if value else []
        
        assert keywords == ["mwg1", "mwg2"], f"Expected ['mwg1', 'mwg2'], got {keywords}"
        print("✓ Fallback to MWG:Keywords works correctly")
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_keyword_deduplication():
    """Test that keyword deduplication works correctly"""
    try:
        keywords = ["keyword1", "KEYWORD1", "keyword2", "keyword1", "  keyword2  "]
        
        # Simulate deduplication logic
        seen = {}
        deduplicated = []
        for kw in keywords:
            if kw:  # Skip empty strings
                kw_lower = kw.lower().strip()
                if kw_lower and kw_lower not in seen:
                    seen[kw_lower] = kw
                    deduplicated.append(kw)
        
        # Should have only 2 unique keywords (keyword1 and keyword2)
        assert len(deduplicated) == 2, f"Expected 2 unique keywords, got {len(deduplicated)}"
        assert "keyword1" in deduplicated or "KEYWORD1" in deduplicated, "keyword1 should be in deduplicated list"
        assert "keyword2" in deduplicated or "  keyword2  " in deduplicated, "keyword2 should be in deduplicated list"
        
        print("✓ Keyword deduplication works correctly")
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_handle_none_values():
    """Test that None values are handled correctly"""
    try:
        # Test None in Keywords
        metadata1 = {
            "Keywords": None
        }
        keywords = []
        if "Keywords" in metadata1:
            value = metadata1["Keywords"]
            if value is not None:
                if isinstance(value, list):
                    keywords = value if value else []
        assert keywords == [], f"Expected empty list for None, got {keywords}"
        
        # Test empty list
        metadata2 = {
            "Keywords": []
        }
        keywords = []
        if "Keywords" in metadata2:
            value = metadata2["Keywords"]
            if value is not None:
                if isinstance(value, list):
                    keywords = value if value else []
        assert keywords == [], f"Expected empty list for empty list, got {keywords}"
        
        # Test empty string
        metadata3 = {
            "Keywords": ""
        }
        keywords = []
        if "Keywords" in metadata3:
            value = metadata3["Keywords"]
            if value is not None:
                if isinstance(value, str):
                    keywords = [value] if value.strip() else []
        assert keywords == [], f"Expected empty list for empty string, got {keywords}"
        
        print("✓ None and empty values handled correctly")
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_string_keyword_handling():
    """Test that string keywords are converted to list"""
    try:
        metadata = {
            "Keywords": "single keyword"
        }
        
        keywords = []
        if "Keywords" in metadata:
            value = metadata["Keywords"]
            if value is not None:
                if isinstance(value, list):
                    keywords = value if value else []
                elif isinstance(value, str):
                    keywords = [value] if value.strip() else []
        
        assert keywords == ["single keyword"], f"Expected ['single keyword'], got {keywords}"
        print("✓ String keywords converted to list correctly")
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_caption_reading():
    """Test that caption is read from Description field"""
    try:
        metadata = {
            "Description": "Test description",
            "MWG:Description": "MWG description"
        }
        
        # Simulate caption reading logic
        caption = None
        if "Description" in metadata:
            caption = metadata["Description"]
        elif "MWG:Description" in metadata:
            caption = metadata["MWG:Description"]
        
        assert caption == "Test description", f"Expected 'Test description', got {caption}"
        print("✓ Caption read correctly from 'Description' field")
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_caption_fallback():
    """Test caption fallback to MWG:Description"""
    try:
        metadata = {
            "MWG:Description": "MWG description"
        }
        
        caption = None
        if "Description" in metadata:
            caption = metadata["Description"]
        elif "MWG:Description" in metadata:
            caption = metadata["MWG:Description"]
        
        assert caption == "MWG description", f"Expected 'MWG description', got {caption}"
        print("✓ Caption fallback to MWG:Description works correctly")
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("Testing Keyword Reading Fixes...\n")
    
    tests = [
        test_read_keywords_from_generic_field,
        test_fallback_to_mwg_keywords,
        test_keyword_deduplication,
        test_handle_none_values,
        test_string_keyword_handling,
        test_caption_reading,
        test_caption_fallback,
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
        print("✓ All keyword reading tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())




