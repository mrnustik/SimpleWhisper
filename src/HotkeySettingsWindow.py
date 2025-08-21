"""
Hotkey Settings Window for SimpleWhisper application.
Provides interface for configuring global hotkeys.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Callable, Optional
from pynput import keyboard
from pynput.keyboard import Key, KeyCode
import threading
import time

from GlobalHotkeyManager import HotkeyValidator
from SettingsManager import SettingsManager
from UIConstants import UIConstants


class HotkeyEntryWidget(ttk.Frame):
    """Widget for capturing and displaying hotkey combinations."""
    
    def __init__(self, parent, initial_hotkey: str = "", on_change: Optional[Callable] = None):
        """
        Initialize HotkeyEntryWidget.
        
        Args:
            parent: Parent widget
            initial_hotkey: Initial hotkey value
            on_change: Callback for when hotkey changes
        """
        super().__init__(parent)
        self.on_change = on_change
        self.current_hotkey = initial_hotkey
        self.is_capturing = False
        self.capture_listener: Optional[keyboard.Listener] = None
        self.pressed_keys = set()
        
        self._create_widgets()
        self._update_display()
    
    def _create_widgets(self):
        """Create the widget components."""
        # Hotkey display/entry field
        self.hotkey_var = tk.StringVar()
        self.hotkey_entry = ttk.Entry(
            self, 
            textvariable=self.hotkey_var,
            state='readonly',
            width=25
        )
        self.hotkey_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        # Capture button
        self.capture_button = ttk.Button(
            self,
            text=UIConstants.HOTKEY_CAPTURE_BUTTON,
            command=self._toggle_capture
        )
        self.capture_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Clear button
        self.clear_button = ttk.Button(
            self,
            text=UIConstants.HOTKEY_CLEAR_BUTTON,
            command=self._clear_hotkey
        )
        self.clear_button.pack(side=tk.LEFT)
    
    def _update_display(self):
        """Update the hotkey display."""
        display_text = self.current_hotkey if self.current_hotkey else UIConstants.HOTKEY_NONE_DISPLAY
        self.hotkey_var.set(display_text)
    
    def _toggle_capture(self):
        """Toggle hotkey capture mode."""
        if self.is_capturing:
            self._stop_capture()
        else:
            self._start_capture()
    
    def _start_capture(self):
        """Start capturing hotkey input."""
        self.is_capturing = True
        self.pressed_keys.clear()
        self.capture_button.config(text=UIConstants.HOTKEY_STOP_CAPTURE_BUTTON, state='normal')
        self.hotkey_var.set(UIConstants.HOTKEY_CAPTURE_PROMPT)
        
        # Start listening for key presses
        self.capture_listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release
        )
        self.capture_listener.start()
    
    def _stop_capture(self):
        """Stop capturing hotkey input."""
        self.is_capturing = False
        self.capture_button.config(text=UIConstants.HOTKEY_CAPTURE_BUTTON, state='normal')
        
        if self.capture_listener:
            self.capture_listener.stop()
            self.capture_listener = None
        
        self._update_display()
    
    def _on_key_press(self, key):
        """Handle key press during capture."""
        if not self.is_capturing:
            return
        
        # Cancel capture on ESC
        if key == Key.esc:
            self._stop_capture()
            return
        
        self.pressed_keys.add(key)
        self._update_capture_display()
    
    def _on_key_release(self, key):
        """Handle key release during capture."""
        if not self.is_capturing:
            return
        
        # If this was the last key released and we have a valid combination
        if len(self.pressed_keys) > 1:  # Require at least modifier + key
            hotkey_string = self._convert_keys_to_string(self.pressed_keys)
            if hotkey_string:
                self.current_hotkey = hotkey_string
                if self.on_change:
                    self.on_change(self.current_hotkey)
            self._stop_capture()
    
    def _update_capture_display(self):
        """Update display during capture to show current key combination."""
        if not self.pressed_keys:
            return
        
        display_keys = []
        for key in self.pressed_keys:
            if isinstance(key, Key):
                display_keys.append(key.name.capitalize())
            elif isinstance(key, KeyCode):
                if key.char:
                    display_keys.append(key.char.upper())
                else:
                    display_keys.append(f"Key({key.vk})")
        
        self.hotkey_var.set(" + ".join(sorted(display_keys)))
    
    def _convert_keys_to_string(self, keys) -> str:
        """
        Convert pressed keys to hotkey string format.
        
        Args:
            keys: Set of pressed keys
            
        Returns:
            Hotkey string in pynput format
        """
        modifiers = []
        regular_key = None
        
        for key in keys:
            if isinstance(key, Key):
                if key in [Key.ctrl, Key.ctrl_l, Key.ctrl_r]:
                    modifiers.append("ctrl")
                elif key in [Key.shift, Key.shift_l, Key.shift_r]:
                    modifiers.append("shift")
                elif key in [Key.alt, Key.alt_l, Key.alt_r]:
                    modifiers.append("alt")
                elif key in [Key.cmd, Key.cmd_l, Key.cmd_r]:
                    modifiers.append("cmd")
                else:
                    # Function keys and other special keys
                    regular_key = key.name.lower()
            elif isinstance(key, KeyCode):
                if key.char and key.char.isalnum():
                    regular_key = key.char.lower()
        
        # Must have at least one modifier and one regular key
        if not modifiers or not regular_key:
            return ""
        
        # Remove duplicates and sort
        modifiers = sorted(list(set(modifiers)))
        
        # Build hotkey string
        parts = [f"<{mod}>" for mod in modifiers]
        parts.append(regular_key)
        
        return "+".join(parts)
    
    def _clear_hotkey(self):
        """Clear the current hotkey."""
        self.current_hotkey = ""
        self._update_display()
        if self.on_change:
            self.on_change(self.current_hotkey)
    
    def set_hotkey(self, hotkey: str):
        """Set the hotkey value programmatically."""
        self.current_hotkey = hotkey
        self._update_display()
    
    def get_hotkey(self) -> str:
        """Get the current hotkey value."""
        return self.current_hotkey


class HotkeySettingsWindow(tk.Toplevel):
    """Window for configuring global hotkeys."""
    
    def __init__(self, parent, settings_manager: SettingsManager, on_save: Optional[Callable] = None):
        """
        Initialize HotkeySettingsWindow.
        
        Args:
            parent: Parent window
            settings_manager: Settings manager instance
            on_save: Callback for when settings are saved
        """
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.on_save = on_save
        self.hotkey_widgets: Dict[str, HotkeyEntryWidget] = {}
        self.pending_changes: Dict[str, str] = {}
        
        self._setup_window()
        self._create_widgets()
        self._load_current_settings()
    
    def _setup_window(self):
        """Configure window properties."""
        self.title(UIConstants.HOTKEY_SETTINGS_WINDOW_TITLE)
        self.geometry("450x300")
        self.resizable(False, False)
        self.transient(self.master)
        self.grab_set()
        
        # Center the window
        self.geometry("+%d+%d" % (
            self.master.winfo_rootx() + 50,
            self.master.winfo_rooty() + 50
        ))
    
    def _create_widgets(self):
        """Create the window widgets."""
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Configure Global Hotkeys",
            font=("Segoe UI", 12, "bold")
        )
        title_label.pack(pady=(0, 15))
        
        # Instructions
        instructions = ttk.Label(
            main_frame,
            text="Click 'Capture' and press your desired key combination.\n"
                 "Use Ctrl, Shift, Alt plus another key.",
            justify=tk.CENTER
        )
        instructions.pack(pady=(0, 20))
        
        # Hotkey settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Hotkey Assignments", padding="10")
        settings_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Toggle Recording hotkey
        toggle_frame = ttk.Frame(settings_frame)
        toggle_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(toggle_frame, text=UIConstants.HOTKEY_TOGGLE_RECORDING_LABEL, width=15).pack(side=tk.LEFT)
        self.hotkey_widgets["toggle_recording"] = HotkeyEntryWidget(
            toggle_frame,
            on_change=lambda hk: self._on_hotkey_change("toggle_recording", hk)
        )
        self.hotkey_widgets["toggle_recording"].pack(side=tk.RIGHT)
        
        # Stop Recording hotkey
        stop_frame = ttk.Frame(settings_frame)
        stop_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(stop_frame, text=UIConstants.HOTKEY_STOP_RECORDING_LABEL, width=15).pack(side=tk.LEFT)
        self.hotkey_widgets["stop_recording"] = HotkeyEntryWidget(
            stop_frame,
            on_change=lambda hk: self._on_hotkey_change("stop_recording", hk)
        )
        self.hotkey_widgets["stop_recording"].pack(side=tk.RIGHT)
        
        # Validation status
        self.status_label = ttk.Label(main_frame, text="", foreground="red")
        self.status_label.pack(pady=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(
            button_frame,
            text=UIConstants.HOTKEY_RESET_BUTTON,
            command=self._reset_to_defaults
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            button_frame,
            text=UIConstants.HOTKEY_CANCEL_BUTTON,
            command=self.destroy
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(
            button_frame,
            text=UIConstants.HOTKEY_SAVE_BUTTON,
            command=self._save_settings
        ).pack(side=tk.RIGHT, padx=(5, 0))
    
    def _load_current_settings(self):
        """Load current hotkey settings into widgets."""
        current_hotkeys = self.settings_manager.get_all_hotkeys()
        
        for action, widget in self.hotkey_widgets.items():
            hotkey = current_hotkeys.get(action, "")
            widget.set_hotkey(hotkey)
            self.pending_changes[action] = hotkey
    
    def _on_hotkey_change(self, action: str, hotkey: str):
        """Handle hotkey change in widget."""
        self.pending_changes[action] = hotkey
        self._validate_all_hotkeys()
    
    def _validate_all_hotkeys(self):
        """Validate all current hotkey combinations."""
        errors = []
        hotkeys_in_use = []
        
        for action, hotkey in self.pending_changes.items():
            if not hotkey:  # Empty hotkey is allowed
                continue
            
            # Validate individual hotkey
            is_valid, error_msg = HotkeyValidator.is_valid_hotkey(hotkey)
            if not is_valid:
                errors.append(f"{action.replace('_', ' ').title()}: {error_msg}")
                continue
            
            # Check for duplicates
            if hotkey in hotkeys_in_use:
                errors.append(f"Duplicate hotkey: {hotkey}")
            else:
                hotkeys_in_use.append(hotkey)
        
        # Update status
        if errors:
            self.status_label.config(text="; ".join(errors), foreground="red")
        else:
            self.status_label.config(text=UIConstants.HOTKEY_VALIDATION_SUCCESS, foreground="green")
        
        return len(errors) == 0
    
    def _reset_to_defaults(self):
        """Reset all hotkeys to default values."""
        if messagebox.askyesno(
            UIConstants.RESET_HOTKEYS_TITLE,
            UIConstants.RESET_HOTKEYS_MESSAGE,
            parent=self
        ):
            # Load defaults from UIConstants
            from UIConstants import UIConstants
            defaults = {
                "toggle_recording": UIConstants.GLOBAL_HOTKEY_TOGGLE_RECORDING,
                "stop_recording": UIConstants.GLOBAL_HOTKEY_STOP_RECORDING
            }
            
            for action, hotkey in defaults.items():
                if action in self.hotkey_widgets:
                    self.hotkey_widgets[action].set_hotkey(hotkey)
                    self.pending_changes[action] = hotkey
            
            self._validate_all_hotkeys()
    
    def _save_settings(self):
        """Save the current hotkey settings."""
        if not self._validate_all_hotkeys():
            messagebox.showerror(
                UIConstants.VALIDATION_INVALID_HOTKEYS_TITLE,
                UIConstants.VALIDATION_INVALID_HOTKEYS_MESSAGE,
                parent=self
            )
            return
        
        # Save hotkeys
        success = self.settings_manager.set_all_hotkeys(self.pending_changes)
        
        if success:
            messagebox.showinfo(
                UIConstants.SETTINGS_SAVED_TITLE,
                UIConstants.SETTINGS_SAVED_MESSAGE,
                parent=self
            )
            
            # Notify parent of changes
            if self.on_save:
                self.on_save(self.pending_changes)
            
            self.destroy()
        else:
            messagebox.showerror(
                UIConstants.SETTINGS_SAVE_FAILED_TITLE,
                UIConstants.SETTINGS_SAVE_FAILED_MESSAGE,
                parent=self
            )