"""
Configuration Manager for Runic Lands
Handles loading, saving and accessing game settings
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, Union, Tuple

class ConfigManager:
    """
    Manages game configuration settings with hierarchical sections,
    default values, and persistent storage
    """
    
    def __init__(self, config_dir: str = None):
        """
        Initialize the configuration manager
        If config_dir is None, uses ~/.runiclands
        """
        # Set up config directory
        if config_dir is None:
            self.config_dir = Path.home() / ".runiclands"
        else:
            self.config_dir = Path(config_dir)
            
        # Create directory if it doesn't exist
        self.config_dir.mkdir(exist_ok=True)
        
        # Set up config file path
        self.config_file = self.config_dir / "settings.json"
        
        # Default configuration values
        self.defaults = {
            'video': {
                'fullscreen': False,
                'resolution': (800, 600),
                'vsync': True
            },
            'audio': {
                'master_volume': 0.7,
                'music_volume': 0.5,
                'sfx_volume': 0.8
            },
            'controls': {
                'player1': {
                    'up': 119,     # W key
                    'down': 115,   # S key
                    'left': 97,    # A key
                    'right': 100,  # D key
                    'attack': 32,  # Space key
                    'inventory': 101  # E key
                },
                'player2': {
                    'up': 273,     # Up Arrow
                    'down': 274,   # Down Arrow
                    'left': 276,   # Left Arrow
                    'right': 275,  # Right Arrow
                    'attack': 303, # Right Ctrl
                    'inventory': 304  # Right Shift
                }
            },
            'game': {
                'difficulty': 'normal',
                'auto_save': True,
                'show_fps': False,
                'particles_enabled': True
            }
        }
        
        # Current configuration (will be populated by load_config)
        self.config = {}
        
        # Load configuration or create default
        self.load_config()
        
        # Register of callbacks for config changes
        self.change_callbacks = {}
    
    def load_config(self) -> bool:
        """
        Load configuration from file, applying defaults for missing values
        Returns True if successful, False otherwise
        """
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                
                # Merge with defaults (recursively)
                self.config = self._merge_configs(self.defaults, loaded_config)
                
                # Handle special types like tuples
                self._process_special_types()
                
                return True
            else:
                # Use defaults for new configuration
                self.config = self._deep_copy_config(self.defaults)
                return self.save_config()
        except Exception as e:
            print(f"Error loading configuration: {e}")
            self.config = self._deep_copy_config(self.defaults)
            return False
    
    def _process_special_types(self):
        """Process special types like converting lists to tuples"""
        # Convert resolution from list to tuple if needed
        if 'video' in self.config and 'resolution' in self.config['video']:
            if isinstance(self.config['video']['resolution'], list):
                self.config['video']['resolution'] = tuple(self.config['video']['resolution'])
    
    def _merge_configs(self, defaults: Dict, loaded: Dict) -> Dict:
        """
        Recursively merge loaded config with defaults
        This ensures that new config options get default values
        """
        result = self._deep_copy_config(defaults)
        
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursive merge for nested dictionaries
                result[key] = self._merge_configs(result[key], value)
            else:
                # Direct assignment for non-dict values
                result[key] = value
                
        return result
    
    def _deep_copy_config(self, config: Dict) -> Dict:
        """Create a deep copy of a configuration dictionary"""
        result = {}
        for key, value in config.items():
            if isinstance(value, dict):
                result[key] = self._deep_copy_config(value)
            else:
                result[key] = value
        return result
    
    def save_config(self) -> bool:
        """
        Save current configuration to file
        Returns True if successful, False otherwise
        """
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """
        Get a configuration value
        Returns default if the section or key doesn't exist
        """
        if section in self.config and key in self.config[section]:
            return self.config[section][key]
        return default
    
    def set(self, section: str, key: str, value: Any) -> bool:
        """
        Set a configuration value and save
        Returns True if the value was changed, False otherwise
        """
        # Make sure section exists
        if section not in self.config:
            self.config[section] = {}
        
        # Check if value is actually changing
        if key in self.config[section] and self.config[section][key] == value:
            return False
            
        # Set new value
        old_value = self.config[section].get(key)
        self.config[section][key] = value
        
        # Save configuration
        success = self.save_config()
        
        # Call registered callbacks
        callback_id = f"{section}.{key}"
        if success and callback_id in self.change_callbacks:
            for callback in self.change_callbacks[callback_id]:
                try:
                    callback(section, key, old_value, value)
                except Exception as e:
                    print(f"Error in config change callback: {e}")
        
        return success
    
    def register_change_callback(self, section: str, key: str, callback):
        """Register a callback function to be called when a specific config value changes"""
        callback_id = f"{section}.{key}"
        
        if callback_id not in self.change_callbacks:
            self.change_callbacks[callback_id] = []
            
        if callback not in self.change_callbacks[callback_id]:
            self.change_callbacks[callback_id].append(callback)
    
    def unregister_change_callback(self, section: str, key: str, callback):
        """Unregister a previously registered change callback"""
        callback_id = f"{section}.{key}"
        
        if callback_id in self.change_callbacks and callback in self.change_callbacks[callback_id]:
            self.change_callbacks[callback_id].remove(callback)
    
    def get_resolution(self) -> Tuple[int, int]:
        """Helper to get the current resolution setting"""
        resolution = self.get('video', 'resolution', (800, 600))
        if isinstance(resolution, list):
            return tuple(resolution)
        return resolution
    
    def get_fullscreen(self) -> bool:
        """Helper to get the current fullscreen setting"""
        return self.get('video', 'fullscreen', False)
    
    def get_vsync(self) -> bool:
        """Helper to get the current vsync setting"""
        return self.get('video', 'vsync', True)
    
    def get_keybind(self, player: str, action: str) -> int:
        """Helper to get a specific keybinding"""
        return self.get('controls', player, {}).get(action, 0)
    
    def set_keybind(self, player: str, action: str, key_code: int) -> bool:
        """Helper to set a specific keybinding"""
        controls = self.get('controls', player, {})
        controls[action] = key_code
        return self.set('controls', player, controls) 