"""
Global Hotkey Manager for SimpleWhisper application.
Handles system-wide hotkey registration and management.
"""

import threading
import tkinter as tk
from typing import Callable, Optional, Dict, Any
from pynput import keyboard
from pynput.keyboard import Key, KeyCode


class GlobalHotkeyManager:
    """Manages global hotkeys that work system-wide, even when app is not in focus."""
    
    def __init__(self, root: Optional[tk.Tk] = None):
        """
        Initialize GlobalHotkeyManager.
        
        Args:
            root: Tkinter root for scheduling callbacks on main thread
        """
        self.root = root
        self.listener: Optional[keyboard.GlobalHotKeys] = None
        self.hotkeys: Dict[str, Callable] = {}
        self.is_active = False
        
        # Default hotkey combinations
        self.default_hotkeys = {
            'toggle_recording': '<ctrl>+<shift>+r',
            'stop_recording': '<ctrl>+<shift>+s'
        }
        
    def _schedule_callback(self, callback: Callable, *args):
        """Schedule a callback to run on the main thread."""
        if callback and self.root:
            self.root.after(0, lambda: callback(*args))
        elif callback:
            # Fallback if no root provided
            callback(*args)
    
    def _parse_hotkey(self, hotkey_string: str) -> str:
        """
        Parse hotkey string into pynput format.
        
        Args:
            hotkey_string: Hotkey in format like '<ctrl>+<shift>+r'
            
        Returns:
            Parsed hotkey string for pynput
        """
        # Convert from our format to pynput format
        # '<ctrl>+<shift>+r' -> '<ctrl>+<shift>+r'
        return hotkey_string.lower()
    
    def register_hotkey(self, name: str, hotkey_string: str, callback: Callable):
        """
        Register a global hotkey.
        
        Args:
            name: Unique name for this hotkey
            hotkey_string: Hotkey combination (e.g., '<ctrl>+<shift>+r')
            callback: Function to call when hotkey is pressed
        """
        parsed_hotkey = self._parse_hotkey(hotkey_string)
        
        # Wrap callback to ensure it runs on main thread
        def wrapped_callback():
            self._schedule_callback(callback)
        
        self.hotkeys[parsed_hotkey] = wrapped_callback
        
        # If listener is active, restart it to include new hotkey
        if self.is_active:
            self._restart_listener()
    
    def unregister_hotkey(self, hotkey_string: str):
        """
        Unregister a global hotkey.
        
        Args:
            hotkey_string: Hotkey combination to remove
        """
        parsed_hotkey = self._parse_hotkey(hotkey_string)
        
        if parsed_hotkey in self.hotkeys:
            del self.hotkeys[parsed_hotkey]
            
            # If listener is active, restart it to exclude removed hotkey
            if self.is_active:
                self._restart_listener()
    
    def start_listening(self):
        """Start listening for global hotkeys."""
        if self.is_active or not self.hotkeys:
            return
            
        try:
            self.listener = keyboard.GlobalHotKeys(self.hotkeys)
            self.listener.start()
            self.is_active = True
            
        except Exception as e:
            print(f"Failed to start global hotkey listener: {e}")
            self.is_active = False
    
    def stop_listening(self):
        """Stop listening for global hotkeys."""
        if not self.is_active or not self.listener:
            return
            
        try:
            self.listener.stop()
            self.listener = None
            self.is_active = False
            
        except Exception as e:
            print(f"Failed to stop global hotkey listener: {e}")
    
    def _restart_listener(self):
        """Restart the hotkey listener with current hotkeys."""
        self.stop_listening()
        if self.hotkeys:  # Only restart if there are hotkeys to listen for
            self.start_listening()
    
    def is_listening(self) -> bool:
        """Check if currently listening for hotkeys."""
        return self.is_active
    
    def get_registered_hotkeys(self) -> Dict[str, str]:
        """Get list of currently registered hotkeys."""
        return {hotkey: "registered" for hotkey in self.hotkeys.keys()}
    
    def register_default_hotkeys(self, toggle_callback: Callable, stop_callback: Callable):
        """
        Register default hotkeys for recording control.
        
        Args:
            toggle_callback: Callback for toggle recording hotkey
            stop_callback: Callback for stop recording hotkey
        """
        self.register_hotkey(
            'toggle_recording',
            self.default_hotkeys['toggle_recording'],
            toggle_callback
        )
        self.register_hotkey(
            'stop_recording', 
            self.default_hotkeys['stop_recording'],
            stop_callback
        )
    
    def cleanup(self):
        """Clean up hotkey listener resources."""
        self.stop_listening()
        self.hotkeys.clear()
    
    def __del__(self):
        """Ensure cleanup on object destruction."""
        self.cleanup()


class HotkeyValidator:
    """Utility class for validating hotkey combinations."""
    
    VALID_MODIFIERS = {'ctrl', 'shift', 'alt', 'cmd', 'win'}
    RESERVED_COMBINATIONS = {
        '<ctrl>+c',  # Copy
        '<ctrl>+v',  # Paste
        '<ctrl>+x',  # Cut
        '<ctrl>+z',  # Undo
        '<ctrl>+y',  # Redo
        '<alt>+<f4>',  # Close window
        '<ctrl>+<alt>+<del>',  # Task manager
    }
    
    @classmethod
    def is_valid_hotkey(cls, hotkey_string: str) -> tuple[bool, str]:
        """
        Validate a hotkey string.
        
        Args:
            hotkey_string: Hotkey to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not hotkey_string:
            return False, "Hotkey cannot be empty"
        
        # Check for reserved combinations
        if hotkey_string.lower() in cls.RESERVED_COMBINATIONS:
            return False, f"Hotkey {hotkey_string} is reserved by the system"
        
        # Basic format validation
        if not hotkey_string.startswith('<') or not hotkey_string.endswith('>'):
            # Allow simple key format
            if '+' not in hotkey_string:
                return True, ""
        
        # More detailed validation could be added here
        return True, ""
    
    @classmethod
    def suggest_alternatives(cls, invalid_hotkey: str) -> list[str]:
        """
        Suggest alternative hotkeys if the provided one is invalid.
        
        Args:
            invalid_hotkey: The invalid hotkey string
            
        Returns:
            List of suggested alternatives
        """
        suggestions = [
            '<ctrl>+<shift>+r',
            '<ctrl>+<alt>+r', 
            '<shift>+<f1>',
            '<shift>+<f2>',
            '<ctrl>+<shift>+space'
        ]
        
        # Filter out the invalid hotkey if it's in suggestions
        return [s for s in suggestions if s != invalid_hotkey.lower()]