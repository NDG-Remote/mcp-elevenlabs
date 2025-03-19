import os
import argparse
import subprocess
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from datetime import datetime

# Load environment variables
load_dotenv()

def setup_elevenlabs():
    """Set up ElevenLabs client."""
    api_key = os.getenv('ELEVENLABS_API_KEY')
    if not api_key:
        raise ValueError("ELEVENLABS_API_KEY not found in .env file")
    return ElevenLabs(api_key=api_key)

def get_voice_id(client: ElevenLabs, voice_name: str) -> str:
    """
    Get the voice ID for a given voice name.
    
    Args:
        client (ElevenLabs): ElevenLabs client instance
        voice_name (str): Name of the voice to find
    
    Returns:
        str: Voice ID if found, raises ValueError if not found
    """
    response = client.voices.get_all()
    for voice in response.voices:
        if voice.name.lower() == voice_name.lower():
            return voice.voice_id
    
    # If voice not found, list available voices and raise error
    available_voices = [v.name for v in response.voices]
    raise ValueError(f"Voice '{voice_name}' not found. Available voices: {', '.join(available_voices)}")

def text_to_speech(client: ElevenLabs, text: str, voice_name: str = "Aria") -> str:
    """
    Convert text to speech using ElevenLabs API.
    
    Args:
        client (ElevenLabs): ElevenLabs client instance
        text (str): Text to convert to speech
        voice_name (str): Name of the voice to use (default: Aria)
    
    Returns:
        str: Path to the generated audio file
    """
    # Get voice ID
    voice_id = get_voice_id(client, voice_name)
    
    # Generate audio
    audio_generator = client.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128"
    )
    
    # Collect all audio data from the generator
    audio_data = b''.join(audio_generator)
    
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"output/speech_{timestamp}.mp3"
    
    # Save the audio file
    with open(filename, 'wb') as f:
        f.write(audio_data)
    
    return filename

def play_audio(file_path: str):
    """
    Play audio file using macOS afplay command.
    
    Args:
        file_path (str): Path to the audio file
    """
    try:
        subprocess.run(['afplay', file_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error playing audio: {str(e)}")

def list_voices(client: ElevenLabs):
    """
    List all available voices.
    
    Args:
        client (ElevenLabs): ElevenLabs client instance
    """
    response = client.voices.get_all()
    print("\nAvailable voices:")
    for voice in response.voices:
        print(f"- {voice.name}")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Convert text to speech using ElevenLabs API')
    parser.add_argument('text', nargs='?', help='Text to convert to speech')
    parser.add_argument('--voice', default='Aria', help='Voice to use (default: Aria)')
    parser.add_argument('--no-play', action='store_true', help='Don\'t play the audio after generation')
    parser.add_argument('--list-voices', action='store_true', help='List available voices')
    
    args = parser.parse_args()
    
    try:
        # Set up ElevenLabs
        client = setup_elevenlabs()
        
        # List voices if requested
        if args.list_voices:
            list_voices(client)
            return
        
        # Check if text is provided
        if not args.text:
            parser.error("the following arguments are required: text")
        
        # Convert text to speech
        print("Generating audio...")
        audio_file = text_to_speech(client, args.text, args.voice)
        print(f"Audio saved to: {audio_file}")
        
        # Play the audio if not disabled
        if not args.no_play:
            print("Playing audio...")
            play_audio(audio_file)
            
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main() 