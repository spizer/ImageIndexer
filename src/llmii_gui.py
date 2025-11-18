import sys
import os
import json
import shutil
import base64
import requests
import uuid
import exiftool

from PyQt6.QtCore import QThread, pyqtSignal, QObject, Qt, QSize, QTimer, QPoint
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QLabel, QLineEdit, QCheckBox, QPushButton, QFileDialog,
                           QTextEdit, QGroupBox, QSpinBox, QDoubleSpinBox, QRadioButton, QButtonGroup,
                           QProgressBar, QTableWidget, QTableWidgetItem, QComboBox,
                           QPlainTextEdit, QScrollArea, QMessageBox, QDialog, QMenuBar,
                           QMenu, QSizePolicy, QSplitter, QFrame, QPushButton, QFrame,
                           QSizePolicy, QSpacerItem)


from PyQt6.QtGui import QPixmap, QImage, QPalette, QColor, QFont, QIcon, QPainter, QPen, QMouseEvent, QEnterEvent, QCursor


# Handle imports for both normal execution and py2app bundle
try:
    from . import llmii
    from . import help_text
except ImportError:
    # Running as main script (e.g., in py2app bundle)
    pass

if not hasattr(sys, 'frozen'):
    # Running as main script (not in py2app bundle)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)
    import src.llmii as llmii
    import src.help_text as help_text
    
    if hasattr(sys, 'frozen'):
        # Running from py2app bundle
        # py2app sets RESOURCEPATH environment variable to Contents/Resources/
        resourcepath = os.environ.get('RESOURCEPATH')
        if resourcepath and os.path.exists(resourcepath):
            resources_dir = resourcepath
        else:
            # Fallback: get from __file__
            try:
                resources_dir = os.path.dirname(os.path.abspath(__file__))
            except NameError:
                # Last fallback: get from executable path
                bundle_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.executable))))
                resources_dir = os.path.join(bundle_dir, "Contents", "Resources")
        
        # Add lib/python3.9 to path (parent of src/)
        lib_path = os.path.join(resources_dir, 'lib', 'python3.9')
        
        # Debug: print paths to help diagnose
        print(f"DEBUG: resources_dir={resources_dir}")
        print(f"DEBUG: lib_path={lib_path}")
        print(f"DEBUG: lib_path exists={os.path.exists(lib_path)}")
        
        if os.path.exists(lib_path):
            # Verify src directory exists
            src_path = os.path.join(lib_path, 'src')
            print(f"DEBUG: src_path={src_path}")
            print(f"DEBUG: src_path exists={os.path.exists(src_path)}")
            
            if os.path.exists(src_path):
                # Add to path and verify it's there
                if lib_path not in sys.path:
                    sys.path.insert(0, lib_path)
                print(f"DEBUG: sys.path[0:3]={sys.path[0:3]}")
                print(f"DEBUG: lib_path in sys.path={lib_path in sys.path}")
                print(f"DEBUG: lib_path index in sys.path={sys.path.index(lib_path) if lib_path in sys.path else 'NOT FOUND'}")
                
                # Check what's in src directory
                try:
                    src_contents = os.listdir(src_path)
                    print(f"DEBUG: src directory contents={src_contents}")
                    print(f"DEBUG: llmii.py exists={os.path.exists(os.path.join(src_path, 'llmii.py'))}")
                    print(f"DEBUG: help_text.py exists={os.path.exists(os.path.join(src_path, 'help_text.py'))}")
                    print(f"DEBUG: __init__.py exists={os.path.exists(os.path.join(src_path, '__init__.py'))}")
                except Exception as e:
                    print(f"DEBUG: Error listing src directory: {e}")
                
                # Try the import
                try:
                    import src.llmii as llmii
                    import src.help_text as help_text
                except ImportError as e:
                    # More detailed error
                    raise ImportError(
                        f"Failed to import src.llmii. "
                        f"lib_path={lib_path}, "
                        f"src_path={src_path}, "
                        f"sys.path[0]={sys.path[0] if sys.path else 'empty'}, "
                        f"error={str(e)}"
                    )
            else:
                raise ImportError(
                    f"Could not find src directory at {src_path}. "
                    f"Resources dir: {resources_dir}, lib_path: {lib_path}"
                )
        else:
            raise ImportError(
                f"Could not find lib/python3.9 directory at {lib_path}. "
                f"Resources dir: {resources_dir}"
            )
    else:
        # Normal execution - add project root to path
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, project_root)
        import src.llmii as llmii
        import src.help_text as help_text

class GuiConfig:
    """ Configuration class for GUI dimensions and properties
    """
    WINDOW_WIDTH = 704
    WINDOW_HEIGHT = 720
    WINDOW_FIXED = False
    
    IMAGE_PREVIEW_WIDTH = 340
    IMAGE_PREVIEW_HEIGHT = 450
    
    METADATA_WIDTH = 360
    METADATA_HEIGHT = 450
    
    LOG_WIDTH = 700
    LOG_HEIGHT = 140
    
    CONTROL_PANEL_HEIGHT = 75
    SPLITTER_HANDLE_WIDTH = 4
    
    SETTINGS_HEIGHT = 660
    SETTINGS_WIDTH = 460
    
    FONT_SIZE_NORMAL = 9
    FONT_SIZE_HEADER = 10
    
    COLOR_KEYWORD_BG = "#e1f0ff"
    COLOR_KEYWORD_TEXT = "#0066cc"
    COLOR_KEYWORD_BORDER = "#99ccff"
    COLOR_CAPTION_BG = "#f9f9f9"
    COLOR_BORDER = "#cccccc"
    
    CONTENT_MARGINS = 1
    SPACING = 1
    KEYWORDS_PER_ROW = 5
    FILENAME_LABEL_HEIGHT = 20
    CAPTION_BOX_HEIGHT = 200
    KEYWORDS_BOX_HEIGHT = abs(METADATA_HEIGHT - (FILENAME_LABEL_HEIGHT + CAPTION_BOX_HEIGHT))
    DEFAULT_INSTRUCTION = """Return a JSON object containing a Description for the image and a list of Keywords.

Write the Description using the active voice.

Generate 5 to 10 Keywords. Each Keyword is an item in a list and will be composed of a maximum of two words.

For both Description and Keywords, make sure to include:

 - Themes, concepts
 - Items, animals, objects
 - Structures, landmarks, setting
 - Foreground and background elements
 - Notable colors, textures, styles
 - Actions, activities

If humans are present, include:
 - Physical appearance
 - Gender
 - Clothing
 - Age range
 - Visibly apparent ancestry
 - Occupation/role
 - Relationships between individuals
 - Emotions, expressions, body language

Use ENGLISH only. Generate ONLY a JSON object with the keys Description and Keywords as follows {"Description": str, "Keywords": []}"""

class SettingsHelpDialog(QDialog):
    """ Dialog that shows help information for all settings """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings Help")
        self.resize(600, 500)
        
        layout = QVBoxLayout(self)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        from src.help_text import get_settings_help
        help_label = QLabel(get_settings_help())
        help_label.setWordWrap(True)
        help_label.setTextFormat(Qt.TextFormat.RichText)
        help_label.setOpenExternalLinks(True)
        
        scroll_area.setWidget(help_label)
        layout.addWidget(scroll_area)
        
        button_layout = QHBoxLayout()
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addStretch(1)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(GuiConfig.SETTINGS_WIDTH, GuiConfig.SETTINGS_HEIGHT)
        
        layout = QVBoxLayout(self)
        
        # Scroll area in case it gets too long
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        api_layout = QHBoxLayout()
        self.api_url_input = QLineEdit("http://localhost:5001")
        self.api_password_input = QLineEdit()
        api_layout.addWidget(QLabel("API URL:"))
        api_layout.addWidget(self.api_url_input)
        api_layout.addWidget(QLabel("API Password:"))
        api_layout.addWidget(self.api_password_input)
        scroll_layout.addLayout(api_layout)

        system_instruction_layout = QHBoxLayout()
        self.system_instruction_input = QLineEdit("You are a helpful assistant.")
        system_instruction_layout.addWidget(QLabel("System Instruction:"))
        system_instruction_layout.addWidget(self.system_instruction_input)
        scroll_layout.addLayout(system_instruction_layout)

        # Instruction Settings Group
        instruction_group = QGroupBox("Instruction Settings")
        instruction_layout = QVBoxLayout()
        
        # General Instruction (for "Both" mode)
        instruction_layout.addWidget(QLabel("General Instruction (for 'Both' mode):"))
        self.general_instruction_input = QPlainTextEdit()
        self.general_instruction_input.setFixedHeight(150)
        self.general_instruction_input.setPlainText(GuiConfig.DEFAULT_INSTRUCTION)
        instruction_layout.addWidget(self.general_instruction_input)
        
        # Description Instruction (for "Description only" mode)
        instruction_layout.addWidget(QLabel("Description Instruction (for 'Description only' mode):"))
        self.description_instruction_input = QPlainTextEdit()
        self.description_instruction_input.setFixedHeight(120)
        self.description_instruction_input.setPlainText("Describe the image. Be specific.")
        instruction_layout.addWidget(self.description_instruction_input)
        
        # Keyword Instruction (for "Keywords only" mode)
        instruction_layout.addWidget(QLabel("Keyword Instruction (for 'Keywords only' mode):"))
        self.keyword_instruction_input = QPlainTextEdit()
        self.keyword_instruction_input.setFixedHeight(150)
        # Default will be set in load_settings if not in settings.json
        instruction_layout.addWidget(self.keyword_instruction_input)
        
        instruction_group.setLayout(instruction_layout)
        scroll_layout.addWidget(instruction_group)

        # Generation Mode Options
        generation_mode_group = QGroupBox("Generation Mode")
        generation_mode_layout = QVBoxLayout()
        
        self.generation_mode_radio_group = QButtonGroup(self)
        self.both_radio = QRadioButton("Both (Description and Keywords)")
        self.description_only_radio = QRadioButton("Description only")
        self.keywords_only_radio = QRadioButton("Keywords only")
        
        self.generation_mode_radio_group.addButton(self.both_radio)
        self.generation_mode_radio_group.addButton(self.description_only_radio)
        self.generation_mode_radio_group.addButton(self.keywords_only_radio)
        
        self.both_radio.setChecked(True)  # Default to "both"
        
        generation_mode_layout.addWidget(self.both_radio)
        
        # Sub-options for "Both" mode (query method) - placed between Both and Description
        self.both_options_widget = QWidget()
        both_options_layout = QVBoxLayout(self.both_options_widget)
        both_options_layout.setContentsMargins(20, 5, 0, 5)  # Indent sub-options
        
        self.both_query_radio_group = QButtonGroup(self)
        self.combined_query_radio = QRadioButton("Combined query (single API call)")
        self.separate_query_radio = QRadioButton("Separate queries (two API calls)")
        
        self.both_query_radio_group.addButton(self.combined_query_radio)
        self.both_query_radio_group.addButton(self.separate_query_radio)
        
        self.combined_query_radio.setChecked(True)  # Default to combined
        
        both_options_layout.addWidget(self.combined_query_radio)
        both_options_layout.addWidget(self.separate_query_radio)
        
        generation_mode_layout.addWidget(self.both_options_widget)
        generation_mode_layout.addWidget(self.description_only_radio)
        generation_mode_layout.addWidget(self.keywords_only_radio)
        
        # Connect radio buttons to show/hide sub-options
        self.both_radio.toggled.connect(self.update_both_options_visibility)
        self.update_both_options_visibility(self.both_radio.isChecked())
        
        generation_mode_group.setLayout(generation_mode_layout)
        scroll_layout.addWidget(generation_mode_group)

        gen_count_layout = QHBoxLayout()
        self.gen_count = QSpinBox()
        self.gen_count.setMinimum(50)
        self.gen_count.setMaximum(1000)
        self.gen_count.setValue(250)
        gen_count_layout.addWidget(QLabel("GenTokens: "))
        gen_count_layout.addWidget(self.gen_count)
        scroll_layout.addLayout(gen_count_layout)
        
        res_limit_layout = QHBoxLayout()
        self.res_limit = QSpinBox()
        self.res_limit.setMinimum(112)
        self.res_limit.setMaximum(896)
        self.res_limit.setValue(448)
        self.res_limit.setSingleStep(14)
        res_limit_layout.addWidget(QLabel("Dimension length: "))
        res_limit_layout.addWidget(self.res_limit)
        scroll_layout.addLayout(res_limit_layout)

        # Sampler Settings Group
        sampler_group = QGroupBox("Sampler Settings")
        sampler_layout = QVBoxLayout()

        # Temperature
        temp_layout = QHBoxLayout()
        self.temperature_spinbox = QDoubleSpinBox()
        self.temperature_spinbox.setMinimum(0.0)
        self.temperature_spinbox.setMaximum(2.0)
        self.temperature_spinbox.setValue(0.2)
        self.temperature_spinbox.setSingleStep(0.05)
        self.temperature_spinbox.setDecimals(2)
        temp_layout.addWidget(QLabel("Temperature:"))
        temp_layout.addWidget(self.temperature_spinbox)
        temp_layout.addStretch()
        sampler_layout.addLayout(temp_layout)

        # Top P
        top_p_layout = QHBoxLayout()
        self.top_p_spinbox = QDoubleSpinBox()
        self.top_p_spinbox.setMinimum(0.0)
        self.top_p_spinbox.setMaximum(1.0)
        self.top_p_spinbox.setValue(1.0)
        self.top_p_spinbox.setSingleStep(0.01)
        self.top_p_spinbox.setDecimals(2)
        top_p_layout.addWidget(QLabel("Top P:"))
        top_p_layout.addWidget(self.top_p_spinbox)
        top_p_layout.addStretch()
        sampler_layout.addLayout(top_p_layout)

        # Top K
        top_k_layout = QHBoxLayout()
        self.top_k_spinbox = QSpinBox()
        self.top_k_spinbox.setMinimum(0)
        self.top_k_spinbox.setMaximum(100)
        self.top_k_spinbox.setValue(100)
        top_k_layout.addWidget(QLabel("Top K:"))
        top_k_layout.addWidget(self.top_k_spinbox)
        top_k_layout.addStretch()
        sampler_layout.addLayout(top_k_layout)

        # Min P
        min_p_layout = QHBoxLayout()
        self.min_p_spinbox = QDoubleSpinBox()
        self.min_p_spinbox.setMinimum(0.0)
        self.min_p_spinbox.setMaximum(2.0)
        self.min_p_spinbox.setValue(0.05)
        self.min_p_spinbox.setSingleStep(0.01)
        self.min_p_spinbox.setDecimals(2)
        min_p_layout.addWidget(QLabel("Min P:"))
        min_p_layout.addWidget(self.min_p_spinbox)
        min_p_layout.addStretch()
        sampler_layout.addLayout(min_p_layout)

        # Repetition Penalty
        rep_pen_layout = QHBoxLayout()
        self.rep_pen_spinbox = QDoubleSpinBox()
        self.rep_pen_spinbox.setMinimum(1.0)
        self.rep_pen_spinbox.setMaximum(2.0)
        self.rep_pen_spinbox.setValue(1.01)
        self.rep_pen_spinbox.setSingleStep(0.01)
        self.rep_pen_spinbox.setDecimals(2)
        rep_pen_layout.addWidget(QLabel("Repetition Penalty:"))
        rep_pen_layout.addWidget(self.rep_pen_spinbox)
        rep_pen_layout.addStretch()
        sampler_layout.addLayout(rep_pen_layout)

        sampler_group.setLayout(sampler_layout)
        scroll_layout.addWidget(sampler_group)

        options_group = QGroupBox("File Options")
        options_layout = QVBoxLayout()
        
        # Auto-save option (preview mode control) - at top of File Options
        self.auto_save_checkbox = QCheckBox("Auto-save (write metadata automatically)")
        self.auto_save_checkbox.setChecked(False)  # Default to preview mode
        options_layout.addWidget(self.auto_save_checkbox)
        
        self.no_crawl_checkbox = QCheckBox("Don't go in subdirectories")
        self.reprocess_all_checkbox = QCheckBox("Reprocess everything")
        self.reprocess_failed_checkbox = QCheckBox("Reprocess failures")
        self.reprocess_orphans_checkbox = QCheckBox("Fix any orphans")
        self.no_backup_checkbox = QCheckBox("No backups")
        self.dry_run_checkbox = QCheckBox("Pretend mode")
        self.skip_verify_checkbox = QCheckBox("No file validation")
        self.quick_fail_checkbox = QCheckBox("No retries")
        self.use_sidecar_checkbox = QCheckBox("Use metadata sidecar file instead of writing to image") 
        options_layout.addWidget(self.no_crawl_checkbox)
        options_layout.addWidget(self.reprocess_all_checkbox)
        options_layout.addWidget(self.reprocess_failed_checkbox)
        options_layout.addWidget(self.reprocess_orphans_checkbox)
        options_layout.addWidget(self.no_backup_checkbox)
        options_layout.addWidget(self.dry_run_checkbox)
        options_layout.addWidget(self.skip_verify_checkbox)
        options_layout.addWidget(self.quick_fail_checkbox)
        options_layout.addWidget(self.use_sidecar_checkbox)
        
        options_group.setLayout(options_layout)
        scroll_layout.addWidget(options_group)
        
        xmp_group = QGroupBox("Existing Metadata")
        xmp_layout = QVBoxLayout()
        
        # Removed update_keywords_checkbox - feature no longer needed
        self.update_caption_checkbox = QCheckBox("Don't clear existing caption (new will be added surrounded by tags)")
        self.update_caption_checkbox.setChecked(False)
        
        xmp_layout.addWidget(self.update_caption_checkbox)
        
        xmp_group.setLayout(xmp_layout)
        scroll_layout.addWidget(xmp_group)

        keyword_corrections_group = QGroupBox("Keyword Corrections")
        corrections_layout = QVBoxLayout()
        
        self.depluralize_checkbox = QCheckBox("Depluralize keywords")
        self.depluralize_checkbox.setChecked(False)
        self.word_limit_layout = QHBoxLayout()
        self.word_limit_checkbox = QCheckBox("Limit to")
        self.word_limit_spinbox = QSpinBox()
        self.word_limit_spinbox.setMinimum(1)
        self.word_limit_spinbox.setMaximum(5)
        self.word_limit_spinbox.setValue(2)
        self.word_limit_layout.addWidget(self.word_limit_checkbox)
        self.word_limit_layout.addWidget(self.word_limit_spinbox)
        self.word_limit_layout.addWidget(QLabel("words in keyword entry"))
        self.word_limit_layout.addStretch(1)
        self.word_limit_checkbox.setChecked(True)
        self.split_and_checkbox = QCheckBox("Split 'and'/'or' entries")
        self.split_and_checkbox.setChecked(True)
        self.ban_prompt_words_checkbox = QCheckBox("Ban prompt word repetitions")
        self.ban_prompt_words_checkbox.setChecked(True)
        self.no_digits_start_checkbox = QCheckBox("Cannot start with 3+ digits")
        self.no_digits_start_checkbox.setChecked(True)
        self.min_word_length_checkbox = QCheckBox("Words must be 2+ characters")
        self.min_word_length_checkbox.setChecked(True)
        self.latin_only_checkbox = QCheckBox("Only Latin characters")
        self.latin_only_checkbox.setChecked(True)
        
        corrections_layout.addWidget(self.depluralize_checkbox)
        corrections_layout.addLayout(self.word_limit_layout)
        corrections_layout.addWidget(self.split_and_checkbox)
        corrections_layout.addWidget(self.ban_prompt_words_checkbox)
        corrections_layout.addWidget(self.no_digits_start_checkbox)
        corrections_layout.addWidget(self.min_word_length_checkbox)
        corrections_layout.addWidget(self.latin_only_checkbox)
        
        keyword_corrections_group.setLayout(corrections_layout)
        scroll_layout.addWidget(keyword_corrections_group)
        
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area, 1)
        
        button_layout = QHBoxLayout()
        help_button = QPushButton("Help")
        help_button.clicked.connect(self.show_help)
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(help_button)
        button_layout.addStretch(1)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        # Get default keyword instruction from Config
        from .llmii import Config
        default_config = Config()
        self.default_keyword_instruction = default_config.keyword_instruction
        
        self.load_settings()
        
        # Ensure visibility is set correctly after loading (in case no settings file exists)
        self.update_both_options_visibility(self.both_radio.isChecked())
    
    def show_help(self):
        """Show the settings help dialog"""
        dialog = SettingsHelpDialog(self)
        dialog.exec()
        
    def update_both_options_visibility(self, is_checked):
        """Show/hide sub-options when 'Both' mode is selected"""
        self.both_options_widget.setVisible(is_checked)
        
    def load_settings(self):
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r') as f:
                    settings = json.load(f)
                    
                self.api_url_input.setText(settings.get('api_url', 'http://localhost:5001'))
                self.api_password_input.setText(settings.get('api_password', ''))
                self.system_instruction_input.setText(settings.get('system_instruction', 'You are a helpful assistant.'))
                self.gen_count.setValue(settings.get('gen_count', 250))
                self.res_limit.setValue(settings.get('res_limit', 448))
                
                # Load instruction settings with migration support
                # If old 'instruction' key exists but new keys don't, migrate it
                if 'instruction' in settings and 'general_instruction' not in settings:
                    # Migrate old instruction to general_instruction
                    self.general_instruction_input.setPlainText(settings.get('instruction', GuiConfig.DEFAULT_INSTRUCTION))
                else:
                    self.general_instruction_input.setPlainText(settings.get('general_instruction', GuiConfig.DEFAULT_INSTRUCTION))
                
                # Load description instruction (migrate from old caption_instruction if needed)
                if 'description_instruction' in settings:
                    self.description_instruction_input.setPlainText(settings.get('description_instruction', 'Describe the image. Be specific.'))
                elif 'caption_instruction' in settings:
                    # Migrate old caption_instruction
                    self.description_instruction_input.setPlainText(settings.get('caption_instruction', 'Describe the image. Be specific.'))
                else:
                    self.description_instruction_input.setPlainText('Describe the image. Be specific.')
                
                # Load keyword instruction
                self.keyword_instruction_input.setPlainText(settings.get('keyword_instruction', self.default_keyword_instruction))
                
                self.no_crawl_checkbox.setChecked(settings.get('no_crawl', False))
                self.reprocess_failed_checkbox.setChecked(settings.get('reprocess_failed', False))
                self.reprocess_all_checkbox.setChecked(settings.get('reprocess_all', False))
                self.reprocess_orphans_checkbox.setChecked(settings.get('reprocess_orphans', True))
                self.no_backup_checkbox.setChecked(settings.get('no_backup', False))
                self.dry_run_checkbox.setChecked(settings.get('dry_run', False))
                self.skip_verify_checkbox.setChecked(settings.get('skip_verify', False))
                self.quick_fail_checkbox.setChecked(settings.get('quick_fail', False))
                self.use_sidecar_checkbox.setChecked(settings.get('use_sidecar', False))
                self.auto_save_checkbox.setChecked(settings.get('auto_save', False))
                
                # Load generation mode setting
                generation_mode = settings.get('generation_mode', 'both')
                if generation_mode == 'description_only':
                    self.description_only_radio.setChecked(True)
                    self.both_radio.setChecked(False)
                    self.keywords_only_radio.setChecked(False)
                elif generation_mode == 'keywords_only':
                    self.keywords_only_radio.setChecked(True)
                    self.both_radio.setChecked(False)
                    self.description_only_radio.setChecked(False)
                else:
                    self.both_radio.setChecked(True)
                    self.description_only_radio.setChecked(False)
                    self.keywords_only_radio.setChecked(False)
                
                # Load both mode query method (migrate from old detailed_caption/short_caption)
                # If old settings exist, migrate them
                if 'detailed_caption' in settings:
                    if settings.get('detailed_caption', False):
                        self.separate_query_radio.setChecked(True)
                        self.combined_query_radio.setChecked(False)
                    else:
                        self.combined_query_radio.setChecked(True)
                        self.separate_query_radio.setChecked(False)
                elif 'both_query_method' in settings:
                    if settings.get('both_query_method') == 'separate':
                        self.separate_query_radio.setChecked(True)
                        self.combined_query_radio.setChecked(False)
                    else:
                        self.combined_query_radio.setChecked(True)
                        self.separate_query_radio.setChecked(False)
                else:
                    # Default to combined
                    self.combined_query_radio.setChecked(True)
                    self.separate_query_radio.setChecked(False)
                
                # Update visibility based on selected mode
                self.update_both_options_visibility(self.both_radio.isChecked())
                    
                # Removed update_keywords - feature removed
                self.update_caption_checkbox.setChecked(settings.get('update_caption', False))
                
                # Load keyword correction settings
                self.depluralize_checkbox.setChecked(settings.get('depluralize_keywords', False))
                self.word_limit_checkbox.setChecked(settings.get('limit_word_count', True))
                self.word_limit_spinbox.setValue(settings.get('max_words_per_keyword', 2))
                self.split_and_checkbox.setChecked(settings.get('split_and_entries', True))
                self.ban_prompt_words_checkbox.setChecked(settings.get('ban_prompt_words', True))
                self.no_digits_start_checkbox.setChecked(settings.get('no_digits_start', True))
                self.min_word_length_checkbox.setChecked(settings.get('min_word_length', True))
                self.latin_only_checkbox.setChecked(settings.get('latin_only', True))

                # Load sampler settings
                self.temperature_spinbox.setValue(settings.get('temperature', 0.2))
                self.top_p_spinbox.setValue(settings.get('top_p', 1.0))
                self.top_k_spinbox.setValue(settings.get('top_k', 100))
                self.min_p_spinbox.setValue(settings.get('min_p', 0.05))
                self.rep_pen_spinbox.setValue(settings.get('rep_pen', 1.01))

        except Exception as e:
            print(f"Error loading settings: {e}")
            
    def save_settings(self):
        settings = {
            'api_url': self.api_url_input.text(),
            'api_password': self.api_password_input.text(),
            'system_instruction': self.system_instruction_input.text(),
            'general_instruction': self.general_instruction_input.toPlainText(),
            'description_instruction': self.description_instruction_input.toPlainText(),
            'keyword_instruction': self.keyword_instruction_input.toPlainText(),
            'gen_count': self.gen_count.value(),
            'res_limit': self.res_limit.value(),
            'no_crawl': self.no_crawl_checkbox.isChecked(),
            'reprocess_failed': self.reprocess_failed_checkbox.isChecked(),
            'reprocess_all': self.reprocess_all_checkbox.isChecked(),
            'reprocess_orphans': self.reprocess_orphans_checkbox.isChecked(),
            'no_backup': self.no_backup_checkbox.isChecked(),
            'dry_run': self.dry_run_checkbox.isChecked(),
            'skip_verify': self.skip_verify_checkbox.isChecked(),
            'quick_fail': self.quick_fail_checkbox.isChecked(),
            # Removed update_keywords - feature removed
            'update_caption': self.update_caption_checkbox.isChecked(),
            'generation_mode': 'description_only' if self.description_only_radio.isChecked() else ('keywords_only' if self.keywords_only_radio.isChecked() else 'both'),
            'both_query_method': 'separate' if self.separate_query_radio.isChecked() else 'combined',
            'use_sidecar': self.use_sidecar_checkbox.isChecked(),
            'auto_save': self.auto_save_checkbox.isChecked(),
            'depluralize_keywords': self.depluralize_checkbox.isChecked(),
            'limit_word_count': self.word_limit_checkbox.isChecked(),
            'max_words_per_keyword': self.word_limit_spinbox.value(),
            'split_and_entries': self.split_and_checkbox.isChecked(),
            'ban_prompt_words': self.ban_prompt_words_checkbox.isChecked(),
            'no_digits_start': self.no_digits_start_checkbox.isChecked(),
            'min_word_length': self.min_word_length_checkbox.isChecked(),
            'latin_only': self.latin_only_checkbox.isChecked(),
            'temperature': self.temperature_spinbox.value(),
            'top_p': self.top_p_spinbox.value(),
            'top_k': self.top_k_spinbox.value(),
            'min_p': self.min_p_spinbox.value(),
            'rep_pen': self.rep_pen_spinbox.value(),
        }
        
        try:
            with open('settings.json', 'w') as f:
                json.dump(settings, f, indent=4)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save settings: {e}")

class APICheckThread(QThread):
    api_status = pyqtSignal(bool)
    
    def __init__(self, api_url):
        super().__init__()
        self.api_url = api_url
        self.running = True
        
    def run(self):

        while self.running:
            try:
                # Direct HTTP request to the version endpoint
                response = requests.get(f"{self.api_url}/api/extra/version", timeout=5)
                if response.status_code == 200:
                    self.api_status.emit(True)
                    break
                response = requests.get(f"{self.api_url}/health", timeout=5)
                if response.status_code == 200:
                    self.api_status.emit(True)
                    break
            except Exception:
                self.api_status.emit(False)
            self.msleep(1000)
            
    def stop(self):
        self.running = False
        
class RegenerationHelper:
    """Lightweight helper for regenerating metadata for a single image"""
    def __init__(self, config):
        self.config = config
        self.llm_processor = llmii.LLMProcessor(config)
        self.et = exiftool.ExifToolHelper(encoding='utf-8')
        
        # Banned words for keyword processing (same as FileProcessor)
        self.banned_words = ["no", "unspecified", "unknown", "unidentified", "identify", "topiary", 
                            "themes concepts", "items animals", "animals objects", "structures landmarks", 
                            "Foreground and background", "notable colors", "textures styles", 
                            "actions activities", "physical appearance", "Gender", "Age range", 
                            "visibly apparent", "apparent ancestry", "Occupation/role", 
                            "Relationships between individuals", "Emotions expressions", "body language"]
    
    def read_metadata(self, file_path):
        """Read current metadata from file"""
        try:
            # Check for sidecar file
            if self.config.use_sidecar and os.path.exists(file_path + ".xmp"):
                file_path = file_path + ".xmp"
            
            # Read metadata - request all keyword and caption fields (matching main collection logic)
            # This ensures we read metadata regardless of which field ExifTool returns it in
            keyword_fields = [
                "Keywords", "IPTC:Keywords", "Composite:keywords", "Subject",
                "DC:Subject", "XMP:Subject", "XMP-dc:Subject", "MWG:Keywords"
            ]
            caption_fields = [
                "Description", "XMP:Description", "ImageDescription", "DC:Description",
                "EXIF:ImageDescription", "Composite:Description", "Caption", "IPTC:Caption",
                "Composite:Caption", "IPTC:Caption-Abstract", "XMP-dc:Description",
                "PNG:Description", "MWG:Description"
            ]
            exiftool_fields = (
                ["SourceFile", "XMP:Identifier", "XMP:Status"] +
                keyword_fields +
                caption_fields
            )
            
            result = self.et.get_tags([file_path], tags=exiftool_fields)
            if result and len(result) > 0:
                return result[0]
            return {}
        except Exception as e:
            print(f"Error reading metadata: {e}")
            return {}
    
    def process_keywords(self, metadata, new_keywords):
        """Normalize extracted keywords and deduplicate them.
        Returns only the new keywords (no merging with existing).
        Uses case-insensitive deduplication to prevent duplicates.
        """
        from src.llmii import normalize_keyword
        
        all_keywords = {}  # Use dict to preserve original case while deduplicating case-insensitively
        
        # Process only new keywords (no merging with existing)
        for keyword in new_keywords:
            if not keyword:
                continue
            normalized = normalize_keyword(keyword, self.banned_words, self.config)
            if normalized:
                # Use lowercase as key for case-insensitive deduplication
                # Only add if not already present (case-insensitive check)
                if normalized.lower() not in all_keywords:
                    all_keywords[normalized.lower()] = normalized
        
        if all_keywords:
            return list(all_keywords.values())
        else:
            return []
    
    def generate_metadata(self, metadata, processed_image):
        """Generate new metadata (reusing logic from FileProcessor.generate_metadata)"""
        from src.llmii import clean_json, clean_string
        
        new_metadata = {}
        existing_caption = metadata.get("MWG:Description")
        caption = None
        keywords = None
        detailed_caption = ""
        old_keywords = metadata.get("MWG:Keywords", [])
        file_path = metadata["SourceFile"]
        
        try:
            # Determine what to generate based on generation_mode
            generation_mode = getattr(self.config, 'generation_mode', 'both')
            
            if generation_mode == "description_only":
                detailed_caption = clean_string(self.llm_processor.describe_content(task="caption", processed_image=processed_image))
                if existing_caption and self.config.update_caption:
                    caption = existing_caption + "<generated>" + detailed_caption + "</generated>"
                else:
                    caption = detailed_caption
                keywords = []
                status = "success" if caption else "retry"
                
            elif generation_mode == "keywords_only":
                data = clean_json(self.llm_processor.describe_content(task="keywords_only", processed_image=processed_image))
                if isinstance(data, dict):
                    keywords = data.get("Keywords")
                else:
                    keywords = None
                caption = existing_caption
                if not keywords:
                    status = "retry"
                else:
                    status = "success"
                    # For regeneration, don't merge existing keywords - only process new ones
                    # Create metadata copy without existing keywords to prevent duplication
                    metadata_without_keywords = metadata.copy()
                    metadata_without_keywords.pop("MWG:Keywords", None)
                    keywords = self.process_keywords(metadata_without_keywords, keywords)
                    
            else:  # generation_mode == "both"
                if not self.config.no_caption and self.config.detailed_caption:
                    data = clean_json(self.llm_processor.describe_content(task="keywords_only", processed_image=processed_image))
                    detailed_caption = clean_string(self.llm_processor.describe_content(task="caption", processed_image=processed_image))
                    if existing_caption and self.config.update_caption:
                        caption = existing_caption + "<generated>" + detailed_caption + "</generated>"
                    else:
                        caption = detailed_caption
                    if isinstance(data, dict):
                        keywords = data.get("Keywords")
                else:
                    data = clean_json(self.llm_processor.describe_content(task="caption_and_keywords", processed_image=processed_image))
                    if isinstance(data, dict):
                        keywords = data.get("Keywords")
                        if not existing_caption and not self.config.no_caption:
                            caption = data.get("Description")
                        elif existing_caption and self.config.update_caption:
                            caption = existing_caption + "<generated>" + data.get("Description", "") + "</generated>"
                        else:
                            caption = data.get("Description")
                
                if keywords:
                    keywords = self.process_keywords(metadata, keywords)
                else:
                    keywords = []
                
                if not caption and not self.config.no_caption:
                    status = "retry"
                elif not keywords:
                    status = "retry"
                else:
                    status = "success"
            
            # Build new metadata dict
            new_metadata = metadata.copy()
            
            # For description_only: preserve existing keywords
            if generation_mode == "description_only":
                # Don't overwrite keywords - keep existing ones
                if caption:
                    new_metadata["MWG:Description"] = caption
                # Keywords remain from metadata.copy() above
            
            # For keywords_only: preserve existing description
            elif generation_mode == "keywords_only":
                # Always preserve existing description (even if empty)
                if existing_caption is not None:
                    new_metadata["MWG:Description"] = existing_caption
                if keywords is not None:
                    new_metadata["MWG:Keywords"] = keywords if keywords else []
            
            # For both: set both
            else:  # generation_mode == "both"
                if keywords is not None:
                    new_metadata["MWG:Keywords"] = keywords if keywords else []
                if caption:
                    new_metadata["MWG:Description"] = caption
            
            # Set identifier if not present
            if not new_metadata.get("XMP:Identifier"):
                new_metadata["XMP:Identifier"] = str(uuid.uuid4())
            
            new_metadata["XMP:Status"] = status
            
            return new_metadata
            
        except Exception as e:
            print(f"Error generating metadata: {e}")
            new_metadata = metadata.copy()
            new_metadata["XMP:Status"] = "failed"
            return new_metadata
    
    def prepare_metadata_for_save(self, metadata):
        """Prepare metadata dictionary for saving to file
        
        Ensures all required fields are present and correctly formatted:
        - XMP:Status set to "success"
        - MWG:Keywords is a list (not None)
        - XMP:Identifier exists (creates if missing)
        - SourceFile is preserved for ExifTool
        
        Args:
            metadata: Metadata dictionary to prepare
            
        Returns:
            Prepared metadata dictionary ready for writing
        """
        # Create a copy to avoid modifying the original
        prepared = metadata.copy()
        
        # Ensure status is "success" when saving
        prepared["XMP:Status"] = "success"
        
        # Ensure keywords is always a list, not None
        # DEBUG: Log keywords in metadata before preparation
        print(f"DEBUG PREPARE: Keywords in metadata: {prepared.get('MWG:Keywords', 'NOT FOUND')}")
        
        if "MWG:Keywords" not in prepared or prepared["MWG:Keywords"] is None:
            prepared["MWG:Keywords"] = []
        elif not isinstance(prepared["MWG:Keywords"], list):
            # Handle case where keywords might be a string
            if isinstance(prepared["MWG:Keywords"], str):
                prepared["MWG:Keywords"] = [prepared["MWG:Keywords"]]
            else:
                prepared["MWG:Keywords"] = []
        
        # Ensure identifier exists
        if "XMP:Identifier" not in prepared or not prepared["XMP:Identifier"]:
            prepared["XMP:Identifier"] = str(uuid.uuid4())
        
        # Ensure SourceFile is set (needed by ExifTool to identify the file)
        # Note: ExifTool uses SourceFile internally but doesn't write it as a tag
        if "SourceFile" not in prepared:
            # This shouldn't happen, but handle gracefully
            pass
        
        return prepared
    
    def write_metadata(self, file_path, metadata, use_sidecar=False, no_backup=False, dry_run=False):
        """Write metadata to file using ExifTool
        
        Reuses logic from FileProcessor.write_metadata() but adapted for GUI use.
        
        Args:
            file_path: Path to the image file
            metadata: Metadata dictionary to write
            use_sidecar: Whether to write to sidecar .xmp file
            no_backup: Whether to skip creating backup files
            dry_run: If True, don't actually write (for testing)
            
        Returns:
            True if successful, False otherwise
        """
        if dry_run:
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
                # Use comprehensive list of all possible fields to ensure complete deletion
                delete_params = [
                    "-Keywords=",
                    "-IPTC:Keywords=",
                    "-XMP:Subject=",
                    "-XMP-dc:Subject=",
                    "-DC:Subject=",
                    "-Subject=",
                    "-Composite:Keywords=",
                    "-MWG:Keywords=",
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
            self.et.set_tags(write_path, tags=metadata, params=params)
            
            return True
            
        except Exception as e:
            print(f"Error writing metadata to {file_path}: {str(e)}")
            return False
    
    def cleanup(self):
        """Clean up resources"""
        try:
            self.et.terminate()
        except:
            pass

class RegenerateThread(QThread):
    """Thread for regenerating metadata for a single image"""
    regeneration_complete = pyqtSignal(str, str, list, str, str, str, dict)  # base64_image, caption, keywords, filename, file_path, save_status, metadata
    regeneration_error = pyqtSignal(str)  # error message
    log_message = pyqtSignal(str)  # log message
    
    def __init__(self, config, base64_image, caption, keywords, filename, file_path, save_status, metadata, manual_keywords=None):
        super().__init__()
        self.config = config
        self.base64_image = base64_image
        self.caption = caption
        self.keywords = keywords
        self.filename = filename
        self.file_path = file_path
        self.save_status = save_status
        self.metadata = metadata
        self.manual_keywords = set(manual_keywords) if manual_keywords else set()
    
    def run(self):
        """Run regeneration in background thread"""
        try:
            # Create regeneration helper
            helper = RegenerationHelper(self.config)
            
            try:
                # Use metadata from history as source of truth (has unsaved changes)
                # Only read from file if status is "saved" to get the latest saved state
                if self.save_status == "saved":
                    # Read current metadata from file (has saved changes)
                    current_metadata = helper.read_metadata(self.file_path)
                    if not current_metadata:
                        # Fallback to metadata from history
                        current_metadata = self.metadata.copy()
                    else:
                        # Ensure SourceFile is set correctly
                        current_metadata["SourceFile"] = self.file_path
                        # Update description from current caption (may have manual edits from UI)
                        current_metadata["MWG:Description"] = self.caption
                        # Merge with history metadata to preserve any unsaved changes (except description which we just set)
                        if "MWG:Keywords" in self.metadata and "MWG:Keywords" not in current_metadata:
                            current_metadata["MWG:Keywords"] = self.metadata["MWG:Keywords"]
                else:
                    # Status is "pending" - use metadata from history (has unsaved changes)
                    current_metadata = self.metadata.copy()
                    current_metadata["SourceFile"] = self.file_path
                    # Update description from current caption (may have manual edits from UI)
                    current_metadata["MWG:Description"] = self.caption
                
                # Generate new metadata using existing processed_image (base64)
                new_metadata = helper.generate_metadata(current_metadata, self.base64_image)
                
                # Extract new caption and keywords
                new_caption = new_metadata.get("MWG:Description", "")
                new_keywords = new_metadata.get("MWG:Keywords", [])
                
                # Merge manual keywords with generated keywords (preserve manual ones)
                if self.manual_keywords:
                    # Convert manual keywords to lowercase for comparison
                    manual_keywords_lower = {kw.lower() for kw in self.manual_keywords}
                    # Add manual keywords that aren't already in generated keywords
                    for manual_kw in self.manual_keywords:
                        if manual_kw.lower() not in {kw.lower() for kw in new_keywords}:
                            new_keywords.append(manual_kw)
                
                # Determine new save_status (pending since we're in preview mode)
                new_save_status = "pending"
                
                # Emit success signal with new data (matching image_history tuple order)
                self.regeneration_complete.emit(
                    self.base64_image, new_caption, new_keywords, 
                    self.filename, self.file_path, new_save_status, new_metadata
                )
                
            finally:
                # Clean up helper
                helper.cleanup()
                
        except Exception as e:
            error_msg = f"Error regenerating metadata for {os.path.basename(self.filename)}: {str(e)}"
            self.regeneration_error.emit(error_msg)
        
class IndexerThread(QThread):
    output_received = pyqtSignal(str)
    image_processed = pyqtSignal(str, str, list, str, dict, str)  # base64_image, caption, keywords, filename, metadata, save_status

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.paused = False
        self.stopped = False

    def process_callback(self, message):
        """Callback for llmii's process_file function"""
        # Check if message is a dictionary with image data
        if isinstance(message, dict) and 'type' in message and message['type'] == 'image_data':
            # Extract the image data and emit signal
            base64_image = message.get('base64_image', '')
            caption = message.get('caption', '')
            keywords = message.get('keywords') or []  # Handle None explicitly
            file_path = message.get('file_path', '')
            metadata = message.get('metadata', {})
            save_status = message.get('save_status', 'pending')
            self.image_processed.emit(base64_image, caption, keywords, file_path, metadata, save_status)
        else:
            # Regular text message for the log
            self.output_received.emit(str(message))

    def run(self):
        try:
            # Pass our callback function to llmii
            llmii.main(self.config, self.process_callback, self.check_paused_or_stopped)
        except Exception as e:
            self.output_received.emit(f"Error: {str(e)}")

    def check_paused_or_stopped(self):
        if self.stopped:
            raise Exception("Indexer stopped by user")
        if self.paused:
            while self.paused and not self.stopped:
                self.msleep(100)
            if self.stopped:
                raise Exception("Indexer stopped by user")
        return self.paused

class CustomTooltip(QLabel):
    """Custom tooltip widget that can be positioned above the cursor"""
    
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.setText(text)
        self.setWordWrap(True)
        self.setMaximumWidth(500)
        self.setStyleSheet("""
            QLabel {
                background-color: #2b2b2b;
                color: white;
                padding: 4px 8px;
                border: 1px solid #555555;
                border-radius: 4px;
                font-size: 9px;
            }
        """)
        self.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.adjustSize()
    
    def showAtPosition(self, global_pos):
        """Show tooltip above the cursor position"""
        # Position above cursor with small offset
        tooltip_height = self.height()
        tooltip_width = self.width()
        x = global_pos.x() - tooltip_width // 2
        y = global_pos.y() - tooltip_height - 10  # 10px above cursor
        self.move(x, y)
        self.show()

class KeywordPillWidget(QWidget):
    """Custom widget for keyword pill with integrated remove button"""
    
    def __init__(self, keyword, is_manual=False, parent=None):
        super().__init__(parent)
        self.keyword = keyword
        self.is_manual = is_manual
        
        # Create horizontal layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 2, 2)  # Left padding for text, right padding for button
        layout.setSpacing(4)
        
        # Define colors based on whether this is a manual keyword
        if is_manual:
            # Green theme for manual keywords
            text_color = "#22aa22"
            bg_color = "#d4f4d4"  # Light green background
            border_color = "#88dd88"  # Medium green border
            button_color = "#22aa22"  # Green text for remove button
        else:
            # Default blue theme for generated keywords
            text_color = GuiConfig.COLOR_KEYWORD_TEXT
            bg_color = GuiConfig.COLOR_KEYWORD_BG
            border_color = GuiConfig.COLOR_KEYWORD_BORDER
            button_color = GuiConfig.COLOR_KEYWORD_TEXT
        
        # Keyword text label - allow it to expand to show full text
        self.keyword_label = QLabel(keyword)
        self.keyword_label.setWordWrap(False)  # Don't wrap text
        self.keyword_label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        self.keyword_label.setStyleSheet(f"""
            background-color: transparent;
            color: {text_color};
            padding: 0px;
            border: none;
            font-size: {GuiConfig.FONT_SIZE_NORMAL}px;
        """)
        
        # Remove button (12x12, integrated)
        self.remove_button = QPushButton("×")
        self.remove_button.setFixedSize(12, 12)
        self.remove_button.setToolTip("Remove Keyword")
        self.remove_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {button_color};
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 8px;
                padding: 0px;
                min-width: 12px;
                max-width: 12px;
                min-height: 12px;
                max-height: 12px;
            }}
            QPushButton:hover {{
                background-color: #ff4444;
                color: white;
            }}
            QPushButton:pressed {{
                background-color: #cc0000;
                color: white;
            }}
        """)
        
        # Add widgets to layout - label should expand, button stays fixed
        layout.addWidget(self.keyword_label, 1)  # Stretch factor 1 to allow expansion
        layout.addWidget(self.remove_button, 0)  # No stretch for button
        
        # Set fixed height, flexible width - use Preferred to allow expansion
        self.setFixedHeight(20)  # Fixed height for consistent appearance
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        
        # Store colors for paintEvent
        self.bg_color = bg_color
        self.border_color = border_color
        
        # Custom tooltip for keyword text
        self.custom_tooltip = None
        self.tooltip_timer = QTimer()
        self.tooltip_timer.setSingleShot(True)
        self.tooltip_timer.timeout.connect(self.show_tooltip)
        
        # Enable mouse tracking for tooltip
        self.setMouseTracking(True)
    
    def paintEvent(self, event):
        """Override paintEvent to draw the pill background with rounded corners"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw rounded rectangle background
        rect = self.rect().adjusted(0, 0, -1, -1)  # Adjust for border
        painter.setBrush(QColor(self.bg_color))
        painter.setPen(QPen(QColor(self.border_color), 1))
        painter.drawRoundedRect(rect, 4, 4)  # 4px radius for rounded corners
        
        super().paintEvent(event)
    
    def enterEvent(self, event):
        """Show tooltip after a short delay when mouse enters"""
        # Store the cursor position for tooltip positioning
        if isinstance(event, QEnterEvent):
            self.last_cursor_pos = event.globalPosition().toPoint()
        else:
            # Fallback: get current global cursor position
            self.last_cursor_pos = QCursor.pos()
        self.tooltip_timer.start(500)  # 500ms delay
        super().enterEvent(event)
    
    def mouseMoveEvent(self, event):
        """Update cursor position for tooltip"""
        self.last_cursor_pos = event.globalPosition().toPoint()
        super().mouseMoveEvent(event)
    
    def leaveEvent(self, event):
        """Hide tooltip when mouse leaves"""
        self.tooltip_timer.stop()
        if self.custom_tooltip:
            self.custom_tooltip.hide()
            self.custom_tooltip.deleteLater()
            self.custom_tooltip = None
        super().leaveEvent(event)
    
    def show_tooltip(self):
        """Show the custom tooltip above the cursor"""
        if not self.custom_tooltip:
            self.custom_tooltip = CustomTooltip(self.keyword, self.window())
        # Use the stored cursor position
        if hasattr(self, 'last_cursor_pos'):
            self.custom_tooltip.showAtPosition(self.last_cursor_pos)
        else:
            # Fallback to center if position not available
            cursor_pos = self.mapToGlobal(self.rect().center())
            self.custom_tooltip.showAtPosition(cursor_pos)

class KeywordWidget(QWidget):
    keywords_changed = pyqtSignal(list)  # Signal emitted when keywords change
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.keywords = []
        self.manual_keywords = set()  # Track manually added keywords
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(GuiConfig.CONTENT_MARGINS, GuiConfig.CONTENT_MARGINS, GuiConfig.CONTENT_MARGINS, GuiConfig.CONTENT_MARGINS)
        
        # Add input field and button for adding keywords
        input_container = QWidget()
        input_container_layout = QVBoxLayout(input_container)
        input_container_layout.setContentsMargins(0, 0, 0, 0)
        input_container_layout.setSpacing(4)
        
        input_layout = QHBoxLayout()
        input_layout.setSpacing(4)
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("Enter keyword...")
        self.keyword_input.textChanged.connect(self.validate_input_realtime)
        self.keyword_input.returnPressed.connect(self.add_keyword_from_input)
        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add_keyword_from_input)
        self.add_button.setEnabled(False)  # Initially disabled
        input_layout.addWidget(self.keyword_input)
        input_layout.addWidget(self.add_button)
        input_container_layout.addLayout(input_layout)
        
        # Error message label (initially hidden)
        self.error_label = QLabel("Only letters, numbers, and spaces allowed")
        self.error_label.setStyleSheet("color: #ff4444; font-size: 11px; padding: 2px 0px;")
        self.error_label.hide()
        input_container_layout.addWidget(self.error_label)
        
        self.layout.addWidget(input_container)
        
        # Create the container for keyword rows
        self.keywords_container = QWidget()
        self.keywords_layout = QVBoxLayout(self.keywords_container)
        self.keywords_container.setStyleSheet("border: none; padding: 0px")
        self.keywords_layout.setContentsMargins(GuiConfig.CONTENT_MARGINS, GuiConfig.CONTENT_MARGINS, GuiConfig.CONTENT_MARGINS, GuiConfig.CONTENT_MARGINS)
        self.keywords_layout.setSpacing(0)
        self.keywords_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        
        # Set fixed size policy for container
        self.keywords_container.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        
        # Add container to layout
        self.layout.addWidget(self.keywords_container)
        
        # Ensure widget doesn't expand beyond its allocated space
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
    
    def clear(self):
        # Clear keywords layout synchronously
        while self.keywords_layout.count():
            item = self.keywords_layout.takeAt(0)
            if item:
                widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()
        self.keywords = []
        # Force immediate update to ensure widgets are removed
        QApplication.processEvents()
    
    def show_generating_message(self):
        """Show a temporary 'Regenerating Keywords...' message"""
        self.clear()
        # Create a container widget for the message (similar to how keywords are displayed in rows)
        message_widget = QWidget()
        message_layout = QHBoxLayout(message_widget)
        message_layout.setContentsMargins(0, 0, 0, 0)
        message_layout.setSpacing(2)
        
        generating_label = QLabel("Regenerating Keywords...")
        generating_label.setStyleSheet("color: #2196F3; font-style: italic; padding: 4px;")
        generating_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        generating_label.setWordWrap(True)
        # Ensure the label is visible and has proper size
        generating_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        generating_label.setMinimumHeight(20)  # Ensure label has minimum height to be visible
        
        message_layout.addWidget(generating_label)
        message_layout.addStretch()  # Push label to the left
        
        message_widget.show()
        self.keywords_layout.addWidget(message_widget)
        # Ensure container is visible and updated
        self.keywords_container.show()
        self.keywords_container.update()
        self.update()  # Update the widget itself
        # Force update to ensure label is displayed
        QApplication.processEvents()
    
    def set_keywords(self, keywords, manual_keywords=None):
        """Set keywords to display
        
        Args:
            keywords: List of keyword strings
            manual_keywords: Set of manually added keywords (for green styling)
        """
        # DEBUG: Log when set_keywords is called - Option 4
        print(f"DEBUG SET_KEYWORDS: Setting {len(keywords) if keywords else 0} keywords: {keywords}")
        print(f"DEBUG SET_KEYWORDS: Manual keywords: {manual_keywords}")
        
        self.clear()
        self.keywords = keywords
        
        # Update manual_keywords set if provided
        if manual_keywords is not None:
            self.manual_keywords = manual_keywords.copy() if isinstance(manual_keywords, set) else set(manual_keywords)
        
        if not keywords:
            return
        
        # Display keywords with natural wrapping based on available width
        # Get the container width for wrapping calculation
        container_width = self.keywords_container.width()
        if container_width <= 0:
            # If container hasn't been sized yet, use a default
            container_width = 400
        
        current_row = 0
        row_layouts = []
        current_row_width = 0
        spacing = 2  # Spacing between keywords
        
        # Create the first row
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(spacing)
        row_layouts.append(row_layout)
        self.keywords_layout.addWidget(row_widget)
        
        # Add keyword pills with natural wrapping
        for keyword in keywords:
            # Check if this keyword is manual (case-insensitive)
            keyword_lower = keyword.lower()
            is_manual = any(kw.lower() == keyword_lower for kw in self.manual_keywords)
            
            # Create keyword pill widget with manual indicator
            keyword_pill = KeywordPillWidget(keyword, is_manual=is_manual)
            keyword_pill.remove_button.clicked.connect(lambda checked, kw=keyword: self.remove_keyword(kw))
            
            # Get the preferred size of the pill
            keyword_pill.adjustSize()
            pill_width = keyword_pill.sizeHint().width()
            
            # Check if we need to wrap to a new row
            # Account for margins and spacing
            if current_row_width > 0 and (current_row_width + spacing + pill_width) > container_width:
                # Start a new row
                current_row += 1
                current_row_width = 0
                row_widget = QWidget()
                row_layout = QHBoxLayout(row_widget)
                row_layout.setContentsMargins(0, 0, 0, 0)
                row_layout.setSpacing(spacing)
                row_layouts.append(row_layout)
                self.keywords_layout.addWidget(row_widget)
            
            # Add the keyword pill to the current row
            row_layouts[current_row].addWidget(keyword_pill)
            current_row_width += pill_width + (spacing if current_row_width > 0 else 0)
        
        # Add stretch to each row to push keywords to the left
        for row_layout in row_layouts:
            row_layout.addStretch(1)
    
    def validate_input_realtime(self):
        """Validate input field in real-time and update UI state"""
        import re
        text = self.keyword_input.text()
        
        # Check if input contains invalid characters (only check for invalid chars, not empty)
        if text and not re.match(r'^[a-zA-Z0-9\s]+$', text):
            # Invalid: show error state
            self.keyword_input.setStyleSheet("border: 2px solid #ff4444; padding: 4px;")
            self.error_label.show()
            self.add_button.setEnabled(False)
        else:
            # Valid or empty: clear error state
            self.keyword_input.setStyleSheet("border: 1px solid palette(mid); padding: 4px;")  # Explicit default style
            self.error_label.hide()
            # Enable button only if there's text (not empty)
            self.add_button.setEnabled(bool(text.strip()))
    
    def validate_keyword(self, keyword):
        """Validate keyword: only letters, numbers, and spaces allowed
        
        Args:
            keyword: Keyword string to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not keyword or not keyword.strip():
            return (False, "Keyword cannot be empty")
        
        # Trim whitespace
        keyword = keyword.strip()
        
        # Check for special characters (allow only letters, numbers, and spaces)
        import re
        if not re.match(r'^[a-zA-Z0-9\s]+$', keyword):
            return (False, "Keyword can only contain letters, numbers, and spaces")
        
        return (True, None)
    
    def add_keyword(self, keyword):
        """Programmatically add a keyword to the list
        
        Args:
            keyword: Keyword string to add
        """
        # Validate keyword
        is_valid, error_msg = self.validate_keyword(keyword)
        if not is_valid:
            print(f"Invalid keyword: {error_msg}")
            return False
        
        keyword = keyword.strip()
        
        # Check for duplicates (case-insensitive)
        keyword_lower = keyword.lower()
        if any(kw.lower() == keyword_lower for kw in self.keywords):
            print(f"Keyword '{keyword}' already exists")
            return False
        
        # Add keyword
        self.keywords.append(keyword)
        
        # Mark as manual keyword (when added via UI)
        self.manual_keywords.add(keyword)
        
        # Re-display keywords
        self.set_keywords(self.keywords, manual_keywords=self.manual_keywords)
        
        # Emit signal to notify parent
        self.keywords_changed.emit(self.keywords)
        
        return True
    
    def add_keyword_from_input(self):
        """Add keyword from input field"""
        keyword = self.keyword_input.text()
        
        # Check if button is enabled (input is valid)
        if not self.add_button.isEnabled():
            return
        
        if self.add_keyword(keyword):
            # Clear input field on success and reset validation state
            self.keyword_input.clear()
            self.validate_input_realtime()  # Reset UI state
    
    def remove_keyword(self, keyword):
        """Remove a keyword from the list
        
        Args:
            keyword: Keyword string to remove
        """
        # Remove keyword (case-insensitive match)
        keyword_lower = keyword.lower()
        self.keywords = [kw for kw in self.keywords if kw.lower() != keyword_lower]
        
        # Remove from manual_keywords if present
        self.manual_keywords = {kw for kw in self.manual_keywords if kw.lower() != keyword_lower}
        
        # Re-display keywords
        self.set_keywords(self.keywords, manual_keywords=self.manual_keywords)
        
        # Emit signal to notify parent
        self.keywords_changed.emit(self.keywords)

class PauseHandler(QObject):
    pause_signal = pyqtSignal(bool)
    stop_signal = pyqtSignal()

class ImageIndexerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Apply fixed window size
        self.setWindowTitle("Image Indexer GUI")
        self.setFixedSize(GuiConfig.WINDOW_WIDTH, GuiConfig.WINDOW_HEIGHT)
        # Disable maximize button and resizing
        if GuiConfig.WINDOW_FIXED:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowMaximizeButtonHint)
            self.setFixedSize(GuiConfig.WINDOW_WIDTH, GuiConfig.WINDOW_HEIGHT)
            
        self.settings_dialog = SettingsDialog(self)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(2)
        main_layout.setContentsMargins(GuiConfig.CONTENT_MARGINS, GuiConfig.CONTENT_MARGINS, GuiConfig.CONTENT_MARGINS, GuiConfig.CONTENT_MARGINS)
        
        # Upper section with controls - fixed height
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(GuiConfig.SPACING)
        
        # Directory and Settings section
        dir_layout = QHBoxLayout()
        self.dir_input = QLineEdit()
        dir_button = QPushButton("Select Directory")
        dir_button.clicked.connect(self.select_directory)
        dir_layout.addWidget(QLabel("Directory:"))
        dir_layout.addWidget(self.dir_input)
        dir_layout.addWidget(dir_button)
        controls_layout.addLayout(dir_layout)

        # Settings button, Auto-save toggle, and API status in one row
        settings_api_layout = QHBoxLayout()
        settings_button = QPushButton("Settings")
        settings_button.clicked.connect(self.show_settings)
        
        # Auto-save toggle button
        self.auto_save_button = QPushButton("Auto-save: OFF")
        self.auto_save_button.setCheckable(True)
        self.auto_save_button.setChecked(False)  # Default to preview mode
        self.auto_save_button.clicked.connect(self.toggle_auto_save)
        self.auto_save_button.setStyleSheet("""
            QPushButton {
                background-color: #555555;
                border: 1px solid palette(mid);
                border-radius: 3px;
                padding: 4px 12px;
                min-width: 100px;
            }
            QPushButton:checked {
                background-color: #4CAF50;
                color: white;
            }
            QPushButton:hover {
                background-color: palette(light);
            }
            QPushButton:checked:hover {
                background-color: #45a049;
            }
        """)
        
        self.api_status_label = QLabel("API Status: Checking...")
        settings_api_layout.addWidget(settings_button)
        settings_api_layout.addWidget(self.auto_save_button)
        settings_api_layout.addStretch(1)
        settings_api_layout.addWidget(self.api_status_label)
        controls_layout.addLayout(settings_api_layout)
        
        # Control buttons
        button_layout = QHBoxLayout()
        self.run_button = QPushButton("Run Image Indexer")
        self.run_button.clicked.connect(self.run_indexer)
        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.toggle_pause)
        self.pause_button.setEnabled(False)
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_indexer)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.run_button)
        button_layout.addWidget(self.pause_button)
        button_layout.addWidget(self.stop_button)
        controls_layout.addLayout(button_layout)
        
        # Set fixed height for controls widget
        controls_widget.setFixedHeight(GuiConfig.CONTROL_PANEL_HEIGHT)
        main_layout.addWidget(controls_widget)
        nav_widget = QWidget()
        
        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(GuiConfig.CONTENT_MARGINS, GuiConfig.CONTENT_MARGINS, GuiConfig.CONTENT_MARGINS, GuiConfig.CONTENT_MARGINS)
        nav_layout.setSpacing(GuiConfig.SPACING)

        # Create navigation buttons
        self.first_button = QPushButton("|<")  # Go to first image
        self.prev_button = QPushButton("<")    # Go to previous image
        self.position_label = QLabel("No images processed")
        self.position_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.next_button = QPushButton(">")    # Go to next image
        self.last_button = QPushButton(">|")   # Go to most recent image

        # Add widgets to layout
        nav_layout.addWidget(self.first_button)
        nav_layout.addWidget(self.prev_button)
        nav_layout.addStretch(1)
        nav_layout.addWidget(self.position_label)
        nav_layout.addStretch(1)
        nav_layout.addWidget(self.next_button)
        nav_layout.addWidget(self.last_button)

        # Connect button signals to slots
        self.first_button.clicked.connect(self.navigate_first)
        self.prev_button.clicked.connect(self.navigate_prev)
        self.next_button.clicked.connect(self.navigate_next)
        self.last_button.clicked.connect(self.navigate_last)

        # Set initial button states (disabled until we have images)
        self.first_button.setEnabled(False)
        self.prev_button.setEnabled(False)
        self.next_button.setEnabled(False)
        self.last_button.setEnabled(False)

        # Add to the main layout
        main_layout.addWidget(nav_widget)
        
        # Middle section with image and metadata side by side
        middle_section = QWidget()
        middle_layout = QHBoxLayout(middle_section)
        middle_layout.setContentsMargins(0, 0, 0, 0)
        middle_layout.setSpacing(GuiConfig.SPACING)
        
        # Image preview panel - fixed size
        image_frame = QFrame()
        image_frame.setFrameShape(QFrame.Shape.Box)
        image_frame.setStyleSheet(f"border: 1px solid {GuiConfig.COLOR_BORDER}; padding: 0px;")
        
        image_layout = QVBoxLayout(image_frame)
        image_layout.setContentsMargins(1, 1, 1, 1)
        
        # Image preview label with fixed size
        self.image_preview = QLabel("No image processed yet")
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_preview.setFixedSize(GuiConfig.IMAGE_PREVIEW_WIDTH -12, GuiConfig.IMAGE_PREVIEW_HEIGHT -12)
        self.image_preview.setFrameShape(QFrame.Shape.NoFrame)
        self.image_preview.setStyleSheet("border: none; background-color: transparent;")
               
        image_layout.addWidget(self.image_preview, 0, Qt.AlignmentFlag.AlignCenter)
        
        image_frame.setFixedSize(GuiConfig.IMAGE_PREVIEW_WIDTH, GuiConfig.IMAGE_PREVIEW_HEIGHT)
        middle_layout.addWidget(image_frame)
        
        # Metadata panel - fixed size
        metadata_frame = QFrame()
        
        metadata_frame.setFrameShape(QFrame.Shape.Box)
        metadata_frame.setStyleSheet(f"border: 1px solid {GuiConfig.COLOR_BORDER};")
        #metadata_frame.setStyleSheet("")
        metadata_layout = QVBoxLayout(metadata_frame)
        metadata_layout.setContentsMargins(GuiConfig.CONTENT_MARGINS, GuiConfig.CONTENT_MARGINS, GuiConfig.CONTENT_MARGINS, GuiConfig.CONTENT_MARGINS)
        metadata_layout.setSpacing(GuiConfig.SPACING)
        
        # Image filename
        self.filename_label = QLabel("Filename: ")
        self.filename_label.setStyleSheet("font-weight: bold; border:none;")
        self.filename_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.filename_label.setFixedHeight(GuiConfig.FILENAME_LABEL_HEIGHT)
        
        metadata_layout.addWidget(self.filename_label)
        
        # Action buttons row (Save, Regenerate, Ignore)
        action_buttons_layout = QHBoxLayout()
        action_buttons_layout.setSpacing(10)
        
        self.save_button = QPushButton("Save")
        self.save_button.setEnabled(False)  # Disabled initially
        self.regenerate_button = QPushButton("Regenerate")
        self.regenerate_button.setEnabled(False)  # Disabled initially
        self.ignore_button = QPushButton("Ignore")
        self.ignore_button.setEnabled(False)  # Disabled initially
        self.clear_button = QPushButton("Clear metadata")
        self.clear_button.setEnabled(False)  # Disabled initially (no image selected)
        # Style clear button as red/destructive
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: 1px solid #dc3545;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #c82333;
                border-color: #bd2130;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
            QPushButton:disabled {
                background-color: #e0e0e0;
                color: #888888;
                border: 1px solid #c0c0c0;
            }
        """)
        
        # Button styles are now applied globally in run_gui(), so all buttons have consistent styling
        
        action_buttons_layout.addWidget(self.save_button)
        action_buttons_layout.addWidget(self.regenerate_button)
        action_buttons_layout.addWidget(self.ignore_button)
        action_buttons_layout.addWidget(self.clear_button)
        action_buttons_layout.addStretch()  # Push buttons to the left
        
        # Connect button signals
        self.save_button.clicked.connect(self.save_current_image)
        self.regenerate_button.clicked.connect(self.regenerate_current_image)
        self.ignore_button.clicked.connect(self.ignore_current_image)
        self.clear_button.clicked.connect(self.clear_current_image_metadata)
        
        metadata_layout.addLayout(action_buttons_layout)
        
        # Caption
        caption_container = QWidget()  # Simple container instead of QGroupBox
        caption_layout = QVBoxLayout(caption_container)
        caption_layout.setContentsMargins(0, 0, 0, 0)  # No extra margins
        caption_layout.setSpacing(4)  # Small spacing between label and edit
        
        # Label for "Caption" (store reference for indicator updates)
        self.caption_label = QLabel("Caption")
        self.caption_label.setStyleSheet("font-weight: bold;")
        caption_layout.addWidget(self.caption_label)
        
        # Editable caption field
        self.caption_edit = QPlainTextEdit()
        self.caption_edit.setPlaceholderText("No description. Write an image description here or click Regenerate to get started.")
        self.caption_edit.setFixedHeight(200)  # Fixed height for caption area
        self.caption_edit.setStyleSheet("padding: 4px; font-weight: normal; border: 1px solid palette(mid);")
        # Explicit scrollbar control - only show when needed
        self.caption_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.caption_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        # Connect textChanged signal to track manual edits
        self.caption_edit.textChanged.connect(self.on_caption_edited)
        caption_layout.addWidget(self.caption_edit)
        
        metadata_layout.addWidget(caption_container, 0, Qt.AlignmentFlag.AlignTop)
        
        # Keywords
        self.keywords_widget = KeywordWidget(self)
        # Connect signal to handle keyword changes
        self.keywords_widget.keywords_changed.connect(self.on_keywords_changed)
        metadata_layout.addWidget(self.keywords_widget)
        
        # Set fixed size for metadata frame
        metadata_frame.setFixedSize(GuiConfig.METADATA_WIDTH, GuiConfig.METADATA_HEIGHT)
        middle_layout.addWidget(metadata_frame)
        
        # Add middle section to main layout
        main_layout.addWidget(middle_section)
        
        # Bottom section - log output with fixed size
        log_frame = QFrame()
        log_frame.setFrameShape(QFrame.Shape.Box)
        log_frame.setFrameStyle(QFrame.Shape.NoFrame)
        log_layout = QVBoxLayout(log_frame)
        log_layout.setContentsMargins(GuiConfig.CONTENT_MARGINS, GuiConfig.CONTENT_MARGINS, GuiConfig.CONTENT_MARGINS, GuiConfig.CONTENT_MARGINS)
        log_label = QLabel("Processing Log:")
        log_layout.addWidget(log_label)
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        log_layout.addWidget(self.output_area)
        
        # Set fixed size for log frame
        log_frame.setFixedSize(GuiConfig.LOG_WIDTH, GuiConfig.LOG_HEIGHT)
        main_layout.addWidget(log_frame)
        
        # Store the previous image data to keep showing something
        self.previous_image_data = None
        self.previous_caption = None
        self.previous_keywords = None
        self.previous_filename = None
        self.pause_handler = PauseHandler()
        self.api_check_thread = None
        self.api_is_ready = False
        self.run_button.setEnabled(False)
        self.image_history = []  # [(base64_image, caption, keywords, filename, file_path, save_status, metadata_dict)]
        self.current_position = -1
        self.manual_edits = {}  # {file_path: {'caption_edited': bool, 'keywords_manual': set}}
        self._updating_caption = False  # Flag to prevent signal handler during programmatic updates
        
        if os.path.exists('settings.json'):
            try:
                with open('settings.json', 'r') as f:
                    settings = json.load(f)
                    self.dir_input.setText(settings.get('directory', ''))
                    # Sync auto-save button with settings
                    auto_save_enabled = settings.get('auto_save', False)
                    self.auto_save_button.setChecked(auto_save_enabled)
                    if auto_save_enabled:
                        self.auto_save_button.setText("Auto-save: ON")
                    else:
                        self.auto_save_button.setText("Auto-save: OFF")
                    self.start_api_check(settings.get('api_url', 'http://localhost:5001'))
                    
            except Exception as e:
                print(f"Error loading settings: {e}")
                self.start_api_check('http://localhost:5001')
        else:
            self.start_api_check('http://localhost:5001')

    def toggle_auto_save(self):
        """Toggle auto-save mode and update UI"""
        is_enabled = self.auto_save_button.isChecked()
        
        if is_enabled:
            self.auto_save_button.setText("Auto-save: ON")
            # Sync with settings dialog
            self.settings_dialog.auto_save_checkbox.setChecked(True)
        else:
            self.auto_save_button.setText("Auto-save: OFF")
            # Sync with settings dialog
            self.settings_dialog.auto_save_checkbox.setChecked(False)
        
        # Update Save button state based on current image
        if self.image_history:
            if self.current_position == -1:
                idx = len(self.image_history) - 1
            else:
                idx = self.current_position
            if idx >= 0 and idx < len(self.image_history):
                _, _, _, _, _, save_status, _ = self.image_history[idx]
                self.update_action_buttons(save_status)

    def show_settings(self):
        if self.settings_dialog.exec() == QDialog.DialogCode.Accepted:
            self.settings_dialog.save_settings()
            
            # Sync auto-save button with settings dialog
            auto_save_enabled = self.settings_dialog.auto_save_checkbox.isChecked()
            self.auto_save_button.setChecked(auto_save_enabled)
            if auto_save_enabled:
                self.auto_save_button.setText("Auto-save: ON")
            else:
                self.auto_save_button.setText("Auto-save: OFF")
            
            self.start_api_check(self.settings_dialog.api_url_input.text())
            
            try:
                with open('settings.json', 'r') as f:
                    settings = json.load(f)
                settings['directory'] = self.dir_input.text()
                with open('settings.json', 'w') as f:
                    json.dump(settings, f, indent=4)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save directory setting: {e}")

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.dir_input.setText(directory)

    def start_api_check(self, api_url):
        self.api_url = api_url
        if self.api_check_thread and self.api_check_thread.isRunning():
            self.api_check_thread.stop()
            self.api_check_thread.wait()
            
        self.api_is_ready = False
        self.run_button.setEnabled(False)
        self.api_status_label.setText("API Status: Checking...")
        self.api_status_label.setStyleSheet("color: orange; padding: 4px")

        self.api_check_thread = APICheckThread(api_url if api_url else self.settings_dialog.api_url_input.text())
        self.api_check_thread.api_status.connect(self.update_api_status)
        self.api_check_thread.start()

    def update_api_status(self, is_available):
        if is_available:
            self.api_is_ready = True
            self.api_status_label.setText("API Status: Connected")
            self.api_status_label.setStyleSheet("color: green; padding: 4px")
            self.run_button.setEnabled(True)
            
            # Stop the check thread once we're connected
            if self.api_check_thread:
                self.api_check_thread.stop()
        else:
            self.api_is_ready = False
            self.api_status_label.setText("API Status: Waiting for connection...")
            self.api_status_label.setStyleSheet("color: red; padding: 4px")
            self.run_button.setEnabled(False)
    
    def update_image_preview(self, base64_image, caption, keywords, filename, metadata, save_status):
        self.previous_image_data = base64_image
        self.previous_caption = caption
        self.previous_keywords = keywords
        self.previous_filename = filename
        
        # Extract file_path from metadata if not provided directly
        file_path = metadata.get('SourceFile', filename) if isinstance(metadata, dict) else filename
        
        # Add to history with extended structure
        self.image_history.append((base64_image, caption, keywords, filename, file_path, save_status, metadata))
        
        # If user was viewing the most recent image (or this is the first image),
        # update current_position to point to the new image
        if self.current_position == -1 or len(self.image_history) <= 1:
            self.current_position = -1  # Keep at most recent
            self.display_image(base64_image, caption, keywords, filename, save_status)
            self.update_action_buttons(save_status)
        else:
            # Just update navigation buttons without changing the view
            self.update_navigation_buttons()
            # Also update action buttons for the currently viewed image
            if self.current_position >= 0 and self.current_position < len(self.image_history):
                _, _, _, _, _, current_status, _ = self.image_history[self.current_position]
                self.update_action_buttons(current_status)
            
    def display_image(self, base64_image, caption, keywords, filename, save_status="pending"):
        # Update the UI with the image data
        try:
            # Convert base64 to QImage
            image_data = base64.b64decode(base64_image)
            image = QImage.fromData(image_data)
            if not image.isNull():
                pixmap = QPixmap.fromImage(image)
                
                # Scale the pixmap to fit the fixed container while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(
                    GuiConfig.IMAGE_PREVIEW_WIDTH,
                    GuiConfig.IMAGE_PREVIEW_HEIGHT, 
                    Qt.AspectRatioMode.KeepAspectRatio, 
                    Qt.TransformationMode.SmoothTransformation
                )
                
                self.image_preview.setPixmap(scaled_pixmap)
                self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
            else:
                self.image_preview.setText("Error loading image")
        except Exception as e:
            self.image_preview.setText(f"Error: {str(e)}")
        
        file_basename = os.path.basename(filename)
        
        # Get file_path from current image history to check manual edits
        file_path = None
        if self.image_history:
            if self.current_position == -1:
                idx = len(self.image_history) - 1
            else:
                idx = self.current_position
            if idx >= 0 and idx < len(self.image_history):
                _, _, _, _, file_path, _, _ = self.image_history[idx]
        
        # Check if manually edited to show "Pending (Modified)" status
        is_modified = False
        if file_path and file_path in self.manual_edits:
            is_modified = (
                self.manual_edits[file_path].get('caption_edited', False) or
                bool(self.manual_edits[file_path].get('keywords_manual', set()))
            )
        
        # Update filename label with save status (right-aligned)
        if save_status == "pending" and is_modified:
            status_text = "Pending (Modified)"
        else:
            status_text = save_status.capitalize()
        
        status_color = {
            'pending': '#ff8c00',  # Orange
            'saved': '#4caf50',     # Green
            'ignored': '#808080',   # Gray
            'generating': '#2196F3'  # Blue
        }.get(save_status.lower(), '#808080')
        
        # Use HTML table for proper alignment (QLabel supports basic HTML)
        filename_text = f"Filename: {file_basename}"
        status_html = f'<span style="color: {status_color}; font-weight: bold;">[{status_text}]</span>'
        # Use a table to achieve right alignment
        html_content = f'<table width="100%"><tr><td>{filename_text}</td><td align="right">{status_html}</td></tr></table>'
        self.filename_label.setText(html_content)
        
        # Set flag to prevent signal handler from firing during programmatic update
        self._updating_caption = True
        self.caption_edit.setPlainText(caption or "")
        # Restore normal style (in case it was changed during regeneration)
        self.caption_edit.setStyleSheet("padding: 4px; font-weight: normal; border: 1px solid palette(mid);")
        self._updating_caption = False
        
        # Update caption label indicator based on manual edits
        self.update_caption_edit_indicator()
        
        # Get manual keywords for this file (if any)
        manual_keywords_set = set()
        if file_path and file_path in self.manual_edits:
            manual_keywords_lower = self.manual_edits[file_path].get('keywords_manual', set())
            # Convert back to original case by matching with current keywords
            if keywords:
                for kw in keywords:
                    if kw.lower() in manual_keywords_lower:
                        manual_keywords_set.add(kw)
        
        # Update KeywordWidget with manual keywords tracking
        self.keywords_widget.manual_keywords = manual_keywords_set.copy()
        self.keywords_widget.set_keywords(keywords or [], manual_keywords=manual_keywords_set)
        self.update_navigation_buttons()
        self.update_action_buttons(save_status)

    def on_caption_edited(self):
        """Handle manual caption edits"""
        # Ignore if this is a programmatic update
        if self._updating_caption:
            return
        
        # Get current image data
        if not self.image_history:
            return
        
        # Determine current image index
        if self.current_position == -1:
            idx = len(self.image_history) - 1
        else:
            idx = self.current_position
        
        if idx < 0 or idx >= len(self.image_history):
            return
        
        # Get current image data
        base64_image, old_caption, keywords, filename, file_path, save_status, metadata = self.image_history[idx]
        
        # Get new caption from edit field
        new_caption = self.caption_edit.toPlainText()
        
        # Mark as manually edited
        if file_path not in self.manual_edits:
            self.manual_edits[file_path] = {}
        self.manual_edits[file_path]['caption_edited'] = True
        
        # Update image_history with new caption
        new_save_status = "pending" if save_status == "saved" else save_status
        self.image_history[idx] = (base64_image, new_caption, keywords, filename, file_path, new_save_status, metadata)
        
        # Update visual indicators and status
        self.update_caption_edit_indicator()
        self.update_action_buttons(new_save_status)
        
        # Update status display to show "Pending (Modified)" if applicable
        # Only update the status label, not the full display (to avoid recursion)
        if new_save_status == "pending":
            file_basename = os.path.basename(filename)
            status_text = "Pending (Modified)"
            status_color = '#ff8c00'  # Orange
            filename_text = f"Filename: {file_basename}"
            status_html = f'<span style="color: {status_color}; font-weight: bold;">[{status_text}]</span>'
            html_content = f'<table width="100%"><tr><td>{filename_text}</td><td align="right">{status_html}</td></tr></table>'
            self.filename_label.setText(html_content)
    
    def update_caption_edit_indicator(self):
        """Update visual indicators for manually edited caption"""
        if not self.image_history:
            # No images, clear indicator
            self.caption_label.setText("Caption")
            return
        
        # Determine current image index
        if self.current_position == -1:
            idx = len(self.image_history) - 1
        else:
            idx = self.current_position
        
        if idx < 0 or idx >= len(self.image_history):
            return
        
        # Get current image file path
        _, _, _, _, file_path, _, _ = self.image_history[idx]
        
        # Check if caption has been manually edited
        is_edited = (file_path in self.manual_edits and 
                    self.manual_edits[file_path].get('caption_edited', False))
        
        if is_edited:
            # Show asterisk and orange border
            self.caption_label.setText("Caption *")
            self.caption_edit.setStyleSheet("padding: 4px; font-weight: normal; border: 2px solid #ff8c00;")
        else:
            # Normal state
            self.caption_label.setText("Caption")
            self.caption_edit.setStyleSheet("padding: 4px; font-weight: normal; border: 1px solid palette(mid);")

    def on_keywords_changed(self, keywords):
        """Handle keyword changes from KeywordWidget
        
        Args:
            keywords: Updated list of keywords
        """
        # Get current image data
        if not self.image_history:
            return
        
        # Determine current image index
        if self.current_position == -1:
            idx = len(self.image_history) - 1
        else:
            idx = self.current_position
        
        if idx < 0 or idx >= len(self.image_history):
            return
        
        # Get current image data
        base64_image, caption, old_keywords, filename, file_path, save_status, metadata = self.image_history[idx]
        
        # Track manual keywords in manual_edits
        if file_path not in self.manual_edits:
            self.manual_edits[file_path] = {}
        
        # Update manual keywords set (case-insensitive)
        manual_keywords_set = {kw.lower() for kw in self.keywords_widget.manual_keywords}
        self.manual_edits[file_path]['keywords_manual'] = manual_keywords_set
        
        # Update image_history with new keywords
        new_save_status = "pending" if save_status == "saved" else save_status
        self.image_history[idx] = (base64_image, caption, keywords, filename, file_path, new_save_status, metadata)
        
        # Update status display if needed (only update status label, not full display to avoid recursion)
        if new_save_status == "pending":
            file_basename = os.path.basename(filename)
            status_text = "Pending (Modified)"
            status_color = '#ff8c00'  # Orange
            filename_text = f"Filename: {file_basename}"
            status_html = f'<span style="color: {status_color}; font-weight: bold;">[{status_text}]</span>'
            html_content = f'<table width="100%"><tr><td>{filename_text}</td><td align="right">{status_html}</td></tr></table>'
            self.filename_label.setText(html_content)
            self.update_action_buttons(new_save_status)
        else:
            self.update_action_buttons(new_save_status)

    def read_file_metadata_for_display(self, file_path, save_status):
        """Read actual metadata from file and return for display
        
        Args:
            file_path: Path to the image file
            save_status: Current save status ("saved", "pending", etc.)
            
        Returns:
            tuple: (caption, keywords, metadata_dict) or None if file doesn't exist or status is not "saved"
        """
        try:
            # Only read from file if status is "saved" (file has been written)
            if save_status != "saved":
                return None
            
            # Create a minimal config for RegenerationHelper
            config = llmii.Config()
            config.use_sidecar = self.settings_dialog.use_sidecar_checkbox.isChecked()
            
            helper = RegenerationHelper(config)
            try:
                file_metadata = helper.read_metadata(file_path)
                if file_metadata:
                    # Collect keywords and caption from all fields (matching main collection logic)
                    # This ensures we read metadata regardless of which field ExifTool returns it in
                    keyword_fields = [
                        "Keywords", "IPTC:Keywords", "Composite:keywords", "Subject",
                        "DC:Subject", "XMP:Subject", "XMP-dc:Subject", "MWG:Keywords"
                    ]
                    caption_fields = [
                        "Description", "XMP:Description", "ImageDescription", "DC:Description",
                        "EXIF:ImageDescription", "Composite:Description", "Caption", "IPTC:Caption",
                        "Composite:Caption", "IPTC:Caption-Abstract", "XMP-dc:Description",
                        "PNG:Description", "MWG:Description"
                    ]
                    
                    collected_keywords = []
                    caption = None
                    
                    for key, value in file_metadata.items():
                        # Collect from all keyword fields (matching main collection logic)
                        if key in keyword_fields:
                            if isinstance(value, list):
                                collected_keywords.extend(value)
                            elif isinstance(value, str):
                                collected_keywords.append(value)
                        # Collect from all caption fields (matching main collection logic)
                        elif key in caption_fields:
                            caption = value
                    
                    keywords = collected_keywords
                    
                    # DEBUG: Log keywords read from file
                    print(f"DEBUG READ: Collected keywords: {keywords}")
                    
                    # Ensure keywords is a list
                    if isinstance(keywords, str):
                        keywords = [keywords]
                    elif keywords is None:
                        keywords = []
                    
                    # Deduplicate keywords (case-insensitive) - matching main collection logic
                    if keywords:
                        seen = {}
                        deduplicated = []
                        for kw in keywords:
                            if kw:  # Skip empty strings
                                kw_lower = kw.lower().strip()
                                if kw_lower and kw_lower not in seen:
                                    seen[kw_lower] = kw
                                    deduplicated.append(kw)
                        keywords = deduplicated
                    
                    # DEBUG: Log final keywords after deduplication
                    print(f"DEBUG READ: Final keywords (after deduplication): {keywords}")
                    
                    return (caption or "", keywords, file_metadata)
            finally:
                helper.cleanup()
        except Exception as e:
            print(f"Error reading file metadata: {e}")
            return None
    
    def _update_navigation_with_file_metadata(self, idx):
        """Helper to update navigation with file metadata if saved
        
        Args:
            idx: Index in image_history to update and display
        """
        if idx < 0 or idx >= len(self.image_history):
            return
        
        base64_image, caption, keywords, filename, file_path, save_status, metadata = self.image_history[idx]
        
        # Read file metadata if saved, merge with history
        file_data = self.read_file_metadata_for_display(file_path, save_status)
        if file_data:
            file_caption, file_keywords, file_metadata = file_data
            # Use file data (fresh from disk)
            caption = file_caption
            keywords = file_keywords
            # Standardize metadata dict to use MWG fields (not raw ExifTool fields)
            # This ensures generate_metadata and prepare_metadata_for_save work correctly
            file_metadata["MWG:Keywords"] = keywords
            file_metadata["MWG:Description"] = caption
            metadata = file_metadata
            # Update history with fresh file data (standardized)
            self.image_history[idx] = (base64_image, caption, keywords, filename, file_path, save_status, metadata)
        
        self.display_image(base64_image, caption, keywords, filename, save_status)
        self.update_action_buttons(save_status)

    def navigate_first(self):
        if self.image_history:
            self.current_position = 0
            self._update_navigation_with_file_metadata(0)

    def navigate_prev(self):
        if not self.image_history:
            return
            
        if self.current_position == -1:
            # If at the most recent, go to the second most recent
            if len(self.image_history) > 1:
                self.current_position = len(self.image_history) - 2
                self._update_navigation_with_file_metadata(self.current_position)
        elif self.current_position > 0:
            self.current_position -= 1
            self._update_navigation_with_file_metadata(self.current_position)

    def navigate_next(self):
        if not self.image_history:
            return
            
        if self.current_position != -1 and self.current_position < len(self.image_history) - 1:
            self.current_position += 1
            
            # If we've reached the end, set to -1 to indicate "most recent"
            if self.current_position == len(self.image_history) - 1:
                self.current_position = -1
                
            idx = len(self.image_history) - 1 if self.current_position == -1 else self.current_position
            self._update_navigation_with_file_metadata(idx)

    def navigate_last(self):
        if self.image_history:
            self.current_position = -1
            self._update_navigation_with_file_metadata(len(self.image_history) - 1)

    def update_action_buttons(self, save_status="pending"):
        """Update action button states based on save_status
        
        Args:
            save_status: One of "pending", "saved", "ignored", "generating", or "" (empty for no images)
        """
        # Special case: "generating" status - disable all buttons during regeneration
        if save_status == "generating":
            self.save_button.setEnabled(False)
            self.regenerate_button.setEnabled(False)
            self.ignore_button.setEnabled(False)
            self.clear_button.setEnabled(False)
            # Force visual update
            self.save_button.update()
            self.regenerate_button.update()
            self.ignore_button.update()
            self.clear_button.update()
            QApplication.processEvents()
            return
        
        # If empty status (no images), disable all buttons
        if not save_status:
            self.save_button.setEnabled(False)
            self.regenerate_button.setEnabled(False)
            self.ignore_button.setEnabled(False)
            self.clear_button.setEnabled(False)
            # Force visual update
            self.save_button.update()
            self.regenerate_button.update()
            self.ignore_button.update()
            self.clear_button.update()
            QApplication.processEvents()
            return
        
        # Check if auto-save is enabled
        auto_save_enabled = self.auto_save_button.isChecked()
        
        # Save: only enabled when status is "pending" AND auto-save is disabled
        self.save_button.setEnabled(save_status == "pending" and not auto_save_enabled)
        
        # Regenerate: enabled when status is "pending" or "saved"
        self.regenerate_button.setEnabled(save_status in ["pending", "saved"])
        
        # Ignore: only enabled when status is "pending"
        self.ignore_button.setEnabled(save_status == "pending")
        
        # Clear: enabled when any image is displayed (not when no image selected)
        self.clear_button.setEnabled(save_status != "" and save_status is not None)
        
        # Force visual update
        self.save_button.update()
        self.regenerate_button.update()
        self.ignore_button.update()
        self.clear_button.update()
        QApplication.processEvents()
    
    def save_current_image(self):
        """Save the current image's metadata to file"""
        if not self.image_history or self.current_position < 0:
            # If at most recent, use the last item
            if self.current_position == -1 and self.image_history:
                idx = len(self.image_history) - 1
            else:
                self.update_output("Error: No image selected to save.")
                return
        else:
            idx = self.current_position
        
        # Get the current image data from history
        base64_image, old_caption, old_keywords, filename, file_path, save_status, metadata = self.image_history[idx]
        
        # Only save if status is "pending"
        if save_status != "pending":
            self.update_output(f"Image {os.path.basename(filename)} is already saved or ignored.")
            return
        
        # Read current values from UI widgets (source of truth for manual edits)
        current_caption = self.caption_edit.toPlainText()
        current_keywords = self.keywords_widget.keywords.copy() if self.keywords_widget.keywords else []
        
        # DEBUG: Log keywords read from UI
        print(f"DEBUG SAVE: Reading from UI - keywords: {current_keywords}")
        print(f"DEBUG SAVE: Metadata before prepare - MWG:Keywords: {metadata.get('MWG:Keywords', 'NOT FOUND')}")
        
        # Ensure keywords is a list (not None)
        if current_keywords is None:
            current_keywords = []
        
        # Update image_history with current UI values (keep in sync)
        self.image_history[idx] = (base64_image, current_caption, current_keywords, filename, file_path, save_status, metadata)
        
        # Create minimal config for helper (only needed for initialization)
        config = llmii.Config()
        config.use_sidecar = self.settings_dialog.use_sidecar_checkbox.isChecked()
        config.no_backup = self.settings_dialog.no_backup_checkbox.isChecked()
        config.dry_run = self.settings_dialog.dry_run_checkbox.isChecked()
        
        # Create helper for writing metadata
        helper = RegenerationHelper(config)
        
        try:
            # Get config settings from settings dialog
            use_sidecar = config.use_sidecar
            no_backup = config.no_backup
            dry_run = config.dry_run
            
            # Prepare metadata for saving (ensures status="success", keywords is list, etc.)
            prepared_metadata = helper.prepare_metadata_for_save(metadata)
            
            # Update prepared_metadata with current UI values (manual edits)
            prepared_metadata["MWG:Description"] = current_caption
            prepared_metadata["MWG:Keywords"] = current_keywords
            
            # DEBUG: Log final keywords to write
            print(f"DEBUG SAVE: Final keywords to write: {prepared_metadata['MWG:Keywords']}")
            
            # Ensure SourceFile is set correctly
            prepared_metadata["SourceFile"] = file_path
            
            if dry_run:
                self.update_output(f"Dry run: Would save metadata to {os.path.basename(filename)}")
                # Update status to "saved" even in dry run for UI consistency
                # Use prepared metadata so status is "success"
                self.image_history[idx] = (base64_image, current_caption, current_keywords, filename, file_path, "saved", prepared_metadata)
                self.display_image(base64_image, current_caption, current_keywords, filename, "saved")
                self.update_action_buttons("saved")
                return
            
            # Write metadata using helper
            success = helper.write_metadata(
                file_path, 
                prepared_metadata, 
                use_sidecar=use_sidecar, 
                no_backup=no_backup, 
                dry_run=dry_run
            )
            
            if success:
                # Update status in history with prepared metadata (using current UI values)
                self.image_history[idx] = (base64_image, current_caption, current_keywords, filename, file_path, "saved", prepared_metadata)
                
                # Clear manual edit flags after successful save
                if file_path in self.manual_edits:
                    self.manual_edits[file_path]['caption_edited'] = False
                    self.manual_edits[file_path]['keywords_manual'] = set()
                
                # Refresh display
                self.display_image(base64_image, current_caption, current_keywords, filename, "saved")
                self.update_action_buttons("saved")
                
                # Log success
                self.update_output(f"Successfully saved metadata to {os.path.basename(filename)}")
            else:
                # Write failed
                error_msg = f"Failed to save metadata to {os.path.basename(filename)}"
                self.update_output(error_msg)
                print(error_msg)
            
        except Exception as e:
            error_msg = f"Error saving metadata to {os.path.basename(filename)}: {str(e)}"
            self.update_output(error_msg)
            print(error_msg)
        finally:
            # Clean up helper
            helper.cleanup()
    
    def ignore_current_image(self):
        """Mark the current image as ignored"""
        if not self.image_history or self.current_position < 0:
            # If at most recent, use the last item
            if self.current_position == -1 and self.image_history:
                idx = len(self.image_history) - 1
            else:
                self.update_output("Error: No image selected to ignore.")
                return
        else:
            idx = self.current_position
        
        # Get the current image data from history
        base64_image, caption, keywords, filename, file_path, save_status, metadata = self.image_history[idx]
        
        # Only ignore if status is "pending"
        if save_status != "pending":
            self.update_output(f"Image {os.path.basename(filename)} cannot be ignored (already saved or ignored).")
            return
        
        # Update status in history
        self.image_history[idx] = (base64_image, caption, keywords, filename, file_path, "ignored", metadata)
        
        # Refresh display
        self.display_image(base64_image, caption, keywords, filename, "ignored")
        
        # Log action
        self.update_output(f"Ignored {os.path.basename(filename)}")
    
    def clear_current_image_metadata(self):
        """Clear all Description and Keywords from the current image"""
        if not self.image_history:
            self.update_output("Error: No image selected to clear.")
            return
        
        # Get current image index
        if self.current_position < 0:
            # If at most recent, use the last item
            if self.current_position == -1 and self.image_history:
                idx = len(self.image_history) - 1
            else:
                self.update_output("Error: No image selected to clear.")
                return
        else:
            idx = self.current_position
        
        # Get the current image data from history
        base64_image, caption, keywords, filename, file_path, save_status, metadata = self.image_history[idx]
        
        # Show confirmation dialog
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Clear Metadata")
        msg.setText("Continuing will erase the Description and all Keywords (tags).")
        msg.setInformativeText("This cannot be undone. Are you sure you want to continue?")
        
        # Add buttons: Cancel (left) and Continue (right)
        cancel_button = msg.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
        continue_button = msg.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)
        
        # Set Cancel as default (highlighted)
        msg.setDefaultButton(cancel_button)
        
        # Show dialog and get result
        msg.exec()
        
        if msg.clickedButton() == cancel_button:
            # User cancelled
            return
        
        # User confirmed - proceed with clearing metadata
        try:
            # Create minimal config for helper
            config = llmii.Config()
            config.use_sidecar = self.settings_dialog.use_sidecar_checkbox.isChecked()
            config.no_backup = self.settings_dialog.no_backup_checkbox.isChecked()
            config.dry_run = self.settings_dialog.dry_run_checkbox.isChecked()
            
            helper = RegenerationHelper(config)
            
            # Adjust file path for sidecar if needed
            write_path = file_path
            if config.use_sidecar:
                write_path = file_path + ".xmp"
            
            if config.dry_run:
                self.update_output(f"Dry run: Would clear metadata from {os.path.basename(filename)}")
                # Update UI even in dry run
                empty_caption = ""
                empty_keywords = []
                updated_metadata = metadata.copy()
                updated_metadata["MWG:Description"] = ""
                updated_metadata["MWG:Keywords"] = []
                self.image_history[idx] = (base64_image, empty_caption, empty_keywords, filename, file_path, "saved", updated_metadata)
                self.display_image(base64_image, empty_caption, empty_keywords, filename, "saved")
                self.update_action_buttons("saved")
                helper.cleanup()
                return
            
            # Use ExifTool's execute method with deletion syntax (confirmed working)
            # Command: exiftool -MWG:Keywords= -MWG:Description= -overwrite_original -P file.jpg
            params = ["-MWG:Keywords=", "-MWG:Description="]
            
            if config.no_backup or config.use_sidecar:
                params.append("-overwrite_original")
            
            params.append("-P")
            params.append(write_path)
            
            # Execute the deletion command
            helper.et.execute(*params)
            
            # Update image history with cleared values
            empty_caption = ""
            empty_keywords = []
            updated_metadata = metadata.copy()
            updated_metadata["MWG:Description"] = ""
            updated_metadata["MWG:Keywords"] = []
            updated_metadata["XMP:Status"] = "success"  # Mark as successfully cleared
            
            self.image_history[idx] = (base64_image, empty_caption, empty_keywords, filename, file_path, "saved", updated_metadata)
            
            # Refresh display
            self.display_image(base64_image, empty_caption, empty_keywords, filename, "saved")
            self.update_action_buttons("saved")
            
            # Clear manual edits tracking
            if file_path in self.manual_edits:
                self.manual_edits[file_path] = {'caption_edited': False, 'keywords_manual': set()}
            
            self.update_output(f"Successfully cleared metadata from {os.path.basename(filename)}")
            
            helper.cleanup()
            
        except Exception as e:
            self.update_output(f"Error clearing metadata from {os.path.basename(filename)}: {str(e)}")
            print(f"Error clearing metadata: {e}")
    
    def regenerate_current_image(self):
        """Regenerate metadata for the current image"""
        if not self.image_history or self.current_position < 0:
            # If at most recent, use the last item
            if self.current_position == -1 and self.image_history:
                idx = len(self.image_history) - 1
            else:
                self.update_output("Error: No image selected to regenerate.")
                return
        else:
            idx = self.current_position
        
        # Get the current image data from history
        base64_image, old_caption, keywords, filename, file_path, save_status, metadata = self.image_history[idx]
        
        # Read current caption from UI (source of truth for manual edits)
        current_caption = self.caption_edit.toPlainText()
        
        # Only regenerate if status is "pending" or "saved"
        if save_status not in ["pending", "saved"]:
            self.update_output(f"Image {os.path.basename(filename)} cannot be regenerated (status: {save_status}).")
            return
        
        # Disable buttons during regeneration
        self.save_button.setEnabled(False)
        self.regenerate_button.setEnabled(False)
        self.ignore_button.setEnabled(False)
        self.clear_button.setEnabled(False)
        QApplication.processEvents()
        
        # Check generation mode to determine if we're regenerating keywords
        generation_mode = 'description_only' if self.settings_dialog.description_only_radio.isChecked() else ('keywords_only' if self.settings_dialog.keywords_only_radio.isChecked() else 'both')
        
        # Check if caption has been manually edited and will be overwritten
        caption_will_be_regenerated = generation_mode in ['description_only', 'both']
        caption_is_edited = (file_path in self.manual_edits and 
                           self.manual_edits[file_path].get('caption_edited', False))
        
        if caption_will_be_regenerated and caption_is_edited:
            # Show confirmation dialog
            reply = QMessageBox.warning(
                self,
                "Overwrite Manual Edits?",
                "This will overwrite and replace the content in the description including any manual edits you've made. Any manually added keywords will be safe. Are you sure you want to continue?",
                QMessageBox.StandardButton.Cancel | QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Cancel
            )
            
            if reply != QMessageBox.StandardButton.Ok:
                # User cancelled, re-enable buttons and return
                self.update_action_buttons(save_status)
                return
        
        # Show "Generating" status
        file_basename = os.path.basename(filename)
        status_text = "Generating"
        status_color = '#2196F3'  # Blue
        filename_text = f"Filename: {file_basename}"
        status_html = f'<span style="color: {status_color}; font-weight: bold;">[{status_text}]</span>'
        html_content = f'<table width="100%"><tr><td>{filename_text}</td><td align="right">{status_html}</td></tr></table>'
        self.filename_label.setText(html_content)
        
        if generation_mode == "keywords_only":
            # Only regenerating keywords - preserve description, show generating message for keywords
            self._updating_caption = True
            self.caption_edit.setPlainText(current_caption or "")  # Preserve current description from UI
            self._updating_caption = False
            self.keywords_widget.show_generating_message()  # Show "Regenerating Keywords..." message
        elif generation_mode == "description_only":
            # Only regenerating description - preserve keywords, show generating message for description
            self._updating_caption = True
            self.caption_edit.setPlainText("Regenerating Description...")  # Show generating message
            self.caption_edit.setStyleSheet("padding: 4px; font-weight: normal; border: 1px solid palette(mid); color: #2196F3; font-style: italic;")
            self._updating_caption = False
            # Don't update keywords - leave them as they are (no clear, no set_keywords call)
        else:  # generation_mode == "both"
            # Regenerating both - show generating messages for both
            self._updating_caption = True
            self.caption_edit.setPlainText("Regenerating Description...")  # Show generating message
            self.caption_edit.setStyleSheet("padding: 4px; font-weight: normal; border: 1px solid palette(mid); color: #2196F3; font-style: italic;")
            self._updating_caption = False
            self.keywords_widget.show_generating_message()  # Show "Regenerating Keywords..." message
        
        self.update_action_buttons("generating")
        self.update_output(f"Regenerating metadata for {os.path.basename(filename)}...")
        QApplication.processEvents()
        
        # Check if a regeneration thread is already running
        if hasattr(self, 'regenerate_thread') and self.regenerate_thread and self.regenerate_thread.isRunning():
            self.update_output("Regeneration already in progress. Please wait...")
            return
        
        # Create config from current settings
        config = llmii.Config()
        config.api_url = self.settings_dialog.api_url_input.text()
        config.api_password = self.settings_dialog.api_password_input.text()
        config.system_instruction = self.settings_dialog.system_instruction_input.text()
        config.generation_mode = generation_mode
        config.instruction = self.settings_dialog.general_instruction_input.toPlainText()
        config.caption_instruction = self.settings_dialog.description_instruction_input.toPlainText()
        config.keyword_instruction = self.settings_dialog.keyword_instruction_input.toPlainText()
        # Removed config.update_keywords - feature removed
        config.update_caption = self.settings_dialog.update_caption_checkbox.isChecked()
        config.detailed_caption = self.settings_dialog.separate_query_radio.isChecked() if config.generation_mode == "both" else False
        config.short_caption = not config.detailed_caption if config.generation_mode == "both" else True
        config.no_caption = False
        config.gen_count = self.settings_dialog.gen_count.value()
        config.res_limit = self.settings_dialog.res_limit.value()
        config.temperature = self.settings_dialog.temperature_spinbox.value()
        config.top_p = self.settings_dialog.top_p_spinbox.value()
        config.top_k = self.settings_dialog.top_k_spinbox.value()
        config.min_p = self.settings_dialog.min_p_spinbox.value()
        config.rep_pen = self.settings_dialog.rep_pen_spinbox.value()
        config.use_sidecar = self.settings_dialog.use_sidecar_checkbox.isChecked()
        config.normalize_keywords = True
        config.depluralize_keywords = self.settings_dialog.depluralize_checkbox.isChecked()
        config.limit_word_count = self.settings_dialog.word_limit_checkbox.isChecked()
        config.max_words_per_keyword = self.settings_dialog.word_limit_spinbox.value()
        config.split_and_entries = self.settings_dialog.split_and_checkbox.isChecked()
        config.ban_prompt_words = self.settings_dialog.ban_prompt_words_checkbox.isChecked()
        
        # Store the index for updating history when regeneration completes
        self.regenerate_idx = idx
        self.regenerate_original_data = (base64_image, current_caption, keywords, filename, save_status)
        
        # Get manual keywords for this file (if any)
        manual_keywords = set()
        if file_path and file_path in self.manual_edits:
            manual_keywords_lower = self.manual_edits[file_path].get('keywords_manual', set())
            # Convert back to original case by matching with current keywords
            if keywords:
                for kw in keywords:
                    if kw.lower() in manual_keywords_lower:
                        manual_keywords.add(kw)
        
        # Create and start regeneration thread
        # Use current_caption from UI instead of caption from history
        self.regenerate_thread = RegenerateThread(
            config, base64_image, current_caption, keywords, filename, file_path, save_status, metadata, manual_keywords
        )
        self.regenerate_thread.regeneration_complete.connect(self.on_regeneration_complete)
        self.regenerate_thread.regeneration_error.connect(self.on_regeneration_error)
        self.regenerate_thread.finished.connect(self.on_regeneration_finished)
        self.regenerate_thread.start()
    
    def on_regeneration_complete(self, base64_image, new_caption, new_keywords, filename, file_path, new_save_status, new_metadata):
        """Handle successful regeneration"""
        # Update history entry
        idx = self.regenerate_idx
        self.image_history[idx] = (base64_image, new_caption, new_keywords, filename, file_path, new_save_status, new_metadata)
        
        # Determine generation mode to check if description was regenerated
        generation_mode = 'description_only' if self.settings_dialog.description_only_radio.isChecked() else ('keywords_only' if self.settings_dialog.keywords_only_radio.isChecked() else 'both')
        
        # Clear manual edit flag if description was regenerated
        if generation_mode in ['description_only', 'both']:
            if file_path in self.manual_edits:
                self.manual_edits[file_path]['caption_edited'] = False
        
        # Preserve manual keywords tracking after regeneration
        # Manual keywords are preserved in the merged keywords list
        if file_path in self.manual_edits and self.manual_edits[file_path].get('keywords_manual'):
            # Update manual keywords set to match what's actually in the new keywords
            manual_keywords_lower = self.manual_edits[file_path].get('keywords_manual', set())
            # Keep only keywords that are still present in new_keywords
            preserved_manual = {kw.lower() for kw in new_keywords if kw.lower() in manual_keywords_lower}
            self.manual_edits[file_path]['keywords_manual'] = preserved_manual
        
        # Check if auto-save is enabled - if so, automatically save
        if self.auto_save_button.isChecked():
            # Auto-save the regenerated metadata
            try:
                # Create minimal config for helper
                config = llmii.Config()
                config.use_sidecar = self.settings_dialog.use_sidecar_checkbox.isChecked()
                config.no_backup = self.settings_dialog.no_backup_checkbox.isChecked()
                config.dry_run = self.settings_dialog.dry_run_checkbox.isChecked()
                
                helper = RegenerationHelper(config)
                try:
                    # Prepare metadata for saving
                    prepared_metadata = helper.prepare_metadata_for_save(new_metadata)
                    prepared_metadata["SourceFile"] = file_path
                    
                    if not config.dry_run:
                        # Write metadata
                        success = helper.write_metadata(
                            file_path,
                            prepared_metadata,
                            use_sidecar=config.use_sidecar,
                            no_backup=config.no_backup,
                            dry_run=config.dry_run
                        )
                        
                        if success:
                            # Update status to "saved"
                            self.image_history[idx] = (base64_image, new_caption, new_keywords, filename, file_path, "saved", prepared_metadata)
                            new_save_status = "saved"
                            self.update_output(f"Auto-saved regenerated metadata to {os.path.basename(filename)}")
                        else:
                            self.update_output(f"Warning: Failed to auto-save regenerated metadata to {os.path.basename(filename)}")
                    else:
                        # Dry run - just update status
                        self.image_history[idx] = (base64_image, new_caption, new_keywords, filename, file_path, "saved", prepared_metadata)
                        new_save_status = "saved"
                        self.update_output(f"Dry run: Would auto-save regenerated metadata to {os.path.basename(filename)}")
                finally:
                    helper.cleanup()
            except Exception as e:
                error_msg = f"Error auto-saving regenerated metadata: {str(e)}"
                self.update_output(error_msg)
                print(error_msg)
        
        # Refresh display
        self.display_image(base64_image, new_caption, new_keywords, filename, new_save_status)
        
        # Log success
        if not self.auto_save_button.isChecked():
            self.update_output(f"Successfully regenerated metadata for {os.path.basename(filename)}")
    
    def on_regeneration_error(self, error_msg):
        """Handle regeneration error"""
        self.update_output(error_msg)
        print(error_msg)
        
        # Restore original display on error
        if hasattr(self, 'regenerate_original_data'):
            base64_image, caption, keywords, filename, save_status = self.regenerate_original_data
            self.display_image(base64_image, caption, keywords, filename, save_status)
            # Restore button states based on original status
            self.update_action_buttons(save_status)
    
    def on_regeneration_finished(self):
        """Handle thread completion - re-enable buttons"""
        # Check if user is still viewing the regenerated image
        if hasattr(self, 'regenerate_idx') and self.regenerate_idx < len(self.image_history):
            # Determine the current position (handle -1 for "most recent")
            current_idx = self.current_position if self.current_position >= 0 else (len(self.image_history) - 1 if self.image_history else -1)
            
            # Only update buttons if user is still viewing the regenerated image
            if current_idx == self.regenerate_idx:
                _, _, _, _, _, save_status, _ = self.image_history[self.regenerate_idx]
                self.update_action_buttons(save_status)
            # If user navigated away, buttons will be updated when they navigate back
        else:
            # Fallback: update buttons based on currently viewed image
            if self.image_history and self.current_position >= 0:
                _, _, _, _, _, save_status, _ = self.image_history[self.current_position]
                self.update_action_buttons(save_status)
            elif self.image_history and self.current_position == -1:
                _, _, _, _, _, save_status, _ = self.image_history[-1]
                self.update_action_buttons(save_status)
            else:
                self.update_action_buttons("")
        
        # Clean up thread reference and index
        if hasattr(self, 'regenerate_thread'):
            self.regenerate_thread = None
        if hasattr(self, 'regenerate_idx'):
            delattr(self, 'regenerate_idx')
        if hasattr(self, 'regenerate_original_data'):
            delattr(self, 'regenerate_original_data')

    def update_navigation_buttons(self):
        history_size = len(self.image_history)
        
        if history_size == 0:
            # No images yet
            self.first_button.setEnabled(False)
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)
            self.last_button.setEnabled(False)
            self.position_label.setText("No images processed")
            # Disable action buttons when no images
            self.update_action_buttons("")  # Empty status disables all buttons
            return
        
        # Determine position for display
        if self.current_position == -1:
            # At the most recent image
            position = history_size
            self.next_button.setEnabled(False)
            self.last_button.setEnabled(False)
        else:
            position = self.current_position + 1  # 1-based for display
            self.next_button.setEnabled(self.current_position < history_size - 1)
            self.last_button.setEnabled(self.current_position < history_size - 1)
        
        # Update position text
        self.position_label.setText(f"Image {position} of {history_size}")
        
        # Enable/disable first/prev buttons
        self.first_button.setEnabled(history_size > 1 and (self.current_position > 0 or self.current_position == -1))
        self.prev_button.setEnabled(history_size > 1 and (self.current_position > 0 or self.current_position == -1))
          
    def run_indexer(self):
        
        if not self.api_is_ready:
            QMessageBox.warning(self, "API Not Ready", 
                              "Please wait for the API to be available before running the indexer.")
            return
        
        self.image_history = []
        self.current_position = -1
        self.update_navigation_buttons()
        
        config = llmii.Config()
        
        self.image_preview.setText("No image processed yet")
        self.filename_label.setText("Filename: ")
        self.caption_edit.setPlainText("")
        self.caption_edit.setStyleSheet("padding: 4px; font-weight: normal; border: 1px solid palette(mid);")
        self.keywords_widget.clear()
        
        # Get directory from main window
        config.directory = self.dir_input.text()
        
        # Load settings from settings dialog
        config.api_url = self.settings_dialog.api_url_input.text()
        config.api_password = self.settings_dialog.api_password_input.text()
        config.system_instruction = self.settings_dialog.system_instruction_input.text()
        config.no_crawl = self.settings_dialog.no_crawl_checkbox.isChecked()
        config.reprocess_failed = self.settings_dialog.reprocess_failed_checkbox.isChecked()
        config.reprocess_all = self.settings_dialog.reprocess_all_checkbox.isChecked()
        config.reprocess_orphans = self.settings_dialog.reprocess_orphans_checkbox.isChecked()
        config.no_backup = self.settings_dialog.no_backup_checkbox.isChecked()
        config.dry_run = self.settings_dialog.dry_run_checkbox.isChecked()
        config.skip_verify = self.settings_dialog.skip_verify_checkbox.isChecked()
        config.quick_fail = self.settings_dialog.quick_fail_checkbox.isChecked()
        config.use_sidecar = self.settings_dialog.use_sidecar_checkbox.isChecked()
        config.normalize_keywords = True
        config.depluralize_keywords = self.settings_dialog.depluralize_checkbox.isChecked()
        config.limit_word_count = self.settings_dialog.word_limit_checkbox.isChecked()
        config.max_words_per_keyword = self.settings_dialog.word_limit_spinbox.value()
        config.split_and_entries = self.settings_dialog.split_and_checkbox.isChecked()
        config.ban_prompt_words = self.settings_dialog.ban_prompt_words_checkbox.isChecked()
        config.no_digits_start = self.settings_dialog.no_digits_start_checkbox.isChecked()
        config.min_word_length = self.settings_dialog.min_word_length_checkbox.isChecked()
        config.latin_only = self.settings_dialog.latin_only_checkbox.isChecked()
        
        # Load caption instruction
        config.caption_instruction = self.settings_dialog.description_instruction_input.toPlainText()
        
        # Load generation mode setting
        if self.settings_dialog.description_only_radio.isChecked():
            config.generation_mode = "description_only"
            config.detailed_caption = False
            config.short_caption = False
            config.no_caption = False
        elif self.settings_dialog.keywords_only_radio.isChecked():
            config.generation_mode = "keywords_only"
            config.detailed_caption = False
            config.short_caption = False
            config.no_caption = True  # Don't generate caption in keywords_only mode
        else:
            config.generation_mode = "both"
            config.no_caption = False
            # Set detailed_caption based on both_query_method
            if self.settings_dialog.separate_query_radio.isChecked():
                config.detailed_caption = True
                config.short_caption = False
            else:
                config.detailed_caption = False
                config.short_caption = True
        
        # Load instruction settings
        config.instruction = self.settings_dialog.general_instruction_input.toPlainText()
        config.keyword_instruction = self.settings_dialog.keyword_instruction_input.toPlainText()
        
        # Removed config.update_keywords - feature removed
        config.update_caption = self.settings_dialog.update_caption_checkbox.isChecked()
        # Use auto-save button state (which is synced with settings dialog)
        config.auto_save = self.auto_save_button.isChecked()
        config.gen_count = self.settings_dialog.gen_count.value()
        config.res_limit = self.settings_dialog.res_limit.value()

        # Load sampler settings
        config.temperature = self.settings_dialog.temperature_spinbox.value()
        config.top_p = self.settings_dialog.top_p_spinbox.value()
        config.top_k = self.settings_dialog.top_k_spinbox.value()
        config.min_p = self.settings_dialog.min_p_spinbox.value()
        config.rep_pen = self.settings_dialog.rep_pen_spinbox.value()

        self.indexer_thread = IndexerThread(config)
        self.indexer_thread.output_received.connect(self.update_output)
        self.indexer_thread.image_processed.connect(self.update_image_preview)
        self.indexer_thread.finished.connect(self.indexer_finished)
        self.pause_handler.pause_signal.connect(self.set_paused)
        self.pause_handler.stop_signal.connect(self.set_stopped)
        self.indexer_thread.start()

        self.output_area.clear()
        self.output_area.append("Running Image Indexer...")
        self.run_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.stop_button.setEnabled(True)

    def set_paused(self, paused):
        if self.indexer_thread:
            self.indexer_thread.paused = paused

    def set_stopped(self):
        if self.indexer_thread:
            self.indexer_thread.stopped = True

    def toggle_pause(self):
        if self.pause_button.text() == "Pause":
            self.pause_handler.pause_signal.emit(True)
            self.pause_button.setText("Resume")
            self.update_output("Indexer paused.")
        else:
            self.pause_handler.pause_signal.emit(False)
            self.pause_button.setText("Pause")
            self.update_output("Indexer resumed.")

    def stop_indexer(self):
        self.pause_handler.stop_signal.emit()
        self.update_output("Stopping indexer...")
        self.run_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)

    def indexer_finished(self):
        self.update_output("\nImage Indexer finished.")
        self.run_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.pause_button.setText("Pause")

    def update_output(self, text):
        self.output_area.append(text)
        self.output_area.verticalScrollBar().setValue(self.output_area.verticalScrollBar().maximum())
        QApplication.processEvents()

    # Override resizeEvent to disable it since we're using fixed sizes
    def resizeEvent(self, event):
        """We override this but it shouldn't be called since window is fixed"""
        super().resizeEvent(event)
        
    def has_unsaved_changes(self):
        """Check if there are any unsaved changes in image_history"""
        if not hasattr(self, 'image_history') or not self.image_history:
            return False, 0
        
        unsaved_count = 0
        for entry in self.image_history:
            # Entry format: (base64_image, caption, keywords, filename, file_path, save_status, metadata)
            if len(entry) >= 6:
                save_status = entry[5]  # save_status is at index 5
                if save_status == "pending":
                    unsaved_count += 1
        
        return unsaved_count > 0, unsaved_count
        
    def closeEvent(self, event):
        # Check for unsaved changes
        has_unsaved, unsaved_count = self.has_unsaved_changes()
        
        if has_unsaved:
            # Show confirmation dialog
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Unsaved Changes")
            msg.setText(f"You have {unsaved_count} unsaved change{'s' if unsaved_count > 1 else ''}.")
            msg.setInformativeText("Are you sure you want to exit without saving?")
            
            # Add buttons: Cancel (left) and Exit without saving (right)
            cancel_button = msg.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
            exit_button = msg.addButton("Exit without saving", QMessageBox.ButtonRole.AcceptRole)
            
            # Set Cancel as default (highlighted)
            msg.setDefaultButton(cancel_button)
            
            # Show dialog and get result
            result = msg.exec()
            
            # If user clicked Cancel, ignore the close event
            if msg.clickedButton() == cancel_button:
                event.ignore()
                return
        
        # Check if threads are running (API calls in progress)
        indexer_running = hasattr(self, 'indexer_thread') and self.indexer_thread and self.indexer_thread.isRunning()
        regenerate_running = hasattr(self, 'regenerate_thread') and self.regenerate_thread and self.regenerate_thread.isRunning()
        
        if indexer_running or regenerate_running:
            # Show waiting dialog (non-dismissible modal, frameless)
            waiting_dialog = QDialog(self)
            waiting_dialog.setModal(True)
            # Frameless window - no title bar or close button
            waiting_dialog.setWindowFlags(
                Qt.WindowType.Dialog | 
                Qt.WindowType.FramelessWindowHint | 
                Qt.WindowType.WindowStaysOnTopHint
            )
            
            # Create layout with message and progress bar
            layout = QVBoxLayout(waiting_dialog)
            layout.setSpacing(15)
            layout.setContentsMargins(30, 30, 30, 30)
            
            # Add message label
            message_label = QLabel("The window will close once the current progress is complete.")
            message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            message_label.setWordWrap(True)
            layout.addWidget(message_label)
            
            # Add indeterminate progress bar (spinner)
            progress_bar = QProgressBar()
            progress_bar.setRange(0, 0)  # Indeterminate
            progress_bar.setMinimumWidth(300)
            layout.addWidget(progress_bar)
            
            # Override closeEvent to prevent dismissal
            def non_dismissible_close(event):
                event.ignore()  # Ignore close attempts
            waiting_dialog.closeEvent = non_dismissible_close
            waiting_dialog.reject = lambda: None  # Prevent reject (escape key)
            
            # Center the dialog on the main window
            waiting_dialog.adjustSize()
            main_window_geometry = self.geometry()
            dialog_x = main_window_geometry.x() + (main_window_geometry.width() - waiting_dialog.width()) // 2
            dialog_y = main_window_geometry.y() + (main_window_geometry.height() - waiting_dialog.height()) // 2
            waiting_dialog.move(dialog_x, dialog_y)
            
            waiting_dialog.show()
            QApplication.processEvents()  # Ensure dialog is visible
            
            # Signal threads to stop
            if indexer_running:
                self.indexer_thread.stopped = True
            if regenerate_running:
                # RegenerateThread doesn't have a stopped flag, so we'll just wait for it
                pass
            
            # Wait for threads to finish (with 150 second timeout to allow for API processing)
            # Process events periodically to keep dialog responsive
            timeout_ms = 150000  # 150 seconds
            elapsed = 0
            check_interval = 100  # Check every 100ms
            
            while elapsed < timeout_ms:
                # Check if threads are still running
                indexer_still_running = indexer_running and self.indexer_thread.isRunning()
                regenerate_still_running = regenerate_running and self.regenerate_thread.isRunning()
                
                if not indexer_still_running and not regenerate_still_running:
                    # Both threads finished
                    break
                
                # Wait a bit and process events to keep UI responsive
                QThread.msleep(check_interval)
                QApplication.processEvents()
                elapsed += check_interval
            
            # Close the waiting dialog
            waiting_dialog.close()
        
        # Clean up API check thread when closing the window
        if self.api_check_thread and self.api_check_thread.isRunning():
            self.api_check_thread.stop()
            self.api_check_thread.wait()
        
        event.accept()

def run_gui():
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    app.setStyle("Fusion")  # Modern cross-platform style
    
    # Apply global button stylesheet for consistent disabled state across all buttons
    # This ensures navigation buttons and all other buttons have consistent styling
    global_button_style = """
        QPushButton {
            background-color: palette(button);
            border: 1px solid palette(mid);
            border-radius: 3px;
            padding: 4px 12px;
            min-width: 60px;
        }
        QPushButton:hover {
            background-color: palette(light);
        }
        QPushButton:pressed {
            background-color: palette(dark);
        }
        QPushButton:disabled {
            background-color: #e0e0e0;
            color: #888888;
            border: 1px solid #c0c0c0;
        }
        QToolTip {
            max-width: 250px;
        }
    """
    app.setStyleSheet(global_button_style)

    
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    
    app.setPalette(palette)
    window = ImageIndexerGUI()
    window.show()
    sys.exit(app.exec())    
    
def main():
    run_gui()
    
if __name__ == "__main__":
    main()
