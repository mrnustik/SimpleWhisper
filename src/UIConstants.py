"""
UI Constants for SimpleWhisper application.
Centralizes all UI-related constants for consistency and maintainability.
"""

class UIConstants:
    # Window settings
    WINDOW_TITLE = "Simple Whisper"
    MIN_WINDOW_WIDTH = 600
    MIN_WINDOW_HEIGHT = 400
    
    # Spacing and layout
    PADDING_SMALL = 5
    PADDING_MEDIUM = 10
    PADDING_LARGE = 15
    BUTTON_WIDTH = 120
    COMBOBOX_WIDTH = 200
    
    # Status messages
    STATUS_READY = "(Nothing said yet)"
    STATUS_RECORDING = "Recording... Click stop when done"
    STATUS_TRANSCRIBING = "Transcribing audio..."
    STATUS_MODEL_LOADING = "Loading model..."
    STATUS_TRANSCRIPTION_COMPLETE = "Text transcribed and copied to clipboard"
    
    # Button text
    BUTTON_RECORD = "Record"
    BUTTON_STOP = "Stop"
    BUTTON_SETTINGS = "Settings"
    BUTTON_SELECT_MODEL = "Select Model"
    
    # Labels
    LABEL_NO_MODEL = "No model selected"
    LABEL_MODEL_FAILED = "Model load failed"
    LABEL_DEVICE_PREFIX = "Used device: "
    
    # Dialog titles and messages
    DIALOG_NO_MODEL_TITLE = "No Model Selected"
    DIALOG_NO_MODEL_MESSAGE = "Please select a model from the dropdown."
    DIALOG_WHISPER_ERROR_TITLE = "Whisper Error"
    DIALOG_AUDIO_ERROR_TITLE = "Audio Error"
    DIALOG_NO_MODEL_FOR_RECORDING = "Please load a model before recording."
    
    # Keyboard shortcuts
    SHORTCUT_RECORD = "<Control-r>"
    SHORTCUT_STOP = "<Control-s>"
    SHORTCUT_SETTINGS = "<Control-t>"
    
    # Colors (for future theming)
    COLOR_RECORDING = "#ff4444"
    COLOR_SUCCESS = "#44aa44" 
    COLOR_WARNING = "#ffaa44"
    COLOR_ERROR = "#aa4444"
    
    # Fonts
    FONT_STATUS = ("Segoe UI", 9)
    FONT_BUTTON = ("Segoe UI", 9)
    FONT_LABEL = ("Segoe UI", 8)