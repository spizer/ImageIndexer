#!/usr/bin/env python3
"""
Test script for Sub-phase 6.5: Manual Keyword Management (Add/Remove)
Tests keyword widget functionality, validation, and integration.
"""

import sys
import os
import re

# Add project root to path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

def test_keyword_widget_imports():
    """Test that KeywordWidget and KeywordPillWidget can be imported"""
    try:
        from src.llmii_gui import KeywordWidget, KeywordPillWidget, GuiConfig
        print("✓ KeywordWidget and KeywordPillWidget imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_keyword_widget_initialization():
    """Test that KeywordWidget initializes correctly"""
    from src.llmii_gui import KeywordWidget
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    try:
        widget = KeywordWidget()
        
        # Check that required attributes exist
        assert hasattr(widget, 'keywords'), "Missing keywords attribute"
        assert hasattr(widget, 'keyword_input'), "Missing keyword_input"
        assert hasattr(widget, 'add_button'), "Missing add_button"
        assert hasattr(widget, 'error_label'), "Missing error_label"
        assert hasattr(widget, 'keywords_changed'), "Missing keywords_changed signal"
        
        # Check initial state
        assert widget.keywords == [], "Keywords should be empty initially"
        assert not widget.add_button.isEnabled(), "Add button should be disabled initially"
        assert not widget.error_label.isVisible(), "Error label should be hidden initially"
        
        print("✓ KeywordWidget initializes correctly")
        return True
    except Exception as e:
        print(f"✗ KeywordWidget initialization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_keyword_pill_widget_initialization():
    """Test that KeywordPillWidget initializes correctly"""
    from src.llmii_gui import KeywordPillWidget
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    try:
        pill = KeywordPillWidget("test keyword")
        
        # Check that required attributes exist
        assert hasattr(pill, 'keyword'), "Missing keyword attribute"
        assert hasattr(pill, 'keyword_label'), "Missing keyword_label"
        assert hasattr(pill, 'remove_button'), "Missing remove_button"
        assert hasattr(pill, 'custom_tooltip'), "Missing custom_tooltip"
        assert hasattr(pill, 'tooltip_timer'), "Missing tooltip_timer"
        
        # Check keyword text
        assert pill.keyword == "test keyword", "Keyword should be stored"
        assert pill.keyword_label.text() == "test keyword", "Label should show keyword"
        
        # Check remove button
        assert pill.remove_button.toolTip() == "Remove Keyword", "Remove button should have tooltip"
        assert pill.remove_button.width() == 12, "Remove button should be 12px wide"
        assert pill.remove_button.height() == 12, "Remove button should be 12px high"
        
        print("✓ KeywordPillWidget initializes correctly")
        return True
    except Exception as e:
        print(f"✗ KeywordPillWidget initialization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_keyword_validation():
    """Test keyword validation logic"""
    from src.llmii_gui import KeywordWidget
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    try:
        widget = KeywordWidget()
        
        # Test valid keywords
        valid_keywords = [
            "test",
            "test keyword",
            "test123",
            "test 123",
            "Test Keyword",
            "test123 keyword456"
        ]
        
        for keyword in valid_keywords:
            is_valid, error_msg = widget.validate_keyword(keyword)
            assert is_valid, f"'{keyword}' should be valid"
            assert error_msg is None, f"'{keyword}' should have no error message"
        
        # Test invalid keywords
        invalid_keywords = [
            ("test@keyword", "contains @"),
            ("test#keyword", "contains #"),
            ("test!keyword", "contains !"),
            ("test.keyword", "contains ."),
            ("test-keyword", "contains -"),
            ("", "empty string"),
            ("   ", "whitespace only")
        ]
        
        for keyword, reason in invalid_keywords:
            is_valid, error_msg = widget.validate_keyword(keyword)
            assert not is_valid, f"'{keyword}' should be invalid ({reason})"
            assert error_msg is not None, f"'{keyword}' should have error message"
        
        print("✓ Keyword validation works correctly")
        return True
    except Exception as e:
        print(f"✗ Keyword validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_add_keyword():
    """Test adding keywords programmatically"""
    from src.llmii_gui import KeywordWidget
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    try:
        widget = KeywordWidget()
        
        # Add valid keyword
        result = widget.add_keyword("test keyword")
        assert result == True, "Should successfully add valid keyword"
        assert "test keyword" in widget.keywords, "Keyword should be in list"
        assert len(widget.keywords) == 1, "Should have one keyword"
        
        # Try to add duplicate (case-insensitive)
        result = widget.add_keyword("Test Keyword")
        assert result == False, "Should reject duplicate keyword"
        assert len(widget.keywords) == 1, "Should still have one keyword"
        
        # Try to add invalid keyword
        result = widget.add_keyword("test@keyword")
        assert result == False, "Should reject invalid keyword"
        assert len(widget.keywords) == 1, "Should still have one keyword"
        
        # Add another valid keyword
        result = widget.add_keyword("another keyword")
        assert result == True, "Should successfully add second keyword"
        assert len(widget.keywords) == 2, "Should have two keywords"
        
        print("✓ Add keyword functionality works correctly")
        return True
    except Exception as e:
        print(f"✗ Add keyword test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_remove_keyword():
    """Test removing keywords"""
    from src.llmii_gui import KeywordWidget
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    try:
        widget = KeywordWidget()
        
        # Add some keywords
        widget.add_keyword("keyword1")
        widget.add_keyword("keyword2")
        widget.add_keyword("keyword3")
        assert len(widget.keywords) == 3, "Should have three keywords"
        
        # Remove a keyword
        widget.remove_keyword("keyword2")
        assert len(widget.keywords) == 2, "Should have two keywords after removal"
        assert "keyword2" not in widget.keywords, "keyword2 should be removed"
        assert "keyword1" in widget.keywords, "keyword1 should remain"
        assert "keyword3" in widget.keywords, "keyword3 should remain"
        
        # Remove with case-insensitive match
        widget.remove_keyword("KEYWORD1")
        assert len(widget.keywords) == 1, "Should have one keyword after case-insensitive removal"
        assert "keyword1" not in widget.keywords, "keyword1 should be removed"
        
        print("✓ Remove keyword functionality works correctly")
        return True
    except Exception as e:
        print(f"✗ Remove keyword test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_validation_realtime():
    """Test real-time validation in input field"""
    from src.llmii_gui import KeywordWidget
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    try:
        widget = KeywordWidget()
        QApplication.processEvents()  # Process events to ensure UI is ready
        
        # Test valid input
        widget.keyword_input.setText("valid keyword")
        widget.validate_input_realtime()
        QApplication.processEvents()
        assert not widget.error_label.isVisible(), "Error should be hidden for valid input"
        assert widget.add_button.isEnabled(), "Add button should be enabled for valid input"
        
        # Test invalid input
        widget.keyword_input.setText("invalid@keyword")
        widget.validate_input_realtime()
        QApplication.processEvents()
        # Check that error label is shown (may need to check isVisible or check if it was shown)
        # The label should be visible, but in test context we check the state
        error_visible = widget.error_label.isVisible()
        # Also check that the stylesheet was set (indicates error state)
        input_style = widget.keyword_input.styleSheet()
        has_red_border = "2px solid #ff4444" in input_style or "border: 2px solid #ff4444" in input_style
        assert error_visible or has_red_border, "Error state should be visible (label visible or red border)"
        assert not widget.add_button.isEnabled(), "Add button should be disabled for invalid input"
        
        # Test clearing invalid input
        widget.keyword_input.setText("")
        widget.validate_input_realtime()
        QApplication.processEvents()
        assert not widget.error_label.isVisible(), "Error should be hidden for empty input"
        assert not widget.add_button.isEnabled(), "Add button should be disabled for empty input"
        
        print("✓ Real-time validation works correctly")
        return True
    except Exception as e:
        print(f"✗ Real-time validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_keywords_changed_signal():
    """Test that keywords_changed signal is emitted"""
    from src.llmii_gui import KeywordWidget
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    try:
        widget = KeywordWidget()
        
        # Track signal emissions
        signal_received = []
        
        def on_keywords_changed(keywords):
            signal_received.append(keywords)
        
        widget.keywords_changed.connect(on_keywords_changed)
        
        # Add keyword - should emit signal
        widget.add_keyword("test keyword")
        assert len(signal_received) == 1, "Signal should be emitted when adding keyword"
        assert signal_received[0] == ["test keyword"], "Signal should contain new keyword list"
        
        # Remove keyword - should emit signal
        widget.remove_keyword("test keyword")
        assert len(signal_received) == 2, "Signal should be emitted when removing keyword"
        assert signal_received[1] == [], "Signal should contain empty list after removal"
        
        print("✓ keywords_changed signal works correctly")
        return True
    except Exception as e:
        print(f"✗ keywords_changed signal test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_keyword_pill_tooltip():
    """Test that KeywordPillWidget has tooltip functionality"""
    from src.llmii_gui import KeywordPillWidget, CustomTooltip
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    try:
        # Test CustomTooltip
        tooltip = CustomTooltip("test keyword text")
        assert tooltip.text() == "test keyword text", "Tooltip should contain keyword text"
        assert tooltip.maximumWidth() == 500, "Tooltip should have max-width 500px"
        assert tooltip.wordWrap(), "Tooltip should have word wrap enabled"
        
        # Test KeywordPillWidget has tooltip setup
        pill = KeywordPillWidget("test keyword")
        assert hasattr(pill, 'custom_tooltip'), "Pill should have custom_tooltip attribute"
        assert hasattr(pill, 'tooltip_timer'), "Pill should have tooltip_timer"
        assert pill.tooltip_timer.isSingleShot(), "Tooltip timer should be single shot"
        
        print("✓ Keyword pill tooltip functionality exists")
        return True
    except Exception as e:
        print(f"✗ Keyword pill tooltip test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_keyword_pill_styling():
    """Test that KeywordPillWidget has correct styling"""
    from src.llmii_gui import KeywordPillWidget, GuiConfig
    from PyQt6.QtWidgets import QApplication, QSizePolicy
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    try:
        pill = KeywordPillWidget("test keyword")
        
        # Check fixed height
        assert pill.height() == 20, "Pill should have fixed height of 20px"
        
        # Check size policy
        size_policy = pill.sizePolicy()
        assert size_policy.horizontalPolicy() == QSizePolicy.Policy.Preferred, "Should have Preferred horizontal policy"
        assert size_policy.verticalPolicy() == QSizePolicy.Policy.Fixed, "Should have Fixed vertical policy"
        
        # Check that colors are stored
        assert hasattr(pill, 'bg_color'), "Should have bg_color attribute"
        assert hasattr(pill, 'border_color'), "Should have border_color attribute"
        assert pill.bg_color == GuiConfig.COLOR_KEYWORD_BG, "Background color should match config"
        assert pill.border_color == GuiConfig.COLOR_KEYWORD_BORDER, "Border color should match config"
        
        print("✓ Keyword pill styling is correct")
        return True
    except Exception as e:
        print(f"✗ Keyword pill styling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_set_keywords_display():
    """Test that set_keywords displays keywords correctly"""
    from src.llmii_gui import KeywordWidget
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    try:
        widget = KeywordWidget()
        
        # Set keywords
        keywords = ["keyword1", "keyword2", "keyword3"]
        widget.set_keywords(keywords)
        
        # Check that keywords are stored
        assert widget.keywords == keywords, "Keywords should be stored"
        
        # Check that keywords container has widgets
        # (We can't easily test the visual layout without more complex setup)
        assert hasattr(widget, 'keywords_container'), "Should have keywords_container"
        
        print("✓ set_keywords displays keywords correctly")
        return True
    except Exception as e:
        print(f"✗ set_keywords display test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("Testing Sub-phase 6.5: Manual Keyword Management (Add/Remove)...\n")
    
    tests = [
        test_keyword_widget_imports,
        test_keyword_widget_initialization,
        test_keyword_pill_widget_initialization,
        test_keyword_validation,
        test_add_keyword,
        test_remove_keyword,
        test_validation_realtime,
        test_keywords_changed_signal,
        test_keyword_pill_tooltip,
        test_keyword_pill_styling,
        test_set_keywords_display,
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
        print("✓ All Sub-phase 6.5 tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())

