import contextlib
import tkinter as tk
from tkinter import ttk
from tkinter.simpledialog import Dialog
from typing import Optional, Callable

import sounddevice as sd

from HotkeySettingsWindow import HotkeySettingsWindow
from SettingsManager import SettingsManager
from UIConstants import UIConstants


class SettingsWindow(Dialog):
    """Enhanced settings window with tabbed interface for audio and hotkey settings."""
    
    def __init__(self, parent, settings_manager: Optional[SettingsManager] = None, 
                 on_hotkey_change: Optional[Callable] = None):
        """
        Initialize SettingsWindow.
        
        Args:
            parent: Parent window
            settings_manager: Settings manager instance
            on_hotkey_change: Callback for when hotkeys change
        """
        self.settings_manager = settings_manager
        self.on_hotkey_change = on_hotkey_change
        self.device_ids = []
        super().__init__(parent)
    
    def body(self, master):
        """Create the dialog body with tabbed interface."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Audio settings tab
        self.audio_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.audio_frame, text=UIConstants.SETTINGS_AUDIO_TAB)
        self._create_audio_tab()
        
        # Hotkey settings tab
        self.hotkey_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.hotkey_frame, text=UIConstants.SETTINGS_HOTKEY_TAB)
        self._create_hotkey_tab()
        
        return self.audio_frame  # Return initial focus widget
    
    def _create_audio_tab(self):
        """Create the audio device settings tab."""
        # Padding frame
        content_frame = ttk.Frame(self.audio_frame, padding="10")
        content_frame.pack(fill='both', expand=True)
        
        ttk.Label(content_frame, text='Select sound device:').pack(anchor='w', pady=(0, 5))
        
        self.hostapi_list = ttk.Combobox(content_frame, state='readonly', width=50)
        self.hostapi_list.pack(pady=(0, 10))
        self.hostapi_list['values'] = [
            hostapi['name'] for hostapi in sd.query_hostapis()]
        
        self.device_list = ttk.Combobox(content_frame, state='readonly', width=50)
        self.device_list.pack()

        self.hostapi_list.bind('<<ComboboxSelected>>', self.update_device_list)
        with contextlib.suppress(sd.PortAudioError):
            self.hostapi_list.current(sd.default.hostapi)
            self.hostapi_list.event_generate('<<ComboboxSelected>>')
    
    def _create_hotkey_tab(self):
        """Create the hotkey settings tab."""
        # Padding frame
        content_frame = ttk.Frame(self.hotkey_frame, padding="10")
        content_frame.pack(fill='both', expand=True)
        
        # Instructions
        ttk.Label(
            content_frame,
            text=UIConstants.SETTINGS_HOTKEY_INSTRUCTIONS,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor='w', pady=(0, 10))
        
        # Current hotkeys display
        if self.settings_manager:
            hotkeys = self.settings_manager.get_all_hotkeys()
            
            info_frame = ttk.LabelFrame(content_frame, text="Current Hotkeys", padding="10")
            info_frame.pack(fill='x', pady=(0, 15))
            
            # Toggle recording
            toggle_frame = ttk.Frame(info_frame)
            toggle_frame.pack(fill='x', pady=(0, 5))
            ttk.Label(toggle_frame, text="Toggle Recording:").pack(side='left')
            ttk.Label(
                toggle_frame, 
                text=hotkeys.get('toggle_recording', 'Not set'),
                font=("Consolas", 9)
            ).pack(side='right')
            
            # Stop recording
            stop_frame = ttk.Frame(info_frame)
            stop_frame.pack(fill='x')
            ttk.Label(stop_frame, text="Stop Recording:").pack(side='left')
            ttk.Label(
                stop_frame,
                text=hotkeys.get('stop_recording', 'Not set'),
                font=("Consolas", 9)
            ).pack(side='right')
        
        # Configure button
        ttk.Button(
            content_frame,
            text="Configure Hotkeys...",
            command=self._open_hotkey_settings
        ).pack(pady=(15, 0))
        
        # Note
        note_text = UIConstants.SETTINGS_HOTKEY_NOTE
        note_label = ttk.Label(
            content_frame,
            text=note_text,
            wraplength=400,
            justify='left',
            foreground='gray'
        )
        note_label.pack(pady=(15, 0))

    def update_device_list(self, *args):
        """Update the device list based on selected host API."""
        hostapi = sd.query_hostapis(self.hostapi_list.current())
        self.device_ids = [
            idx
            for idx in hostapi['devices']
            if sd.query_devices(idx)['max_input_channels'] > 0]
        self.device_list['values'] = [
            sd.query_devices(idx)['name'] for idx in self.device_ids]
        default = hostapi['default_input_device']
        if default >= 0:
            self.device_list.current(self.device_ids.index(default))

    def _open_hotkey_settings(self):
        """Open the dedicated hotkey settings window."""
        if not self.settings_manager:
            tk.messagebox.showerror(
                "Error",
                "Settings manager not available.",
                parent=self
            )
            return
        
        def on_hotkey_save(new_hotkeys):
            """Handle hotkey settings save."""
            # Refresh the hotkey display in this window
            self._refresh_hotkey_display()
            
            # Notify parent of changes
            if self.on_hotkey_change:
                self.on_hotkey_change(new_hotkeys)
        
        HotkeySettingsWindow(self, self.settings_manager, on_save=on_hotkey_save)
    
    def _refresh_hotkey_display(self):
        """Refresh the hotkey display in the tab."""
        # This would ideally refresh the display, but since we're using 
        # static labels, we'll just note that changes were made
        # In a more advanced implementation, we could rebuild the display
        pass

    def validate(self):
        """Validate settings and prepare result."""
        # Get selected audio device
        if hasattr(self, 'device_list') and self.device_ids:
            try:
                self.result = self.device_ids[self.device_list.current()]
                return True
            except (IndexError, tk.TclError):
                pass
        
        # No device selected or invalid selection
        self.result = None
        return True