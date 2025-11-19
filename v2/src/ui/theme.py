"""
Design tokens and theme configuration for Batch Image Metadata Tool
Extracted from mockup designs - will be refined in Phase 9
"""
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt


# Window and Dialog Sizes
SETTINGS_DIALOG_WIDTH = 500
SETTINGS_DIALOG_HEIGHT = 460

# Colors (extracted from mockups - dark theme)
COLOR_BACKGROUND = QColor(53, 53, 53)
COLOR_BACKGROUND_DARK = QColor(35, 35, 35)
COLOR_TEXT = QColor(255, 255, 255)
COLOR_TEXT_DISABLED = QColor(136, 136, 136)
COLOR_BUTTON = QColor(53, 53, 53)
COLOR_BUTTON_HOVER = QColor(70, 70, 70)
COLOR_BUTTON_PRESSED = QColor(40, 40, 40)
COLOR_BUTTON_DISABLED = QColor(224, 224, 224)
COLOR_HIGHLIGHT = QColor(42, 130, 218)
COLOR_HIGHLIGHT_TEXT = QColor(0, 0, 0)
COLOR_BORDER = QColor(100, 100, 100)
COLOR_BORDER_LIGHT = QColor(150, 150, 150)

# Spacing
SPACING_SMALL = 4
SPACING_MEDIUM = 8
SPACING_LARGE = 16

# Margins
MARGIN_SMALL = 8
MARGIN_MEDIUM = 12
MARGIN_LARGE = 16

# Fonts
FONT_SIZE_NORMAL = 12
FONT_SIZE_SMALL = 10
FONT_SIZE_LARGE = 14
FONT_FAMILY = "Arial"  # Will be refined in Phase 9

# Border radius
BORDER_RADIUS_SMALL = 3
BORDER_RADIUS_MEDIUM = 5
BORDER_RADIUS_LARGE = 8


def apply_dark_theme(app):
    """
    Apply dark theme to QApplication.
    
    Args:
        app: QApplication instance
    """
    palette = QPalette()
    
    # Window colors
    palette.setColor(QPalette.ColorRole.Window, COLOR_BACKGROUND)
    palette.setColor(QPalette.ColorRole.WindowText, COLOR_TEXT)
    palette.setColor(QPalette.ColorRole.Base, COLOR_BACKGROUND_DARK)
    palette.setColor(QPalette.ColorRole.AlternateBase, COLOR_BACKGROUND)
    
    # Text colors
    palette.setColor(QPalette.ColorRole.Text, COLOR_TEXT)
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
    
    # Button colors
    palette.setColor(QPalette.ColorRole.Button, COLOR_BUTTON)
    palette.setColor(QPalette.ColorRole.ButtonText, COLOR_TEXT)
    
    # Tooltip colors
    palette.setColor(QPalette.ColorRole.ToolTipBase, COLOR_TEXT)
    palette.setColor(QPalette.ColorRole.ToolTipText, COLOR_BACKGROUND_DARK)
    
    # Link and highlight colors
    palette.setColor(QPalette.ColorRole.Link, COLOR_HIGHLIGHT)
    palette.setColor(QPalette.ColorRole.Highlight, COLOR_HIGHLIGHT)
    palette.setColor(QPalette.ColorRole.HighlightedText, COLOR_HIGHLIGHT_TEXT)
    
    app.setPalette(palette)
    app.setStyle("Fusion")


def get_button_stylesheet():
    """
    Get stylesheet for buttons.
    
    Returns:
        str: CSS stylesheet string
    """
    return f"""
        QPushButton {{
            background-color: {COLOR_BUTTON.name()};
            color: {COLOR_TEXT.name()};
            border: 1px solid {COLOR_BORDER.name()};
            border-radius: {BORDER_RADIUS_SMALL}px;
            padding: {SPACING_SMALL}px {SPACING_MEDIUM}px;
            min-width: 60px;
        }}
        QPushButton:hover {{
            background-color: {COLOR_BUTTON_HOVER.name()};
        }}
        QPushButton:pressed {{
            background-color: {COLOR_BUTTON_PRESSED.name()};
        }}
        QPushButton:disabled {{
            background-color: {COLOR_BUTTON_DISABLED.name()};
            color: {COLOR_TEXT_DISABLED.name()};
            border: 1px solid {COLOR_BORDER_LIGHT.name()};
        }}
        QPushButton:focus {{
            border: 2px solid {COLOR_HIGHLIGHT.name()};
        }}
    """


def get_input_stylesheet():
    """
    Get stylesheet for input fields.
    
    Returns:
        str: CSS stylesheet string
    """
    return f"""
        QLineEdit, QPlainTextEdit, QTextEdit, QSpinBox, QDoubleSpinBox {{
            background-color: {COLOR_BACKGROUND_DARK.name()};
            color: {COLOR_TEXT.name()};
            border: 1px solid {COLOR_BORDER.name()};
            border-radius: {BORDER_RADIUS_SMALL}px;
            padding: {SPACING_SMALL}px;
        }}
        QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 2px solid {COLOR_HIGHLIGHT.name()};
        }}
        QLineEdit:disabled, QPlainTextEdit:disabled, QTextEdit:disabled {{
            background-color: {COLOR_BACKGROUND.name()};
            color: {COLOR_TEXT_DISABLED.name()};
        }}
    """


def get_checkbox_stylesheet():
    """
    Get stylesheet for checkboxes.
    
    Returns:
        str: CSS stylesheet string
    """
    return f"""
        QCheckBox {{
            color: {COLOR_TEXT.name()};
            spacing: {SPACING_SMALL}px;
        }}
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border: 1px solid {COLOR_BORDER.name()};
            border-radius: {BORDER_RADIUS_SMALL}px;
            background-color: {COLOR_BACKGROUND_DARK.name()};
        }}
        QCheckBox::indicator:checked {{
            background-color: {COLOR_HIGHLIGHT.name()};
            border: 1px solid {COLOR_HIGHLIGHT.name()};
        }}
        QCheckBox::indicator:focus {{
            border: 2px solid {COLOR_HIGHLIGHT.name()};
        }}
        QCheckBox:disabled {{
            color: {COLOR_TEXT_DISABLED.name()};
        }}
    """


def get_radiobutton_stylesheet():
    """
    Get stylesheet for radio buttons.
    
    Returns:
        str: CSS stylesheet string
    """
    return f"""
        QRadioButton {{
            color: {COLOR_TEXT.name()};
            spacing: {SPACING_SMALL}px;
        }}
        QRadioButton::indicator {{
            width: 16px;
            height: 16px;
            border: 1px solid {COLOR_BORDER.name()};
            border-radius: 8px;
            background-color: {COLOR_BACKGROUND_DARK.name()};
        }}
        QRadioButton::indicator:checked {{
            background-color: {COLOR_HIGHLIGHT.name()};
            border: 1px solid {COLOR_HIGHLIGHT.name()};
        }}
        QRadioButton::indicator:focus {{
            border: 2px solid {COLOR_HIGHLIGHT.name()};
        }}
        QRadioButton:disabled {{
            color: {COLOR_TEXT_DISABLED.name()};
        }}
    """


def get_groupbox_stylesheet():
    """
    Get stylesheet for group boxes.
    
    Returns:
        str: CSS stylesheet string
    """
    return f"""
        QGroupBox {{
            color: {COLOR_TEXT.name()};
            border: 1px solid {COLOR_BORDER.name()};
            border-radius: {BORDER_RADIUS_MEDIUM}px;
            margin-top: {SPACING_MEDIUM}px;
            padding-top: {SPACING_MEDIUM}px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: {SPACING_MEDIUM}px;
            padding: 0 {SPACING_SMALL}px;
        }}
    """


def get_tab_stylesheet():
    """
    Get stylesheet for tab widgets.
    
    Returns:
        str: CSS stylesheet string
    """
    return f"""
        QTabWidget::pane {{
            border: 1px solid {COLOR_BORDER.name()};
            background-color: {COLOR_BACKGROUND.name()};
        }}
        QTabBar::tab {{
            background-color: {COLOR_BACKGROUND_DARK.name()};
            color: {COLOR_TEXT.name()};
            border: 1px solid {COLOR_BORDER.name()};
            padding: {SPACING_SMALL}px {SPACING_MEDIUM}px;
            margin-right: 2px;
        }}
        QTabBar::tab:selected {{
            background-color: {COLOR_BACKGROUND.name()};
            border-bottom: 2px solid {COLOR_HIGHLIGHT.name()};
        }}
        QTabBar::tab:hover {{
            background-color: {COLOR_BUTTON_HOVER.name()};
        }}
        QTabBar::tab:focus {{
            border: 2px solid {COLOR_HIGHLIGHT.name()};
        }}
    """
