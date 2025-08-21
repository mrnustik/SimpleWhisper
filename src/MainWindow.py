import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

import pyperclip

from SettingsWindow import SettingsWindow
from WhisperManager import WhisperManager
from AudioManager import AudioManager
from UIConstants import UIConstants
from UIStateManager import UIStateManager, AppState


class MainWindow(tk.Tk):

    def __init__(self):
        super().__init__()
        
        # Initialize state manager
        self.state_manager = UIStateManager(ui_update_callback=self._on_state_changed)
        
        # Configure main window
        self._setup_window()
        
        # Initialize managers
        self._initialize_managers()
        
        # Create UI components
        self._create_ui()
        
        # Set up keyboard shortcuts
        self._setup_keyboard_shortcuts()
        
        # Set initial state
        self._determine_initial_state()

    def _setup_window(self):
        """Configure main window properties."""
        self.title(UIConstants.WINDOW_TITLE)
        self.minsize(UIConstants.MIN_WINDOW_WIDTH, UIConstants.MIN_WINDOW_HEIGHT)
        self.protocol('WM_DELETE_WINDOW', self.close_window)
        
        # Configure grid weights for proper resizing
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # Status area should expand

    def _initialize_managers(self):
        """Initialize WhisperManager and AudioManager with callbacks."""
        self.whisper_manager = WhisperManager(
            on_model_loaded=self.on_model_loaded,
            on_transcription_complete=self.on_transcription_complete,
            on_error=self.on_whisper_error
        )
        
        self.audio_manager = AudioManager(
            on_recording_started=self.on_recording_started,
            on_recording_stopped=self.on_recording_stopped,
            on_file_ready=self.on_file_ready,
            on_error=self.on_audio_error,
            root=self
        )

    def _create_ui(self):
        """Create and layout all UI components."""
        self._create_control_frame()
        self._create_model_frame() 
        self._create_status_frame()
        self._create_info_frame()

    def _create_control_frame(self):
        """Create the main control buttons frame."""
        self.control_frame = ttk.LabelFrame(self, text="Recording Controls", padding=UIConstants.PADDING_MEDIUM)
        self.control_frame.grid(row=0, column=0, sticky="ew", padx=UIConstants.PADDING_MEDIUM, pady=UIConstants.PADDING_SMALL)
        
        # Configure grid
        self.control_frame.grid_columnconfigure(1, weight=1)
        
        self.record_button = ttk.Button(
            self.control_frame,
            text=UIConstants.BUTTON_RECORD,
            width=UIConstants.BUTTON_WIDTH // 8,
            command=self.on_record_button_clicked
        )
        self.record_button.grid(row=0, column=0, padx=(0, UIConstants.PADDING_MEDIUM))
        
        self.settings_button = ttk.Button(
            self.control_frame,
            text=UIConstants.BUTTON_SETTINGS,
            command=self.on_settings
        )
        self.settings_button.grid(row=0, column=2, padx=(UIConstants.PADDING_MEDIUM, 0))

    def _create_model_frame(self):
        """Create the model selection frame."""
        self.model_frame = ttk.LabelFrame(self, text="Whisper Model", padding=UIConstants.PADDING_MEDIUM)
        self.model_frame.grid(row=1, column=0, sticky="ew", padx=UIConstants.PADDING_MEDIUM, pady=UIConstants.PADDING_SMALL)
        
        # Configure grid
        self.model_frame.grid_columnconfigure(0, weight=1)
        
        self.model_combobox = ttk.Combobox(
            self.model_frame,
            values=self.whisper_manager.get_available_models(),
            state='readonly',
            width=UIConstants.COMBOBOX_WIDTH // 8
        )
        self.model_combobox.grid(row=0, column=0, sticky="ew", padx=(0, UIConstants.PADDING_MEDIUM))
        
        self.model_select_button = ttk.Button(
            self.model_frame,
            text=UIConstants.BUTTON_SELECT_MODEL,
            command=self.on_select_model
        )
        self.model_select_button.grid(row=0, column=1)
        
        self.model_status_label = ttk.Label(
            self.model_frame,
            text=UIConstants.LABEL_NO_MODEL,
            font=UIConstants.FONT_LABEL
        )
        self.model_status_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(UIConstants.PADDING_SMALL, 0))
        
        # Progress bar for model loading and transcription
        self.progress_bar = ttk.Progressbar(
            self.model_frame,
            mode='indeterminate'
        )
        self.progress_bar.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(UIConstants.PADDING_SMALL, 0))
        self.progress_bar.grid_remove()  # Hide initially

    def _create_status_frame(self):
        """Create the status display frame."""
        self.status_frame = ttk.LabelFrame(self, text="Status", padding=UIConstants.PADDING_MEDIUM)
        self.status_frame.grid(row=2, column=0, sticky="nsew", padx=UIConstants.PADDING_MEDIUM, pady=UIConstants.PADDING_SMALL)
        
        # Configure grid for expansion
        self.status_frame.grid_columnconfigure(0, weight=1)
        self.status_frame.grid_rowconfigure(0, weight=1)
        
        # Create scrollable text area for transcribed text
        self.status_text = tk.Text(
            self.status_frame,
            height=6,
            wrap=tk.WORD,
            font=UIConstants.FONT_STATUS
        )
        scrollbar = ttk.Scrollbar(self.status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        self.status_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Insert initial status message
        self.status_text.insert(tk.END, UIConstants.STATUS_READY)
        self.status_text.config(state=tk.DISABLED)

    def _create_info_frame(self):
        """Create the information display frame."""
        self.info_frame = ttk.Frame(self, padding=UIConstants.PADDING_SMALL)
        self.info_frame.grid(row=3, column=0, sticky="ew", padx=UIConstants.PADDING_MEDIUM, pady=(0, UIConstants.PADDING_MEDIUM))
        
        # Configure grid
        self.info_frame.grid_columnconfigure(1, weight=1)
        
        self.device_label = ttk.Label(
            self.info_frame,
            text=f"{UIConstants.LABEL_DEVICE_PREFIX}{self.whisper_manager.get_device()}",
            font=UIConstants.FONT_LABEL
        )
        self.device_label.grid(row=0, column=0, sticky="w")

    def _setup_keyboard_shortcuts(self):
        """Set up keyboard shortcuts."""
        self.bind_all(UIConstants.SHORTCUT_RECORD, self._on_record_shortcut)
        self.bind_all(UIConstants.SHORTCUT_STOP, self._on_stop_shortcut)
        self.bind_all(UIConstants.SHORTCUT_SETTINGS, lambda e: self.on_settings())

    def _determine_initial_state(self):
        """Determine and set the initial application state."""
        if not self.audio_manager.is_ready():
            self.state_manager.set_state(AppState.NO_AUDIO)
        else:
            self.state_manager.set_state(AppState.NO_MODEL)

    def _on_state_changed(self, new_state: AppState):
        """Called when application state changes. Updates UI accordingly."""
        # Update button states
        button_states = self.state_manager.get_button_states()
        
        self.record_button.configure(
            text=button_states['record_text'],
            state='normal' if button_states['record_enabled'] else 'disabled'
        )
        
        self.settings_button.configure(
            state='normal' if button_states['settings_enabled'] else 'disabled'
        )
        
        self.model_select_button.configure(
            state='normal' if button_states['model_select_enabled'] else 'disabled'
        )
        
        # Update progress bar visibility
        if new_state in [AppState.MODEL_LOADING, AppState.PROCESSING]:
            self.progress_bar.grid()
            self.progress_bar.start(10)  # Start animation
        else:
            self.progress_bar.stop()
            self.progress_bar.grid_remove()
        
        # Update status display
        self._update_status_display(self.state_manager.status_message)

    def _update_status_display(self, message: str):
        """Update the status text display."""
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete('1.0', tk.END)
        self.status_text.insert(tk.END, message)
        self.status_text.config(state=tk.DISABLED)
        self.status_text.see(tk.END)

    def _on_record_shortcut(self, event):
        """Handle record keyboard shortcut."""
        if self.state_manager.current_state == AppState.READY:
            self.on_record_button_clicked()
        elif self.state_manager.current_state == AppState.RECORDING:
            self.on_record_button_clicked()

    def _on_stop_shortcut(self, event):
        """Handle stop keyboard shortcut."""
        if self.state_manager.current_state == AppState.RECORDING:
            self.on_record_button_clicked()

    def on_record_button_clicked(self):
        """Handle record button click - either start or stop recording."""
        if self.state_manager.current_state == AppState.READY:
            self.audio_manager.start_recording()
        elif self.state_manager.current_state == AppState.RECORDING:
            self.audio_manager.stop_recording()

    def on_select_model(self):
        """Handle model selection."""
        if not self.state_manager.can_change_model():
            return
            
        model_name = self.model_combobox.get()
        if model_name:
            self.state_manager.set_state(AppState.MODEL_LOADING)
            self.state_manager.set_model_info(model_name)
            self.model_status_label.configure(text=f"Loading {model_name}...")
            self.whisper_manager.load_model_async(model_name)
        else:
            messagebox.showwarning(
                UIConstants.DIALOG_NO_MODEL_TITLE,
                UIConstants.DIALOG_NO_MODEL_MESSAGE
            )

    def on_model_loaded(self, model_name: str):
        """Callback when model is successfully loaded."""
        self.state_manager.set_model_info(model_name)
        self.model_status_label.configure(text=f"Model {model_name} loaded successfully")
        
        # Determine new state based on system readiness
        if self.audio_manager.is_ready():
            self.state_manager.set_state(AppState.READY)
        else:
            self.state_manager.set_state(AppState.NO_AUDIO)

    def on_transcription_complete(self, transcribed_text: str):
        """Callback when transcription is complete."""
        pyperclip.copy(transcribed_text)
        
        # Update status with transcription result
        status_message = f"{UIConstants.STATUS_TRANSCRIPTION_COMPLETE}\n\n{transcribed_text}"
        self.state_manager.set_state(AppState.READY, status_message)

    def on_whisper_error(self, error_message: str):
        """Callback when WhisperManager encounters an error."""
        messagebox.showerror(UIConstants.DIALOG_WHISPER_ERROR_TITLE, error_message)
        self.model_status_label.configure(text=UIConstants.LABEL_MODEL_FAILED)
        self.state_manager.set_state(AppState.ERROR, f"Whisper error: {error_message}")

    def on_recording_started(self):
        """Callback when AudioManager starts recording."""
        self.state_manager.set_state(AppState.RECORDING)

    def on_recording_stopped(self):
        """Callback when AudioManager stops recording."""
        self.state_manager.set_state(AppState.PROCESSING)

    def on_file_ready(self, filename: str):
        """Callback when AudioManager has audio file ready for transcription."""
        if self.whisper_manager.is_model_loaded():
            self.whisper_manager.transcribe_async(filename)
        else:
            messagebox.showwarning("No Model", UIConstants.DIALOG_NO_MODEL_FOR_RECORDING)
            self.state_manager.set_state(AppState.NO_MODEL)

    def on_audio_error(self, error_message: str):
        """Callback when AudioManager encounters an error."""
        messagebox.showerror(UIConstants.DIALOG_AUDIO_ERROR_TITLE, error_message)
        self.state_manager.set_state(AppState.ERROR, f"Audio error: {error_message}")

    def on_settings(self, *args):
        """Open settings dialog and update audio device."""
        if not self.state_manager.can_change_settings():
            return
            
        try:
            settings_window = SettingsWindow(self, 'Settings')
            if settings_window.result is not None:
                self.audio_manager.set_device(device_id=settings_window.result)
        except Exception as e:
            messagebox.showerror("Settings Error", f"Failed to open settings: {str(e)}")

    def close_window(self):
        """Clean shutdown of the application."""
        self.audio_manager.cleanup()
        self.destroy()