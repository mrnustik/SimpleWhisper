import threading
from typing import Optional, Callable, Dict, Any
import torch
import whisper


class WhisperManager:
    def __init__(self, on_model_loaded: Optional[Callable[[str], None]] = None,
                 on_transcription_complete: Optional[Callable[[str], None]] = None,
                 on_error: Optional[Callable[[str], None]] = None):
        self.model: Optional[whisper.Whisper] = None
        self.current_model_name: Optional[str] = None
        self.loading = False
        
        # Callbacks for UI updates
        self.on_model_loaded = on_model_loaded
        self.on_transcription_complete = on_transcription_complete
        self.on_error = on_error

    @staticmethod
    def get_device() -> str:
        """Get the best available device for Whisper model execution."""
        return 'cuda' if torch.cuda.is_available() else 'cpu'

    @staticmethod
    def get_available_models():
        """Get list of available Whisper models."""
        return whisper.available_models()

    def load_model_async(self, model_name: str) -> None:
        """Load a Whisper model asynchronously."""
        if self.loading:
            if self.on_error:
                self.on_error("Model is already loading. Please wait.")
            return
        
        if not model_name:
            if self.on_error:
                self.on_error("Please select a model first.")
            return

        self.loading = True
        thread = threading.Thread(target=self._load_model_worker, args=(model_name,))
        thread.daemon = True
        thread.start()

    def _load_model_worker(self, model_name: str) -> None:
        """Worker method to load model in background thread."""
        try:
            self.model = whisper.load_model(model_name)
            self.current_model_name = model_name

            self.loading = False

            if self.on_model_loaded:
                self.on_model_loaded(model_name)
                
        except Exception as e:
            self.model = None
            self.current_model_name = None
            self.loading = False

            if self.on_error:
                self.on_error(f"Failed to load model '{model_name}': {str(e)}")

    def transcribe_async(self, audio_file_path: str) -> None:
        """Transcribe an audio file asynchronously."""
        if not self.model:
            if self.on_error:
                self.on_error("No model loaded. Please select and load a model first.")
            return

        if not audio_file_path:
            if self.on_error:
                self.on_error("No audio file provided for transcription.")
            return

        thread = threading.Thread(target=self._transcribe_worker, args=(audio_file_path,))
        thread.daemon = True
        thread.start()

    def _transcribe_worker(self, audio_file_path: str) -> None:
        """Worker method to transcribe audio in background thread."""
        try:
            result = self.model.transcribe(audio_file_path)
            transcribed_text = result.get("text", "").strip()
            
            if self.on_transcription_complete:
                self.on_transcription_complete(transcribed_text)
                
        except Exception as e:
            if self.on_error:
                self.on_error(f"Transcription failed: {str(e)}")

    def is_model_loaded(self) -> bool:
        """Check if a model is currently loaded and ready."""
        return self.model is not None and not self.loading

    def get_current_model_name(self) -> Optional[str]:
        """Get the name of the currently loaded model."""
        return self.current_model_name

    def is_loading(self) -> bool:
        """Check if a model is currently being loaded."""
        return self.loading