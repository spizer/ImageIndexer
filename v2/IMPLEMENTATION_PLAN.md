# Batch Image Metadata Tool v2 - Implementation Plan

## Overview

This document outlines the phased implementation plan for refactoring and updating the Batch Image Metadata Tool (formerly "Image Indexer"). The refactor focuses on improving UX/UI, adding accessibility features, and creating a more maintainable codebase.

---

## Phase 1: Create v2 Folder Structure ✅

**Status**: Completed

**Goals**:
- Create `v2/` folder structure
- Copy essential files
- Update imports to be self-contained
- Set up test structure

**Deliverables**:
- ✅ `v2/src/` directory structure
- ✅ Core modules (`core/`, `ui/`, `utils/`, `helpers/`)
- ✅ Test fixtures and utilities
- ✅ Resources directory setup

---

## Phase 2: Extract Core Business Logic ✅

**Status**: Completed

**Goals**:
- Extract metadata operations to `core/metadata.py`
- Extract LLM processing to `core/llm.py`
- Extract configuration management to `core/config.py`
- Ensure all core logic is self-contained

**Deliverables**:
- ✅ `v2/src/core/metadata.py` - ExifTool read/write operations
- ✅ `v2/src/core/llm.py` - LLM API interaction
- ✅ `v2/src/core/config.py` - Configuration with settings.json load/save
- ✅ Two-pass write logic with separate ExifTool instance for deletion

---

## Phase 3: Redesign Settings Dialog ✅

**Status**: Completed

**Goals**:
- Redesign settings dialog into 3 tabs
- Update visual style based on mockups
- Add new settings (`mark_ignore`)
- Remove deprecated settings (`general_instruction`, `update_keywords`)

**Deliverables**:
- ✅ `v2/src/ui/settings_dialog.py` - 3-tab structure
  - Content Options tab
  - Query Instructions tab
  - Advanced LLM Configuration tab
- ✅ `v2/src/ui/theme.py` - Design tokens and stylesheets
- ✅ Scroll areas for all tabs
- ✅ Fixed size: 500x460 pixels

---

## Phase 4: Create LLM Selection Modal 🔄

**Status**: In Progress

**Goals**:
- Create modal for LLM model selection
- Query available models via KoboldCPP
- Display model metadata (size, requirements, etc.)
- Download models with progress indication
- Manage model selection and storage

**Requirements**:
- Fixed size: 400x440 pixels with scrollable area
- Show GPU/VRAM information
- Display model status (Downloaded/Not Downloaded)
- Download button with spinner during download
- Delete button (trash icon) for downloaded models
- Queue multiple downloads (one at a time)
- Error handling with retry option

**Technical Details**:
- Copy `GpuDetector` and `download_file` functions to v2
- Convert HuggingFace blob URLs to resolve URLs for downloads
- Store selected model in both `settings.json` and `kobold_args.json`
- Check for local files to determine download status
- Use local file paths in `kobold_args.json` after download

**Deliverables**:
- `v2/src/ui/components/llm_selection_modal.py`
- `v2/src/core/gpu_detector.py` (copied from `src/llmii_setup.py`)
- `v2/src/utils/model_manager.py` (download, status checking, file management)
- Integration with `v2/src/core/config.py` for selected model storage

**Custom Models**:
- Copy `AddModelDialog` logic to v2
- Allow adding custom models to `model_list.json`
- Required fields: Model Name, Language URL, MMProj URL, Adapter Type, Description, Size, Flash Attention

**Debugging and Testing**:
- **Debug Flags**: Class-level flags for enabling debug logging
  - `DEBUG_MODE = False` - Enable/disable debug logging
  - `DEBUG_VERBOSE = False` - Enable extra verbose logging (includes state dumps)
  - `USE_MOCK_DOWNLOADS = False` - Use MockDownloadThread for testing (no network required)
- **Debug Logging**: Comprehensive logging at key points:
  - Queue operations (add, remove, pop)
  - Download start/completion
  - Signal call counts
  - State dumps (queue contents, current download, active threads)
- **Assertions**: Built-in assertions to catch bugs:
  - Model not in queue when starting download
  - current_download is None when processing queue
  - No duplicate models in queue
- **MockDownloadThread**: Simulates downloads without network:
  - Fast downloads (10MB test files)
  - Configurable delays
  - Error simulation support
- **Usage**:
  ```python
  # Enable debugging
  LLMSelectionModal.DEBUG_MODE = True
  LLMSelectionModal.DEBUG_VERBOSE = True  # Optional: extra detail
  LLMSelectionModal.USE_MOCK_DOWNLOADS = True  # For testing
  
  modal = LLMSelectionModal(config)
  ```

---

## Phase 5: Create New Main Window Layout

**Status**: Pending

**Goals**:
- Create new main window based on mockups
- Rearrange UI layout
- Apply design tokens from theme

**Deliverables**:
- `v2/src/ui/main_window.py`
- Layout matching mockups
- Integration with settings dialog
- Integration with LLM selection modal

---

## Phase 6: Implement Split Process Button

**Status**: Pending

**Goals**:
- Create split Process button (Keywords/Description/Both)
- Implement regenerate actions
- Update button states based on context

**Requirements**:
- Split button with icon + text
- "Process Keywords" - uses Keyword instruction only
- "Process Description" - uses Description instruction only
- "Process (both)" - uses both instructions
- Regenerate actions use same instructions as Process
- "Combined vs Separate queries" affects only "Process (both)" action

**Deliverables**:
- Split button component
- Process action handlers
- Regenerate action handlers
- Integration with LLM processor

---

## Phase 7: Create Process Logs Modal

**Status**: Pending

**Goals**:
- Create modal for displaying processing logs
- Auto-scroll to bottom
- Move existing "Processing Logs" functionality to modal

**Deliverables**:
- `v2/src/ui/components/process_logs_modal.py`
- Auto-scroll functionality
- Log formatting and display

---

## Phase 8: Implement First Run Wizard

**Status**: Pending

**Goals**:
- Create wizard for first-time users
- Guide through LLM model selection
- Only show if user hasn't selected/downloaded a model

**Deliverables**:
- `v2/src/ui/components/first_run_wizard.py`
- Integration with LLM selection modal
- Check for existing model selection

---

## Phase 9: Extract and Apply Design Tokens

**Status**: Pending

**Goals**:
- Ask for design tokens, when not provided extract design tokens from mockups
- Apply consistently throughout UI
- Update all components with new styling

**Deliverables**:
- Updated `v2/src/ui/theme.py` with all design tokens
- Applied styles to all UI components
- Consistent visual design

---

## Phase 9.5: UX Improvements 🆕

**Status**: Pending

**Goals**:
- Enhance model selection and management UX
- Improve information display
- Reduce manual data entry

**Deliverables**:

1. **Model Details Panel**
   - Show detailed model information when model is selected
   - Display GPU/VRAM compatibility
   - Show model specifications
   - Visual indicators for compatibility
   - Add ability to detect presence and support Apple Metal GPU 
   - 

2. **Auto-extract Model Details**
   - Explore scraping/extracting model details from HuggingFace
   - Use HuggingFace API if available
   - Auto-fill model information when adding custom models
   - Reduce manual entry requirements

3. **LLM Model List Management**
   - Enhanced model list organization
   - Filtering and sorting options
   - Better model status indicators
   - Model grouping (downloaded, available, custom)

4. **Update Ignore Status Behavior**
   - Update default state in settings
   - Update how Ignore status affects the Manual update behaviors of Descriptions and Keywords

5. **Reconcile "Caption" and "Description" in codebase and UI**
   - Assess where we are using these terms interchangeably and pick one

**Note**: This phase will be expanded as the project progresses.

---

## Phase 10: Add Keyboard Navigation, Focus States, and Tooltips

**Status**: Pending

**Goals**:
- Implement full keyboard navigation
- Add visual focus indicators
- Add tooltips to all controls
- Ensure accessibility compliance

**Requirements**:
- Full tab order navigation
- Keyboard shortcuts for common actions
- Visual focus states on all interactive elements
- Tooltips for all controls
- ARIA labels where appropriate

**Deliverables**:
- Keyboard navigation handlers
- Focus state styling
- Tooltip system
- Accessibility improvements

---

## Phase 11: Integrate Regeneration Helper, Keyword Widget, and Complete Features

**Status**: Pending

**Goals**:
- Integrate regeneration functionality
- Add keyword management widget
- Complete all remaining features
- Ensure feature parity with v1

**Deliverables**:
- Regeneration helper integration
- Keyword widget component
- Complete feature set
- Feature parity validation

---

## Phase 12: Comprehensive Testing and Validation

**Status**: Pending

**Goals**:
- Test all features thoroughly
- Validate against mockups
- Performance testing
- Cross-platform testing

**Deliverables**:
- Test suite for all features
- Validation report
- Performance benchmarks
- Cross-platform compatibility report

---

## Phase 13: Setup Packaging for Standalone App

**Status**: Pending

**Goals**:
- Package app into standalone launchable app
- Update app name to "Batch Image Metadata Tool"
- Create installer/distribution packages
- Update `setup.py` for new structure

**Deliverables**:
- Updated `setup.py`
- Standalone app bundle
- Distribution packages
- Installation documentation

---

## Migration Strategy

**Approach**: Parallel Development (Option A)
- v1 and v2 coexist
- Gradual migration
- No breaking changes to v1
- v2 is self-contained

---

## Testing Strategy

- Tests on every commit
- Reuse existing tests when possible
- Create new tests for new features
- Integration tests for UI components

---

## Notes

- All phases should include regular git commits
- Incremental progress with regular check-ins
- Focus on preventing regressions
- Regular validation against mockups

---

## Current Status Summary

- ✅ Phase 1: Foundation Setup
- ✅ Phase 2: Core Logic Extraction
- ✅ Phase 3: Settings Dialog Redesign
- 🔄 Phase 4: LLM Selection Modal (In Progress)
- ⏳ Phase 5-13: Pending

---

*Last Updated: 2025-01-XX*

