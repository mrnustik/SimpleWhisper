import contextlib
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
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
        
        # Whisper settings tab
        self.whisper_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.whisper_frame, text=UIConstants.SETTINGS_WHISPER_TAB)
        self._create_whisper_tab()
        
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
    
    def _create_whisper_tab(self):
        """Create the Whisper model settings tab."""
        # Padding frame
        content_frame = ttk.Frame(self.whisper_frame, padding="10")
        content_frame.pack(fill='both', expand=True)
        
        # Instructions
        ttk.Label(
            content_frame,
            text=UIConstants.SETTINGS_WHISPER_INSTRUCTIONS,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor='w', pady=(0, 10))
        
        # Model download path setting
        path_frame = ttk.LabelFrame(content_frame, text="Model Storage Location", padding="10")
        path_frame.pack(fill='x', pady=(0, 15))
        
        # Current path display
        current_path_frame = ttk.Frame(path_frame)
        current_path_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(current_path_frame, text="Current path:").pack(anchor='w')
        
        # Get current path from settings
        current_path = ""
        if self.settings_manager:
            stored_path = self.settings_manager.get_model_download_path()
            current_path = stored_path if stored_path else "Default (~/.cache/whisper)"
        
        self.path_display = ttk.Label(
            current_path_frame, 
            text=current_path,
            font=("Consolas", 9),
            foreground="gray"
        )
        self.path_display.pack(anchor='w', pady=(5, 0))
        
        # Path input frame
        input_frame = ttk.Frame(path_frame)
        input_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Label(input_frame, text="New path (leave blank for default):").pack(anchor='w')
        
        # Path entry and browse button
        path_entry_frame = ttk.Frame(input_frame)
        path_entry_frame.pack(fill='x', pady=(5, 0))
        
        self.path_entry = ttk.Entry(path_entry_frame)
        self.path_entry.pack(side='left', fill='x', expand=True)
        
        ttk.Button(
            path_entry_frame,
            text="Browse...",
            command=self._browse_model_path
        ).pack(side='right', padx=(5, 0))
        
        # Set and Reset buttons
        button_frame = ttk.Frame(path_frame)
        button_frame.pack(fill='x', pady=(15, 0))
        
        ttk.Button(
            button_frame,
            text="Set Path",
            command=self._set_model_path
        ).pack(side='left', padx=(0, 5))
        
        ttk.Button(
            button_frame,
            text="Reset to Default",
            command=self._reset_model_path
        ).pack(side='left')
        
        # Note
        note_label = ttk.Label(
            content_frame,
            text=UIConstants.SETTINGS_WHISPER_NOTE,
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
    
    def _browse_model_path(self):
        """Open directory browser for selecting model storage path."""
        initial_dir = os.path.expanduser("~")
        if self.settings_manager:
            current_path = self.settings_manager.get_model_download_path()
            if current_path and os.path.exists(current_path):
                initial_dir = current_path
        
        selected_dir = filedialog.askdirectory(
            parent=self,
            title="Select Whisper Model Storage Directory",
            initialdir=initial_dir
        )
        
        if selected_dir:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, selected_dir)
    
    def _set_model_path(self):
        """Set the model download path from the entry field."""
        if not self.settings_manager:
            messagebox.showerror(
                "Error",
                "Settings manager not available.",
                parent=self
            )
            return
        
        new_path = self.path_entry.get().strip()
        
        # Validate path if provided
        if new_path:
            if not os.path.exists(new_path):
                create = messagebox.askyesno(
                    "Directory Not Found",
                    f"Directory '{new_path}' does not exist. Create it?",
                    parent=self
                )
                if create:
                    try:
                        os.makedirs(new_path, exist_ok=True)
                    except OSError as e:
                        messagebox.showerror(
                            "Error",
                            f"Failed to create directory: {e}",
                            parent=self
                        )
                        return
                else:
                    return
            
            if not os.path.isdir(new_path):
                messagebox.showerror(
                    "Error",
                    "Selected path is not a directory.",
                    parent=self
                )
                return
        
        # Set the path (None if empty string)
        path_to_set = new_path if new_path else None
        if self.settings_manager.set_model_download_path(path_to_set):
            # Update display
            display_text = new_path if new_path else "Default (~/.cache/whisper)"
            self.path_display.config(text=display_text)
            
            # Clear entry
            self.path_entry.delete(0, tk.END)
            
            messagebox.showinfo(
                "Success",
                "Model download path updated successfully.\n\n" +
                "Note: This setting will take effect when loading new models.",
                parent=self
            )
        else:
            messagebox.showerror(
                "Error",
                "Failed to save model download path.",
                parent=self
            )
    
    def _reset_model_path(self):
        """Reset model download path to default."""
        if not self.settings_manager:
            messagebox.showerror(
                "Error",
                "Settings manager not available.",
                parent=self
            )
            return
        
        confirm = messagebox.askyesno(
            "Reset to Default",
            "Reset model download path to default location?",
            parent=self
        )
        
        if confirm:
            if self.settings_manager.set_model_download_path(None):
                self.path_display.config(text="Default (~/.cache/whisper)")
                self.path_entry.delete(0, tk.END)
                
                messagebox.showinfo(
                    "Success",
                    "Model download path reset to default.",
                    parent=self
                )
            else:
                messagebox.showerror(
                    "Error",
                    "Failed to reset model download path.",
                    parent=self
                )

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