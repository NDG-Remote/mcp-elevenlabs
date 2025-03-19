# ElevenLabs Text-to-Speech CLI

A command-line interface and GUI application for converting text to speech using the ElevenLabs API.

## Setup

1. Create a virtual environment and activate it:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root and add your ElevenLabs API key:

```
ELEVENLABS_API_KEY=your_api_key_here
```

## Usage

### Command Line Interface

Basic usage:

```bash
python src/main.py "Your text here"
```

Options:

- `--voice`: Specify the voice to use (default: Aria)
- `--no-play`: Don't play the audio after generation
- `--list-voices`: List all available voices

Example with options:

```bash
python src/main.py "Hello, world!" --voice "Adam" --no-play
```

### Graphical User Interface

To launch the GUI application:

```bash
python src/gui.py
```

The GUI provides:

- A dropdown menu to select from available voices
- A text input area for entering text to convert
- A chat-like display showing conversion history
- Play buttons to replay generated audio
- Automatic playback of newly generated audio

## Output

Generated audio files are saved in the `output` directory with timestamps in the filename.
