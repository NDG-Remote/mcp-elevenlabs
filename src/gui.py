import tkinter as tk
from tkinter import ttk, scrolledtext
import os
from datetime import datetime
import time
from main import setup_elevenlabs, text_to_speech, play_audio

class TextToSpeechGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ElevenLabs Text to Speech")
        self.root.geometry("800x600")
        
        # Initialize ElevenLabs client
        self.client = setup_elevenlabs()
        
        # Create main container
        self.main_container = ttk.Frame(root, padding="10")
        self.main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.main_container.columnconfigure(0, weight=1)
        self.main_container.columnconfigure(1, weight=2)
        self.main_container.rowconfigure(0, weight=1)
        
        # Left side - Input area
        self.create_input_area()
        
        # Right side - Chat display area
        self.create_chat_area()
        
        # Configure root grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        
        # Store audio files and their messages
        self.audio_messages = []

    def create_input_area(self):
        """Create the left side input area."""
        input_frame = ttk.LabelFrame(self.main_container, text="Input", padding="5")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        # Voice selection
        ttk.Label(input_frame, text="Voice:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.voice_var = tk.StringVar(value="Aria")
        self.voice_combo = ttk.Combobox(input_frame, textvariable=self.voice_var)
        self.voice_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        self.update_voice_list()
        
        # Text input
        ttk.Label(input_frame, text="Text to convert:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.text_input = scrolledtext.ScrolledText(input_frame, width=30, height=10)
        self.text_input.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Convert button
        self.convert_button = ttk.Button(input_frame, text="Convert to Speech", command=self.convert_text)
        self.convert_button.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Configure grid weights
        input_frame.columnconfigure(1, weight=1)
        input_frame.rowconfigure(2, weight=1)

    def create_chat_area(self):
        """Create the right side chat display area."""
        chat_frame = ttk.LabelFrame(self.main_container, text="Messages", padding="5")
        chat_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD)
        self.chat_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)

    def update_voice_list(self):
        """Update the voice selection dropdown with available voices."""
        try:
            response = self.client.voices.get_all()
            voices = [voice.name for voice in response.voices]
            self.voice_combo['values'] = voices
        except Exception as e:
            self.add_message(f"Error loading voices: {str(e)}")

    def add_message(self, message, is_audio=False, audio_file=None):
        """Add a message to the chat display."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.chat_display.insert(tk.END, f"[{timestamp}] {message}\n")
        
        if is_audio and audio_file:
            # Create a frame for the audio message
            audio_frame = ttk.Frame(self.chat_display)
            self.chat_display.window_create(tk.END, window=audio_frame)
            
            # Add the audio file name
            ttk.Label(audio_frame, text=f"Audio file: {os.path.basename(audio_file)}").pack(side=tk.LEFT, padx=5)
            
            # Add play button
            play_button = ttk.Button(audio_frame, text="Play Again", 
                                   command=lambda: play_audio(audio_file))
            play_button.pack(side=tk.LEFT, padx=5)
            
            # Add newline after the audio message
            self.chat_display.insert(tk.END, "\n")
        
        # Scroll to the bottom
        self.chat_display.see(tk.END)
        # Update the GUI
        self.root.update()

    def update_message(self, message, delay=0.2, is_audio=False, audio_file=None):
        """Update a message with a delay and GUI update."""
        self.add_message(message, is_audio=is_audio, audio_file=audio_file)
        time.sleep(delay)

    def convert_text(self):
        """Convert the input text to speech."""
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            self.add_message("Please enter some text to convert.")
            return
        
        # Disable the convert button while processing
        self.convert_button.state(['disabled'])
        
        try:
            # Add the input text to the chat (truncated to 10 characters)
            truncated_text = text[:16] + "..." if len(text) > 16 else text
            self.update_message(f"Converting text: {truncated_text}")
            
            # Add generating message
            self.update_message("Generating audio...")
            
            # Convert text to speech
            audio_file = text_to_speech(self.client, text, self.voice_var.get())
            
            # Add success message and audio file
            self.update_message("Audio generated successfully!", is_audio=True, audio_file=audio_file)
            
            # Play the audio (without showing message)
            play_audio(audio_file)
            
        except Exception as e:
            self.add_message(f"Error: {str(e)}")
        
        finally:
            # Re-enable the convert button
            self.convert_button.state(['!disabled'])
            
            # Clear the input field
            self.text_input.delete("1.0", tk.END)

def main():
    root = tk.Tk()
    app = TextToSpeechGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 