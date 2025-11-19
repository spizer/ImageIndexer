# Testing the Settings Dialog

## Quick Test

To test the new Settings Dialog independently, run:

```bash
cd v2
source ../llmii_env/bin/activate  # Activate virtual environment
python3 test_settings_dialog.py
```

Or if you're already in the virtual environment:

```bash
cd v2
python3 test_settings_dialog.py
```

## What to Test

1. **Content Options Tab**:
   - Verify all checkboxes and radio buttons work
   - Test "Combined Query" vs "Separate Queries" radio buttons
   - Test `mark_ignore` checkbox (should be checked by default)
   - Verify all File Options checkboxes
   - Verify Keyword Corrections options

2. **Query Instructions Tab**:
   - Verify System Instruction field
   - Verify Description Instruction text area
   - Verify Keyword Instruction text area
   - Test editing and saving

3. **Advanced LLM Configuration Tab**:
   - Verify API URL and Password fields
   - Test all sampler settings (temperature, top_p, top_k, min_p, rep_pen)
   - Test GenTokens and Dimension length spinboxes

4. **Save/Load**:
   - Make changes and click OK
   - Reopen dialog and verify changes persisted
   - Check that settings.json was updated correctly

5. **Visual**:
   - Verify dark theme is applied
   - Check that all controls have proper styling
   - Verify tab switching works smoothly
   - Check focus states on controls

## Notes

- The dialog is fixed size (500x460)
- Settings are saved to `v2/settings.json`
- The dialog loads from the config file on startup
- Changes are only saved when you click "OK"

