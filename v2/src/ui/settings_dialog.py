"""
Settings Dialog for Batch Image Metadata Tool
3-tab design: Content Options, Query Instructions, Advanced LLM Configuration
"""
import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, QLabel,
    QLineEdit, QCheckBox, QPushButton, QPlainTextEdit, QSpinBox,
    QDoubleSpinBox, QRadioButton, QButtonGroup, QGroupBox, QMessageBox,
    QScrollArea
)
from PyQt6.QtCore import Qt

from ..core.config import Config
from .theme import (
    SETTINGS_DIALOG_WIDTH, SETTINGS_DIALOG_HEIGHT,
    get_button_stylesheet, get_input_stylesheet, get_checkbox_stylesheet,
    get_radiobutton_stylesheet, get_groupbox_stylesheet, get_tab_stylesheet
)


class SettingsDialog(QDialog):
    """Settings dialog with 3 tabs: Content Options, Query Instructions, Advanced LLM Config"""
    
    def __init__(self, parent=None, config=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setFixedSize(SETTINGS_DIALOG_WIDTH, SETTINGS_DIALOG_HEIGHT)
        
        # Store config reference
        self.config = config or Config.load_from_file()
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(8)
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(get_tab_stylesheet())
        
        # Create tabs
        self.content_options_tab = self._create_content_options_tab()
        self.query_instructions_tab = self._create_query_instructions_tab()
        self.advanced_llm_tab = self._create_advanced_llm_tab()
        
        self.tabs.addTab(self.content_options_tab, "Content Options")
        self.tabs.addTab(self.query_instructions_tab, "Query Instructions")
        self.tabs.addTab(self.advanced_llm_tab, "Advanced LLM Configuration")
        
        main_layout.addWidget(self.tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.ok_button = QPushButton("OK")
        self.ok_button.setStyleSheet(get_button_stylesheet())
        self.ok_button.clicked.connect(self.accept_and_save)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setStyleSheet(get_button_stylesheet())
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(button_layout)
        
        # Load settings into UI
        self.load_settings()
    
    def _create_content_options_tab(self):
        """Create Content Options tab with subsections"""
        # Create content widget
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # Query Options subsection
        query_group = QGroupBox("Query Options")
        query_group.setStyleSheet(get_groupbox_stylesheet())
        query_layout = QVBoxLayout()
        query_layout.setSpacing(8)
        
        # Combined vs Separate Query (for Process both action)
        query_method_label = QLabel("Process (both) query method:")
        query_layout.addWidget(query_method_label)
        
        self.query_method_group = QButtonGroup()
        self.combined_query_radio = QRadioButton("Combined Query")
        self.separate_query_radio = QRadioButton("Separate Queries")
        self.query_method_group.addButton(self.combined_query_radio, 0)
        self.query_method_group.addButton(self.separate_query_radio, 1)
        self.separate_query_radio.setChecked(True)  # Default
        
        query_method_layout = QHBoxLayout()
        query_method_layout.addWidget(self.combined_query_radio)
        query_method_layout.addWidget(self.separate_query_radio)
        query_method_layout.addStretch()
        query_layout.addLayout(query_method_layout)
        
        # mark_ignore checkbox
        self.mark_ignore_checkbox = QCheckBox('Mark status as "Ignored" if image already has keyword(s) and a description.')
        self.mark_ignore_checkbox.setChecked(True)  # Default checked
        query_layout.addWidget(self.mark_ignore_checkbox)
        
        # no_crawl checkbox
        self.no_crawl_checkbox = QCheckBox("Don't go in subdirectories")
        query_layout.addWidget(self.no_crawl_checkbox)
        
        query_group.setLayout(query_layout)
        layout.addWidget(query_group)
        
        # File Options subsection
        file_group = QGroupBox("File Options")
        file_group.setStyleSheet(get_groupbox_stylesheet())
        file_layout = QVBoxLayout()
        file_layout.setSpacing(8)
        
        self.auto_save_checkbox = QCheckBox("Auto-save")
        file_layout.addWidget(self.auto_save_checkbox)
        
        self.no_backup_checkbox = QCheckBox("No backups")
        file_layout.addWidget(self.no_backup_checkbox)
        
        self.use_sidecar_checkbox = QCheckBox("Use metadata sidecar instead of writing to image")
        file_layout.addWidget(self.use_sidecar_checkbox)
        
        self.reprocess_failed_checkbox = QCheckBox("Reprocess failures")
        file_layout.addWidget(self.reprocess_failed_checkbox)
        
        self.reprocess_all_checkbox = QCheckBox("Reprocess everything")
        file_layout.addWidget(self.reprocess_all_checkbox)
        
        self.reprocess_orphans_checkbox = QCheckBox("Fix any orphans")
        file_layout.addWidget(self.reprocess_orphans_checkbox)
        
        self.dry_run_checkbox = QCheckBox("Pretend mode")
        file_layout.addWidget(self.dry_run_checkbox)
        
        self.skip_verify_checkbox = QCheckBox("No file validation")
        file_layout.addWidget(self.skip_verify_checkbox)
        
        self.quick_fail_checkbox = QCheckBox("No retries")
        file_layout.addWidget(self.quick_fail_checkbox)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Existing Metadata subsection
        metadata_group = QGroupBox("Existing Metadata")
        metadata_group.setStyleSheet(get_groupbox_stylesheet())
        metadata_layout = QVBoxLayout()
        metadata_layout.setSpacing(8)
        
        self.update_caption_checkbox = QCheckBox("Don't clear existing caption")
        metadata_layout.addWidget(self.update_caption_checkbox)
        
        metadata_group.setLayout(metadata_layout)
        layout.addWidget(metadata_group)
        
        # Keyword Corrections subsection
        keyword_group = QGroupBox("Keyword Corrections")
        keyword_group.setStyleSheet(get_groupbox_stylesheet())
        keyword_layout = QVBoxLayout()
        keyword_layout.setSpacing(8)
        
        self.depluralize_checkbox = QCheckBox("Depluralize keywords")
        keyword_layout.addWidget(self.depluralize_checkbox)
        
        word_limit_layout = QHBoxLayout()
        self.word_limit_checkbox = QCheckBox("Limit to")
        self.word_limit_spinbox = QSpinBox()
        self.word_limit_spinbox.setMinimum(1)
        self.word_limit_spinbox.setMaximum(10)
        self.word_limit_spinbox.setValue(2)
        word_limit_label = QLabel("words")
        word_limit_layout.addWidget(self.word_limit_checkbox)
        word_limit_layout.addWidget(self.word_limit_spinbox)
        word_limit_layout.addWidget(word_limit_label)
        word_limit_layout.addStretch()
        keyword_layout.addLayout(word_limit_layout)
        
        self.split_and_checkbox = QCheckBox("Split 'and'/'or' entries")
        keyword_layout.addWidget(self.split_and_checkbox)
        
        self.ban_prompt_words_checkbox = QCheckBox("Ban prompt word repetitions")
        keyword_layout.addWidget(self.ban_prompt_words_checkbox)
        
        self.no_digits_start_checkbox = QCheckBox("Cannot start with 3+ digits")
        keyword_layout.addWidget(self.no_digits_start_checkbox)
        
        self.min_word_length_checkbox = QCheckBox("Words must be 2+ characters")
        keyword_layout.addWidget(self.min_word_length_checkbox)
        
        self.latin_only_checkbox = QCheckBox("Only Latin characters")
        keyword_layout.addWidget(self.latin_only_checkbox)
        
        keyword_group.setLayout(keyword_layout)
        layout.addWidget(keyword_group)
        
        layout.addStretch()
        
        # Apply stylesheets
        for checkbox in tab.findChildren(QCheckBox):
            checkbox.setStyleSheet(get_checkbox_stylesheet())
        for radio in tab.findChildren(QRadioButton):
            radio.setStyleSheet(get_radiobutton_stylesheet())
        for spinbox in tab.findChildren(QSpinBox):
            spinbox.setStyleSheet(get_input_stylesheet())
        
        # Wrap in scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setWidget(tab)
        
        return scroll_area
    
    def _create_query_instructions_tab(self):
        """Create Query Instructions tab"""
        # Create content widget
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # System Instruction
        system_label = QLabel("System Instruction:")
        layout.addWidget(system_label)
        
        self.system_instruction_input = QLineEdit()
        self.system_instruction_input.setStyleSheet(get_input_stylesheet())
        self.system_instruction_input.setPlaceholderText("You are a helpful assistant.")
        layout.addWidget(self.system_instruction_input)
        
        # Description Instruction
        desc_label = QLabel("Description Instruction:")
        layout.addWidget(desc_label)
        
        self.description_instruction_input = QPlainTextEdit()
        self.description_instruction_input.setStyleSheet(get_input_stylesheet())
        self.description_instruction_input.setFixedHeight(120)
        self.description_instruction_input.setPlaceholderText("Describe the image in detail. Be specific.")
        layout.addWidget(self.description_instruction_input)
        
        # Keyword Instruction
        keyword_label = QLabel("Keyword Instruction:")
        layout.addWidget(keyword_label)
        
        self.keyword_instruction_input = QPlainTextEdit()
        self.keyword_instruction_input.setStyleSheet(get_input_stylesheet())
        self.keyword_instruction_input.setFixedHeight(200)
        self.keyword_instruction_input.setPlaceholderText("Return a JSON object containing only a list of Keywords...")
        layout.addWidget(self.keyword_instruction_input)
        
        layout.addStretch()
        
        # Wrap in scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setWidget(tab)
        
        return scroll_area
    
    def _create_advanced_llm_tab(self):
        """Create Advanced LLM Configuration tab"""
        # Create content widget
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # API Settings
        api_group = QGroupBox("API Settings")
        api_group.setStyleSheet(get_groupbox_stylesheet())
        api_layout = QVBoxLayout()
        api_layout.setSpacing(8)
        
        api_url_layout = QHBoxLayout()
        api_url_layout.addWidget(QLabel("API URL:"))
        self.api_url_input = QLineEdit()
        self.api_url_input.setStyleSheet(get_input_stylesheet())
        api_url_layout.addWidget(self.api_url_input)
        api_layout.addLayout(api_url_layout)
        
        api_password_layout = QHBoxLayout()
        api_password_layout.addWidget(QLabel("API Password:"))
        self.api_password_input = QLineEdit()
        self.api_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_password_input.setStyleSheet(get_input_stylesheet())
        api_password_layout.addWidget(self.api_password_input)
        api_layout.addLayout(api_password_layout)
        
        api_group.setLayout(api_layout)
        layout.addWidget(api_group)
        
        # Generation Options
        gen_group = QGroupBox("Generation Options")
        gen_group.setStyleSheet(get_groupbox_stylesheet())
        gen_layout = QVBoxLayout()
        gen_layout.setSpacing(8)
        
        gen_count_layout = QHBoxLayout()
        gen_count_layout.addWidget(QLabel("GenTokens:"))
        self.gen_count_spinbox = QSpinBox()
        self.gen_count_spinbox.setMinimum(1)
        self.gen_count_spinbox.setMaximum(2000)
        self.gen_count_spinbox.setValue(250)
        self.gen_count_spinbox.setStyleSheet(get_input_stylesheet())
        gen_count_layout.addWidget(self.gen_count_spinbox)
        gen_count_layout.addStretch()
        gen_layout.addLayout(gen_count_layout)
        
        res_limit_layout = QHBoxLayout()
        res_limit_layout.addWidget(QLabel("Dimension length:"))
        self.res_limit_spinbox = QSpinBox()
        self.res_limit_spinbox.setMinimum(100)
        self.res_limit_spinbox.setMaximum(2000)
        self.res_limit_spinbox.setValue(448)
        self.res_limit_spinbox.setStyleSheet(get_input_stylesheet())
        res_limit_layout.addWidget(self.res_limit_spinbox)
        res_limit_layout.addStretch()
        gen_layout.addLayout(res_limit_layout)
        
        gen_group.setLayout(gen_layout)
        layout.addWidget(gen_group)
        
        # Sampler Options
        sampler_group = QGroupBox("Sampler Options")
        sampler_group.setStyleSheet(get_groupbox_stylesheet())
        sampler_layout = QVBoxLayout()
        sampler_layout.setSpacing(8)
        
        # Temperature
        temp_layout = QHBoxLayout()
        temp_layout.addWidget(QLabel("Temperature:"))
        self.temperature_spinbox = QDoubleSpinBox()
        self.temperature_spinbox.setMinimum(0.0)
        self.temperature_spinbox.setMaximum(2.0)
        self.temperature_spinbox.setSingleStep(0.1)
        self.temperature_spinbox.setValue(0.2)
        self.temperature_spinbox.setDecimals(2)
        self.temperature_spinbox.setStyleSheet(get_input_stylesheet())
        temp_layout.addWidget(self.temperature_spinbox)
        temp_layout.addStretch()
        sampler_layout.addLayout(temp_layout)
        
        # top_p
        top_p_layout = QHBoxLayout()
        top_p_layout.addWidget(QLabel("top_p:"))
        self.top_p_spinbox = QDoubleSpinBox()
        self.top_p_spinbox.setMinimum(0.0)
        self.top_p_spinbox.setMaximum(1.0)
        self.top_p_spinbox.setSingleStep(0.1)
        self.top_p_spinbox.setValue(1.0)
        self.top_p_spinbox.setDecimals(2)
        self.top_p_spinbox.setStyleSheet(get_input_stylesheet())
        top_p_layout.addWidget(self.top_p_spinbox)
        top_p_layout.addStretch()
        sampler_layout.addLayout(top_p_layout)
        
        # top_k
        top_k_layout = QHBoxLayout()
        top_k_layout.addWidget(QLabel("top_k:"))
        self.top_k_spinbox = QSpinBox()
        self.top_k_spinbox.setMinimum(0)
        self.top_k_spinbox.setMaximum(200)
        self.top_k_spinbox.setValue(100)
        self.top_k_spinbox.setStyleSheet(get_input_stylesheet())
        top_k_layout.addWidget(self.top_k_spinbox)
        top_k_layout.addStretch()
        sampler_layout.addLayout(top_k_layout)
        
        # min_p
        min_p_layout = QHBoxLayout()
        min_p_layout.addWidget(QLabel("min_p:"))
        self.min_p_spinbox = QDoubleSpinBox()
        self.min_p_spinbox.setMinimum(0.0)
        self.min_p_spinbox.setMaximum(1.0)
        self.min_p_spinbox.setSingleStep(0.05)
        self.min_p_spinbox.setValue(0.1)
        self.min_p_spinbox.setDecimals(2)
        self.min_p_spinbox.setStyleSheet(get_input_stylesheet())
        min_p_layout.addWidget(self.min_p_spinbox)
        min_p_layout.addStretch()
        sampler_layout.addLayout(min_p_layout)
        
        # rep_pen
        rep_pen_layout = QHBoxLayout()
        rep_pen_layout.addWidget(QLabel("rep_pen:"))
        self.rep_pen_spinbox = QDoubleSpinBox()
        self.rep_pen_spinbox.setMinimum(1.0)
        self.rep_pen_spinbox.setMaximum(2.0)
        self.rep_pen_spinbox.setSingleStep(0.01)
        self.rep_pen_spinbox.setValue(1.01)
        self.rep_pen_spinbox.setDecimals(2)
        self.rep_pen_spinbox.setStyleSheet(get_input_stylesheet())
        rep_pen_layout.addWidget(self.rep_pen_spinbox)
        rep_pen_layout.addStretch()
        sampler_layout.addLayout(rep_pen_layout)
        
        sampler_group.setLayout(sampler_layout)
        layout.addWidget(sampler_group)
        
        layout.addStretch()
        
        # Wrap in scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setWidget(tab)
        
        return scroll_area
    
    def load_settings(self):
        """Load settings from config into UI"""
        # Content Options tab
        if self.config.both_query_method == "combined":
            self.combined_query_radio.setChecked(True)
        else:
            self.separate_query_radio.setChecked(True)
        
        self.mark_ignore_checkbox.setChecked(self.config.mark_ignore)
        self.no_crawl_checkbox.setChecked(self.config.no_crawl)
        self.auto_save_checkbox.setChecked(self.config.auto_save)
        self.no_backup_checkbox.setChecked(self.config.no_backup)
        self.use_sidecar_checkbox.setChecked(self.config.use_sidecar)
        self.reprocess_failed_checkbox.setChecked(self.config.reprocess_failed)
        self.reprocess_all_checkbox.setChecked(self.config.reprocess_all)
        self.reprocess_orphans_checkbox.setChecked(self.config.reprocess_orphans)
        self.dry_run_checkbox.setChecked(self.config.dry_run)
        self.skip_verify_checkbox.setChecked(self.config.skip_verify)
        self.quick_fail_checkbox.setChecked(self.config.quick_fail)
        self.update_caption_checkbox.setChecked(self.config.update_caption)
        
        # Keyword Corrections
        self.depluralize_checkbox.setChecked(self.config.depluralize_keywords)
        self.word_limit_checkbox.setChecked(self.config.limit_word_count)
        self.word_limit_spinbox.setValue(self.config.max_words_per_keyword)
        self.split_and_checkbox.setChecked(self.config.split_and_entries)
        self.ban_prompt_words_checkbox.setChecked(self.config.ban_prompt_words)
        self.no_digits_start_checkbox.setChecked(self.config.no_digits_start)
        self.min_word_length_checkbox.setChecked(self.config.min_word_length)
        self.latin_only_checkbox.setChecked(self.config.latin_only)
        
        # Query Instructions tab
        self.system_instruction_input.setText(self.config.system_instruction)
        self.description_instruction_input.setPlainText(self.config.description_instruction)
        self.keyword_instruction_input.setPlainText(self.config.keyword_instruction)
        
        # Advanced LLM Configuration tab
        self.api_url_input.setText(self.config.api_url)
        self.api_password_input.setText(self.config.api_password)
        self.gen_count_spinbox.setValue(self.config.gen_count)
        self.res_limit_spinbox.setValue(self.config.res_limit)
        self.temperature_spinbox.setValue(self.config.temperature)
        self.top_p_spinbox.setValue(self.config.top_p)
        self.top_k_spinbox.setValue(self.config.top_k)
        self.min_p_spinbox.setValue(self.config.min_p)
        self.rep_pen_spinbox.setValue(self.config.rep_pen)
    
    def save_settings(self):
        """Save settings from UI to config"""
        # Content Options tab
        if self.combined_query_radio.isChecked():
            self.config.both_query_method = "combined"
        else:
            self.config.both_query_method = "separate"
        
        self.config.mark_ignore = self.mark_ignore_checkbox.isChecked()
        self.config.no_crawl = self.no_crawl_checkbox.isChecked()
        self.config.auto_save = self.auto_save_checkbox.isChecked()
        self.config.no_backup = self.no_backup_checkbox.isChecked()
        self.config.use_sidecar = self.use_sidecar_checkbox.isChecked()
        self.config.reprocess_failed = self.reprocess_failed_checkbox.isChecked()
        self.config.reprocess_all = self.reprocess_all_checkbox.isChecked()
        self.config.reprocess_orphans = self.reprocess_orphans_checkbox.isChecked()
        self.config.dry_run = self.dry_run_checkbox.isChecked()
        self.config.skip_verify = self.skip_verify_checkbox.isChecked()
        self.config.quick_fail = self.quick_fail_checkbox.isChecked()
        self.config.update_caption = self.update_caption_checkbox.isChecked()
        
        # Keyword Corrections
        self.config.depluralize_keywords = self.depluralize_checkbox.isChecked()
        self.config.limit_word_count = self.word_limit_checkbox.isChecked()
        self.config.max_words_per_keyword = self.word_limit_spinbox.value()
        self.config.split_and_entries = self.split_and_checkbox.isChecked()
        self.config.ban_prompt_words = self.ban_prompt_words_checkbox.isChecked()
        self.config.no_digits_start = self.no_digits_start_checkbox.isChecked()
        self.config.min_word_length = self.min_word_length_checkbox.isChecked()
        self.config.latin_only = self.latin_only_checkbox.isChecked()
        
        # Query Instructions tab
        self.config.system_instruction = self.system_instruction_input.text()
        self.config.description_instruction = self.description_instruction_input.toPlainText()
        self.config.keyword_instruction = self.keyword_instruction_input.toPlainText()
        
        # Advanced LLM Configuration tab
        self.config.api_url = self.api_url_input.text()
        self.config.api_password = self.api_password_input.text()
        self.config.gen_count = self.gen_count_spinbox.value()
        self.config.res_limit = self.res_limit_spinbox.value()
        self.config.temperature = self.temperature_spinbox.value()
        self.config.top_p = self.top_p_spinbox.value()
        self.config.top_k = self.top_k_spinbox.value()
        self.config.min_p = self.min_p_spinbox.value()
        self.config.rep_pen = self.rep_pen_spinbox.value()
        
        # Save to file
        return self.config.save_to_file()
    
    def accept_and_save(self):
        """Save settings and accept dialog"""
        try:
            if self.save_settings():
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Failed to save settings.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save settings: {e}")
