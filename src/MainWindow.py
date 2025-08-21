import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

import pyperclip

from SettingsWindow import SettingsWindow
from WhisperManager import WhisperManager
from AudioManager import AudioManager


class MainWindow(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title('Simple Whisper')
        
        # Initialize WhisperManager with callbacks
        self.whisper_manager = WhisperManager(
            on_model_loaded=self.on_model_loaded,
            on_transcription_complete=self.on_transcription_complete,
            on_error=self.on_whisper_error
        )
        
        # Initialize AudioManager with callbacks
        self.audio_manager = AudioManager(
            on_recording_started=self.on_recording_started,
            on_recording_stopped=self.on_recording_stopped,
            on_file_ready=self.on_file_ready,
            on_error=self.on_audio_error,
            root=self
        )

        padding = 10

        f = ttk.Frame()

        self.record_button = ttk.Button(f)
        self.record_button.pack(side='left', padx=padding, pady=padding)

        self.settings_button = ttk.Button(
            f, text='settings', command=self.on_settings)
        self.settings_button.pack(side='left', padx=padding, pady=padding)

        f.pack(expand=True, padx=padding, pady=padding)

        self.translated_text = tk.Label(text="(Nothing said yet)")
        self.translated_text.pack(fill='x')

        self.cuda_label = tk.Label(text=f"Used device: {self.whisper_manager.get_device()}")
        self.cuda_label.pack(side='left', padx=padding, pady=padding)

        self.model_label = tk.Label(text="No model")
        self.model_label.pack(side='right', padx=padding, pady=padding)

        self.model_combobox = ttk.Combobox()
        self.model_combobox['values'] = self.whisper_manager.get_available_models()
        self.model_combobox.pack(side='left', padx=padding, pady=padding)

        self.model_select = ttk.Button(text="Select model", command=self.on_select_model)
        self.model_select.pack(side='right', padx=padding, pady=padding)

        self.protocol('WM_DELETE_WINDOW', self.close_window)
        self.init_buttons()

    def on_select_model(self):
        model_name = self.model_combobox.get()
        if model_name:
            self.model_label['text'] = f"Loading model {model_name}..."
            self.model_select['state'] = 'disabled'
            self.whisper_manager.load_model_async(model_name)
        else:
            messagebox.showwarning("No Model Selected", "Please select a model from the dropdown.")

    def on_model_loaded(self, model_name: str):
        """Callback when model is successfully loaded."""
        self.model_label['text'] = f"Selected model {model_name}"
        self.model_select['state'] = 'normal'
        self.init_buttons()

    def on_transcription_complete(self, transcribed_text: str):
        """Callback when transcription is complete."""
        pyperclip.copy(transcribed_text)
        self.translated_text.configure(text=transcribed_text)

    def on_whisper_error(self, error_message: str):
        """Callback when WhisperManager encounters an error."""
        messagebox.showerror("Whisper Error", error_message)
        self.model_label['text'] = "Model load failed"
        self.model_select['state'] = 'normal'
        self.init_buttons()

    def on_recording_started(self):
        """Callback when AudioManager starts recording."""
        self.record_button['text'] = 'stop'
        self.record_button['command'] = self.on_stop
        self.record_button['state'] = 'normal'
        self.settings_button['state'] = 'disabled'

    def on_recording_stopped(self):
        """Callback when AudioManager stops recording."""
        self.record_button['state'] = 'disabled'

    def on_file_ready(self, filename: str):
        """Callback when AudioManager has audio file ready for transcription."""
        self.init_buttons()
        if self.whisper_manager.is_model_loaded():
            self.translated_text.configure(text="Transcribing...")
            self.whisper_manager.transcribe_async(filename)
        else:
            messagebox.showwarning("No Model", "Please load a model before recording.")

    def on_audio_error(self, error_message: str):
        """Callback when AudioManager encounters an error."""
        messagebox.showerror("Audio Error", error_message)
        self.init_buttons()

    def on_rec(self):
        """Start recording using AudioManager."""
        self.audio_manager.start_recording()

    def on_stop(self, *args):
        """Stop recording using AudioManager."""
        self.audio_manager.stop_recording()

    def on_settings(self, *args):
        """Open settings dialog and update audio device."""
        w = SettingsWindow(self, 'Settings')
        if w.result is not None:
            self.audio_manager.set_device(device_id=w.result)

    def init_buttons(self):
        """Initialize button states based on system readiness."""
        self.record_button['text'] = 'record'
        self.record_button['command'] = self.on_rec
        if self.audio_manager.is_ready() and self.whisper_manager.is_model_loaded():
            self.record_button['state'] = 'normal'
        else:
            self.record_button['state'] = 'disabled'
        self.settings_button['state'] = 'normal'

    def close_window(self):
        """Clean shutdown of the application."""
        self.audio_manager.cleanup()
        self.destroy()