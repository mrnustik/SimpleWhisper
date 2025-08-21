"""
Settings Manager for SimpleWhisper application.
Handles loading, saving, and managing application settings.
"""

import json
import os
from typing import Dict, Any, Optional
from UIConstants import UIConstants


class SettingsManager:
    """Manages application settings with JSON persistence."""
    
    def __init__(self, settings_file: str = "settings.json"):
        """
        Initialize SettingsManager.
        
        Args:
            settings_file: Path to settings file relative to application directory
        """
        self.settings_file = settings_file
        self.settings: Dict[str, Any] = {}
        self._load_default_settings()
        self.load_settings()
    
    def _load_default_settings(self):
        """Load default application settings."""
        self.settings = {
            "hotkeys": {
                "toggle_recording": UIConstants.GLOBAL_HOTKEY_TOGGLE_RECORDING,
                "stop_recording": UIConstants.GLOBAL_HOTKEY_STOP_RECORDING
            },
            "audio": {
                "device_id": None  # Will use system default
            },
            "whisper": {
                "model_download_path": None  # Will use default ~/.cache/whisper
            },
            "ui": {
                "global_hotkeys_enabled": True
            }
        }
    
    def load_settings(self) -> bool:
        """
        Load settings from file.
        
        Returns:
            True if settings were loaded successfully, False otherwise
        """
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    self._merge_settings(loaded_settings)
                return True
        except (json.JSONDecodeError, IOError) as e:
            print(f"Failed to load settings: {e}")
            # Keep default settings if loading fails
        return False
    
    def save_settings(self) -> bool:
        """
        Save current settings to file.
        
        Returns:
            True if settings were saved successfully, False otherwise
        """
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Failed to save settings: {e}")
            return False
    
    def _merge_settings(self, loaded_settings: Dict[str, Any]):
        """
        Merge loaded settings with defaults, preserving structure.
        
        Args:
            loaded_settings: Settings loaded from file
        """
        for category, values in loaded_settings.items():
            if category in self.settings and isinstance(values, dict):
                self.settings[category].update(values)
            else:
                self.settings[category] = values
    
    def get_hotkey(self, action: str) -> str:
        """
        Get hotkey for specified action.
        
        Args:
            action: Action name ('toggle_recording' or 'stop_recording')
            
        Returns:
            Hotkey string for the action
        """
        return self.settings.get("hotkeys", {}).get(action, "")
    
    def set_hotkey(self, action: str, hotkey: str) -> bool:
        """
        Set hotkey for specified action.
        
        Args:
            action: Action name ('toggle_recording' or 'stop_recording')
            hotkey: Hotkey string to set
            
        Returns:
            True if hotkey was set successfully
        """
        if "hotkeys" not in self.settings:
            self.settings["hotkeys"] = {}
        
        self.settings["hotkeys"][action] = hotkey
        return self.save_settings()
    
    def get_all_hotkeys(self) -> Dict[str, str]:
        """
        Get all configured hotkeys.
        
        Returns:
            Dictionary of action -> hotkey mappings
        """
        return self.settings.get("hotkeys", {}).copy()
    
    def set_all_hotkeys(self, hotkeys: Dict[str, str]) -> bool:
        """
        Set multiple hotkeys at once.
        
        Args:
            hotkeys: Dictionary of action -> hotkey mappings
            
        Returns:
            True if hotkeys were set successfully
        """
        if "hotkeys" not in self.settings:
            self.settings["hotkeys"] = {}
        
        self.settings["hotkeys"].update(hotkeys)
        return self.save_settings()
    
    def reset_hotkeys_to_default(self) -> bool:
        """
        Reset all hotkeys to default values.
        
        Returns:
            True if reset was successful
        """
        default_hotkeys = {
            "toggle_recording": UIConstants.GLOBAL_HOTKEY_TOGGLE_RECORDING,
            "stop_recording": UIConstants.GLOBAL_HOTKEY_STOP_RECORDING
        }
        return self.set_all_hotkeys(default_hotkeys)
    
    def get_audio_device_id(self) -> Optional[int]:
        """Get configured audio device ID."""
        return self.settings.get("audio", {}).get("device_id")
    
    def set_audio_device_id(self, device_id: Optional[int]) -> bool:
        """
        Set audio device ID.
        
        Args:
            device_id: Audio device ID to set
            
        Returns:
            True if device ID was set successfully
        """
        if "audio" not in self.settings:
            self.settings["audio"] = {}
        
        self.settings["audio"]["device_id"] = device_id
        return self.save_settings()
    
    def is_global_hotkeys_enabled(self) -> bool:
        """Check if global hotkeys are enabled."""
        return self.settings.get("ui", {}).get("global_hotkeys_enabled", True)
    
    def set_global_hotkeys_enabled(self, enabled: bool) -> bool:
        """
        Set global hotkeys enabled state.
        
        Args:
            enabled: Whether global hotkeys should be enabled
            
        Returns:
            True if setting was saved successfully
        """
        if "ui" not in self.settings:
            self.settings["ui"] = {}
        
        self.settings["ui"]["global_hotkeys_enabled"] = enabled
        return self.save_settings()
    
    def get_model_download_path(self) -> Optional[str]:
        """Get configured Whisper model download path."""
        return self.settings.get("whisper", {}).get("model_download_path")
    
    def set_model_download_path(self, path: Optional[str]) -> bool:
        """
        Set Whisper model download path.
        
        Args:
            path: Path to store downloaded models (None for default)
            
        Returns:
            True if path was set successfully
        """
        if "whisper" not in self.settings:
            self.settings["whisper"] = {}
        
        self.settings["whisper"]["model_download_path"] = path
        return self.save_settings()
    
    def get_setting(self, category: str, key: str, default: Any = None) -> Any:
        """
        Get a specific setting value.
        
        Args:
            category: Settings category
            key: Setting key
            default: Default value if setting doesn't exist
            
        Returns:
            Setting value or default
        """
        return self.settings.get(category, {}).get(key, default)
    
    def set_setting(self, category: str, key: str, value: Any) -> bool:
        """
        Set a specific setting value.
        
        Args:
            category: Settings category
            key: Setting key
            value: Value to set
            
        Returns:
            True if setting was saved successfully
        """
        if category not in self.settings:
            self.settings[category] = {}
        
        self.settings[category][key] = value
        return self.save_settings()
    
    def export_settings(self, file_path: str) -> bool:
        """
        Export settings to specified file.
        
        Args:
            file_path: Path to export settings to
            
        Returns:
            True if export was successful
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Failed to export settings: {e}")
            return False
    
    def import_settings(self, file_path: str) -> bool:
        """
        Import settings from specified file.
        
        Args:
            file_path: Path to import settings from
            
        Returns:
            True if import was successful
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_settings = json.load(f)
                self._merge_settings(imported_settings)
                return self.save_settings()
        except (json.JSONDecodeError, IOError) as e:
            print(f"Failed to import settings: {e}")
            return False