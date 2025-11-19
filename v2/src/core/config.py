import os
import sys
import json


def _get_project_root():
    """Get project root directory, handling both normal execution and app bundle"""
    # Check if we're running from an app bundle
    if getattr(sys, 'frozen', False):
        # Running from py2app bundle
        # sys.executable points to the app bundle's executable
        # We need to go up to Contents/Resources/
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller style (not used here, but for compatibility)
            base_path = sys._MEIPASS
        else:
            # py2app: sys.executable is the app bundle executable
            # Go from MacOS/executable to Contents/Resources/
            bundle_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.executable))))
            # In app bundle, resources are in Contents/Resources/resources/
            resources_path = os.path.join(bundle_dir, "Contents", "Resources")
            # Check if resources directory exists there
            if os.path.exists(os.path.join(resources_path, "resources")):
                return resources_path
            else:
                # Fallback: use the bundle directory as project root
                return bundle_dir
    else:
        # Normal execution: project root is three levels up from src/core/config.py (v2/src/core/config.py)
        # Go up: v2/src/core -> v2/src -> v2 -> project root
        return os.path.normpath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Get project root directory 
PROJECT_ROOT = _get_project_root()

# Resources directory at project root level
# In app bundle, this will be Contents/Resources/resources/
# In normal execution, this will be project_root/v2/resources/
# For v2, we look in v2/resources/ first, then fall back to project_root/resources/
v2_resources = os.path.normpath(os.path.join(PROJECT_ROOT, "v2", "resources"))
if os.path.exists(v2_resources):
    RESOURCES_DIR = v2_resources
else:
    RESOURCES_DIR = os.path.normpath(os.path.join(PROJECT_ROOT, "resources"))


class Config:
    """Configuration class for Batch Image Metadata Tool"""
    
    def __init__(self):
        # Default values
        self.directory = None
        self.api_url = "http://localhost:5001"
        self.api_password = ""
        self.system_instruction = "You are a helpful assistant."
        self.description_instruction = "Describe the image in detail. Be specific."
        self.keyword_instruction = """Return a JSON object containing only a list of Keywords.

Generate 5 to 10 Keywords. Each Keyword is an item in a list and will be composed of a maximum of two words.

For Keywords, make sure to include:

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

Use ENGLISH only. Generate ONLY a JSON object with the key Keywords as follows {"Keywords": []}"""
        # Processing options
        self.gen_count = 250
        self.res_limit = 448
        self.no_crawl = False
        self.reprocess_failed = False
        self.reprocess_all = False
        self.reprocess_orphans = False
        self.no_backup = False
        self.dry_run = False
        self.skip_verify = False
        self.quick_fail = False
        self.update_caption = False
        # NOTE: generation_mode values ("description_only", "keywords_only", "both") are kept in code
        # for future Process Keywords/Description actions, but UI only shows "Combined Query" vs "Separate Query"
        # which maps to both_query_method. Assess value/need/location when implementing Process Keywords/Description.
        self.generation_mode = "both"  # "description_only", "keywords_only", "both" - kept for future use
        self.both_query_method = "separate"  # "combined" or "separate" - this is what UI shows
        self.mark_ignore = True  # Mark status as "Ignored" if image already has keyword(s) and description
        self.use_sidecar = False
        self.auto_save = False
        
        # Keyword processing options
        self.depluralize_keywords = False
        self.limit_word_count = True
        self.max_words_per_keyword = 2
        self.split_and_entries = True
        self.ban_prompt_words = True
        self.no_digits_start = True
        self.min_word_length = True
        self.latin_only = True
        
        # LLM sampler settings
        self.temperature = 0.2
        self.top_p = 1.0
        self.top_k = 100
        self.min_p = 0.1
        self.rep_pen = 1.01
    
    @classmethod
    def load_from_file(cls, settings_path=None):
        """
        Load configuration from settings.json file.
        
        Args:
            settings_path: Optional path to settings.json. If None, looks in v2/ directory.
            
        Returns:
            Config instance with loaded settings
        """
        config = cls()
        
        # Determine settings file path
        if settings_path is None:
            # Look for settings.json in v2/ directory
            v2_dir = os.path.join(PROJECT_ROOT, "v2")
            settings_path = os.path.join(v2_dir, "settings.json")
        
        if not os.path.exists(settings_path):
            # Return default config if file doesn't exist
            return config
        
        try:
            with open(settings_path, 'r') as f:
                settings = json.load(f)
            
            # Map settings to config attributes (with backward compatibility)
            config.directory = settings.get('directory')
            config.api_url = settings.get('api_url', config.api_url)
            config.api_password = settings.get('api_password', config.api_password)
            config.system_instruction = settings.get('system_instruction', config.system_instruction)
            
            # Handle instruction migration (old format -> new format)
            # Old format had: instruction, caption_instruction, general_instruction
            # New format has: description_instruction, keyword_instruction (general_instruction removed)
            # Note: general_instruction is no longer used - Process (both) uses both instructions together
            if 'description_instruction' in settings:
                config.description_instruction = settings['description_instruction']
            elif 'caption_instruction' in settings:
                # Migrate old caption_instruction to description_instruction
                config.description_instruction = settings['caption_instruction']
            
            if 'keyword_instruction' in settings:
                config.keyword_instruction = settings['keyword_instruction']
            elif 'instruction' in settings:
                # If old instruction exists but no keyword_instruction, use it as fallback
                # (though ideally keyword_instruction should be set separately)
                pass  # Don't set keyword_instruction from old instruction
            
            # Processing options
            config.gen_count = settings.get('gen_count', config.gen_count)
            config.res_limit = settings.get('res_limit', config.res_limit)
            config.no_crawl = settings.get('no_crawl', config.no_crawl)
            config.reprocess_failed = settings.get('reprocess_failed', config.reprocess_failed)
            config.reprocess_all = settings.get('reprocess_all', config.reprocess_all)
            config.reprocess_orphans = settings.get('reprocess_orphans', config.reprocess_orphans)
            config.no_backup = settings.get('no_backup', config.no_backup)
            config.dry_run = settings.get('dry_run', config.dry_run)
            config.skip_verify = settings.get('skip_verify', config.skip_verify)
            config.quick_fail = settings.get('quick_fail', config.quick_fail)
            config.update_caption = settings.get('update_caption', config.update_caption)
            config.generation_mode = settings.get('generation_mode', config.generation_mode)
            config.both_query_method = settings.get('both_query_method', config.both_query_method)
            config.mark_ignore = settings.get('mark_ignore', config.mark_ignore)
            config.use_sidecar = settings.get('use_sidecar', config.use_sidecar)
            config.auto_save = settings.get('auto_save', config.auto_save)
            
            # Keyword processing options
            config.depluralize_keywords = settings.get('depluralize_keywords', config.depluralize_keywords)
            config.limit_word_count = settings.get('limit_word_count', config.limit_word_count)
            config.max_words_per_keyword = settings.get('max_words_per_keyword', config.max_words_per_keyword)
            config.split_and_entries = settings.get('split_and_entries', config.split_and_entries)
            config.ban_prompt_words = settings.get('ban_prompt_words', config.ban_prompt_words)
            config.no_digits_start = settings.get('no_digits_start', config.no_digits_start)
            config.min_word_length = settings.get('min_word_length', config.min_word_length)
            config.latin_only = settings.get('latin_only', config.latin_only)
            
            # LLM sampler settings
            config.temperature = settings.get('temperature', config.temperature)
            config.top_p = settings.get('top_p', config.top_p)
            config.top_k = settings.get('top_k', config.top_k)
            config.min_p = settings.get('min_p', config.min_p)
            config.rep_pen = settings.get('rep_pen', config.rep_pen)
            
        except Exception as e:
            print(f"Error loading settings: {e}")
            # Return default config on error
        
        return config
    
    def save_to_file(self, settings_path=None):
        """
        Save configuration to settings.json file.
        
        Args:
            settings_path: Optional path to settings.json. If None, saves to v2/settings.json.
            
        Returns:
            True if successful, False otherwise
        """
        # Determine settings file path
        if settings_path is None:
            v2_dir = os.path.join(PROJECT_ROOT, "v2")
            settings_path = os.path.join(v2_dir, "settings.json")
        
        try:
            settings = {
                'api_url': self.api_url,
                'api_password': self.api_password,
                'system_instruction': self.system_instruction,
                'description_instruction': self.description_instruction,
                'keyword_instruction': self.keyword_instruction,
                'gen_count': self.gen_count,
                'res_limit': self.res_limit,
                'no_crawl': self.no_crawl,
                'reprocess_failed': self.reprocess_failed,
                'reprocess_all': self.reprocess_all,
                'reprocess_orphans': self.reprocess_orphans,
                'no_backup': self.no_backup,
                'dry_run': self.dry_run,
                'skip_verify': self.skip_verify,
                'quick_fail': self.quick_fail,
                'update_caption': self.update_caption,
                'generation_mode': self.generation_mode,
                'both_query_method': self.both_query_method,
                'mark_ignore': self.mark_ignore,
                'use_sidecar': self.use_sidecar,
                'auto_save': self.auto_save,
                'depluralize_keywords': self.depluralize_keywords,
                'limit_word_count': self.limit_word_count,
                'max_words_per_keyword': self.max_words_per_keyword,
                'split_and_entries': self.split_and_entries,
                'ban_prompt_words': self.ban_prompt_words,
                'no_digits_start': self.no_digits_start,
                'min_word_length': self.min_word_length,
                'latin_only': self.latin_only,
                'temperature': self.temperature,
                'top_p': self.top_p,
                'top_k': self.top_k,
                'min_p': self.min_p,
                'rep_pen': self.rep_pen,
            }
            
            # Add directory if set
            if self.directory:
                settings['directory'] = self.directory
            
            # Note: general_instruction is no longer saved - removed in favor of separate instructions
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(settings_path), exist_ok=True)
            
            with open(settings_path, 'w') as f:
                json.dump(settings, f, indent=4)
            
            return True
            
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    # Property aliases for backward compatibility
    @property
    def instruction(self):
        """Alias for keyword_instruction (for backward compatibility)"""
        return self.keyword_instruction
    
    @property
    def caption_instruction(self):
        """Alias for description_instruction (for backward compatibility)"""
        return self.description_instruction

