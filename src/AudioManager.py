import queue
import tempfile
import threading
import tkinter as tk
import os
from typing import Optional, Callable
import sounddevice as sd
import soundfile as sf


class AudioManager:
    def __init__(self, 
                 on_recording_started: Optional[Callable[[], None]] = None,
                 on_recording_stopped: Optional[Callable[[], None]] = None,
                 on_file_ready: Optional[Callable[[str], None]] = None,
                 on_error: Optional[Callable[[str], None]] = None,
                 root: Optional[tk.Tk] = None):
        """
        Initialize AudioManager with callback system for UI integration.
        
        Args:
            on_recording_started: Called when recording starts
            on_recording_stopped: Called when recording stops
            on_file_ready: Called when audio file is ready for transcription (receives file path)
            on_error: Called when an error occurs (receives error message)
            root: Tkinter root for scheduling callbacks on main thread
        """
        # Callbacks for UI updates
        self.on_recording_started = on_recording_started
        self.on_recording_stopped = on_recording_stopped
        self.on_file_ready = on_file_ready
        self.on_error = on_error
        self.root = root
        
        # Audio system state
        self.stream: Optional[sd.InputStream] = None
        self.current_device = None
        
        # Recording state
        self.recording = False
        self.previously_recording = False
        self.audio_q = queue.Queue()
        
        # File and thread management
        self.current_filename: Optional[str] = None
        self.file_writer_thread: Optional[threading.Thread] = None
        
        # Initialize with default audio device
        self._create_stream()

    def _schedule_callback(self, callback: Callable, *args):
        """Schedule a callback to run on the main thread."""
        if callback and self.root:
            self.root.after(0, lambda: callback(*args))
        elif callback:
            # Fallback if no root provided
            callback(*args)

    def _create_stream(self, device=None):
        """Create audio input stream with specified device."""
        try:
            if self.stream is not None:
                self.stream.close()
                
            self.stream = sd.InputStream(
                device=device, 
                channels=1, 
                callback=self._audio_callback
            )
            self.stream.start()
            self.current_device = device
            
        except Exception as e:
            self.stream = None
            self._schedule_callback(self.on_error, f"Failed to create audio stream: {str(e)}")

    def _audio_callback(self, indata, frames, time, status):
        """Audio callback that handles data flow from stream to queue."""
        if status:
            # Log audio status issues but don't stop recording
            print(f"Audio callback status: {status}")
            
        if self.recording:
            self.audio_q.put(indata.copy())
            self.previously_recording = True
        else:
            if self.previously_recording:
                # Signal end of recording to file writer
                self.audio_q.put(None)
                self.previously_recording = False

    def set_device(self, device_id):
        """Change the audio input device."""
        if self.recording:
            self._schedule_callback(self.on_error, "Cannot change device while recording")
            return
            
        try:
            self._create_stream(device=device_id)
        except Exception as e:
            self._schedule_callback(self.on_error, f"Failed to set audio device: {str(e)}")

    def start_recording(self):
        """Start audio recording."""
        if self.recording:
            self._schedule_callback(self.on_error, "Recording is already in progress")
            return
            
        if not self.stream:
            self._schedule_callback(self.on_error, "No audio stream available. Check audio device.")
            return

        try:
            # Clear any leftover data in queue
            if self.audio_q.qsize() != 0:
                print(f"WARNING: Audio queue not empty ({self.audio_q.qsize()} items). Clearing...")
                while not self.audio_q.empty():
                    try:
                        self.audio_q.get_nowait()
                    except queue.Empty:
                        break

            # Create temporary file for recording
            self.current_filename = tempfile.mktemp(
                prefix='delme_rec_gui_', 
                suffix='.wav', 
                dir=''
            )

            # Start file writer thread
            self.file_writer_thread = threading.Thread(
                target=self._file_writer_worker,
                args=(
                    self.current_filename,
                    int(self.stream.samplerate),
                    self.stream.channels,
                ),
                daemon=True
            )
            self.file_writer_thread.start()

            # Start recording
            self.recording = True
            self._schedule_callback(self.on_recording_started)

        except Exception as e:
            self.recording = False
            self.current_filename = None
            self._schedule_callback(self.on_error, f"Failed to start recording: {str(e)}")

    def stop_recording(self):
        """Stop audio recording and wait for file completion."""
        if not self.recording:
            self._schedule_callback(self.on_error, "No recording in progress")
            return

        try:
            # Stop recording
            self.recording = False
            self._schedule_callback(self.on_recording_stopped)
            
            # Wait for file writer thread to complete
            self._wait_for_file_completion()

        except Exception as e:
            self._schedule_callback(self.on_error, f"Failed to stop recording: {str(e)}")

    def _wait_for_file_completion(self):
        """Wait for file writer thread to complete and signal file ready."""
        if self.file_writer_thread and self.file_writer_thread.is_alive():
            # Schedule another check in 10ms
            if self.root:
                self.root.after(10, self._wait_for_file_completion)
            else:
                # Fallback: block and wait
                self.file_writer_thread.join()
                self._file_completion_handler()
        else:
            self._file_completion_handler()

    def _file_writer_worker(self, filename: str, samplerate: int, channels: int):
        """Worker method to write audio data from queue to file."""
        try:
            with sf.SoundFile(
                file=filename,
                mode='x',
                samplerate=samplerate,
                channels=channels
            ) as f:
                while True:
                    data = self.audio_q.get()
                    if data is None:
                        # End of recording signal
                        break
                    f.write(data)
        except Exception as e:
            # Schedule error callback on main thread
            self._schedule_callback(self.on_error, f"Error writing audio file: {str(e)}")

    def _file_completion_handler(self):
        """Handle completion of file writing."""
        try:
            if self.file_writer_thread:
                self.file_writer_thread.join(timeout=1.0)  # Wait up to 1 second
                
            if self.current_filename:
                # File is ready for transcription
                self._schedule_callback(self.on_file_ready, self.current_filename)
            else:
                self._schedule_callback(self.on_error, "Recording completed but no file was created")
                
        except Exception as e:
            self._schedule_callback(self.on_error, f"Error completing file write: {str(e)}")
        finally:
            # Reset file writer thread
            self.file_writer_thread = None

    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self.recording

    def is_ready(self) -> bool:
        """Check if audio system is ready for recording."""
        return self.stream is not None and not self.recording

    def cleanup(self):
        """Clean up all audio resources."""
        try:
            # Stop recording if in progress
            if self.recording:
                self.recording = False
                
            # Wait for file writer thread
            if self.file_writer_thread and self.file_writer_thread.is_alive():
                self.file_writer_thread.join(timeout=2.0)
                
            # Close audio stream
            if self.stream:
                self.stream.close()
                self.stream = None
                
            # Clear queue
            while not self.audio_q.empty():
                try:
                    self.audio_q.get_nowait()
                except queue.Empty:
                    break
                    
        except Exception as e:
            print(f"Error during AudioManager cleanup: {e}")

    def get_current_device(self):
        """Get the current audio device ID."""
        return self.current_device

    def cleanup_audio_file(self, file_path: str) -> bool:
        """
        Clean up a temporary audio file.
        
        Args:
            file_path: Path to the audio file to delete
            
        Returns:
            True if cleanup was successful, False otherwise
        """
        if not file_path:
            return True
            
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Cleaned up temporary audio file: {file_path}")
                return True
            else:
                print(f"Audio file not found for cleanup: {file_path}")
                return True  # File doesn't exist, so cleanup is "successful"
                
        except Exception as e:
            print(f"Failed to cleanup audio file {file_path}: {e}")
            if self.on_error:
                self._schedule_callback(self.on_error, f"Failed to cleanup temporary file: {str(e)}")
            return False

    def __del__(self):
        """Ensure cleanup on object destruction."""
        self.cleanup()