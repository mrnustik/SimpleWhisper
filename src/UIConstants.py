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
    
    # Keyboard shortcuts (local - when app has focus)
    SHORTCUT_RECORD = "<Control-r>"
    SHORTCUT_STOP = "<Control-s>"
    SHORTCUT_SETTINGS = "<Control-t>"
    
    # Global hotkeys (system-wide - work when app is not in focus)
    GLOBAL_HOTKEY_TOGGLE_RECORDING = "<ctrl>+<shift>+r"
    GLOBAL_HOTKEY_STOP_RECORDING = "<ctrl>+<shift>+s"
    
    # Hotkey related messages
    HOTKEY_ENABLED_STATUS = "Global hotkeys enabled"
    HOTKEY_DISABLED_STATUS = "Global hotkeys disabled"
    HOTKEY_ERROR_MESSAGE = "Failed to register global hotkeys"
    HOTKEY_CONFLICT_MESSAGE = "Hotkey conflict detected"
    
    # Settings related constants
    SETTINGS_FILE_NAME = "settings.json"
    SETTINGS_WINDOW_TITLE = "Settings"
    HOTKEY_SETTINGS_WINDOW_TITLE = "Global Hotkey Settings"
    
    # Settings dialog messages
    SETTINGS_AUDIO_TAB = "Audio Device"
    SETTINGS_HOTKEY_TAB = "Global Hotkeys"
    SETTINGS_HOTKEY_INSTRUCTIONS = "Configure global hotkeys that work system-wide:"
    SETTINGS_HOTKEY_NOTE = ("Note: Global hotkeys work even when the application is not in focus. "
                           "Make sure to choose combinations that don't conflict with other applications.")
    
    # Hotkey configuration messages
    HOTKEY_CAPTURE_BUTTON = "Capture"
    HOTKEY_STOP_CAPTURE_BUTTON = "Stop"
    HOTKEY_CLEAR_BUTTON = "Clear"
    HOTKEY_RESET_BUTTON = "Reset to Defaults"
    HOTKEY_SAVE_BUTTON = "Save"
    HOTKEY_CANCEL_BUTTON = "Cancel"
    
    HOTKEY_CAPTURE_PROMPT = "Press keys... (ESC to cancel)"
    HOTKEY_NONE_DISPLAY = "None"
    HOTKEY_VALIDATION_SUCCESS = "All hotkeys valid"
    
    # Hotkey action labels
    HOTKEY_TOGGLE_RECORDING_LABEL = "Toggle Recording:"
    HOTKEY_STOP_RECORDING_LABEL = "Stop Recording:"
    
    # Settings save/load messages
    SETTINGS_SAVED_TITLE = "Settings Saved"
    SETTINGS_SAVED_MESSAGE = "Hotkey settings have been saved successfully."
    SETTINGS_SAVE_FAILED_TITLE = "Save Failed"
    SETTINGS_SAVE_FAILED_MESSAGE = "Failed to save hotkey settings. Please try again."
    SETTINGS_LOAD_FAILED_MESSAGE = "Failed to load settings from file."
    
    # Validation messages
    VALIDATION_INVALID_HOTKEYS_TITLE = "Invalid Hotkeys"
    VALIDATION_INVALID_HOTKEYS_MESSAGE = "Please fix the validation errors before saving."
    VALIDATION_DUPLICATE_HOTKEY = "Duplicate hotkey: {}"
    VALIDATION_EMPTY_HOTKEY = "Hotkey cannot be empty"
    VALIDATION_RESERVED_HOTKEY = "Hotkey {} is reserved by the system"
    
    # Reset confirmation
    RESET_HOTKEYS_TITLE = "Reset to Defaults"
    RESET_HOTKEYS_MESSAGE = "Reset all hotkeys to default values?"
    
    # File cleanup messages
    FILE_CLEANUP_SUCCESS = "Temporary audio file cleaned up"
    FILE_CLEANUP_ERROR = "Failed to cleanup temporary file"
    TRANSCRIPTION_FAILED_CLEANUP = "Transcription failed, but temporary file was cleaned up."
    
    # Colors (for future theming)
    COLOR_RECORDING = "#ff4444"
    COLOR_SUCCESS = "#44aa44" 
    COLOR_WARNING = "#ffaa44"
    COLOR_ERROR = "#aa4444"
    
    # Fonts
    FONT_STATUS = ("Segoe UI", 9)
    FONT_BUTTON = ("Segoe UI", 9)
    FONT_LABEL = ("Segoe UI", 8)