# SimpleWhisper

A Python GUI application for speech-to-text transcription using OpenAI's Whisper model.

## Features

- Record audio from microphone
- Transcribe speech to text using Whisper models
- Automatic clipboard copying of transcribed text
- Audio device selection
- Configurable global hotkeys for system-wide recording control
- Local and global keyboard shortcuts
- Automatic temporary file cleanup
- Modern state-driven UI with progress indicators

## Requirements

- Python 3.9+
- Audio input device (microphone)

## Installation and Usage

1. **Install UV (if not already installed):**
   ```bash
   pip install uv
   ```

2. **Clone or download the project:**
   ```bash
   git clone <repository-url>
   cd SimpleWhisper
   ```

3. **Install dependencies:**
   ```bash
   cd src
   uv sync
   ```

4. **Run the application:**
   ```bash
   cd src
   uv run python main.py
   ```

## Keyboard Shortcuts

### Local Shortcuts (when app has focus)
- `Ctrl+R` - Start recording
- `Ctrl+S` - Stop recording  
- `Ctrl+T` - Open settings

### Global Shortcuts (configurable, work system-wide)
- `Ctrl+Shift+R` - Toggle recording (default)
- `Ctrl+Shift+S` - Stop recording (default)

Configure global hotkeys in Settings > Global Hotkeys tab.

## Settings

- **Audio Device**: Select microphone input device
- **Global Hotkeys**: Configure system-wide keyboard shortcuts
- **Whisper Model**: Choose transcription model for accuracy vs speed

Settings are automatically saved to `settings.json`.
