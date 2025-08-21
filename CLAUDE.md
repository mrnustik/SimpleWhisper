# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SimpleWhisper is a Python GUI application that provides speech-to-text functionality using OpenAI's Whisper model. The application records audio from a microphone, transcribes it using Whisper, and automatically copies the result to the clipboard.

## Architecture

The application follows a clean separation of concerns with specialized manager classes:

- `src/main.py`: Entry point that initializes and runs the MainWindow
- `src/MainWindow.py`: Primary GUI window with modern state-driven UI architecture
- `src/WhisperManager.py`: Manages Whisper model loading and transcription operations
- `src/AudioManager.py`: Handles all audio recording, device management, and integrated file operations
- `src/UIStateManager.py`: Centralized application state management system
- `src/UIConstants.py`: UI constants for consistent styling and messaging
- `src/GlobalHotkeyManager.py`: System-wide global hotkey management
- `src/SettingsWindow.py`: Audio device selection dialog
- `src/sound_file_writer.py`: Legacy utility (no longer used - functionality integrated into AudioManager)

### Key Dependencies
- **tkinter**: GUI framework
- **whisper**: OpenAI's speech-to-text model
- **sounddevice**: Audio recording interface
- **soundfile**: Audio file I/O
- **torch**: PyTorch backend for Whisper
- **pyperclip**: Clipboard operations
- **numpy**: Audio data processing
- **pynput**: Global hotkey support (system-wide keyboard shortcuts)

## Development Commands

### Installation
This project uses UV for modern Python dependency management with pyproject.toml configuration.

Install UV (if not already installed):
```bash
pip install uv
```

Install dependencies:
```bash
uv sync
```

### Running the Application
```bash
cd src
uv run python main.py
```

### Development Dependencies
Install development tools (linting, testing, etc.):
```bash
uv sync --group dev
```

### Global Hotkey Dependencies
The global hotkey functionality requires the `pynput` library. If you encounter issues with global hotkeys:
- On Windows: Usually works out of the box
- On Linux: May require additional packages (`python3-xlib`)
- On macOS: May require accessibility permissions for the terminal/IDE

## Key Components

### MainWindow (src/MainWindow.py:14)
- Modern state-driven UI architecture with proper separation of concerns
- Professional layout using Grid geometry manager with labeled frames
- Centralized state management via UIStateManager for consistent UI updates  
- Progress indicators and visual feedback for all operations
- Local keyboard shortcuts (Ctrl+R record, Ctrl+S stop, Ctrl+T settings)
- Global hotkey support (Ctrl+Shift+R toggle recording, Ctrl+Shift+S stop)
- Responsive design with proper window resizing behavior
- Enhanced status display with scrollable text area
- Toggle control for enabling/disabling global hotkeys

### WhisperManager (src/WhisperManager.py)
- Manages Whisper model loading and selection asynchronously
- Handles transcription operations in background threads
- Provides CUDA/CPU device detection for model execution
- Communicates results via callback system

### AudioManager (src/AudioManager.py)
- Handles all audio recording operations with proper thread management
- Manages audio device selection and stream creation
- Integrated file writer functionality (replaced external sound_file_writer)
- **Automatic file cleanup**: Removes temporary audio files after transcription
- **Startup cleanup**: Cleans up old temporary files left from previous sessions
- Coordinates temporary file creation and cleanup with built-in thread safety
- Provides callback-based status updates to UI

### UIStateManager (src/UIStateManager.py)
- Centralized application state management (Ready, Recording, Processing, etc.)
- State-driven UI updates ensure consistent interface behavior
- Button state management based on current application state
- Validation of user actions based on current state

### UIConstants (src/UIConstants.py)
- Centralized constants for consistent UI styling and messaging
- Local and global keyboard shortcut definitions
- Standardized dialog messages and status text
- Layout constants for spacing and sizing

### GlobalHotkeyManager (src/GlobalHotkeyManager.py)
- System-wide global hotkey registration and management
- Cross-platform hotkey support using pynput library
- Thread-safe callback scheduling for UI integration
- Hotkey validation and conflict detection
- Clean resource management and cleanup

### Audio Pipeline
- Audio recording uses sounddevice's InputStream with callback system
- Audio data is queued and written to temporary WAV files by AudioManager's integrated file writer
- Temporary files are created with 'delme_rec_gui_' prefix in the current directory
- **Automatic cleanup**: Temporary files are automatically deleted after transcription completes
- **Startup cleanup**: Old temporary files are cleaned up when the application starts
- **Error-safe cleanup**: Files are cleaned up even if transcription fails
- Device switching is handled seamlessly through AudioManager.set_device()
- File writing operations are fully integrated with error handling and thread management

### Device Management
- Audio device selection through SettingsWindow dialog (unchanged interface)
- Device changes are applied via AudioManager.set_device() method
- Supports multiple audio host APIs via sounddevice
- Error handling for device-related issues with user feedback

## File Patterns

Temporary audio files are created with the pattern `delme_rec_gui_*.wav` and should be considered disposable artifacts from recording sessions.