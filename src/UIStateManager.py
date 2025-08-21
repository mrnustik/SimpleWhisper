"""
UI State Manager for SimpleWhisper application.
Manages application state and coordinates UI updates.
"""

from enum import Enum
from typing import Callable, Optional
from UIConstants import UIConstants


class AppState(Enum):
    """Application states that drive UI behavior."""
    INITIALIZING = "initializing"
    READY = "ready"  # Ready to record, model loaded, audio ready
    MODEL_LOADING = "model_loading"
    RECORDING = "recording"
    PROCESSING = "processing"  # Transcribing
    ERROR = "error"
    NO_MODEL = "no_model"  # No model selected/loaded
    NO_AUDIO = "no_audio"  # Audio system not ready


class UIStateManager:
    """Manages application state and coordinates UI updates."""
    
    def __init__(self, ui_update_callback: Optional[Callable[['AppState'], None]] = None):
        self._current_state = AppState.INITIALIZING
        self._ui_update_callback = ui_update_callback
        self._status_message = UIConstants.STATUS_READY
        self._model_name = None
        self._device_name = None
        
    @property
    def current_state(self) -> AppState:
        """Get the current application state."""
        return self._current_state
    
    @property
    def status_message(self) -> str:
        """Get the current status message."""
        return self._status_message
        
    @property
    def model_name(self) -> Optional[str]:
        """Get the currently selected model name."""
        return self._model_name
        
    @property
    def device_name(self) -> Optional[str]:
        """Get the current audio device name."""
        return self._device_name
    
    def set_state(self, new_state: AppState, status_message: Optional[str] = None):
        """Change application state and trigger UI update."""
        if new_state != self._current_state:
            self._current_state = new_state
            
            # Update status message based on state if not explicitly provided
            if status_message is not None:
                self._status_message = status_message
            else:
                self._status_message = self._get_default_status_message(new_state)
            
            # Trigger UI update callback
            if self._ui_update_callback:
                self._ui_update_callback(new_state)
    
    def _get_default_status_message(self, state: AppState) -> str:
        """Get default status message for a given state."""
        state_messages = {
            AppState.INITIALIZING: "Starting up...",
            AppState.READY: UIConstants.STATUS_READY,
            AppState.MODEL_LOADING: UIConstants.STATUS_MODEL_LOADING,
            AppState.RECORDING: UIConstants.STATUS_RECORDING,
            AppState.PROCESSING: UIConstants.STATUS_TRANSCRIBING,
            AppState.ERROR: "An error occurred",
            AppState.NO_MODEL: "Please select a Whisper model",
            AppState.NO_AUDIO: "Audio system not available"
        }
        return state_messages.get(state, UIConstants.STATUS_READY)
    
    def set_model_info(self, model_name: Optional[str]):
        """Update model information."""
        self._model_name = model_name
        
    def set_device_info(self, device_name: Optional[str]):
        """Update device information."""
        self._device_name = device_name
    
    def can_record(self) -> bool:
        """Check if recording is allowed in current state."""
        return self._current_state == AppState.READY
        
    def can_change_model(self) -> bool:
        """Check if model changes are allowed in current state."""
        return self._current_state in [AppState.READY, AppState.NO_MODEL, AppState.ERROR]
        
    def can_change_settings(self) -> bool:
        """Check if settings changes are allowed in current state."""
        return self._current_state != AppState.RECORDING
    
    def get_button_states(self) -> dict:
        """Get button states for current application state."""
        states = {
            'record_enabled': False,
            'record_text': UIConstants.BUTTON_RECORD,
            'record_command': 'record',
            'settings_enabled': True,
            'model_select_enabled': True
        }
        
        if self._current_state == AppState.READY:
            states['record_enabled'] = True
            states['record_text'] = UIConstants.BUTTON_RECORD
            states['record_command'] = 'record'
            
        elif self._current_state == AppState.RECORDING:
            states['record_enabled'] = True
            states['record_text'] = UIConstants.BUTTON_STOP
            states['record_command'] = 'stop'
            states['settings_enabled'] = False
            states['model_select_enabled'] = False
            
        elif self._current_state in [AppState.MODEL_LOADING, AppState.PROCESSING]:
            states['record_enabled'] = False
            states['settings_enabled'] = False
            states['model_select_enabled'] = False
            
        elif self._current_state in [AppState.NO_MODEL, AppState.NO_AUDIO, AppState.ERROR]:
            states['record_enabled'] = False
            
        return states