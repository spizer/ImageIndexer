"""
UI components
"""
from .settings_dialog import SettingsDialog
from .theme import apply_dark_theme, SETTINGS_DIALOG_WIDTH, SETTINGS_DIALOG_HEIGHT

__all__ = [
    'SettingsDialog',
    'apply_dark_theme',
    'SETTINGS_DIALOG_WIDTH',
    'SETTINGS_DIALOG_HEIGHT',
]
